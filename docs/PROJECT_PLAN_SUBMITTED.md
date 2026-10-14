# Preliminary Project Plan (as submitted): Team 11

> **Source of truth** for scope when building. Transcribed from the submitted PDF "Team 11 Project Plan _ CS 490.pdf". Supersedes the older draft in `USER_STORIES.md`.
> Team: **Gurdeep, Kush, Arthur, Nick**. Feature: in-world Among Us-style social deduction game in Covey.Town. Working title: **GRAVEYARD SHIFT** (ship: the Nightjar).

## Problem statement (summary)
Covey.Town's interactive features isolate players in modal popups (video, two-player board games): movement stops, the map becomes irrelevant, and there is no synchronous activity for groups larger than two. We propose an **in-world social deduction game for 5 to 10 players**, inspired by Among Us, integrated with the map: players navigate rooms to complete tasks, use line of sight to spot suspicious movement, and gather to vote out Impostors. It extends Covey.Town beyond turn-based board games: real-time role assignment, line-of-sight, synchronized voting, custom game state wired to Phaser 3 and Socket.IO.
*(Note: the problem statement says 5 to 10 players; US3 says the lobby holds 4 to 10 and the host can start with at least 4. Treat 4 as the minimum to start.)*

## Scope levels
- **Essential** = must work for the feature to be complete (Sprints 1-5, committed).
- **Desirable** = Sprints 4-5, only after required work is merged.
- **Extension** = future work, not scheduled.

## User Story 1: Completing tasks (Essential)
*As a player in a Covey.Town social deduction game, I want to complete tasks throughout the map, so that I can contribute to my team's objective and help my team win.*
- E: View assigned task list, with the room of each task.
- E: Approaching an assigned station and interacting opens its task interface; a station with no task for that player shows a message and opens nothing.
- E: A task counts only after the server confirms it; completing one updates the shared team task bar for all players.
- E: Completed tasks no longer show as incomplete to that player.
- E (edge): Closing the task or walking away before finishing resets it, no credit.
- E (edge): Impostors see a fake task list that looks real; it never moves the bar.
- E (edge): Ghosts can move through walls and finish their remaining tasks.
- E (error): A disconnecting player's tasks are removed from the total so the match stays winnable.
- E: At least two mini-games: **keypad entry** (press numbers in order) and **wiring** (match colored wires).
- E: Task bar at 100% ends the game immediately, announces a Crewmate victory to all, returns them to the lobby.
- D: Completed stations show a visual indicator on the map.
- D: Some tasks span two rooms (download in one, upload in another).
- X: More mini-games (slider alignment, timing, pattern memory).

## User Story 2: Meetings and voting (Essential)
*As a crewmate in a Covey.Town social deduction game, I want to participate in meetings and vote for a suspected Impostor, so that my team can remove players working against its objective.*
- E: A living player triggers a meeting via the **emergency meeting table** or by **reporting a fallen avatar** within range.
- E (edge): Limited emergency meetings per player per game (host setting); after that the table no longer starts one for them.
- E: Meeting start: movement stops, fallen avatars are cleared, all living players move to the meeting area.
- E: During a meeting all living players hear each other through Covey.Town video chat, wherever they stood.
- E: Meeting UI shows all participants, alive/eliminated status, and who called the meeting.
- E: After the discussion timer, each living player casts one vote for a living player or skips.
- E (error): No multiple votes, no changing a submitted vote.
- E (edge): Voting timer expiry: non-voters count as casting no vote.
- E: Most votes is ejected and becomes a ghost; result shown to all.
- E (edge): Tie for most votes, Skip has the most, or no votes: no one ejected, play resumes.
- E (error): A player disconnecting during voting has their vote removed before counting.
- E (edge): Eliminated players cannot vote; their chat and voice reach only other eliminated players.
- E: Ejecting the last Impostor ends the game with a Crewmate victory, returns to the lobby.
- D: Ghosts can watch the meeting and vote live.
- X: Anonymous voting mode.

