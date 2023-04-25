
- "Document the areas where your code would not function. In particular, consider multiple simultaneous calls to your service (i.e., race conditions/reentrancy)."

If there are multiple simultaneous calls, they could each be given the same conversation or line IDs, but be posting different conversations/lines. There is no race condition handling, so calls do not wait on each other to complete. The pytests sometimes time out, so my code may not be able to handle a database that is a lot greater in size.  
