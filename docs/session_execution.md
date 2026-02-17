# Functions To Execute After a Player Completes a Session

## 1) complete_session(user)
### This function persist what the user actually completed in a Session in the 'SessionCompletion' model and then advances the progression by recording in the UserNodeProgress.

#### Algorithm:
1. Gets the session of the user, using the get_session(user) which is already documented in the derived-state-logic markdown,
2. Extracts the focus node and the reinforcement nodes (if any reinforcement nodes exists),
3. Record in the SessionCompletion model,
4. Advance progression by recording the focus node in the UserNodeProgress, and   
5. Return the record of the SessionCompletion.


## How Backend Can Know A Session is truly Completed Or Not ?

A Session is complete if and only if:
- The user finishes the last ConceptNodePage of the focus node
- The user completes all required reinforcement ConceptNodes
- The frontend explicitly signals completion to the backend

The flow is like:
- Frontend calls the "get_session(user)", the backend response with the required data in the JSON form, and then the frontend renders it
- The frontend knows how user is moving page by page, whether the user completes the last page,etc., In short, the frontend knows when the ConceptNode is completed or not
- If the frontend comes to know a user has completed all the nodes including the focus and reinforcement in a Session then, calls the "complete_session(user)"
- The backend gets the current Session, records it in the SessionCompletion model and marks the Focus/Pending node completed in the UserNodeProgess model leaving the reinforcement nodes untouched (because they're already completed historically), and makes the next Session available immedietly