## User Story 3: Joining a match and playing a secret role (Essential)
*As a Covey.Town user, I want to join a match from the arcade machine in the town and play my secretly assigned role until one team wins, so that I can play a game of deception with the people around me.*
**Joining**
- E: Walking up to the **arcade machine** shows a prompt with the lobby count (e.g. 3/10); accepting moves the player into the **spaceship lobby**.
- E: Lobby holds 4 to 10; first to join is host; if the host leaves, the next player who joins becomes host.
- E: A player can leave the lobby before the game starts and return to town.
- E (edge): Lobby full (10) or game in progress: the arcade prompt says so; no one can join.
- E (error): Only the host can start, and only with at least 4 players.
**Playing a secret role**
- E: At start each player privately sees Crewmate or Impostor; Impostors also see the other Impostors. No player can infer another's role from browser data.
- E: Living players see each other move in real time. Players in the match and players in the town cannot see or hear each other.
- E (error): An Impostor in range of a living Crewmate can **Eliminate**: leaves a fallen-avatar marker, starts the Impostor's cooldown. Server rejects out of range or on cooldown.
- E: Eliminated players become ghosts; living players cannot see or hear ghosts.
- E (error): Impostors cannot eliminate Impostors, or anyone during a meeting.
- E (race): Two Impostors target the same player at once: only one elimination registers, only that cooldown starts.
- E: Living Crewmates <= living Impostors ends the game immediately: Impostor victory, all roles shown, back to lobby.
- E (error): A mid-game disconnect: the match continues and win conditions are re-checked.
- D: A **viewing radius** hides players outside it.
- D: Impostors can travel through **vents**.
- X: Walls block line of sight.
- X: Sabotage (e.g. lights shrink crewmate vision until repaired).
- X: Security station with camera views.

## Work breakdown (owners)
Sizes: S under 3-4 h, M 1-2 days, L no estimate yet (each L has a prior research task). ~35 h per person over 5 sprints at 4-5 h/week.

| Sprint | Gurdeep | Kush | Arthur | Nick |
|---|---|---|---|---|
| 0 (Sep 21-Oct 2, done) | 0.3 deploy starter app (M) | 0.1 pitch lead (M) | 0.5 Among Us research lead (S) | (all: 0.2 setup, 0.4 code reading) |
| 1 (Oct 5-16) | 1.A1 shared types + socket events (M) | 1.B1 spike: per-recipient playerMoved filter, go/no-go Oct 16 (M) | 1.C1 spike: arcade object + greybox ship + second Phaser scene (S); 1.C2 task specs (S) | 1.D1 spike: ghost-only + whole-meeting audio in nearbyPlayers() (M) |
| 2 (Oct 19-30) | 2.A1 ImpostorSessionController + hooks (M); 2.A2 SessionSettings, seeded RNG, RoleAssigner (S) | 2.B1 VisibilityPolicy + ghosts end to end (L) | 2.C1 ship map skeld.json in Tiled + ShipLayout (M); 2.C2 TaskEngine + Unlock Manifolds (S) | 2.D1 tallyVotes() (S); 2.D2 MeetingManager (M) |
| 3 (Nov 2-13) | 3.A1 ImpostorArcadeArea lobby (M); 3.A2 role reveal + game-over screens + history (S) | 3.B1 forceMove + 100 ms heartbeat (S); 3.B2 KillValidator + kill flow (M) | 3.C1 Fix Wiring + TaskManager (M); 3.C2 TaskStationInteractable (S) | 3.D1 MeetingModal + EjectReveal UI (M); 3.D2 chat filter (S) |
| 4 (Nov 16-27, Prelim Demo 2 Nov 20) | 4.A1 session orchestration + win conditions (L) | 4.B1 Kill/Report buttons, cooldown ring, bodies, ghost rendering (M) | 4.C1 mini-game UIs, TaskModal, task list + bar (M) | 4.D1 meeting triggers (M); 4.D2 session audio rules (S) |
| 5 (Nov 30-Dec 9) | 5.A1 technical overview (S) | 5.B1 manual test scripts (S) | 5.C1 final deploy + Twilio check + README (S) | 5.D1 full playtest (S) |

**Desirable (DS):** DS-1 crewmate sprite art (Nick; now covered by the SVG puppet), DS-2 SVG logo/arcade/HUD (Nick; now done), DS-3 lobby door (Gurdeep), DS-4 Swipe Card + Data Transfer tasks (Arthur), DS-5 vents (Gurdeep), DS-6 server speed check (Kush), DS-7 vision radius fog (Kush), DS-8 bot script (Kush), DS-9 multiple arcade machines (Gurdeep), DS-10 completed-station indicator (Arthur), DS-11 ghosts watch meetings (Nick).
**Future (EX):** EX-1 sabotage, EX-2 impostor doors, EX-3 more tasks, EX-4 security cams + admin map, EX-5 Twilio audio groups, EX-6 load test, EX-7 leaderboard, EX-8 anonymous voting, EX-9 walls block line of sight.

## Milestones
Wizard-of-Oz demo **Fri Oct 16** (faked, ~5 min, all user stories, professional, plausible). Prelim Demo 1 **Oct 30** (real code, >=1 story, mentor). Prelim Demo 2 **Nov 20** (instructor). Final demo after Sprint 5.
