# Level Up — API Reference

## Audience
This document is written for the frontend developer.
It describes every available endpoint, what it expects, and what it returns.
The backend derives all learning states — the frontend only reads and renders.

---

## Base URL
```
http://localhost:8000/api/
```

---

## Authentication

All endpoints require authentication except `/auth/register/` and `/auth/login/`.

### How to authenticate
Every request (except register and login) must include this header:
```
Authorization: Token <your_token>
```

### How to get a token
Call `POST /api/auth/login/` with valid credentials.
The response includes a `token` field — store it and attach it to all future requests.

---

## Standard Error Responses

| Status | Meaning | Response body |
|---|---|---|
| `400` | Bad request / validation error | `{"detail": "..."}` or field errors |
| `401` | Missing or invalid token | `{"detail": "Authentication credentials were not provided."}` |
| `403` | Authenticated but not permitted | `{"detail": "..."}` |
| `404` | Resource not found | `{"detail": "..."}` |

---

## Auth Endpoints

### Register
```
POST /api/auth/register/
```
**Authentication required:** No

**Request body:**
```json
{
    "username": "tanmay",
    "password": "securepassword123",
    "email": "tanmay@example.com"
}
```
- `email` is optional
- `password` minimum 8 characters

**Success response — `201 Created`:**
```json
{
    "token": "a9f3c2e1b4d7...",
    "user": {
        "id": 1,
        "username": "tanmay",
        "email": "tanmay@example.com"
    }
}
```
Store the `token` immediately. Use it for all subsequent requests.

---

### Login
```
POST /api/auth/login/
```
**Authentication required:** No

**Request body:**
```json
{
    "username": "tanmay",
    "password": "securepassword123"
}
```

**Success response — `200 OK`:**
```json
{
    "token": "a9f3c2e1b4d7...",
    "user": {
        "id": 1,
        "username": "tanmay",
        "email": "tanmay@example.com"
    }
}
```

**Failure response — `401`:**
```json
{"detail": "Invalid credentials."}
```

---

### Logout
```
POST /api/auth/logout/
```
**Authentication required:** Yes

**Request body:** None

**Success response — `200 OK`:**
```json
{"detail": "Logged out successfully."}
```
After logout, the token is invalidated. The frontend must discard the stored token.

---

## Quest Endpoints

### List Visible MainQuests
```
GET /api/quests/
```
**Authentication required:** Yes

**Description:**
Returns all MainQuests visible to the current user — completed quests and the current quest.
Future/locked quests are never included.

**Success response — `200 OK`:**
```json
[
    {
        "id": 1,
        "title": "Introduction to Sets",
        "order": 1,
        "is_completed": true
    },
    {
        "id": 2,
        "title": "Functions and Relations",
        "order": 2,
        "is_completed": false
    }
]
```

**Field reference:**

| Field | Type | Description |
|---|---|---|
| `id` | integer | Use to fetch nodes: `GET /api/quests/{id}/nodes/` |
| `title` | string | Display name |
| `order` | integer | Global progression order, ascending |
| `is_completed` | boolean | `true` if all nodes completed |

**Rules:**
- List is ordered by `order` ascending
- The last item where `is_completed: false` is the current quest
- All items where `is_completed: true` are completed quests

---

### List ConceptNodes in a MainQuest
```
GET /api/quests/<quest_id>/nodes/
```
**Authentication required:** Yes

**Success response — `200 OK`:**
```json
[
    {
        "id": 3,
        "title": "Introduction to Relations",
        "order": 1,
        "state": "completed"
    },
    {
        "id": 4,
        "title": "What is a Function?",
        "order": 2,
        "state": "pending"
    },
    {
        "id": 5,
        "title": "Types of Functions",
        "order": 3,
        "state": "locked"
    }
]
```

**The `state` field:**

| Value | Meaning | Frontend behavior |
|---|---|---|
| `"completed"` | User finished this node | Show as done, allow re-reading |
| `"pending"` | User's current actionable node | Highlight, this is what user works on |
| `"locked"` | Not yet reachable | Show as locked, not clickable |

**Rules:**
- Exactly one node will have `state: "pending"` in the current quest
- Completed nodes are clickable for re-reading
- List is ordered by `order` ascending

**Error responses:**
- `404` — quest does not exist
- `403` — quest exists but is not visible to this user

---

### List Pages in a ConceptNode
```
GET /api/nodes/<node_id>/pages/
```
**Authentication required:** Yes

**Description:**
Returns all pages for a ConceptNode in order.
The frontend is responsible for sequential navigation.

**Success response — `200 OK`:**
```json
[
    {
        "id": 11,
        "title": "Introduction",
        "content": "# Introduction\n\nIn this node we will learn...",
        "order": 1
    },
    {
        "id": 12,
        "title": "Definition",
        "content": "# What is a Function?\n\nA function is...",
        "order": 2
    },
    {
        "id": 13,
        "title": "",
        "content": "## Summary\n\nToday we covered...",
        "order": 3
    }
]
```

**Field reference:**

| Field | Type | Description |
|---|---|---|
| `id` | integer | Use when marking complete: `POST /api/pages/{id}/complete/` |
| `title` | string | May be empty string `""` |
| `content` | string | Raw Markdown — frontend must render |
| `order` | integer | Sequential order, ascending |

**Content rendering rules:**
- `content` is raw Markdown
- Must support LaTeX math notation (use KaTeX or MathJax)
- May contain embedded HTML inside Markdown

