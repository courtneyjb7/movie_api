from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
import sqlalchemy

router = APIRouter()


@router.get("/lines/conv/{conv_id}", tags=["lines"])
def get_char_conversations(conv_id: int):
    """
    This endpoint returns a conversation by its identifier. For the conversation it returns:
    * `movie_title`: The title of the movie the conversation is in.
    * `ch1`: the name of one character in the conversation.
    * `ch2`: the name of the other character in the conversation.
    * `lines`: a dictionary of lines that make up the conversation.

    Each line is represented by a dictionary with the following keys:
    * `character`: the name of the character saying the line.
    * `line`: the text of the line.

    """
    stmt = sqlalchemy.text("""
                    SELECT title, name, line_text, 
                            (conversations.character1_id = characters.character_id) AS is_ch1
                    FROM conversations
                    JOIN movies ON movies.movie_id = conversations.movie_id
                    JOIN lines ON lines.conversation_id = conversations.conversation_id
                    JOIN characters ON lines.character_id = characters.character_id
                    WHERE conversations.conversation_id = :id
                    ORDER BY lines.line_sort
                """)
    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"id": conv_id}])
        json = {}
        for idx, row in enumerate(result):
            if idx == 0:
                json = {
                    "movie_title": row.title,  
                    "ch1": None,
                    "ch2": None,
                    "lines":[]
                }
            if json["ch1"] == None and row.is_ch1:
                json["ch1"] = row.name
            elif json["ch2"] == None and not row.is_ch1:
                json["ch2"] = row.name
            json["lines"].append(
                {
                    "character": row.name,
                    "line": row.line_text
                }
            ) 
    if json != {}:      
        return json
    
    raise HTTPException(status_code=404, detail="conversation not found.")


@router.get("/lines/{line_id}", tags=["lines"])
def get_line(line_id: int):
    """
    This endpoint returns a single line by its identifier. For each line it returns:
    * `line_id`: the internal id of the line.
    * `character_name`: the name of the character saying the line
    * `movie_title`: The title of the movie the line is from.
    * `text`: the text of the line
    * `conv_id`: the id of the conversation the line is in
    * `other_character_name`: the name of the other character in the conversation
    * `num_conv_btw_chars`: the number of conversations between these characters in the movie
    * `conversation`: list of the rest of the lines in the conversation

    """
    
    stmt = sqlalchemy.text("""                            
            SELECT line_id, name, title, line_text,
                    lines.conversation_id AS conv_id, 
                    characters.character_id AS speaker_id
            FROM lines
            JOIN characters ON characters.character_id = lines.character_id
            JOIN movies ON movies.movie_id = lines.movie_id
            WHERE lines.line_id = :id                           
        """)
    

    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"id": line_id}])
        json = {}
        
        for idx, row in enumerate(result):
            if idx==0:                
                json = {
                    "line_id": line_id,
                    "character_name": row.name,
                    "movie_title": row.title,
                    "text": row.line_text,
                    "conv_id": row.conv_id,
                    # "other_character_name": None,
                    # "num_conv_btw_chars" : None,
                    # "conversation": []
                }
                conv_id = row.conv_id
                speaker_id = row.speaker_id
    if json == {}:
        raise HTTPException(status_code=404, detail="line not found.")
    # num_conv_stmt = sqlalchemy.text("""                            
    #         SELECT COUNT(conversations) AS num_conv
    #         FROM conversations
    #         WHERE (conversations.character1_id = :ch_id1 and conversations.character2_id = :ch_id2) OR 
    #             (conversations.character2_id = :ch_id1 and conversations.character2_id = :ch_id2)                       
    #     """)
    return json


class lines_sort_options(str, Enum):
    movie_title = "movie_title"
    character_name = "character_name"


# Add get parameters
@router.get("/lines/", tags=["lines"])
def list_movies(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: lines_sort_options = lines_sort_options.movie_title,
):
    """
    This endpoint returns a list of lines. For each line it returns:
    * `line_id`: the internal id of the line. Can be used to query the
      `/lines/{line_id}` endpoint.
    * `movie_title`: The title of the movie that the line is in.
    * `character_name`: The name of the character that said the line.
    * `line_sort`: The order the line is said in the conversation.
    * `line_text`: The line itself.

    You can filter for lines whose text contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `character_name` - Sort by character name alphabetically.
    """
    if sort is lines_sort_options.movie_title:
        stmt = sqlalchemy.text("""                            
            SELECT line_id, line_sort, line_text, movies.title, characters.name
            FROM lines                             
            JOIN characters ON characters.character_id = lines.character_id 
            JOIN movies ON movies.movie_id = lines.movie_id
            WHERE line_text ILIKE :text    
            ORDER BY movies.title, lines.line_id         
            LIMIT :limit 
            OFFSET :offset                     
        """)
    elif sort is lines_sort_options.character_name:
        stmt = sqlalchemy.text("""                            
            SELECT line_id, line_sort, line_text, movies.title, characters.name
            FROM lines                             
            JOIN characters ON characters.character_id = lines.character_id 
            JOIN movies ON movies.movie_id = lines.movie_id
            WHERE line_text ILIKE :text
            ORDER BY characters.name, lines.line_id
            LIMIT :limit
            OFFSET :offset                     
        """)
    else:
        assert False
    
    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"text": f"%{name}%",
                                      "offset": offset,
                                      "limit": limit}])
        json = []
        for row in result:
            json.append(
                {
                    "line_id": row.line_id,
                    "movie_title": row.title,
                    "character_name": row.name,
                    "line_sort": row.line_sort,
                    "line_text": row.line_text
                }
            )

    return json
