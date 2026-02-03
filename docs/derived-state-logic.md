<h1>Derived State Logic (MVP-1)</h1>

# 1. Core Principle (Foundational)

    Only irreversible facts are stored. Everything else is derived.

<b>Stored fact:</B>

- A user has completed a ConceptNode (UserNodeProgress)

<B>Derived states:</B>

- completed ConceptNode

- pending ConceptNode

- past / current / future MainQuest

- visible / non-visible MainQuest (per user)

- Daily Quest (Focus Pool + Reinforcement Pool)


No derived state is persisted in the database.

This approach ensures:

- no duplicated state

- no inconsistent flags

- clean scalability for future maps and progression rules

-----------------------------

# 2. ConceptNode States
## 2.1 Completed Node

<B>Definition</B>
A ConceptNode is completed <U>iff</U>:

There exists a <B>UserNodeProgress</B> row for <B>(user, concept_node)</B>

<B>Important properties</B>
- Completion is irreversible

- Completed nodes remain accessible forever

- Completed nodes can be reopened and reread

- Completed nodes may appear in the Reinforcement Pool

This is the <B>only stored learning fact.</B>

-------------------------------------------------------

## 2.2 Pending Node (Exactly One)

<B>Definition</B>
The pending node is:

    The first ConceptNode (by order) in the current MainQuest that the user has NOT completed.

<B>Key rules</B>

- There is at most one pending node

- If user has completed nothing → first node is pending

- If user completed everything → no pending node exists

<B>Behavior</B>

- Appears at the top of the Focus Pool

- Has a “Mark as Understood” action

- Completion of this node unlocks the next node


-------------------------------------------------------

# 3. MainQuest — (Publication vs Visibility)
## 3.1 Publication (is_published)

"is_published" is a <B>content-level, global flag</B>.

- **is_published = False**

    - MainQuest is considered work-in-progress
    - ignored by all progression logic
    - non-existent from the user’s perspective

- **is_published = True**

    - MainQuest is eligible for progression logic

    - does not automatically imply visibility

---------------------------------------------------------

## 3.2 User-Facing Visibility (Derived)

Visibility is not stored.

For a given user, a published MainQuest can be in exactly one of the following derived states:

---------------------------------------------------

### 3.2.1 Past/Completed MainQuest

- all ConceptNodes are completed by the user

- no pending ConceptNode exists

<B>Behavior:</B>

- visible to the user

- fully accessible for re-reading

-------------------------------------------------------

### 3.2.2 Current/Active MainQuest

- not fully completed

- contains the user’s pending ConceptNode

<B>Behavior:</B>

- visible to the user

- active progression state

<B>Invariant:</B>

- Exactly one Current MainQuest exists per user.

------------------------------------------------------

### 3.2.3 Future MainQuest

- published

- ordered after the Current MainQuest

- user has completed zero ConceptNodes in it

<B>Behavior:</B>

- ***non-visible*** to the user

- exists logically but hidden

-------------------------------------------------------

## 3.3 Visibility Rule (Authoritative)

A MainQuest is visible to a user if and only if:

- is_published = True, and

- it is either:

    - a Past MainQuest, or

    - the Current MainQuest

-------------------------------------------------------

# 4. ConceptNode Visibility

ConceptNode visibility is inherited from its MainQuest:

- if MainQuest is non-visible → all ConceptNodes are non-visible

- if MainQuest is visible:

    - completed nodes are re-readable

    - the pending node is actionable

    - future nodes may be shown as locked (frontend decision)

No visibility flags are stored on ConceptNode.

-------------------------------------------------------



# 5. MainQuest Progression (Critical)
<b>MainQuest is considered completed if:</B>

- ALL its ConceptNodes are completed by the user

<B>Current MainQuest:</B>

- First MainQuest (in order) that is NOT fully completed

- Inferred, never stored

This ensures:

- Strict linear progression,

- No ambiguity,

- No partial quest hopping in MVP-1.

-----------------------------------------------------

# 6. Session (Earlier "Daily Quest")  

It’s a learning orchestration mechanism, which is different, and unique than the Daily Quests found in the other learning platforms.

It consists of two Pools:
- Focus Pool, and 
- Reinforcement Pool.

------------------------------------------------

## 6.1 Focus Pool (Structured Learning)

<B>Earlier Definition</B>
An ordered list of ConceptNodes consisting of:

    1. The pending node (least dependent)

    2. The next consecutive nodes in the current MainQuest

