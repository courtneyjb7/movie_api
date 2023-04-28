from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime
from src.datatypes import Conversation, Line


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
    
    movie = db.movies.get(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="movie not found.")
    
    ch1 = db.characters.get(conversation.character_1_id)
    ch2 = db.characters.get(conversation.character_2_id)
    # check that the characters exist in the given movie and are not the same
    if not ch1 or not ch2:
        raise HTTPException(status_code=404, detail="character not found.")  
    if ch1==ch2:
        raise HTTPException(status_code=404, detail="characters are the same.") 
    if ch1.movie_id != movie_id or ch2.movie_id != movie_id:
        raise HTTPException(status_code=404, detail="character and movie do not match") 
    
    # check that lines match the characters
    for line in conversation.lines: 
        if not (line.character_id == ch1.id or line.character_id == ch2.id):
            raise HTTPException(status_code=404, detail="character does not match line.")

    # update conversations
    if len(db.conv_log) == 0:
        new_conv_id = 0
    else:
        new_conv_id = int(db.conv_log[-1]["conversation_id"]) + 1
    db.conv_log.append({
        "conversation_id": new_conv_id,
        "character1_id": ch1.id, 
        "character2_id": ch2.id, 
        "movie_id": movie_id
    })
    db.conversations[new_conv_id] = Conversation(
        new_conv_id, 
        ch1.id,
        ch2.id,
        movie_id,
        len(conversation.lines)
    )
    db.upload_conversations()

    # update lines
    if len(db.lines_log) == 0:
        new_line_id = 0
    else:
        new_line_id = int(db.lines_log[-1]["line_id"]) + 1
    for idx, line in enumerate(conversation.lines):
        db.lines_log.append({
            "line_id": new_line_id,
            "character_id": line.character_id,
            "movie_id": movie_id,
            "conversation_id": new_conv_id,
            "line_sort": idx + 1,
            "line_text": line.line_text
        })
        db.lines[new_line_id] = Line(
            new_line_id,
            line.character_id,
            movie_id,
            new_conv_id,
            idx + 1,
            line.line_text
        )
        new_line_id += 1
        # update character's num of lines
        db.characters[line.character_id].num_lines += 1
    db.upload_lines()
    return new_conv_id
        
