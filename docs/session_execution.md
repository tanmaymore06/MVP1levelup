# Functions To Execute After a Player Completes a Session

## 1) complete_session(user)
### This function persist what the user actually completed in a Session without modifying streaks, visibility, or progression. 

#### Algorithm:
1. Gets the session of the user, using the get_session(user) which is already documented in the derived-state-logic markdown,
2. Extracts the focus node and the reinforcement nodes (if any reinforcement nodes exists),
3. Record in the SessionCompletion model, and
4. Return the record.