##### <B>Updated and Current Definition
Now the Focus Pool must contain only one ConceptNode, which is the pending of the user. WHY?</B> Because, one should not learn many new things in a single day, otherwise the person would not be able to grasp one new thing, fully.

<B>Earlier Rules</B>

- Ordered from least → most dependent

- Size depends on completion ratio in current MainQuest

- All nodes link to written explanations (Markdown)

- Completing the pending node may:

    - unlock the next node

    - change tomorrow’s Focus Pool

##### <B>Updated and Current Rules</B>

- As the Focus Pool only has one ConceptNode which is the user's Pending ConceptNode, it returns pending ConceptNode of the user otherwise 'None' if, no pending ConceptNode of the user exists.
- Size of the Focus Pool will always be one ConceptNode i.e., the Pending ConceptNode. No need of the completion ratio to determine size.
- The pending node link to written explanation (Markdown)
- Completing only the Focus Pool i.e, the pending node will not update the Session, as the Session needs the user to complete both, the Focus Pool and the Reinforcement Pool.

<B>Purpose</B>

- Forward progress

- Conceptual continuity

- No randomness

-----------------------------------------------

## 6.2 Reinforcement Pool (Retention)

<B>Definition</B>
A list of ConceptNodes:

- Randomly selected from the already completed nodes. That is, completed nodes from the current/active MainQuest and all the completed/past MainQuests.

<B>Rules</B>

- Never includes pending node

- Never includes non-visible nodes

- Size of the Reinforcement Pool will always be four.
- Size of the Reinforcement Pool is static.
    - <B>[Earlier]</B> Size also depends on completion ratio
- Links to written explanations

<b>Purpose</B>

- Reinforce earlier concepts

- Prevent forgetting

- Encourage spaced repetition

-------------------------------------------------------

# 7. Session Lifecycle (Earlier "Daily Quest Lifecycle")

#### <B>Earlier -</B>
    If Daily Quest is completed:

        - Streak increments by 1

        - Tomorrow’s Daily Quest is newly generated

    If Daily Quest is NOT completed:

        - Streak resets to 0

        - Tomorrow shows the same Daily Quest

    This creates:

        - Soft pressure

        - No punishment

        - Psychological continuity

#### <B>Updated and Current -</B>

- If the Player completes the Focus Pool and the Reinforcement Pool, the Session updates immedietly.
- The Player can complete any number of Sessions in one day.
- If the Player completes only one Session in one day then, the Streak increments by one.
- If the Player completes more than two Sessions in one day then, the Freeze Streak increments by one. 
    - The Freeze Streak, freezes the Streak count if, the Player missed to complete at least one Session in one day.
    - The Player can have at most five Freeze Streak.
    - The Freeze Streak cannot be used if, the Player misses more than two consecutive days. This esures that, even if you have some Freeze Streak, you are not allowed to miss more than two consecutive days. 
- If the Player is on his third consecutive missed day then, even if having the Freeze Streak, the Streak count will be reset to zero.
- If the Player is on his first or on the second consecutive missed day and the Freeze Streak count is zero then, the Streak count will be reset to zero. 

------------------------------------------------------

# 8. System Invariants (Must Always Hold)

- No unpublished MainQuest participates in progression

- Exactly one Current MainQuest per user

- At most one pending ConceptNode per MainQuest per user

- Focus Pool never violates ConceptNode order

- Reinforcement Pool contains only completed nodes

- Visibility is always derived, never stored

Any violation indicates a logic error.

------------------------------------------------------
------------------------------------------------------

# Derived State Functions

### 1. Which ConceptNodes are Completed By The User ? [<I>get_completed_nodes(user)</I>]  

A ConceptNode is considered "completed" for a user if and only if
there exists a UserNodeProgress entry for that (user, concept_node) pair.


- <B>What This Function Must Do </B>

    Given a user, it must:

    Look at UserNodeProgress
    Find which ConceptNodes the user has completed
    Return them as a queryset of ConceptNode

    - Work correctly even if:
       - user has completed nothing, and
       - tables are empty

- This logic:
    - works, even with empty databases
    - returns an empty queryset for new users
    - is used as the foundation for all progression rules

-------------------------------------------------
<br>

### 2. What is the user's current MainQuest ?[get_current_main_quest(user)]

Answers <B>one precise question:</B>

    Among all published MainQuests, which one is the user currently progressing through?

