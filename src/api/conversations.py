from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlalchemy


# FastAPI is inferring what the request body should look like
# based on the following two classes.
class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]


router = APIRouter()

def check_input(movie_id, ch_id1, ch_id2):
    if ch_id1 == ch_id2:
        raise HTTPException(status_code=404, detail="characters are the same.")
    with db.engine.connect() as conn:  
        # check if movie exists
        mov_result = conn.execute(sqlalchemy.text("""
            SELECT movies.movie_id
            FROM movies
            WHERE movies.movie_id = :id
        """), [{"id": movie_id}])
        m = 0
        for row in mov_result:
            m +=1
        if m==0:
            raise HTTPException(status_code=404, detail="movie not found.")
        
        # check if characters exist and match movie
        char_result = conn.execute(sqlalchemy.text("""
            SELECT movies.movie_id, character_id
            FROM movies
            JOIN characters ON characters.movie_id = movies.movie_id
            WHERE (character_id = :ch_id1 OR
                character_id = :ch_id2)
        """), [{"ch_id1": ch_id1, "ch_id2": ch_id2}])
        for idx, row in enumerate(char_result):
            if row.movie_id != movie_id:
                raise HTTPException(status_code=404, detail="character and movie do not match") 
        if idx + 1 != 2:
            raise HTTPException(status_code=404, detail="character not found.")



def get_newIDs():
    # get the id of the last line 
    line_id_stmt = sqlalchemy.text("""
            SELECT line_id
            FROM lines
            ORDER BY line_id DESC
            LIMIT 1
        """)
    # get the id of the last conversation 
    conv_id_stmt = sqlalchemy.text("""
            SELECT conversation_id AS conv_id
            FROM conversations
            ORDER BY conversation_id DESC
            LIMIT 1
        """)
    with db.engine.connect() as conn:        
        line_id_result = conn.execute(line_id_stmt)
        conv_id_result = conn.execute(conv_id_stmt)
        ids = []
        # get the highest ids and add 1 for the new ids
        for row in conv_id_result:
            ids.append(row.conv_id + 1)
        for row in line_id_result:
            ids.append(row.line_id + 1)
        return ids
    

@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines between
    those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """ 
    check_input(movie_id, conversation.character_1_id, conversation.character_2_id)
    
    conv_id, line_id = get_newIDs()

    with db.engine.begin() as conn:
        # Insert new conversation
        conn.execute(
            sqlalchemy.text("""
                INSERT INTO conversations (conversation_id, character1_id, character2_id, movie_id) 
                VALUES (:w, :x, :y, :z)
            """),
                [{
                    "w": conv_id, 
                    "x": conversation.character_1_id, 
                    "y": conversation.character_2_id, 
                    "z": movie_id
                }]
        )

        # Insert each line in the conversation
        for idx, line in enumerate(conversation.lines):
            # check if lines character matches conversations character
            if (line.character_id != conversation.character_1_id
                and line.character_id != conversation.character_2_id):
                raise HTTPException(status_code=404, detail="character does not match line.")
            
            conn.execute(
                sqlalchemy.text("""
                    INSERT INTO lines (line_id, character_id, movie_id, conversation_id, line_sort, line_text) 
                    VALUES (:l_id, :ch_id, :m_id, :conv_id, :sort, :text)
                """),
                    [{
                        "l_id": line_id, 
                        "ch_id": line.character_id, 
                        "m_id": movie_id, 
                        "conv_id": conv_id,
                        "sort": idx + 1,
                        "text": line.line_text
                    }]
            )
            line_id += 1
        return conv_id

    

        