**Navigation rules:**
- Show one page at a time
- "Next" button advances to next page and calls `POST /api/pages/{id}/complete/`
- On the last page (highest `order`), replace "Next" with "Complete"
- "Complete" calls `POST /api/pages/{id}/complete/` for the last page

**Error response:**
- `404` — node does not exist

---

## Progress Endpoints

### Get Current Session
```
GET /api/session/
```
**Authentication required:** Yes

**Description:**
Returns the user's current session — one focus node and up to 4 reinforcement nodes.
Call this on app load and after every session completion.

**Success response — `200 OK`:**
```json
{
    "focus_node": {
        "id": 4,
        "title": "What is a Function?",
        "order": 2
    },
    "reinforcement_nodes": [
        {"id": 1, "title": "Introduction to Sets", "order": 1},
        {"id": 2, "title": "Subsets", "order": 2},
        {"id": 3, "title": "Introduction to Relations", "order": 1},
        {"id": 6, "title": "Domain and Range", "order": 3}
    ]
}
```

**When user has completed all quests:**
```json
{
    "focus_node": null,
    "reinforcement_nodes": []
}
```

**Rules:**
- `focus_node` is the user's single pending ConceptNode
- `focus_node` is `null` only when all published quests are completed
- `reinforcement_nodes` contains exactly 4 nodes or is empty `[]`
- Reinforcement nodes are randomly selected from completed nodes
- The session is derived — it is never stored until the user completes it

---

### Complete Current Session
```
POST /api/session/complete/
```
**Authentication required:** Yes

**Request body example:**
{
    "focus_node_id": 8
}

**Description:**
Records the current session as completed and immediately returns a new session.
Can only be called after the focus node has been marked complete via page completion.

**Success response — `200 OK`:**
```json
{
    "focus_node": {
        "id": 5,
        "title": "Types of Functions",
        "order": 3
    },
    "reinforcement_nodes": [
        {"id": 1, "title": "Introduction to Sets", "order": 1},
        {"id": 2, "title": "Subsets", "order": 2},
        {"id": 4, "title": "What is a Function?", "order": 2},
        {"id": 3, "title": "Introduction to Relations", "order": 1}
    ]
}
```
The response is the **new session** — not the completed one.
Update the UI immediately with this new session.

**Failure response — `400`:**
```json
{"detail": "Focus ConceptNode is not completed yet."}
```
This means the user has not completed the focus node's pages.
The "Finish Session" button should only be enabled after focus node completion.

---

### Complete a Page
```
POST /api/pages/<page_id>/complete/
```
**Authentication required:** Yes

**Request body:** None

**Description:**
Marks a page as completed. Call this on every "Next" and "Complete" button click.
Safe to call multiple times — duplicate completions are ignored.

**Success response — `200 OK`:**
```json
{
    "status": "page_completed",
    "node_completed": true,
    "concept_node_id": 4
}
```

**If page was already completed:**
```json
{
    "status": "already_completed",
    "node_completed": false,
    "concept_node_id": 4
}
```

**Field reference:**

| Field | Type | Description |
|---|---|---|
| `status` | string | `"page_completed"` or `"already_completed"` |
| `node_completed` | boolean | `true` if this page completion finished the entire node |
| `concept_node_id` | integer | ID of the parent ConceptNode |

**Critical frontend rule:**
When `node_completed: true` is received, the focus node in the session
is now completed. Enable the "Finish Session" button at this point.

**Error response:**
- `404` — page does not exist

---

### Get Dashboard
```
GET /api/dashboard/
```
**Authentication required:** Yes

**Description:**
Returns the user's engagement stats. Call this when the user opens the Dashboard page.
This endpoint also triggers streak evaluation — always call it on Dashboard load.

**Success response — `200 OK`:**
```json
{
    "streak": 5,
    "freeze_streak": 2,
    "total_nodes_completed": 8,
    "total_sessions_completed": 6,
    "current_quest_title": "Functions and Relations",
    "current_quest_progress": {
        "completed": 2,
        "total": 5
    }
}
```

**When all quests are completed:**
```json
{
    "streak": 12,
    "freeze_streak": 0,
    "total_nodes_completed": 15,
    "total_sessions_completed": 15,
    "current_quest_title": null,
    "current_quest_progress": null
}
```

**Field reference:**

| Field | Type | Description |
|---|---|---|
| `streak` | integer | Current consecutive days with at least one session |
| `freeze_streak` | integer | Freeze tokens available (max 5) |
| `total_nodes_completed` | integer | Total ConceptNodes completed across all quests |
| `total_sessions_completed` | integer | Total sessions completed by this user |
| `current_quest_title` | string or null | Title of the current active quest |
| `current_quest_progress` | object or null | `{completed, total}` nodes in current quest |

---

## Complete Frontend Flow

```
1. User opens app
        ↓
2. GET /api/session/
   → show focus node and reinforcement nodes
        ↓
3. User clicks a ConceptNode
        ↓
4. GET /api/nodes/<node_id>/pages/
   → show first page
        ↓
5. User clicks Next on each page
        ↓
6. POST /api/pages/<page_id>/complete/   (on every Next click)
   → if node_completed: true → enable "Finish Session" button
        ↓
7. User clicks "Finish Session"
        ↓
8. POST /api/session/complete/
   → response is new session → update UI immediately
        ↓
9. User opens Dashboard
        ↓
10. GET /api/dashboard/
    → show streak, stats
```