By definition, this is:

<B>The first published MainQuest (by order) that is NOT fully completed by the user.</B>

If none exists → return "All Published MainQuests are completed OR, other MainQuests are not yet been Published".

#### Step-by-Step Logical Breakdown 

For a given user:

- Get all published MainQuests, ordered

- For each MainQuest:

    - Count how many ConceptNodes it has

    - Count how many of those the user has completed

The first MainQuest where, <B>completed < total</B> is the current MainQuest

If all published MainQuests are completed → return "All Published MainQuests are completed OR, other MainQuests are not yet been Published".

-------------------------------------------------------
<br>

### 3. Which ConceptNode is Pending For the User ? [get_pending_node(user)]


#### Purpose:
To determine exactly one actionable ConceptNode that the user should work on next, ensuring strict progression through MainQuests and their ConceptNodes.

#### Definition:

get_pending_concept_node(user) returns the first incomplete ConceptNode, ordered by dependency (order), belonging to the user’s current published MainQuest.

#### How the “Current MainQuest” Is Determined ?

- The current MainQuest is defined as:

    - The first published MainQuest (ordered globally by order)
    - That is not fully completed by the user

- A MainQuest is considered fully completed if the user has completed all of its ConceptNodes.

#### Detailed Behavior:

1. All published MainQuests are considered, ordered by progression.

2. The system identifies the current MainQuest as the first published MainQuest that the user has not fully completed.

3. Within this MainQuest:
All ConceptNodes are ordered by their dependency order.
The function selects the first ConceptNode that the user has not completed.

4. That ConceptNode is returned as the pending ConceptNode.

#### Return Value:

- Returns a ConceptNode instance if progression is possible.

- Returns "None" only if the user has completed all ConceptNodes in all published MainQuests.

#### Invariants (Always True):

- At most one pending ConceptNode exists per user.

- If a pending ConceptNode exists, it is always:

- Visible

    - Actionable

    - The least dependent incomplete ConceptNode

- Pending ConceptNode automatically advances when the user completes it.

#### Applying all the Previous Derived-state Functions on Dummy Data

##### - Current State of the Dummy Data:
    - In total, there are three users, "user1 = test1", "user2 = Tanmay", and "user3 = test3".

    - There are total of three MainQuests, and their respective titles are:
        - "MQ1", "MQ2", and "MQ3".

    - The MQ1 has three ConceptNode, and their respective titles are:
        - "MQ1_CN1", "MQ1_CN2", and "MQ1_CN3".
        - This MainQuest is published.

    - The MQ2 has two ConceptNode, and their respective titles are:
        - "MQ2_CN1" and "MQ2_CN2".
        - This MainQuest is also published.

    - The MQ3 has only one ConceptNode, and it's title is:
        - "MQ3_CN1".
        - This MainQuest is not published.

    - The MQ1_CN1 has two ConceptNodePage, and their respective titles are:
        - "MQ1_CN1_CP1", and "MQ1_CN1_CP2".

    - The MQ1_CN2 has four ConceptNodePage, and their respective titles are:
        - "MQ1_CN2_CP1", "MQ1_CN2_CP2", "MQ1_CN2_CP3", and "MQ1_CN2_CP4".

    - The MQ1_CN3 has three ConceptNodePage, and their respective titles are:
        - "MQ1_CN3_CP1", "MQ1_CN3_CP2", and "MQ1_CN3_CP3".

    - The MQ2_CN1 has three ConceptNodePage, anad their respective titles are:
        - "MQ2_CN1_CP1", "MQ2_CN1_CP2", and "MQ2_CN1_CP3.

    - The MQ2_CN2 has two ConceptNodePage, anad their respective titles are:
        - "MQ2_CN2_CP1", and "MQ2_CN2_CP2".

    - The MQ3_CN1 has only one ConceptNodepage, and it's title is:
        - "MQ3_CN1_CP1".

    - The "test1" has completed only the MQ1_CN1, the "Tanmay" has completed all the ConceptNode of the MQ1, and the "test3" has completed all ConceptNodes of all the Published MainQuests. 
<br>

- <b>For the "user1 = test1":</b>
    - the "get_completed_nodes(user1)" returns:
        - "<QuerySet [<ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN1 CNOrder: 1>]>"
    - the "get_current_main_quest(user1)" returns:
        - <MainQuest: MQTitle: MQ1 MQDesc: This is the 1st MainQuest.>
    - the "get_pending_node(user1)" returns:
        - <ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN2 CNOrder: 2>
