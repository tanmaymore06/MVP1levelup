# Level Up — Frontend Specification

## Audience
This document is written for the frontend developer (or AI).
It describes every screen, every interaction, and every API call the frontend must make.
Read this alongside `api-reference.md` which defines the exact data shapes.

---

## Tech Stack
- **Framework:** React
- **Styling:** Tailwind CSS
- **Markdown rendering:** React Markdown + KaTeX (for math notation)
- **HTTP client:** Axios or Fetch API
- **Authentication:** Token stored in localStorage, attached to every request header

---

## Authentication Header
Every request except register and login must include:
```
Authorization: Token <stored_token>
```

---

## Visual Style
The overall aesthetic is inspired by the Valorant game UI:
- Dark background
- Sharp, high contrast elements
- Tactical, clean typography
- Subtle animations and transitions
- No rounded, friendly, or playful design elements

---

## Application Structure

```
/               → Map Screen (default, requires auth)
/login          → Login Screen
/register       → Register Screen
/read/:node_id  → Page Reading Screen
/dashboard      → Dashboard Screen
```

Unauthenticated users are redirected to `/login` from any protected route.

---

## Screen 1: Login Screen (`/login`)

### Layout
- Centered card on a dark full-screen background
- Level Up logo or wordmark at the top
- Username and password fields
- Login button
- Link to Register screen

### API Call
```
POST /api/auth/login/
Body: { "username": "...", "password": "..." }
```

### On success
- Store token in localStorage
- Redirect to Map Screen (`/`)

### On failure
- Show error message: "Invalid credentials."

---

## Screen 2: Register Screen (`/register`)

### Layout
- Identical structure to Login Screen
- Username, email (optional), and password fields
- Register button
- Link to Login screen

### API Call
```
POST /api/auth/register/
Body: { "username": "...", "password": "...", "email": "..." }
```

### On success
- Store token in localStorage
- Redirect to Map Screen (`/`)

### On failure
- Show field-level validation errors returned by the backend

---

## Screen 3: Map Screen (`/`)

This is the main screen. It has two layers:
1. The MainQuest Map (always present, full screen)
2. The Session Sidebar (slides in from the right on demand)

### On Load — API Calls (both called simultaneously)
```
GET /api/quests/      → populate MainQuest map
GET /api/session/     → populate Session sidebar
```

---

### Layer 1: MainQuest Map

#### Layout
- Full screen, dark background
- A vertical path runs from bottom to top of the screen
- MainQuests are positioned along this path, bottom to top
- The first MainQuest (lowest `order`) is at the bottom
- Each MainQuest is represented as a node on the path
- Nodes are connected by a visible path line

#### MainQuest Node States
Derive the state of each MainQuest from the API response:

| Condition | State | Visual suggestion |
|---|---|---|
| `is_completed: true` | Completed | Bright, fully lit node |
| Last item with `is_completed: false` | Current | Highlighted, pulsing or glowing |

#### Path Behavior
- The path between completed and current MainQuest nodes is fully visible
- Future MainQuests are never returned by the API — they do not exist on the map

#### Clicking a MainQuest Node
- Opens the ConceptNode Overlay (see below)
- Both completed and current MainQuests are clickable

#### Session Sidebar Toggle Button
- A fixed button on the right edge of the screen
- Labeled "Session" or uses a session icon
- Clicking it slides open the Session Sidebar from the right

---

### Layer 2: ConceptNode Overlay

Triggered when the user clicks a MainQuest node.

#### Layout
- Dark overlay covering the MainQuest map (map still faintly visible behind)
- A vertical path with ConceptNodes, same structure as the MainQuest map
- A close button (top right or top left) to dismiss the overlay

#### API Call
```
GET /api/quests/<quest_id>/nodes/
```

#### ConceptNode States

| `state` value | Visual suggestion |
|---|---|
| `"completed"` | Fully lit node, clickable |
| `"pending"` | Highlighted/glowing node, clickable |
| `"locked"` | Dimmed node, not clickable |

#### Clicking a ConceptNode
- Only `completed` and `pending` nodes are clickable
- Clicking closes the overlay and navigates to the Page Reading Screen:
```
/read/:node_id
```

---

### Layer 3: Session Sidebar

Triggered by clicking the Session toggle button.

#### Layout
- Slides in from the right, covering roughly 35–40% of the screen width
- The MainQuest map remains partially visible behind it
- Clicking outside the sidebar or a close button dismisses it

