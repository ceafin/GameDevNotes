## Path Map

```ascii
                           ┌─ Path 1: Endless Runners
                           ├─ Path 2: Puzzle & Logic
                           ├─ Path 3: Fixed-Screen Arcade ───┐
    PATH 0                 │                                 │
    Shared Foundations ────├─ Path 4: Platformers ───────────┤──── Branch 4A: Metroidvania
      (Pong, Breakout,     │   │                             │     Branch 4B: 3D Platformers
      Snake, Gorillas)     │   └── Branch 4C: Cinematic      │     Branch 4C: Cinematic
                           │                                 │
                           ├─ Path 5: Top-Down Adventure     │
                           ├─ Path 6: Shooters & Shmups ─────┘
                           ├─ Path 7: Physics & Vehicles ─── Branch 7A: Destructible Terrain
                           │                                 Branch 7B: Racing
                           ├─ Path 8: RPGs ───────────────── Branch 8A: Roguelike / Procedural
                           │                                 Branch 8B: Turn-Based
                           │                                 Branch 8C: Action RPG
                           │                                 Branch 8D: Life Sim
                           ├─ Path 9: First-Person Games
                           ├─ Path 10: Adventure Games
                           ├─ Path 11: Strategy & Sim ────── Branch 11A: RTS
                           │                                 Branch 11B: City / World Sim
                           │                                 Branch 11C: Tactical
                           ├─ Path 12: Fighting & Beat 'em Up
                           └─ Standalone Challenges
```

---

## Path 0: Shared Foundations

Every path begins here. These four games teach universal game development fundamentals that apply to every genre.

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Pong | 1972 | Arcade | 0.5 | 0.5 | 1 | Game loop, keyboard/input handling, basic 2D movement, ball-paddle collision, score tracking, win condition |
| 2 | Breakout | 1976 | Arcade | 0.5 | 0.5 | 1 | Brick grid data structure, brick destruction, angle-of-incidence reflection, level completion and reset, powerup concept |
| 3 | Blockade (Snake) | 1976 | Arcade | 1 | 0.5 | 1.5 | Grid-based movement, queue/deque data structure for a growing body, self-collision detection, discrete-step game logic |
| 4 | Gorillas.bas | 1990 | MS-DOS | 1 | 0.5 | 1.5 | Projectile arc physics (gravity + velocity), turn-based two-player, aiming with angle/power, basic destructible terrain |

> After completing these four games, choose one or more paths below based on your interests.

---

## Path 1: Endless Runners & Auto-Scrollers

**What you'll learn:** Scrolling world systems, procedural/infinite content spawning, difficulty ramping over time, mobile-style single-input design, and resource/mechanic layering.

**Prerequisites:** Shared Foundations

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Chrome Dinosaur Game | 2014 | Web Browser | 0.5 | 0.5 | 1 | Simplest endless runner: single-input (jump/duck), ground scrolling, obstacle spawning at intervals, speed ramp over time |
| 2 | Flappy Bird | 2013 | Mobile | 1 | 1 | 2 | Continuous gravity simulation with tap-impulse, gap-based obstacle threading, death/restart loop, tighter timing windows |
| 3 | Doodle Jump | 2009 | Mobile | 1.5 | 1 | 2.5 | Vertical scrolling, procedural platform placement, screen-edge wrapping, tilt/accelerometer input, platform variety (breaking, moving) |
| 4 | Jetpack Joyride | 2011 | Mobile | 1 | 1.5 | 2.5 | Multi-mechanic runner: vehicle switching mid-run, coin/collectible systems, mission/achievement tracking, shop/upgrade loop, powerup variety |
| 5 | Moon Patrol | 1982 | Arcade | 1.5 | 2 | 3.5 | Parallax background scrolling (multiple layers), dual-axis shooting (forward + upward), terrain with gaps to jump, simultaneous air and ground hazards |

> **⚠️ Similarity Note:** Chrome Dinosaur Game and Flappy Bird overlap heavily — both are single-input obstacle avoidance with scrolling. Flappy Bird's continuous gravity makes it slightly more interesting technically. **Pick one** as your starting point.

---

## Path 2: Puzzle & Logic Games

**What you'll learn:** Grid data structures, classic algorithms (flood fill, matching, search), cellular automata, state management, rule-based systems, and agent simulation.

**Prerequisites:** Shared Foundations

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Cookie Clicker | 2013 | PC | 1 | 1 | 2 | Idle/incremental game: exponential growth modeling, prestige/reset systems, upgrade trees, offline progress calculation, UI for large numbers |
| 2 | Minesweeper | 1990 | Windows | 1.5 | 1 | 2.5 | Grid with hidden state, flood-fill reveal algorithm, adjacency counting, flag/mark system, first-click safety guarantee |
| 3 | Dr. Mario | 1990 | NES | 1.5 | 1 | 2.5 | Falling-piece puzzle with color matching: pill dropping with rotation, 4-in-a-row virus clearing, gravity cascade after clears |
| 4 | Bejeweled | 2000 | Web Browser | 1.5 | 1 | 2.5 | Swap-to-match grid: valid move detection, cascade/chain combo scoring, board refill from top, animated transitions between states |
| 5 | Tetris | 1984 | Elektronika 60 | 2 | 1 | 3 | Piece rotation with matrix transforms, wall kicks, gravity/soft-drop/hard-drop, line-clear detection, next-piece preview, increasing speed levels |
| 6 | Tic-Tac-Toe | 1950 | Custom Hardware | 2 | 1.5 | 3.5 | Win-condition evaluation, game state representation (board as data), minimax AI algorithm with perfect play, draw detection |
| 7 | Conway's Game of Life | 1970 | Mainframe | 2 | 1.5 | 3.5 | Cellular automata rules, neighbor counting on grid, double-buffered state updates, infinite canvas (or wrapping), simulation controls (step, play, pause) |
| 8 | Lemmings | 1991 | Amiga | 3 | 3 | 6 | Agent-based simulation: many autonomous agents with individual pathfinding, role/command assignment, terrain modification by agents, real-time command UI, rescue-count win conditions |

