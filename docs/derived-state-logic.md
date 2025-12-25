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

### 3.2.2 Current/Actice MainQuest

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

# 6. Daily Quest 

It’s a learning orchestration mechanism, which is different, and unique than the Daily Quests found in the other learning platforms.

It consists of two Pools:
- Focus Pool, and 
- Reinforcement Pool.

------------------------------------------------

## 6.1 Focus Pool (Structured Learning)

<B>Definition</B>
An ordered list of ConceptNodes consisting of:

    1. The pending node (least dependent)

    2. The next consecutive nodes in the current MainQuest

<B>Rules</B>

- Ordered from least → most dependent

- Size depends on completion ratio in current MainQuest

- All nodes link to written explanations (Markdown)

- Completing the pending node may:

    - unlock the next node

    - change tomorrow’s Focus Pool

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

- Size also depends on completion ratio

- Links to written explanations

<b>Purpose</B>

- Reinforce earlier concepts

- Prevent forgetting

- Encourage spaced repetition

-------------------------------------------------------

# 7. Daily Quest Lifecycle

<B>If Daily Quest is completed:</B>

- Streak increments by 1

- Tomorrow’s Daily Quest is newly generated

<B>If Daily Quest is NOT completed:</B>

- Streak resets to 0

- Tomorrow shows the same Daily Quest

This creates:

- Soft pressure

- No punishment

- Psychological continuity

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