#### Content
```
Section 1: Focus Node
─────────────────────
One ConceptNode card showing:
- Node title
- "Your current focus" label
- Clickable → navigates to /read/:node_id

Section 2: Reinforcement Nodes
───────────────────────────────
Up to 4 ConceptNode cards showing:
- Node title
- "Revisit" label
- Each clickable → navigates to /read/:node_id

If reinforcement_nodes is empty []:
- Show message: "Complete more concepts to unlock reinforcement."
```

#### When focus_node is null
- Show message: "You have completed all available content."
- No Finish Session button

#### Finish Session Button
- Appears at the bottom of the sidebar
- **Disabled by default**
- Enabled only when the frontend receives `node_completed: true`
  from `POST /api/pages/<page_id>/complete/`
- Clicking it calls:
```
POST /api/session/complete/
Body: { "focus_node_id": <id of the focus node> }
```
- On success: update the session sidebar with the new session response
- Then call `GET /api/quests/` to refresh the MainQuest map

---

## Screen 4: Page Reading Screen (`/read/:node_id`)

### On Load — API Call
```
GET /api/nodes/<node_id>/pages/
```
Fetch all pages. Display the first page (lowest `order`) immediately.

### Layout
- Fixed-width content area, centered on screen (max-width ~800px)
- Dark background outside the content area
- Page title at the top (if not empty string)
- Page content rendered as Markdown below the title
- Navigation controls at the bottom:
  - "Previous" button (disabled on first page)
  - Page indicator: "Page 2 of 5"
  - "Next" button (on all pages except the last)
  - "Complete" button (on the last page only — highest `order`)

### Content Rendering Rules
- Render `content` field as Markdown
- Support LaTeX math notation using KaTeX
- Support embedded HTML inside Markdown

### On Every "Next" Click
1. Call page completion for the current page:
```
POST /api/pages/<page_id>/complete/
```
2. If response has `node_completed: true`:
   - Store this state — the Finish Session button must now be enabled
3. Advance to the next page

### On "Complete" Click (last page)
1. Call page completion for the last page:
```
POST /api/pages/<page_id>/complete/
```
2. If response has `node_completed: true`:
   - Store this state
3. Navigate back to Map Screen (`/`)
4. The Finish Session button in the sidebar should now be enabled

### Back Navigation
- A back button navigates to Map Screen (`/`) without completing the current page
- Progress already recorded is never lost — idempotent completions are safe

---

## Screen 5: Dashboard Screen (`/dashboard`)

### On Load — API Call
```
GET /api/dashboard/
```

### Layout
- Full screen, replaces the map entirely
- A navbar or back button to return to the Map Screen
- Stats displayed clearly:

```
┌─────────────────────────────────┐
│  Streak          5 days         │
│  Freeze Streak   2 tokens       │
│  Nodes Completed 8              │
│  Sessions Done   6              │
├─────────────────────────────────┤
│  Current Quest   Functions...   │
│  Quest Progress  ██████░░░ 2/5  │
└─────────────────────────────────┘
```

### When all quests are completed
- `current_quest_title` is null
- `current_quest_progress` is null
- Show message: "You have completed all available content." in place of quest progress

---

## State Management

The frontend must track the following state:

| State | Where used |
|---|---|
| `auth_token` | localStorage, attached to every request |
| `session` | Session sidebar, Finish Session button |
| `node_completed` | Enables Finish Session button |
| `focus_node_id` | Sent in POST /api/session/complete/ body |
| `current_page_index` | Page Reading Screen navigation |
| `pages` | Page Reading Screen content |

---

## Error Handling

| Status | Action |
|---|---|
| `401` | Clear token from localStorage, redirect to `/login` |
| `403` | Show "Access denied" message |
| `404` | Show "Not found" message |
| `400` | Show `detail` field from response body |

---

## Key Behavioral Rules

1. **Never compute learning states on the frontend.** Node states (`pending`, `completed`, `locked`) come from the backend. Render them, do not derive them.

2. **The Finish Session button is disabled by default** on every session. It is only enabled when `node_completed: true` is received from a page completion response.

3. **Call `POST /api/pages/<page_id>/complete/` on every Next and Complete click** — even if the user is re-reading a completed node. The backend handles duplicates safely.

4. **After `POST /api/session/complete/`** — update the session sidebar AND call `GET /api/quests/` to refresh the map. Both must happen.

5. **The Focus Node and Reinforcement Nodes in the sidebar are clickable** — they navigate directly to `/read/:node_id`, bypassing the ConceptNode overlay.

6. **`focus_node_id` must be stored** when the session is first loaded via `GET /api/session/`. It is required in the body of `POST /api/session/complete/`.