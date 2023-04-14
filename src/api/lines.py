from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()

@router.get("/lines/{line_id}", tags=["lines"])
def get_line(line_id: int):
    """
    This endpoint returns a single movie by its identifier. For each movie it returns:
    * `movie_id`: the internal id of the movie.
    * `title`: The title of the movie.
    * `top_characters`: A list of characters that are in the movie. The characters
      are ordered by the number of lines they have in the movie. The top five
      characters are listed.

    Each character is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `num_lines`: The number of lines the character has in the movie.

    """
    json = "hello"
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
    sort: lines_sort_options = lines_sort_options.character_name,
):
    """
    This endpoint returns a list of lines. For each line it returns:
    * `line_id`: the internal id of the line. Can be used to query the
      `/lines/{line_id}` endpoint.
    * `movie_title`: The title of the movie that the line is in.
    * `character_name`: The name of the character that said the line.
    * `line_sort`: The order the line is said in the conversation.
    * `line_text`: The line itself.

    You can filter for movies whose titles contain a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `character_name` - Sort by character name alphabetically.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    if name:

        def filter_fn(l):
            return l.line_text and name.lower() in l.line_text

    else:

        def filter_fn(_):
            return True
    
    items = list(filter(filter_fn, db.lines.values()))
    if sort == lines_sort_options.movie_title:
        items.sort(key=lambda l: l.movie_id)
    elif sort == lines_sort_options.character_name:
        items.sort(key=lambda l: l.c_id)
    # elif sort == lines_sort_options.rating:
    #     items.sort(key=lambda m: m.imdb_rating, reverse=True)

    json = (
        {
            "line_id": l.id,
            "character_name": db.characters[l.c_id].name,
            "movie_title": db.movies[l.movie_id].title,
            "line_sort": l.line_sort,
            "line_text": l.line_text,
        }
        for l in items[offset : offset + limit]
    )

    return json