> **⚠️ Similarity Notes:**
> - **Dr. Mario vs. Bejeweled:** Both involve color-matching on grids. Dr. Mario uses falling pieces (Tetris-like input); Bejeweled uses swap-based matching. The cascade/chain logic differs. Either teaches grid-matching; doing both provides only incremental value.
> - **Cookie Clicker** is mechanically distinct from all other puzzle games (idle/incremental genre). It shares the path's emphasis on "logic over graphics" but could also be treated as a **standalone challenge**.

---

## Path 3: Fixed-Screen Arcade

**What you'll learn:** Enemy AI and behavior patterns, wave/level systems, score mechanics, multi-entity management on a single screen, and classic game feel.

**Prerequisites:** Shared Foundations

| #   | Game            | Year | Platform | Complexity | Scope | Combined | Key New Skills                                                                                                                                            |
| --- | --------------- | :--: | :------: | :--------: | :---: | :------: | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Number Munchers | 1986 | Apple II |     1      |   1   |    2     | Grid-based movement with educational evaluation (math problem checking), enemy spawn patterns, simplest fixed-screen enemy avoidance                      |
| 2   | Space Invaders  | 1978 |  Arcade  |    1.5     |   2   |   3.5    | Enemy formation movement (descending grid), player shooting mechanic, shield/cover degradation, wave progression with speed increase                      |
| 3   | Frogger         | 1981 |  Arcade  |    1.5     |   2   |   3.5    | Lane-based movement and timing, riding moving objects (logs, turtles), multiple hazard types (cars vs. water), safe-zone goal slots                       |
| 4   | Pac-Man         | 1980 |  Arcade  |     2      |  1.5  |   3.5    | Ghost AI with distinct personalities (state machines: chase/scatter/frightened), tile-based maze, pellet tracking, power-up timer, tunnel wrapping        |
| 5   | Donkey Kong     | 1981 |  Arcade  |     2      |  1.5  |   3.5    | Multi-screen sequential levels (each a distinct layout), ladders, barrel AI with random pathing down platforms, jump-over scoring bonus                   |
| 6   | Bubble Bobble   | 1986 |  Arcade  |     2      |   2   |    4     | Projectile-trapping mechanic (bubble enemies then pop), bubble physics (floating, bouncing), cooperative multiplayer on same screen, 100 level designs    |
| 7   | Dig Dug         | 1982 |  Arcade  |    2.5     |   2   |   4.5    | Terrain deformation (tunneling through dirt), pump-to-inflate attack mechanic, rock physics (dislodge and crush), enemies that can move through dirt      |
| 8   | Mario Bros.     | 1983 |  Arcade  |    2.5     |   3   |   5.5    | Platform bumping from below (hit detection from underneath), enemy flipping/stunning mechanic, pipes as spawn points, cooperative-competitive multiplayer |
| 9   | Rampage         | 1986 |  Arcade  |    2.5     |   3   |   5.5    | Destructible multi-story buildings, large-character collision and climbing, eating civilians for health, military counter-attacks, 3-player simultaneous  |

---

## Path 4: Side-Scrolling Platformers

**What you'll learn:** Scrolling camera systems, momentum-based character physics, level design principles, enemy AI patterns, powerup state machines, and world/map structure.

**This is the largest and most branching path.** It splits into **Metroidvania** (4A), **3D Platformers** (4B), and **Cinematic Platformers** (4C).

**Prerequisites:** Shared Foundations; ideally some of Path 3 for enemy pattern experience

### Core Platformer Progression

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Aldo's Adventure | 1987 | DOS | 1.5 | 1.5 | 3 | Simplest side-scroller: horizontal movement, ladders, collectibles, enemy contact death — the minimal viable platformer |
| 2 | Pitfall! | 1982 | Atari 2600 | 2.5 | 3 | 5.5 | Screen-to-screen exploration, vine swinging physics, underground alternate paths, 20-minute timer, treasure collection across 255 screens |
| 3 | Super Mario Bros. | 1985 | NES | 2 | 2 | 4 | **THE** foundational scrolling platformer: momentum/acceleration physics, scrolling camera, powerup state changes (small/big/fire), pipe warps, flagpole goal |
| 4 | Kirby's Dream Land | 1992 | Game Boy | 2 | 2 | 4 | Flight/floating mechanic (sustained aerial movement), inhale + spit projectile from enemies, air puff attack, simpler difficulty as design choice |
| 5 | Super Mario Bros. 2 | 1988 | NES | 2 | 2.5 | 4.5 | Character-specific physics (4 characters with different jump/speed), pick-up and throw mechanics, vertical scrolling levels, digging through sand |
| 6 | DuckTales | 1989 | NES | 2 | 2.5 | 4.5 | Pogo-stick bounce mechanic (cane), non-linear level selection from hub, hidden treasure rooms, boss encounters per level |
| 7 | Castlevania | 1986 | FDS | 2.5 | 2.5 | 5 | Deliberate/committed jump controls (no air steering), subweapon system (knife, axe, cross, holy water), staircase movement, pattern-based boss fights |
| 8 | Mega Man | 1987 | NES | 2.5 | 2.5 | 5 | Non-linear stage select, boss weapon acquisition system (beat boss → gain weapon), rock-paper-scissors weakness chains, sliding mechanic |
| 9 | Contra | 1987 | Arcade | 2.5 | 2.5 | 5 | Run-and-gun with 8-directional aiming, weapon powerup cycling (spread, laser, etc.), fast-paced enemy wave design, 2-player co-op |
| 10 | Sonic the Hedgehog | 1991 | Sega Genesis | 2.5 | 3 | 5.5 | Momentum-based slope physics (acceleration on hills), loop-the-loop traversal, springs/bumpers, ring scatter-and-recollect on hit |
| 11 | Super Mario Bros. 3 | 1988 | NES | 2.5 | 3.5 | 6 | Overworld map with node navigation, P-meter flight system, inventory system for stored powerups, diverse suits (frog, tanooki, hammer), auto-scrolling airship levels |
| 12 | Super Mario World | 1990 | SNES | 2.5 | 3.5 | 6 | Companion AI (Yoshi with eating/spitting/flutter), branching world paths with secret exits, ghost house puzzle levels, spin jump, cape flight with gliding |
| 13 | Donkey Kong Country | 1994 | SNES | 2.5 | 3.5 | 6 | Tag-team partner swapping, barrel cannon launching (trajectory aiming), animal buddy vehicles (rhino, swordfish), mine cart on-rails sections |
| 14 | Kirby's Adventure | 1993 | NES | 2.5 | 3.5 | 6 | Full copy-ability system (20+ powers from enemies) — modular player-ability architecture where each power has a unique moveset |

