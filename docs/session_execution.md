# Functions To Execute After a Player Completes a Session

## 1) complete_session(user)
### Purpose:
The complete_session(user) function records that a user has successfully completed a learning session.
- A session consists of:
    - 1 Focus ConceptNode
    - 0–4 Reinforcement ConceptNodes

The function validates that the session is legitimate before recording it in the database.

### Preconditions

- The function assumes the following conditions:
    1) A session has already been generated for the user via get_session(user).
    2) The Focus ConceptNode must be completed by the user before the session can be recorded.
    3) Reinforcement nodes come from previously completed ConceptNodes.

If the Focus ConceptNode is not completed, the session will not be recorded.

### High Level Workflow

- The function performs the following steps:
    1. Retrieve the user's current session using get_session(user)
    2. Extract:
        - focus_node
        - reinforcement_nodes
    3. Validate that the focus_node is completed
   using UserNodeProgress
    4. Record the session in SessionCompletion
    5. Attach reinforcement nodes to the session    
    6. Return the created SessionCompletion record

### Validation Logic

- Before recording the session, the backend verifies that the focus node is actually completed by the user
- If the focus node is not completed, the backend raises the ValueError("Focus ConceptNode is not completed yet.").
- This prevents the frontend or malicious clients from recording fake sessions.



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