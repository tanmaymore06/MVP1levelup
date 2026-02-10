# Level Up 1st MVP — Database Schema

## Core Entities

- <B>MainQuest</B>
  - Represents a linear learning chapter
- <B>ConceptNode</B>
  - Represents a single mathematical concept
- <B>ConceptNodePage</B>
  - Represents a Markdown-backed reading page
- <B>UserNodeProgress</B>
  - Records that a user has completed a ConceptNode
- <B>SessionCompletion</B>
  - Records that a user has completed a Session(Focus + Reinforcement)

## Entity-Relationship Model
<figure> 
<img src="Database Schema (1st MVP).jpeg">
</figure>

## Relationship Explanations
- <B>User ↔ ConceptNode</B> (via <B>UserNodeProgress</B>)

    <B>Relationship type</B>: Many-to-Many

    <B>Meaning</B>:
    A user can complete many concept nodes,
    and a concept node can be completed by many users.

    <B>Why UserNodeProgress exists</B>:
    To record the fact “User X has completed Concept Node Y”.
---------------------------

- <B>User ↔ SessionCompletion</B>

    <B>Relationship type</B>: One-to-Many

    <B>Meaning</B>:
    A user can complete multiple learning Sessions,
    and each SessionCompletion belongs to exactly one user.

    <B>What SessionCompletion represents</B>:
    A SessionCompletion records a single completed learning Session,
    consisting of:
    - one Focus ConceptNode, and
    - zero or more Reinforcement ConceptNodes.

    <B>Important distinction</B>:
    SessionCompletion records <U>what the user worked on</U>,
    not <U>what the user has completed</U>.
----------------------------

- <B>SessionCompletion ↔ ConceptNode</B>

    <B>Relationship type</B>:
    - Many-to-One (Focus ConceptNode)
    - Many-to-Many (Reinforcement ConceptNodes)

    <B>Meaning</B>:
    Each SessionCompletion:
    - focuses on exactly one ConceptNode (the pending node), and
    - may reinforce multiple previously completed ConceptNodes.

    <B>Why this relationship exists</B>:
    Learning Sessions are experiential.
    A user may revisit completed concepts for reinforcement
    without changing their completion state.

    <B>What this does NOT imply</B>:
    A ConceptNode appearing in a SessionCompletion
    does not mean it is newly completed.
    Completion state is recorded only in <B>UserNodeProgress</B>.
----------------------------


- <B>MainQuest → ConceptNode</B>

    <B>Relationship type</B>: One-to-Many

    <B>Meaning</B>:
    One Main Quest contains multiple Concept Nodes.

    <B>Why this relationship exists</B>:
    Main Quests group nodes into logical chapters and define progression order.
-------------------------------


- <B>ConceptNode → ConceptNodePage</B>

    <B>Relationship type</B>: One-to-Many

    <B>Meaning</B>:
    One Concept Node consists of multiple reading pages.

    <B>Why this relationship exists</B>:
    To support multi-page learning with sequential navigation.
---------

- <B>ConceptNode → UserNodeProgress</B>

    <B>Relationship type</B>: One-to-Many

    <B>Meaning</B>:
    A Concept Node can be completed by many users.

    <B>Why this matters</B>:
    Progress is user-specific, not content-specific.

## Design Principles

- Only two irreversible user actions are stored, which are:
  - SessionCompletion stores immutable learning events (Sessions), while UserNodeProgress stores irreversible progression state.
- Everything else is derived i.e., computed at runtime. For example, 
    - <B>All learning states are derived</B> (e.g., "pending node", "completed node", "visible node", "non-visible node"), 
    - <B>Unlocking Logic</B>: A Concept Node and also a Main Quest is unlock if and only if, all the previous nodes are <U>"completed"</U>, and
    - <B>Session</B>: All the nodes in the Session are derived based on state of a node.
- Content rendering is frontend responsibility.


-------------------------------------------------

# Content Contract (Backend → Frontend)

## Content Storage
- ConceptNodePage.content stores RAW Markdown
- Backend does NOT render, sanitize, or parse content

## Frontend Responsibilities
Frontend MUST:
- Render Markdown
- Support LaTeX-style math (KaTeX / MathJax)
- Support embedded media (images, GIFs, video)

## Allowed Content
- Plain text
- Mathematical notation
- Embedded HTML inside Markdown

Backend treats content as opaque text.

-------------------------------------------------

# Core Backend Questions

1. What is the user's pending ConceptNode?
2. Which ConceptNodes are visible to the user?
3. What is today's Session?
4. How many nodes are completed in the current MainQuest?
5. Can the user mark this node as completed?
<B>and many such questions...</B>

All backend features must answer one of these.