> **⚠️ Similarity Alerts:**
> - **⚠️ Chip 'n Dale: Rescue Rangers (4.5):** Same era Capcom NES platformer as DuckTales. Adds co-op and box throwing but very similar core engine. Skip unless you specifically want co-op platformer experience.
> - **⚠️ Super Mario Land 2: 6 Golden Coins (4.5):** Essentially SMB3/SMW at smaller Game Boy scope. Redundant unless you want to study Game Boy hardware constraints.
> - **⚠️ Mega Man 2 (5.5) & Mega Man 3 (5.5):** Content expansions of Mega Man 1. MM3 adds slide and Rush utility. Same engine, same design. Redundant.
> - **Mega Man X (5.5):** Adds wall-jumping, air-dashing, and hidden armor upgrades — genuinely evolves the platformer moveset. **Worth including** if you want to study how to expand a movement system.
> - **⚠️ SMB3 vs. SMW (both 6):** Very similar challenge. SMB3 leans on **inventory + powerup variety**; SMW leans on **companion AI (Yoshi) + branching paths**. Pick one, or do both to compare approaches.

---

### Branch 4A: Metroidvania

Branches from **Castlevania** and **Mega Man** in the Core Platformer path. Focuses on ability-gated exploration, interconnected non-linear world maps, backtracking, and map systems.

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| — | Castlevania | 1986 | FDS | 2.5 | 2.5 | 5 | *(Foundation — see Core Platformer #7)* |
| 1 | Metroid | 1986 | FDS | 2.5 | 3 | 5.5 | **Core Metroidvania:** ability-gated exploration (missiles open doors, morph ball opens passages), interconnected non-linear world map, backtracking with new abilities |
| 2 | The Goonies II | 1987 | NES | 2.5 | 2.5 | 5 | Dual-mode gameplay: side-scrolling platforming + first-person room exploration, item-puzzle progression, adventure-game elements in an action game |
| 3 | Castlevania II: Simon's Quest | 1987 | FDS | 2.5 | 3 | 5.5 | Day/night cycle affecting enemy strength and town behavior, RPG elements (hearts as currency, leveling), open-world town NPCs, non-linear quest structure |
| 4 | Zelda II: The Adventure of Link | 1987 | FDS | 2.5 | 3 | 5.5 | Hybrid viewpoints: side-scrolling combat dungeons + top-down overworld map, XP and leveling system, magic spells, town NPCs with clues |
| 5 | Metroid II: Return of Samus | 1991 | Game Boy | 2.5 | 2.5 | 5 | Area-locking via enemy kill count (Metroid extermination gates progression), evolving boss forms (same enemy type through multiple evolutions) |
| 6 | Super Metroid | 1994 | SNES | 3 | 3.5 | 6.5 | **Definitive 2D Metroidvania:** advanced map/automap system, environmental storytelling, physics-based movement tech (wall jump, shinespark, mockball), save stations, complex multi-phase boss AI |

> **Continues into Path 9** via **Metroid Prime** (9) for the 3D first-person Metroidvania experience.
>
> **⚠️ Similarity Note:** Metroid, Metroid II, and Super Metroid share the same core Metroidvania challenge. Metroid II's unique contribution (area-locking by kill count) is a minor variation. **Super Metroid** is the definitive refinement. Recommend: **Metroid** (foundational) + **Super Metroid** (evolved). Cut Metroid II unless you want Game Boy constraints.

---

### Branch 4B: 3D Platformers

Branches from the Core Platformer path. Introduces 3D camera systems, 3D collision, spatial movement, and hub-world design.

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Crash Bandicoot | 1996 | PlayStation | 3.5 | 3.5 | 7 | Corridor-style 3D platforming: fixed/tracking camera angles, 3D collision along constrained paths, into-screen and side-view perspectives, crate breaking, bonus rounds |
| 2 | Super Mario 64 | 1996 | Nintendo 64 | 4.5 | 4 | 8.5 | Open 3D platforming: free camera control (Lakitu cam), star-based objective progression, diverse 3D movement set (triple jump, wall kick, long jump, etc.), hub world (Peach's Castle) |

---

### Branch 4C: Cinematic Platformer

A distinct sub-genre focused on realistic animation, precise environmental puzzles, and deliberate pacing.

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Prince of Persia | 1989 | Apple II | 3.5 | 3.5 | 7 | Rotoscoped animation system, realistic momentum and physics, environmental hazard design (spikes, crushers, collapsing floors), sword duel combat, real-time countdown pressure |

---

## Path 5: Top-Down Action-Adventure

**What you'll learn:** Tile-based world building, item/inventory progression systems, dungeon design with keys and puzzles, NPC/dialogue systems, save systems, and the overworld ↔ dungeon structure. Major leap into 3D at the end.

**Prerequisites:** Shared Foundations

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Snail Maze | 1986 | Sega Master System | 1 | 1 | 2 | Tile-based maze traversal, simple top-down movement, goal-seeking under time pressure — simplest top-down game |
| 2 | The Legend of Zelda | 1986 | FDS | 2 | 3 | 5 | Screen-based scrolling overworld, item progression (boomerang, bow, bombs, raft), dungeon map/compass, shops, save/battery backup, open-ended exploration |
| 3 | StarTropics | 1990 | NES | 2.5 | 3 | 5.5 | Grid-locked movement in a top-down action game, isometric-feeling room puzzles, unique jump mechanic in top-down context, chapter-based story structure |
| 4 | The Legend of Zelda: Link's Awakening | 1993 | Game Boy | 2.5 | 3.5 | 6 | Assignable item buttons (equip any two items), trading sequence side-quest chain, side-scrolling sections within top-down game, screen-transition world map, steal-from-shop mechanic |
| 5 | The Legend of Zelda: A Link to the Past | 1991 | SNES | 3 | 4 | 7 | Dual parallel worlds (Light World / Dark World) with mirroring, smooth-scrolling overworld (not screen-locked), complex multi-floor dungeon design, mirror warp mechanic |
| 6 | The Legend of Zelda: Ocarina of Time | 1998 | Nintendo 64 | 4.5 | 4.5 | 9 | **3D action-adventure:** Z-targeting lock-on combat system, 3D dungeon design with spatial puzzles, context-sensitive action button, day/night cycle, horseback riding (Epona), musical instrument mechanic (ocarina songs) |
| 7 | The Legend of Zelda: The Wind Waker | 2002 | GameCube | 4.5 | 4.5 | 9 | Cel-shaded rendering pipeline (toon shading), ocean sailing and wind-direction navigation, island-based open world with chart system, expressive character animation system |

> **⚠️ Similarity Alerts:**
> - **⚠️ Oracle of Ages (6) & Oracle of Seasons (6):** Both built directly on the Link's Awakening engine. Ages adds time-travel puzzles; Seasons adds environmental season-swapping. The *programming* challenge is nearly identical to Link's Awakening. **Redundant** unless you want to study linked-game save transfer between cartridges.
> - **⚠️ OoT vs. Wind Waker (both 9):** Similar 3D Zelda engine. Wind Waker's unique contributions are cel-shaded rendering and the sailing system. If only doing **one** 3D Zelda, OoT covers more foundational 3D action-adventure systems. Wind Waker adds a unique art pipeline challenge.

---

## Path 6: Shooters & Shmups

**What you'll learn:** Projectile spawning and management, enemy wave/pattern design, bullet patterns, scrolling in multiple orientations (vertical, horizontal, isometric, rail-3D), and boss encounter design.

**Prerequisites:** Shared Foundations

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Spacewar! | 1962 | PDP-1 | 1.5 | 1 | 2.5 | Thrust-and-rotate movement in space (Newtonian), two-player combat, torpedo projectiles with limited ammo, optional gravity well, screen wrapping |
| 2 | Asteroids | 1979 | Arcade | 1.5 | 1 | 2.5 | Inertia-based movement (no friction), asteroid splitting on hit (large → medium → small), screen wrapping, hyperspace random teleport, vector-style rendering |
| 3 | Missile Command | 1980 | Arcade | 1.5 | 1.5 | 3 | Cursor/crosshair-targeted shooting, explosion radius area-of-effect damage, multi-base defense management, incoming projectile interception, MIRV splitting missiles |
| 4 | Space Invaders | 1978 | Arcade | 1.5 | 2 | 3.5 | *(Shared with Path 3)* Enemy formation grid movement, shooting mechanics, destructible shield barriers, wave-based progression |
| 5 | River Raid | 1982 | Atari 2600 | 2 | 2 | 4 | Vertical scrolling shooter, fuel management as a core resource, varied terrain (river width narrows/widens), bridge targets, helicopter/jet enemy types |
| 6 | StarGoose! | 1988 | Amiga | 2 | 2 | 4 | Vertical shmup with ground terrain, bombing ground targets + shooting air enemies (dual plane combat), energy management, speed control |
| 7 | The Guardian Legend | 1988 | NES | 2.5 | 3 | 5.5 | **Hybrid genre:** top-down Zelda-style overworld exploration + vertical shmup corridor sections, weapon/upgrade system shared across both modes, chip-based progression |
| 8 | Zaxxon | 1981 | Arcade | 3 | 3 | 6 | Isometric 3D perspective with altitude axis, shadow rendering for height reference, fuel management, pseudo-3D collision detection (height + position), fortress structure |
| 9 | Star Fox | 1993 | SNES | 3.5 | 4 | 7.5 | 3D polygon rail shooter, branching path selection between levels, wingman AI with dialogue, barrel roll and boost mechanics, 3D boss battles, all-range mode |

> **⚠️ Similarity Notes:**
> - **⚠️ Spacewar! vs. Asteroids:** Both feature thrust-rotation in zero-gravity space. Spacewar! is PvP combat; Asteroids is score-attack with fragmentation. Very similar physics model — **pick one**. Asteroids adds the splitting mechanic.
> - **⚠️ River Raid vs. StarGoose!:** Both are vertical scrolling shooters. River Raid adds fuel/resource management; StarGoose! is largely the same with terrain consideration. **Redundant — pick River Raid.**

---

## Path 7: Physics, Vehicles & Racing

**What you'll learn:** Physics simulation (gravity, thrust, friction, torque), terrain interaction, vehicle dynamics, and increasingly realistic physics fidelity.

**Prerequisites:** Shared Foundations (especially Gorillas.bas for projectile physics)

### Core Physics Progression

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Lunar Lander | 1979 | Arcade | 2 | 1 | 3 | Gravity + thrust vector simulation, fuel as limited resource, soft-landing velocity detection, orientation/rotation control |
| 2 | Peggle | 2007 | PC | 2 | 2 | 4 | Ball physics bouncing off pegs, angle-aimed launching, score multipliers and combos, special character powers, bucket catch at bottom, level clear condition |
| 3 | Tiny Wings | 2011 | Mobile | 2.5 | 2 | 4.5 | Procedurally generated terrain hills, slope-based momentum (gain speed downhill, lose uphill), touch-to-dive timing, day/night cycle scoring |
| 4 | Hill Climb Racing | 2012 | Mobile | 2.5 | 2.5 | 5 | 2D vehicle physics with suspension and torque, gas/brake controls, body rotation on terrain, fuel as resource, vehicle upgrade shop system |
| 5 | Line Rider | 2006 | PC | 3 | 1 | 4 | User-drawn physics tracks (Bézier curves or line segments), sled simulation on arbitrary surfaces, physics sandbox/creative tool, replay system |
| 6 | Marble Madness | 1984 | Arcade | 3 | 2 | 5 | Isometric ball physics, tilt/directional momentum control, 3D-in-2D terrain with height, environmental hazards (acid, catapults), race-against-clock |
| 7 | Super Monkey Ball | 2001 | GameCube | 3.5 | 3 | 6.5 | Full 3D ball physics, tilt-the-world control scheme (not the ball), 3D course design with fall-offs, camera management, party mini-game variety |

> **⚠️ Similarity Note:** **Marble Madness vs. Super Monkey Ball** — both are "guide a ball through obstacle courses" with physics. Marble Madness is isometric 2D; Super Monkey Ball is full 3D with world-tilting. Pick based on whether you want a 2D or 3D physics challenge.

### Branch 7A: Destructible Terrain & Digging

Builds on terrain interaction from the physics core (especially Gorillas.bas destructible terrain).

| #   | Game               | Year |  Platform   | Complexity | Scope | Combined | Key New Skills                                                                                                                                                                           |
| --- | ------------------ | :--: | :---------: | :--------: | :---: | :------: | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | (Super) Motherload | 2013 | Adobe Flash |    2.5     |  2.5  |    5     | Tile-based digging/mining, fuel and cargo resource loops, shop/upgrade economy, depth-based difficulty scaling, ore variety with value tiers                                             |
| 2   | Worms              | 1995 |    Amiga    |     3      |   3   |    6     | Turn-based artillery on destructible **pixel-level** terrain (not tiles), wind physics affecting projectiles, diverse weapon arsenal, multiplayer strategy, terrain deformation per shot |

### Branch 7B: Racing

Progresses from simple top-down racing through pseudo-3D to full 3D physics-based driving.

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Indy 500 | 1977 | Atari 2600 | 2 | 1 | 3 | Basic top-down racing: acceleration, steering, track boundaries, lap counting, 2-player split or shared screen |
| 2 | Super Mario Kart | 1992 | SNES | 3.5 | 3.5 | 7 | Mode 7 pseudo-3D track rendering, item/weapon system with rubber-banding, AI racer behavior, split-screen multiplayer, drift/hop mechanics, diverse track themes |
| 3 | Gran Turismo | 1997 | Console | 5 | 4 | 9 | Realistic vehicle physics simulation (tire grip, suspension, weight transfer), car tuning/customization systems, championship/license progression, large car/track roster |
| 4 | Rocket League | 2015 | Console/PC | 4.5 | 2.5 | 7 | 3D physics-based car-soccer hybrid, aerial mechanics (boost into air), boost resource management, online multiplayer networking and prediction, ball physics interaction with cars |

---

## Path 8: RPGs

**What you'll learn:** Character stats and progression systems, combat design (turn-based and real-time), inventory management, dialogue and narrative systems, save data serialization, world building, and encounter design.

### Branch 8A: Roguelike & Procedural RPG

Focuses on procedural generation, permadeath, and systems-driven gameplay.

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Rogue | 1980 | Unix | 2.5 | 1 | 3.5 | Procedural dungeon generation (rooms + corridors), permadeath, turn-based grid combat, ASCII/tile rendering, item randomization, fog of war |
| 2 | Diablo | 1996 | Windows | 3.5 | 5 | 8.5 | Real-time action combat in procedural dungeons, loot table and item affix generation system, character classes with skill trees, town hub, multiplayer networking |
| 3 | FTL: Faster Than Light | 2012 | PC | 4.5 | 5 | 9.5 | Spaceship systems management (shields, weapons, engines), crew assignment AI, real-time-with-pause combat, event/encounter scripting with branching outcomes, sector map generation, meta-progression unlocks |

### Branch 8B: Turn-Based RPG

Classic JRPG progression from simple to complex battle and narrative systems.

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Final Fantasy | 1987 | NES | 3 | 3.5 | 6.5 | Turn-based battle system, 4-character party management, class/job system, overworld + town + dungeon structure, shops and equipment, random encounter system |
| 2 | Pokémon Red and Blue | 1996 | Game Boy | 3.5 | 3 | 6.5 | Creature collection and roster management (151+), type effectiveness matrix, evolution system, wild encounters + trainer battles, Pokédex database, trading/link system |
| 3 | EarthBound | 1994 | SNES | 3 | 4.5 | 7.5 | Rolling HP meter (damage drains in real-time, allowing emergency healing), on-map visible enemies (no random encounters), inventory per-character limits as gameplay, unconventional status effects and battle win conditions |
| 4 | Chrono Trigger | 1995 | SNES | 3.5 | 5 | 8.5 | Active Time Battle system, dual/triple tech combo system (character position matters), on-field battles (no screen transition), multiple endings based on when you fight final boss, time travel affecting world state |
| 5 | Final Fantasy VIII | 1999 | PlayStation | 4 | 5 | 9 | Junction system (magic spells as stat modifiers), Draw mechanic (absorb magic from enemies mid-battle), Guardian Force summoning and leveling, Triple Triad card game sub-system, FMV cutscene integration |

> **⚠️ Similarity Note:** **Breath of Fire II (7)** is a traditional turn-based JRPG mechanically very similar to Final Fantasy. Its unique feature is a township-building system, but the core battle/exploration engine is the same. **Redundant with Final Fantasy** unless you specifically want the town-building side system.

### Branch 8C: Action RPG

Real-time combat combined with RPG progression.

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Secret of Mana | 1993 | SNES | 3.5 | 4 | 7.5 | Real-time combat with stamina/charge meter, ring menu UI system, 3-player cooperative multiplayer, weapon experience leveling, elemental magic system |
| 2 | Final Fantasy Crystal Chronicles | 2003 | GameCube | 3.5 | 3.5 | 7 | Co-op action RPG with chalice tether mechanic (proximity to shared object), spell fusion system (combine player spells), GBA-to-GameCube connectivity as asymmetric UI |

### Branch 8D: Life Sim & Farm RPG

Simulation-heavy RPGs driven by calendar systems and relationship building.

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Harvest Moon | 1996 | SNES | 3 | 3.5 | 6.5 | Calendar and season system driving gameplay, crop growth simulation over time, animal husbandry (feeding, milking, reproduction), NPC relationship and marriage system, stamina management |
| 2 | Animal Crossing | 2001 | Nintendo 64 | 3.5 | 4.5 | 8 | Real-time clock integration (game runs on real time), villager AI with schedules and personalities, museum collection system, seasonal events tied to real calendar, house decoration and debt payment loop, letter writing system |

---

## Path 9: First-Person Games

**What you'll learn:** 3D rendering fundamentals (raycasting → polygon), first-person camera and controls, 3D level design, spatial audio, physics in 3D, and network multiplayer.

**Prerequisites:** Shared Foundations; ideally Path 4 or Path 5 experience for game-feel fundamentals

| #   | Game            | Year |  Platform   | Complexity | Scope | Combined | Key New Skills                                                                                                                                                                                                                  |
| --- | --------------- | :--: | :---------: | :--------: | :---: | :------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Maze War        | 1974 | Imlac PDS-1 |     2      |   1   |    3     | First-person grid-based movement, simple 3D maze rendering (wireframe corridors), early network multiplayer concept                                                                                                             |
| 2   | Doom            | 1993 |     DOS     |    3.5     |  3.5  |    7     | Raycasting / BSP rendering engine, WAD-based level data format, hitscan + projectile weapon types, enemy AI (sight, pursuit, attack), sector-based level design with height                                                     |
| 3   | Quake           | 1996 |     DOS     |     4      |   3   |    7     | **True 3D** polygon rendering (not raycasting), mouselook free-aim, client-server networking architecture, 3D level editor, dynamic lighting, fully 3D enemy models                                                             |
| 4   | Luigi's Mansion | 2001 |  GameCube   |    3.5     |   3   |   6.5    | Flashlight and vacuum (Poltergust) mechanics, ghost AI behavior patterns (stun → capture loop), room-clearing progression, 3D environmental interaction and puzzle solving, portrait gallery collection                         |
| 5   | Portal          | 2007 |     PC      |     4      |   3   |    7     | Portal rendering (stencil buffer or recursive rendering), momentum conservation through portals, physics-based environmental puzzles, spatial reasoning challenge design, companion cube narrative                              |
| 6   | Metroid Prime   | 2002 |  GameCube   |    4.5     |  4.5  |    9     | First-person Metroidvania exploration (ability-gated 3D world), multiple visor modes (scan, thermal, x-ray) as game mechanics, morph ball third-person transition, lock-on strafing combat, environmental lore through scanning |

> **⚠️ Similarity Alerts:**
> - **⚠️ Doom II: Hell on Earth (7.5):** Uses the *exact same engine* as Doom with one new weapon (super shotgun) and new enemy types. The programming challenge is identical. **Cut Doom II.**
> - **Doom vs. Quake:** Genuinely different rendering challenges. Doom is 2.5D raycasting; Quake is true 3D polygon rendering. Both are valuable.
> - **Luigi's Mansion** is technically third-person but its flashlight/vacuum mechanics and ghost-hunting loop are unique enough to stand alone regardless of camera perspective.

---

## Path 10: Adventure Games

**What you'll learn:** Text parsing and natural language processing, dialogue tree systems, inventory-based puzzle design, room/scene graph management, and narrative-driven game architecture.

**Prerequisites:** Shared Foundations

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Zork | 1980 | PDP-10 | 2 | 1 | 3 | Text parser engine (verb-noun input processing), world model with rooms/exits/items, text-based inventory system, puzzle state tracking, narrative writing in code |
| 2 | Super Solvers: Midnight Rescue! | 1989 | DOS | 1.5 | 2 | 3.5 | Exploration with educational mini-game integration, clue gathering and deduction mechanic, multi-room building navigation, robot-painting identification |
| 3 | Maniac Mansion | 1987 | Commodore 64 | 3.5 | 3.5 | 7 | SCUMM verb-based point-and-click GUI, multiple playable characters with unique abilities, branching puzzle solutions, cutscene scripting system, multiple endings |
| 4 | The Secret of Monkey Island | 1990 | DOS | 4 | 4 | 8 | Refined point-and-click interface, insult swordfighting (dialogue-as-combat), complex multi-item combination puzzles, branching dialogue trees with humor, "you can't die" design philosophy |
| 5 | Day of the Tentacle | 1993 | DOS | 4 | 4 | 8 | Multi-character time-travel puzzles (actions in past affect present/future), item passing between time periods via shared object, complex cross-temporal dependency chains |

> **⚠️ Similarity Alerts:**
> - **⚠️ Super Solvers: OutNumbered! (3.5):** Same engine and game structure as Midnight Rescue! with a math theme instead of reading. **Redundant — cut.**
> - **Maniac Mansion → Monkey Island → Day of the Tentacle** all use SCUMM-style engines, but each introduces meaningfully new puzzle paradigms: Maniac Mansion (multi-character branching), Monkey Island (dialogue-as-gameplay), Day of the Tentacle (cross-temporal dependencies). **All three are defensible as separate challenges.**

---

## Path 11: Strategy & Simulation

**What you'll learn:** Complex systems simulation, AI decision-making at scale, resource management, pathfinding for many units, UI design for information-dense games, and simulation loops.

### Branch 11A: Real-Time Strategy

The most demanding programming path. Every entry shares a large core (resource gathering, base building, unit production, fog of war, pathfinding) — the key differentiators are noted.

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Dune II | 1992 | DOS | 5 | 5 | 10 | **Foundational RTS:** resource harvesting loops, base/building placement, unit production queues, fog of war, unit pathfinding (A*), build-order dependency trees |
| 2 | Warcraft: Orcs & Humans | 1994 | DOS | 4.5 | 4 | 8.5 | Refined RTS with unit selection groups, two-faction mirrored balance, mission scripting and objectives, building dependency chains, improved UI |
| 3 | Command & Conquer | 1995 | DOS | 5 | 5 | 10 | Sidebar build UI (build from sidebar, not from buildings), harvester autonomous AI, FMV story integration, asymmetric faction units (GDI vs Nod), multiplayer balance |
| 4 | Warcraft II: Tides of Darkness | 1995 | DOS | 5 | 5 | 10 | Naval combat layer (ships, oil rigs, sea + land), improved pathfinding, fog of war with explored/unexplored distinction, waypoint system |
| 5 | StarCraft | 1998 | Windows | 5 | 5 | 10 | **Fully asymmetric faction design** (3 races with completely different units, buildings, and mechanics), advanced unit AI behaviors, replay system, competitive balance at professional level |
| 6 | Age of Empires II | 1999 | Windows | 5 | 5 | 10 | Technology age progression system (4 ages), civilization-specific bonuses and unique units, 4 resource types, walls/gates/fortifications, large unit count management |

> **⚠️ Major Redundancy Warning:** All six games share the same foundational RTS programming challenge. **Recommend keeping 2 at most:**
> - **Dune II or Command & Conquer** — foundational, symmetric/near-symmetric factions
> - **StarCraft** — asymmetric faction design is the only entry that introduces a *fundamentally* new programming challenge (balancing three completely different unit/building/tech systems)
>
> Warcraft I, Warcraft II, and AoE II are incremental variations on the same core engine. Cut unless studying historical RTS evolution specifically.

### Branch 11B: City & World Simulation

Simulation-driven games focused on emergent systems rather than direct combat.

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Minecraft | 2009 | PC | 4 | 2 | 6 | Voxel world generation (Perlin/simplex noise), chunk loading/streaming system, block placement and destruction, crafting recipe system, survival resource loops, infinite procedural terrain |
| 2 | SimCity | 1989 | Amiga | 5 | 3.5 | 8.5 | City simulation loop (zoning → development → demand), RCI demand model, infrastructure simulation (power, water), tax/budget system, disaster events, emergent city behavior |
| 3 | SimCity 2000 | 1993 | Macintosh | 5 | 4 | 9 | Isometric rendering, underground infrastructure layer (pipes, subways), water table simulation, ordinance system, more granular zone density, detailed advisor feedback |
| 4 | SimCity 3000 | 1999 | Windows | 5 | 4.5 | 9.5 | Neighbor city deals (inter-city trade simulation), waste management system, landmark placement, enhanced advisor AI — incremental over SC2000 |
| 5 | Roller Coaster Tycoon | 1999 | PC | 5 | 5 | 10 | Roller coaster physics simulation (track builder with g-forces), guest AI (needs, pathfinding, satisfaction, nausea), park economy, ride rating calculation, scenario objectives |
| 6 | The Sims | 2000 | Windows | 5 | 5 | 10 | Autonomous agent AI (needs/motives driving behavior), object interaction system (every object advertises actions), house building mode, social relationship simulation, career/skill system |
| 7 | EverQuest | 1999 | Windows | 5 | 5 | 10 | **MMO architecture:** persistent online world, server infrastructure and client-server synchronization, account/character database, guild and social systems, raid encounter design, network latency handling |

> **⚠️ Similarity Alert:** **SimCity / SimCity 2000 / SimCity 3000** are the same core simulation with incremental additions. **Keep SimCity 2000** (best balance of features vs. scope). The other two are redundant as programming challenges.

### Branch 11C: Tactical Strategy

Unique strategy games that don't fit the traditional RTS mold.

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Pikmin | 2001 | GameCube | 4 | 3.5 | 7.5 | Swarm AI (managing 100+ semi-autonomous units simultaneously), unit-type specialization (red/blue/yellow), real-time resource gathering with carrying, time-limited day cycle creating urgency, whistling/throwing command interface |

---

## Path 12: Fighting & Beat 'em Up

**What you'll learn:** Hitbox/hurtbox collision systems, character state machines, combo timing, multiplayer combat balancing, and AI opponents.

**Prerequisites:** Shared Foundations; Path 3 or Path 4 helpful

| # | Game | Year | Platform | Complexity | Scope | Combined | Key New Skills |
|---|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------|
| 1 | Teenage Mutant Ninja Turtles | 1989 | NES | 2.5 | 3 | 5.5 | Character switching (4 turtles with different range/speed), overhead + side-scrolling hybrid sections, vehicle segments, multi-weapon combat |
| 2 | Double Dragon | 1987 | Arcade | 3.5 | 4.5 | 8 | Side-scrolling beat-em-up: multi-directional melee combat (punch, kick, elbow), grab and throw mechanics, weapon pickups (bats, whips), co-op, walking enemy AI |
| 3 | Super Smash Bros. | 1999 | Nintendo 64 | 3.5 | 3 | 6.5 | **Platform fighter:** percentage-based knockback (not HP depletion), ring-out KO system, fundamentally different from health-bar fighters, multi-character unique movesets, 4-player simultaneous, stage hazards, items |

---

## Standalone & Niche Challenges

These games offer unique programming challenges that don't naturally fit into the progression paths above. Each teaches something distinct.

| Game | Year | Platform | Complexity | Scope | Combined | Key Unique Challenge |
|------|:----:|:-------:|:----------:|:-----:|:--------:|----------------------|
| Guitar Hero | 2005 | Console | 1.5 | 1.5 | 3 | **Rhythm game:** Audio-to-gameplay synchronization, note highway scrolling, input timing windows (perfect/good/miss), streak and multiplier systems, song charting format |
| Kirby's Pinball Land | 1993 | Game Boy | 2 | 2 | 4 | **Simplified digital pinball:** Flipper mechanics, ball physics on table, bumpers, multi-table screens with game-character elements (bosses, mini-games) |
| Full Tilt Pinball | 1995 | PC | 2.5 | 2.5 | 5 | **Realistic pinball simulation:** Advanced ball physics (spin, friction), multi-ball management, ramp and lane detection, tilt mechanic, dot-matrix display simulation, real-table feel |

> **⚠️ Pinball Note:** Kirby's Pinball Land and Full Tilt Pinball share the same core challenge (ball physics, flipper mechanics). Full Tilt is more technically demanding with realistic physics. **Pick one.** Kirby's is simpler; Full Tilt is more physics-rigorous.

---

## Games Mentioned Only in Similarity Notes

These games appear in the similarity warnings above but are **not assigned a primary table position** because they are too similar to another entry that already covers the same programming challenge. Listed here for completeness with their closest equivalent:

| Game | Combined | Redundant With | What Little It Adds |
|------|:--------:|----------------|---------------------|
| Chrome Dinosaur Game *or* Flappy Bird | 1 / 2 | Each other | Both are single-input endless avoidance; pick one |
| Super Solvers: OutNumbered! | 3.5 | Midnight Rescue! | Same engine, math theme instead of reading |
| Chip 'n Dale: Rescue Rangers | 4.5 | DuckTales | Same-era Capcom NES platformer; adds co-op throwing |
| Super Mario Land 2: 6 Golden Coins | 4.5 | SMB3 / SMW | Same Mario formula at Game Boy scale |
| Mega Man 2 | 5.5 | Mega Man | More stages, same engine and design |
| Mega Man 3 | 5.5 | Mega Man | Adds slide and Rush; still same engine |
| Mega Man X | 5.5 | Mega Man | Wall-jump, dash, armor upgrades — *most defensible* of the MM sequels |
| Metroid II: Return of Samus | 5 | Metroid / Super Metroid | Area-locking by kill count; minor variation |
| Doom II: Hell on Earth | 7.5 | Doom | Same engine, super shotgun, new enemies — content only |
| Breath of Fire II | 7 | Final Fantasy | Traditional JRPG; adds township building |
| Oracle of Ages | 6 | Link's Awakening | Time-travel puzzles on same engine |
| Oracle of Seasons | 6 | Link's Awakening | Season-swap puzzles on same engine |
| Spacewar! *or* Asteroids | 2.5 / 2.5 | Each other | Both are thrust-rotate-shoot in space; pick one |
| River Raid *or* StarGoose! | 4 / 4 | Each other | Both vertical scrollers; River Raid's fuel mechanic is more interesting |
| SimCity | 8.5 | SimCity 2000 | SC2000 is the same sim with more features |
| SimCity 3000 | 9.5 | SimCity 2000 | Incremental additions to same formula |
| Warcraft: Orcs & Humans | 8.5 | Dune II / C&C | Refined RTS, same core |
| Warcraft II | 10 | C&C / StarCraft | Adds naval; still same RTS engine |
| Command & Conquer | 10 | Dune II | Polished version of same formula |
| Age of Empires II | 10 | StarCraft | Tech ages; same RTS core |

---

## Choosing Your 20

If you're selecting **20 games** for a skill-progression challenge, here's a suggested strategy:

1. **Start with all 4 Shared Foundations** (Pong, Breakout, Snake, Gorillas)
2. **Pick 2-3 paths** that interest you most
3. **Follow each path's progression** — don't skip ahead, as each game builds on the last
4. **At branch points**, pick the branch that interests you — you don't need both
5. **Skip ⚠️ Similar games** unless you have a specific reason to include them
6. **End with 1-2 capstone games** at the top of your chosen paths (SM64, OoT, StarCraft, etc.)

### Example 20-Game Tracks

**Track: Platformer Specialist**
Foundations (4) → Flappy Bird → Space Invaders → SMB → Castlevania → Mega Man → Sonic → SMB3 → Metroid → Super Metroid → Kirby's Adventure → DKC → Prince of Persia → Crash Bandicoot → Super Mario 64 → Ocarina of Time

**Track: Generalist Breadth**
Foundations (4) → Flappy Bird → Minesweeper → Tetris → Pac-Man → SMB → Rogue → Mega Man → Legend of Zelda → Metroid → Zork → Doom → Final Fantasy → Worms → ALttP → Diablo → Super Mario 64

**Track: Systems & Simulation**
Foundations (4) → Cookie Clicker → Tetris → Conway's GoL → Lunar Lander → Rogue → Lemmings → Harvest Moon → Worms → Minecraft → Pokémon → Pikmin → SimCity 2000 → Diablo → FTL → StarCraft
