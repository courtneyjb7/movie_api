
- "Document the areas where your code would not function. In particular, consider multiple simultaneous calls to your service (i.e., race conditions/reentrancy)."

If there are multiple simultaneous calls, they could each be given the same conversation or line IDs, but be posting different conversations/lines. This could mean lines meant for different conversations may share a conversation ID. The pytests sometimes time out, so my code may not be able to handle a database that is a lot greater in size.  