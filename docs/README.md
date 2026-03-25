# Level Up

> *A Gamified Math Educational Platform*

---

## The Problem With Existing Platforms

Every major mathematics learning platform makes a version of the same tradeoff: accessibility over depth, coverage over understanding, engagement over rigor.

**Brilliant.org** excels at interactive problem solving. A learner engages with a concept directly rather than passively watching it explained. However, its structure beyond problem sets is weak — there is no coherent progression logic that mirrors how mathematical ideas actually depend on one another.

**Khan Academy** covers an extraordinary breadth of mathematics. This is precisely its limitation. A platform optimized for coverage cannot be optimized for depth. A learner can move through dozens of topics without genuinely understanding any of them. The video-first format encourages passive consumption rather than active engagement.

**Duolingo** demonstrates that gamification can drive consistent learning habits. However, its game mechanics — streaks, gems, leaderboards, animated characters — are entirely disconnected from the subject being learned. The reward system is fictional. A learner is motivated to maintain a streak, not to understand the material. The platform optimizes for retention metrics, not for learning outcomes.

The common failure across all three is this: **none of them treat mathematics as a game in itself.**

Mathematics already has the structure of a game. It has precise rules, open problems, logical dependencies between ideas, and the deepest intellectual rewards of any discipline. A well-designed learning system should derive its structure from mathematics — not impose an artificial game layer on top of it.

---

## The Vision

Level Up is being built on three principles:

### 1. Progression Derived From Mathematics Itself

The structure of Level Up mirrors how mathematics actually works. One concept leads to another because of logical dependency, not designer preference. A learner cannot proceed to a new idea until the preceding idea is genuinely understood. Completion unlocks the next concept because that is how mathematics works — not because a progress bar demands it.

Game features in Level Up are not decorative. The streak system rewards consistent engagement. The session system enforces spaced repetition. The focus pool ensures a learner works on exactly one new concept at a time. Every mechanic has a mathematical or pedagogical justification.

### 2. Depth Over Breadth

Level Up does not attempt to cover all of mathematics. It introduces a small number of foundational ideas and explores them completely before advancing. The content follows the logical structure of mathematics — a few core concepts, explored deeply, generating the conflicts and questions that motivate the next layer of ideas.

One pending concept per session. One honest step at a time.

### 3. Formal Mathematics as the Long-Term Direction

Future versions of Level Up will integrate the Lean proof assistant directly into the learning experience. The long-term goal is a system where learners do not merely read about mathematical ideas but construct and verify mathematical arguments themselves — the way professional mathematicians work. MVP-1 establishes the foundation on which this capability will be built.

---

## This Repository — MVP-1

MVP-1 is the first step toward the full vision. It establishes the core learning engine and the architectural foundation the system will grow on.

### What MVP-1 Delivers

- **Linear progression engine** — strict concept-by-concept advancement through published MainQuests and ConceptNodes
- **Session system** — each session contains one Focus Node (new learning) and up to four Reinforcement Nodes (spaced repetition from completed concepts)
- **Streak system** — rewards daily consistency with freeze tokens that protect against occasional missed days, without resetting progress punitively
- **REST API** — a complete backend API serving all learning states to any frontend client
- **Derived state architecture** — all learning states (pending node, visible quests, session composition) are computed at runtime from a minimal set of stored facts

### What MVP-1 Does Not Include

- Interactive problem solving
- Lean proof assistant integration
- Social or competitive features
- Mobile application
- Content beyond the foundational curriculum

These are deliberate omissions, not oversights. MVP-1 is scoped to validate the core progression engine before building on top of it.

---

## Technical Documentation

- [Database Schema](docs/schema.md)
- [Derived State Logic](docs/derived-state-logic.md)
- [Page Completion Service](docs/page_completion.md)
- [Session Execution](docs/session_execution.md)
- [API Reference](docs/api-reference.md)

---

## Tech Stack

| Concern | Technology |
|---|---|
| Backend | Django |
| Database | PostgreSQL |
| API | Django REST Framework |
| Authentication | DRF Token Authentication |

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL

### Setup

**1. Clone the repository**
```bash
git clone https://github.com/your-username/level-up.git
cd level-up
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create a `.env` file in the project root**
```
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
```

**5. Run migrations**
```bash
python manage.py migrate
```

**6. Create a superuser**
```bash
python manage.py createsuperuser
```

**7. Run the development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`.
Django Admin will be available at `http://localhost:8000/admin/`.

### Adding Content

All content — MainQuests, ConceptNodes, and ConceptNodePages — is managed through Django Admin. Content follows this hierarchy:

```
MainQuest
    ↓
ConceptNode
    ↓
ConceptNodePage (raw Markdown)
```

Set `is_published = False` while authoring content. Set `is_published = True` to make a MainQuest visible to users in the progression engine.

---

## Architecture Overview

Level Up is built on one foundational principle:

**Only irreversible user actions are stored. Everything else is derived.**

### Stored Facts

| Model | What It Records |
|---|---|
| `UserPageProgress` | User completed a specific page |
| `UserNodeProgress` | User completed a specific concept |
| `SessionCompletion` | User completed a full session |
| `UserStreakState` | Cached streak state for lazy evaluation |

### Derived States

All learning states are computed at runtime from stored facts:

| State | Derived From |
|---|---|
| Pending ConceptNode | First incomplete node in current MainQuest |
| Current MainQuest | First published MainQuest not fully completed |
| Visible MainQuests | All completed quests + current quest |
| Session | Focus pool + reinforcement pool |
| Streak | Lazy evaluation from SessionCompletion history |

No derived state is persisted. This ensures no duplicated state, no inconsistent flags, and clean scalability.

### Service Layer

```
page_progression.py     → page and concept completion
progression.py          → pure derived-state logic (no DB writes)
session_execution.py    → session recording and streak evaluation
```

### Progression Pipeline

```
1. User opens app
        ↓
2. GET /api/quests/          → show MainQuest structure
   GET /api/session/         → show session in sidebar
        ↓
3. User has two paths to progress:

   PATH A — via MainQuest structure:        PATH B — via Session sidebar:
   Click a visible MainQuest                Click the Focus Node directly
        ↓                                        ↓
4. GET /api/quests/<quest_id>/nodes/        GET /api/nodes/<node_id>/pages/
   → show ConceptNodes with their states    → show first page
        ↓                                        ↓
   User clicks the pending ConceptNode           ↓
        ↓                                        ↓
   GET /api/nodes/<node_id>/pages/               ↓
   → show first page                             ↓
        ↓                                        ↓
         ----------------both lead here----------
                            ↓
5. User clicks Next on each page
        ↓
6. POST /api/pages/<page_id>/complete/   (on every Next click)
   → if node_completed: true → enable "Finish Session" button
        ↓
   User may optionally re-visit Reinforcement Nodes from the Session sidebar
   (completed nodes — no completion tracking required)
        ↓
7. User clicks "Finish Session"
        ↓
8. POST /api/session/complete/
    → response is new session → update UI immediately
    → GET /api/quests/ again → update MainQuest structure
        ↓
9. User opens Dashboard
        ↓
10. GET /api/dashboard/
    → show streak, stats
```