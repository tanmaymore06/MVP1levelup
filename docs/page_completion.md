# Page Completion Service - [complet_page(user, page_id)]
<br>

## Overview
- The Page Completion Service is responsible for recording when a user completes a learning page and determining whether the completion of that page results in the completion of the corresponding Concept Node.

- This service belongs to the progress domain because it modifies user progress state rather than learning content.

- The service operates on the page level of the learning hierarchy and forms the first step of the progression pipeline.

## Learning Hierarchy

- User learning progression follows the structure:

    User
    ↓
    ConceptNodePage
    ↓
    ConceptNode
    ↓
    MainQuest

- Progress is recorded at two levels:
    - Page level → recorded in UserPageProgress
    - Node level → recorded in UserNodeProgress
- Page completion therefore acts as the trigger for node completion checks.

## Responsibilities

- The Page Completion Service performs four responsibilities.

<B>1. Validate Page Existence</B>

    - The service ensures that the requested page exists in the content system before recording progress.

    - This prevents invalid progress records from being created.

<B>2. Record Page Completion</B>

    - When a page is completed, a UserPageProgress record is created linking:

        - the user

        - the completed page

        - the timestamp of completion

A user can complete a page only once. Duplicate completions are ignored.

<B>3. Evaluate Concept Node Completion</B>

- After recording page completion, the service evaluates whether the user has now completed all pages belonging to the ConceptNode.

- If all pages of the node are completed, the node is considered completed.

<B>4. Record Concept Node Completion</B>

- If the node is newly completed, a UserNodeProgress record is created.

- This marks the concept as permanently completed for that user.

- Node completion is therefore derived from page completion, not recorded independently.

## Progression Rule

- A ConceptNode is considered completed if and only if all of its pages have been completed by the user.

- This rule ensures:

    - sequential learning

    - complete reading of all concept material

    - deterministic progression.

## Idempotency

- The service is designed to be idempotent.

- If a user attempts to complete a page that has already been completed:

    - no duplicate progress record is created, the system simply returns the current completion state.

- This guarantees safe retries in the event of network failures or repeated client requests.

## Atomicity

- Page completion and potential node completion are treated as a single atomic operation.

- This ensures that the system never enters an inconsistent state where:

    - a page is marked completed, but the node completion evaluation is not performed.

## Scope Boundaries

- The Page Completion Service intentionally limits its responsibilities.

- It does not handle:

    - session creation

    - reinforcement selection

    - streak updates

    - unlocking logic

    - frontend navigation.

    - Those concerns belong to separate services.

## Role in the Learning Pipeline

- The Page Completion Service is the first step in the progression pipeline.

- The broader learning flow is:

        Page Completion
                ↓
        Concept Node Completion
                ↓
        Session Completion
                ↓
        Streak Evaluation

- This separation keeps each component simple and ensures the system remains maintainable as the platform evolves.

## Design Philosophy

- The service follows the core architectural principle of the system:

- Only irreversible learning actions are stored.

- Page completion represents a permanent user action and therefore must be persisted. Higher-level learning states are derived from these stored facts.