from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

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
    conv = db.conversations.get(conv_id)
    conv_lines = filter(
            lambda l: l.conv_id == conv_id,
            db.lines.values(),
        )
    if conv:
        result = {
            "movie_title": db.movies[conv.movie_id].title,
            "ch1": db.characters[conv.c1_id].name,
            "ch2": db.characters[conv.c2_id].name,
            "lines": (
                {
                    "character": db.characters[line.c_id].name,
                    "line": line.line_text
                }
                for line in conv_lines
            ),
        }
    
        return result

    raise HTTPException(status_code=404, detail="movie not found.")


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
    line = db.lines.get(line_id)
    if line:
        conv_lines = filter(
            lambda l: l.conv_id == line.conv_id,
            db.lines.values(),
        )

        conv = db.conversations[line.conv_id]
        character = db.characters[line.c_id].name
        result = {
            "line_id": line_id,
            "character_name": character,
            "movie_title": db.movies[line.movie_id].title,
            "text": line.line_text,
            "conv_id": line.conv_id,
            "other_character_name": db.characters[conv.c1_id].name or None
                                   if db.characters[conv.c1_id].name != character
                                   else db.characters[conv.c2_id].name or None,
            "num_conv_btw_chars": len(list(filter(
                                    lambda conv: conv.movie_id == line.movie_id
                                    and (conv.c1_id == line.c_id or conv.c2_id == line.c_id),
                                    db.conversations.values(),
                                ))),
            "conversation": [
                conv.line_text
                for conv in conv_lines
            ]
        }
        return result

    raise HTTPException(status_code=404, detail="line not found.")


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
