- should we still test lines.py, and if so, how to hardcode if the data is being updated?
- ok to just test status code?
- "Document the areas where your code would not function. In particular, consider multiple simultaneous calls to your service (i.e., race conditions/reentrancy)."

If there are multiple simultaneous calls, they could each be given the same conversation ID, but be posting different conversations. 