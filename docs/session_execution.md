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


## 2) Evaluating Streak [evaluate_streak_if_needed(user)]

### The Problem :
- Evaluating streak can be straight-forward if we use the Cron-job but, because I am building this system for the first time, I don't want to increase the complexity anymore and just want to keep this system as simple as possible. So, how can i calculate Streak anad Freeze streak day-by-day without using the Cron-job ?

### Solution :
- Let's say there is a new player 'test4' who opened this system today, for the first time. The 'test4' completed one Session today. 

- The 'evaluate_streak_if_needed(user)' function, records an entry in the UserStreakState model with the following properties:

        "user" : test4
        "streak": 0,
        "freeze_streak": 0,
        "consecutive_zero_session_days": 0,
        "last_evaluated_date": today - timedelta(days=1) [that is, the day before today]

- Current_date is just (last_evaluated_date+1). While current_date<=today, we create session_count using the information from the UserNodeProgress and need to handle two cases:
    - Case 1 (Player completed at least one session): 
        - If session_count >= 1: increment streak, and consecutive_zero_session_days = 0.
        - If session_count > 2: increment freeze streak (caped at 5)
    - Case 2 (Player completed zero sessions):
        - increment consecutive_zero_session_days
        - if consecutive_zero_session_days <= 2:
            - if Freeze streak > 0: decrement Freeze straeak
        - else: 
            - streak = 0 and consecutive_zero_session_days = 0
    - increment the Current_date.
- Set last_evaluated_date to today and save the updated 1st record in the UserStreakState. 

- This is called as the 'lazy evaluation' because the backend cannot evaluate streak everyday only when the frontend calls this function. Then the function will calculate all the days right from the last_evaluated_date till today. 
- Essentially:
    - evaluate_streak_if_needed(user)
        - process past days
        - update streak state