from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db
import sqlalchemy

router = APIRouter()

@router.get("/characters/{id}", tags=["characters"])
def get_character(id: int):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """

    char_stmt = sqlalchemy.text("""
                SELECT character_id, name, title, gender 
                FROM characters
                JOIN movies ON movies.movie_id = characters.movie_id
                WHERE characters.character_id = (:id)
              """)
    conv_stmt = sqlalchemy.text("""
                  SELECT character1_id, character2_id, COUNT(lines) AS num_lines, name, gender,  characters.character_id
                  FROM conversations
                  JOIN lines ON conversations.conversation_id = lines.conversation_id
                  JOIN characters ON characters.character_id = character1_id OR characters.character_id = character2_id 
                  WHERE (character1_id = :id AND characters.character_id = character2_id) OR
                        (character2_id = :id AND characters.character_id = character1_id)

                  GROUP BY conversations.character1_id, conversations.character2_id, characters.name, characters.gender, characters.character_id
                  ORDER BY num_lines DESC, characters.character_id ASC
                """)
    with db.engine.connect() as conn:
        char_result = conn.execute(char_stmt, [{"id": id}])
        conv_result = conn.execute(conv_stmt, [{"id": id}])
        json = {}
        for row in char_result:
            json["character_id"] = row.character_id
            json["character"] = row.name
            json["movie"] = row.title
            json["gender"] = row.gender
            json["top_conversations"] = []
        for row in conv_result:
            json["top_conversations"].append(
                {
                    "character_id": row.character_id,
                    "character": row.name,
                    "gender": row.gender,
                    "number_of_lines_together": row.num_lines
                }
            ) 
    if json != {}:      
        return json
    
    raise HTTPException(status_code=404, detail="character not found.")


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """

    # if sort is character_sort_options.character:
    #     order_by = """characters.name"""
    # elif sort is character_sort_options.movie:
    #     order_by = """title"""
    # elif sort is character_sort_options.number_of_lines:
    #     order_by = """number_of_lines DESC"""
    # else:
    #     assert False
    if sort is character_sort_options.character:
        stmt = sqlalchemy.text("""                            
            SELECT title, characters.character_id, name, COUNT(lines) AS number_of_lines
            FROM characters                             
            JOIN movies ON movies.movie_id = characters.movie_id
            JOIN lines ON characters.character_id = lines.character_id
            WHERE name ILIKE :char_name
            GROUP BY movies.title, characters.character_id 
            ORDER BY characters.name ASC, characters.character_id ASC             
            OFFSET :offset         
            LIMIT :limit                     
        """)
    elif sort is character_sort_options.movie:
        stmt = sqlalchemy.text("""                            
            SELECT title, characters.character_id, name, COUNT(lines) AS number_of_lines
            FROM characters                             
            JOIN movies ON movies.movie_id = characters.movie_id
            JOIN lines ON characters.character_id = lines.character_id
            WHERE name ILIKE :char_name
            GROUP BY movies.title, characters.character_id 
            ORDER BY title ASC, characters.character_id ASC             
            OFFSET :offset         
            LIMIT :limit                     
        """)
    elif sort is character_sort_options.number_of_lines:
        stmt = sqlalchemy.text("""                            
            SELECT title, characters.character_id, name, COUNT(lines) AS number_of_lines
            FROM characters                             
            JOIN movies ON movies.movie_id = characters.movie_id
            JOIN lines ON characters.character_id = lines.character_id
            WHERE name ILIKE :char_name
            GROUP BY movies.title, characters.character_id 
            ORDER BY number_of_lines DESC, characters.character_id ASC             
            OFFSET :offset         
            LIMIT :limit                     
        """)
    else:
        assert False
    
    #ORDER BY :order_by, characters.character_id ASC  

    
    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"char_name": f"%{name}%",
                                      # "order_by": order_by, 
                                      "offset": offset,
                                      "limit": limit}])
        json = []
        for row in result:
            json.append(
                {
                    "character_id": row.character_id,
                    "character": row.name,
                    "movie": row.title,
                    "number_of_lines": row.number_of_lines
                }
            )

    return json
