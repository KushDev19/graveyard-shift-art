# Among Us in Covey.Town: Problem Statement and User Stories

> Extracted from the submitted Preliminary Project Plan (Team 11). The Wizard-of-Oz demo must showcase every story below.

## Problem Statement

Covey.Town's games pull players out of the world. Tic-Tac-Toe and Connect Four open in a popup that covers the map, seat only two players, and leave movement and exploration with no role while you play. Covey.Town has shared activities for larger groups, such as conversation areas and synchronized videos, but no game that more than two people can play together.

To solve this, we propose an in-world social deduction game for 4 to 10 players, inspired by Among Us. Players join from an arcade machine in the town and play on a spaceship map inside the same 2D world, keeping their avatars, movement and proximity video. Crewmates move between rooms to complete tasks, Impostors try to eliminate them without being seen, and everyone gathers in meetings to discuss by voice and vote someone out.

Our team wants to build this feature to extend Covey.Town's architecture beyond turn-based board games. It requires real-time game state on the server, sending different players different information (secret roles and hidden ghosts), and synchronized meetings and voting, all connected to the Phaser 3 engine and Socket.IO events. This makes it a game that needs Covey.Town's shared map and proximity voice to work.

## User Stories and Acceptance Criteria

Essential conditions must work for the feature to be complete. Desirable conditions match the Desirable work in the work breakdown, and Extension conditions match the future work list at the end of the work breakdown.

### User Story 1: Completing tasks

As a player in a Covey.Town social deduction game, I want to complete tasks throughout the map, so that I can contribute to my team's objective and help my team win. (Essential)

Conditions of Satisfaction:

- (Essential) The player can view their assigned task list, with the room where each task is located.

- (Essential) When a player approaches an assigned station and interacts with it, the corresponding task interface opens. Interacting with a station that has no task for that player shows a message and opens nothing.

- (Essential) A task counts only after the server confirms the player solved it. Completing a task updates the shared team task progress bar for all players in the match.

- (Essential) Completed tasks no longer show as incomplete to that player.

- (Essential) Closing the task interface or walking away from the station before finishing resets that task and awards no team credit. (Edge case)

- (Essential) Impostors see a list of fake tasks that looks like a Crewmate's list, but their tasks never move the progress bar. (Edge case)

- (Essential) Eliminated players (ghosts) can move through walls and complete their remaining assigned tasks. (Edge case)

- (Essential) If a player disconnects, the game removes their tasks from the total so the match remains winnable. (Error case)

- (Essential) Tasks use at least two mini-games: keypad entry (pressing numbers in order) and wiring (matching colored wires).

- (Essential) When the team task bar reaches 100%, the game immediately ends, announces a Crewmate victory to all players in the match, and returns them to the lobby.

- (Desirable) Completed task stations display a visual indicator on the map.

- (Desirable) Some tasks span two rooms, such as downloading data in one room and uploading it in another.

- (Extension) More mini-game types, such as slider alignment, timing and pattern memory.

### User Story 2: Meetings and voting

As a player in a Covey.Town social deduction game, I want to participate in meetings and vote for a suspected Impostor, so that my team can remove players working against its objective. (Essential)

Conditions of Satisfaction:

- (Essential) A living player can trigger a meeting by interacting with the emergency meeting table or by reporting a fallen avatar within reporting range.

- (Essential) Each player can call a limited number of emergency meetings per game, set by the host. After that, the table no longer starts a meeting for them. (Edge case)

- (Essential) When a meeting starts, avatar movement stops, fallen avatars are cleared from the map, and all living players are moved to the meeting area.

- (Essential) During a meeting, all living players can hear each other through Covey.Town's video chat, no matter where they stood before.

- (Essential) The meeting interface shows all participants, their status (alive or eliminated), and who called the meeting.

- (Essential) After the discussion timer ends, each living player can cast one vote for a living player or choose to skip.

- (Essential) Players cannot cast multiple votes or change their vote once submitted. (Error case)

- (Essential) When the voting timer expires, players who have not voted are counted as casting no vote. (Edge case)

- (Essential) The player with the most votes is ejected and becomes a ghost, and the result is shown to all players in the match.

- (Essential) If two or more options tie for the most votes, if Skip has the most votes, or if no one votes, no one is ejected and players resume moving. (Edge case)

- (Essential) If a player disconnects during voting, their vote is removed before the votes are counted. (Error case)

- (Essential) Eliminated players cannot vote, and their chat messages and voice only reach other eliminated players. (Edge case)

- (Essential) If voting ejects the last Impostor, the game immediately ends, announces a Crewmate victory to all players in the match, and returns them to the lobby.

- (Desirable) Eliminated players can watch the meeting and the vote as it happens.

- (Extension) An anonymous voting mode hides who voted for whom.

### User Story 3: Joining a match and playing a secret role

As a Covey.Town user, I want to join a match from the arcade machine in the town and play my secretly assigned role until one team wins, so that I can play a game of deception with the people around me. (Essential)

Conditions of Satisfaction:

Joining the match

- (Essential) Walking up to the arcade machine shows a prompt with the number of players in the lobby (for example 3/10). Accepting it moves the player into the spaceship lobby.

- (Essential) The lobby holds 4 to 10 players. The first player to join is the host. If the host leaves, the next player who joined becomes host.

- (Essential) A player can leave the lobby at any time before the game starts and return to the town.

- (Essential) When the lobby has 10 players or a game is in progress, the arcade prompt says so and no one else can join. (Edge case)

- (Essential) Only the host can start the game, and only when at least 4 players are in the lobby. (Error case)

Playing a secret role

- (Essential) When the game starts, each player privately sees whether they are a Crewmate or an Impostor, and Impostors also see who the other Impostors are. No player can find out another player's role from the data their browser receives.

- (Essential) Players see other living players move in real time. Players inside the match and players in the town cannot see or hear each other.

- (Essential) An Impostor within range of a living Crewmate can use an Eliminate action, which leaves a fallen avatar marker and starts that Impostor's elimination cooldown. The server rejects the action if the target is out of range or the cooldown has not finished. (Error case)

- (Essential) Eliminated players become ghosts. Living players cannot see or hear ghosts.

- (Essential) Impostors cannot eliminate other Impostors or eliminate players during a meeting. (Error case)

- (Essential) If two Impostors target the same player at the same time, only one elimination registers, and only that Impostor's cooldown starts. (Race condition)

- (Essential) If eliminations reduce the number of living Crewmates to equal or fewer than the number of living Impostors, the game immediately ends, announces an Impostor victory to all players in the match, shows every player's role, and returns players to the lobby.

- (Essential) If a player disconnects mid-game, the match continues and the win conditions are checked again. (Error case)

- (Desirable) A viewing radius limits how far each living player can see, so players outside it are hidden.

- (Desirable) Impostors can travel through vents to reposition unseen.

- (Extension) Walls block line of sight, so players behind walls are hidden.

- (Extension) Impostors can trigger sabotage events, such as cutting the lights to shrink the Crewmate viewing radius until someone repairs them.

- (Extension) A security station shows camera views of other rooms.
