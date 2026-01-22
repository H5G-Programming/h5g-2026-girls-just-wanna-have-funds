# Project Plan: Girls Just Wanna Have Funds

## Goals
- Build a Vite + React frontend tailored for girls age 13-16 with lively colors, icons, and friendly copy.
- Build a very simple Python backend (Flask) with in-memory data and clear comments to teach basics.
- Meet all Must/Should/Could requirements, including charts, progress bars, confetti, and sidebars.

## Scope
- Frontend: dashboard, goals list, add/move/close/complete goals, profile name display, left nav, right activity panel, charts, confetti.
- Backend: in-memory goals, transactions, totals, profile name, simple REST endpoints.
- No auth; single fake user returned by backend.

## User Stories Coverage
- Must: goals CRUD, add funds, move funds, close goal, complete/archived, sidebar total, profile name, confetti on goal hit, teen-friendly UI.
- Should: dashboard overview, progress bars per goal, move funds between goals.
- Could: activity bar chart across months, highlight closest goal, transaction history sidebar.

## Tech Choices
- Frontend: Vite + React (JS), React Router (if multi-view), Chart.js or Recharts, confetti library.
- Backend: Flask with simple in-memory lists/dicts and clear property names.

## Data Model (in-memory)
- user: { id, name }
- goals: { id, title, target_amount, saved_amount, emoji, image_url, status }
- transactions: { id, goal_id, type, amount, date, note }

## Transaction Creation Rules
- add-funds: create a "deposit" transaction tied to the goal.
- move-funds: create two transactions: "transfer_out" from the source goal and "transfer_in" to the target goal.
- close-goal: move remaining balance to another goal and log transfer_out/transfer_in.
- complete-goal: create a "complete" transaction and move goal to archived status.
- initial seed data: create a few sample transactions per goal for charting/history.

## API Sketch
- GET /api/user
- GET /api/goals
- POST /api/goals
- POST /api/goals/:id/add-funds
- POST /api/goals/:id/move-funds
- POST /api/goals/:id/close
- POST /api/goals/:id/complete
- GET /api/transactions
- GET /api/summary (totals, closest goal, monthly chart data)

## Milestones
1. Project scaffold (Vite + React, Flask app, basic wiring).
2. Backend endpoints with in-memory data + sample seed.
3. Core UI layout: left sidebar, main dashboard, right activity panel.
4. Goals list + add/move/close/complete flows.
5. Dashboard widgets: totals, closest goal, progress bars.
6. Charts + transaction history + confetti on goal achieved.
7. UI polish: colors, icons, responsiveness.

## Acceptance Checks
- All user stories implemented.
- Dashboard shows profile name, totals, closest goal, progress bars.
- Confetti when saved amount >= target.
- Right sidebar shows transaction history; bar chart compares months.
- Backend code is simple, readable, and commented.