<br>
- <b>For the "user2 = Tanmay":</b>
    - the "get_completed_nodes(user2)" returns:
        - <QuerySet [<ConceptNode: MQTitle: MQ1 CNTitle:    MQ1_CN1 CNOrder: 1>, <ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN2 CNOrder: 2>, <ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN3 CNOrder: 3>]>
    - the "get_current_main_quest(user2)" returns:
        - <MainQuest: MQTitle: MQ2 MQDesc: This is the 2nd MainQuest.>
    - the "get_pending_node(user2)" returns:
        - <ConceptNode: MQTitle: MQ2 CNTitle: MQ2_CN1 CNOrder: 1>    
    <br>
- <b>For the "user3 = test3":</b>
    - the "get_completed_nodes(user2)" returns:
        - <QuerySet [<ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN1 CNOrder: 1>, <ConceptNode: MQTitle: MQ2 CNTitle: MQ2_CN1 CNOrder: 1>, <ConceptNode: MQTitle: MQ3 CNTitle: MQ3_CN1 CNOrder: 1>, <ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN2 CNOrder: 2>, <ConceptNode: MQTitle: MQ2 CNTitle: MQ2_CN2 CNOrder: 2>, <ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN3 CNOrder: 3>]>
    - the "get_current_main_quest(user2)" returns:
        - None
    - the "get_pending_node(user2)" returns:
        - None
<br>
- <b>Hence, all the previuos derived-state functions are behaving as expected.</b>
-------------------------------------------------------------
<br>

## ----------Visibility Functions
### 4. Which MainQuests are Visible to the User at any Point in Time ? [get_visible_main_quests(user)] 

#### Definition

A MainQuest is visible to the user if and only if:

<b>The MainQuest is published, 
AND
The MainQuest is either:
        
    the user’s current MainQuest, or
    a previously completed MainQuest

Future MainQuests (even if published) are not visible.</b>

### Detailed Behaviour
1. All published MainQuests are considered, ordered by global progression order.

2. The system determines the user’s current MainQuest as:

    - the first published MainQuest that is not fully completed by the user.

3. Visibility is derived as follows:

    - If a current MainQuest exists:

        - All published MainQuests up to and including the current MainQuest are visible.

    - If no current MainQuest exists:

        - The user has completed all published MainQuests.
        - All published MainQuests are visible.

#### Return Value

- Returns an ordered QuerySet of MainQuest objects.

- Returns an empty QuerySet only if no MainQuests are published.
<br>

### 5. Given a MainQuest, Which ConceptNodes are visible to the User ? [get_visible_nodes(user, main_quest)]

#### Definition

A ConceptNode is visible to a user if and only if its parent MainQuest is visible to the user.

#### Detailed Behavior

1. The system determines all visible MainQuests for the user.

2. If the given MainQuest is not visible:

    - No ConceptNodes from that MainQuest are visible.

3. If the given MainQuest is visible:

    - All ConceptNodes belonging to that MainQuest are visible.

    - ConceptNodes are ordered by their dependency order.

#### Return Value

- Returns an ordered QuerySet of ConceptNode objects.

- Returns an empty QuerySet if the MainQuest is not visible to the user.

### Applying The Two Visibilty Functions On The Dummy Data

#### State of the Dummy Data:
- It is same as described in the third function.

#### get_visible_main_quests(user)

- For the <b>"user = user1 = test1"</b>:
"""
<QuerySet [<MainQuest: MQTitle: MQ1 MQDesc: This is the 1st MainQuest.>]>
"""
- For the <b>"user = user2 = Tanmay"</b>:
"""
<QuerySet [<MainQuest: MQTitle: MQ1 MQDesc: This is the 1st MainQuest.>, <MainQuest: MQTitle: MQ2 MQDesc: This is the 2nd MainQuest.>]>
"""
- For the <b>"user = user3 = test3"</b>:
"""
<QuerySet [<MainQuest: MQTitle: MQ1 MQDesc: This is the 1st MainQuest.>, <MainQuest: MQTitle: MQ2 MQDesc: This is the 2nd MainQuest.>]>
"""

#### get_visible_nodes(user, main_quest)

