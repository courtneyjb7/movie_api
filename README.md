
- "Document the areas where your code would not function. In particular, consider multiple simultaneous calls to your service (i.e., race conditions/reentrancy)."

If there are multiple simultaneous calls, they could each be given the same conversation or line IDs, but be posting different conversations/lines. There is no race condition handling, so calls do not wait on each other to complete. In terms of reentrancy, if a call is made while another is executing, there is no interrupt handler in place to either keep the new call waiting, or interrupt the current call and resume it once the new call is done. The pytests sometimes time out, so my code may also not be able to handle a database that is a lot greater in size.  