- For the <b>"user = user1 = test1" and "main_quest = mq1" </b>:
"""
<QuerySet [<ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN1 CNOrder: 1>, <ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN2 CNOrder: 2>, <ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN3 CNOrder: 3>]>
"""
- For the <b>"main_quest = mq2"</b>:
"""
"""
- For the <b>"main_quest = mq3"</b>:
"""
"""

- For the <b>"user = user2 = Tanmay" and "main_quest = mq1" </b>:
"""
<QuerySet [<ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN1 CNOrder: 1>, <ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN2 CNOrder: 2>, <ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN3 CNOrder: 3>]>
"""
- For the <b>"main_quest = mq2"</b>:
"""
<QuerySet [<ConceptNode: MQTitle: MQ2 CNTitle: MQ2_CN1 CNOrder: 1>, <ConceptNode: MQTitle: MQ2 CNTitle: MQ2_CN2 CNOrder: 2>]>
"""
- For the <b>"main_quest = mq3"</b>:
"""
"""

- For the <b>"user = user3 = test3" and "main_quest = mq1" </b>:
"""
<QuerySet [<ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN1 CNOrder: 1>, <ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN2 CNOrder: 2>, <ConceptNode: MQTitle: MQ1 CNTitle: MQ1_CN3 CNOrder: 3>]>\
"""
- For the <b>"main_quest = mq2"</b>:
"""
<QuerySet [<ConceptNode: MQTitle: MQ2 CNTitle: MQ2_CN1 CNOrder: 1>, <ConceptNode: MQTitle: MQ2 CNTitle: MQ2_CN2 CNOrder: 2>]>
"""
- For the <b>"main_quest = mq3"</b>:
"""
"""

<b>Hence, the two Visibility Functions are working as expected.</b>

----------------------------------------------------
<br>

## ----------Session Derivation Functions

### 6) What must be the Current Action of the User ? [get_focus_pool(user)]

#### Responsibility

- Return the single ConceptNode that the user should focus on right now.

#### Definition

- The Focus Pool contains exactly one ConceptNode:
the pending ConceptNode of the user.

- Input:

    - user (Django User instance)

- Output:

    - ConceptNode instance OR

    - None (if no pending ConceptNode exists)

#### Applying the get_focus_pool function on the Dummy Data

- We know that, the "user1 = test1" has completed only the MQ1_CN1, which mean, the get_focus_pool should return MQ1_CN2.

- For the "user2 = Tanmay" who completed all the three ConceptNodes of the MQ1, the get_focus_pool should return the MQ2_CN1.

- While the "user3 = test3" who has completed all the ConceptNodes of all the Published MainQuests, the et_focus_pool returns 'None'. 

<br>

### 7) Which ConceptNodes the user should Reinforce Now ? [get_reinforcement_pool(user)]

#### Purpose

- Return a reinforcement pool of exactly 4 ConceptNodes, designed to reinforce prior learning while the user works on the current Session.

#### ConceptNode eligibility

- A ConceptNode is eligible iff:

    - It is completed by the user, which also means it's MainQuest is published, and
    - It belongs to:
        - the current MainQuest, or
        - a previously completed MainQuest

#### Pool size rule
- If the user has fewer than 6 completed ConceptNodes total →
return an empty QuerySet.

#### Sampling Rules (VERY IMPORTANT)

- When eligible nodes ≥ 6:
    - Select exactly two distinct MainQuests

    - One may be the current MainQuest

    - Both may be completed MainQuests

- From each selected MainQuest, randomly select:
    - 2 completed ConceptNodes

- Total reinforcement pool size = 4

#### Return type

- A list of exactly 4 ConceptNode objects OR an empty list ([]) if conditions are not met

- List, not QuerySet — because:
    - ordering is irrelevant

#### Applying the get_reinforcement_pool(user) on the Dummy Data

- We know that, the "user1=test1" has completed only the MQ1_CN1, and his focus pool is the MQ1_CN2 so, the reinforcement pool is [].
- The "user2=Tanmay" has completed all the three nodes of the MQ1 and his focus pool is the MQ2_CN1 and hence, the reinforcement pool is [].
- The "user3=test3" has completed all the nodes of all the published MainQuests and his focus pool is None and because he completed at least two MainQuests, his reinforcement pool is non-empty list.

<br>

### 8) The Current Session of the User ? [get_session(user)]

<B>A Session is a dictionary which consists of - 
- The Focus Pool : One pending ConceptNode,
- The Reinforcement Pool : A List of four Random Completed ConceptNodes.</B>
