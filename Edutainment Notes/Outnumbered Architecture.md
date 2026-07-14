# OutNumbered! — Architecture & Decomposition Plan (Godot 4.6+ / GDScript)

A planning document for rebuilding The Learning Company's *Super Solvers: OutNumbered!* (1990).
The goal here is **not** a feature list — it's a map of *where the hard parts actually are*, *which
Godot construct each subsystem wants to be*, and *what order to build them in* so you never face the
"infinite menu of choices" all at once.

---

## 0. How to use this document

Read sections 1–3 once to get the shape of the problem. Then **live in section 7 (Build Order)**.
Everything else is reference you pull from when a milestone tells you to.

The single most important idea in this whole document:

> **Build the deduction brain first, headless, with no art. The side-scroller is presentation layered
> on top of a game that already works in the console.**

If you internalize only that, you've avoided the most common way this project dies.

---

## 1. What OutNumbered actually is (mechanically)

Strip away the TV-station theme and the game is a **deduction loop wrapped in a light side-scroller**.

**The core loop of one round:**
1. The Master of Mischief hides behind one of **5 room doors**. Each door shows a **4-symbol code**.
2. One room's code is "the answer." You don't know which room until you cross-reference two things:
   - **Door Codes** — found by solving a math puzzle inside each room (pauses the clock).
   - **The Secret Code** — found one symbol at a time by zapping the robot Telly and answering a
     timed math drill (clock keeps running).
3. A **Match Rule** tells you how the Secret Code relates to the door codes:
   - Early game: matches in **symbols AND order** (exact).
   - Expert+ : matches in **symbols only, any order** (harder — you genuinely need all 4).
4. When you can *prove* which door matches, you **accuse** one room. One guess only.
   - Correct → win, collect Energy/Time/Win bonuses, add to lifetime score, possibly rank up.
   - Wrong or clock hits midnight → lose, lifetime score unchanged.

**The deduction is solvable early sometimes.** You do NOT always need all 4 secret symbols or all 5
door codes. If you have all door codes and only one can still match the partial secret code, you're
done. *This partial-solve logic is the single trickiest piece of game logic in the project.* (See §6.)

**The world it lives in:**
- 2 floors, 5 named rooms (Cartoon, Equipment, Sound, News, Game), elevators at each end, random
  recharge-machine placement.
- Player walks left/right, enters doors/elevators/machines via Up, hops over attacks, zaps enemies.
- **Telly** — roams halls, attacks (crashes, discs, sound waves, bolts, stars), must be zapped while
  its screen is red to trigger a secret-code drill.
- **LiveWire** — a floor hazard you jump or zap.
- **Zapper** — depletes; recharged at machines; leftover energy = end-round bonus.

**Time:** round = 9 real minutes = 9:00 PM → midnight (1 game-minute per 3 real seconds). Room puzzles
**pause** the clock; Telly drills **do not**. That pause/no-pause distinction is a real rule, not flavor.

**Difficulty / progression:** 8 ranks (Trainee → Champion) gate 4 difficulty levels, which change:
problem types (add/sub/mult/div), number ranges (0–12), problem format (`3+5=?` vs `?+5=8`), how many
drills per Telly capture (4→6→8→10), puzzles per room (1 → 2 at Expert+), and the Match Rule.

---

## 2. The honest difficulty map (where to spend effort)

Per your "be constructively critical" preference — this is where I'll save you the most time. Effort
should follow real difficulty, and people's intuitions about this game are usually inverted.

| Subsystem | Looks like | Actually is | Spend effort? |
|---|---|---|---|
| Side-scroller movement | The "real game" | Trivial. Left/right + a hop. No platforming, no gravity puzzles. | **Minimal.** Don't gold-plate it. |
| Deduction engine | A minor detail | **The actual game.** Codes, match rules, partial-solve. Pure logic. | **Most of your design care.** |
| The 15 puzzle types | A huge mountain (15×!) | A mountain *only if you hardcode each one*. Data-driven, it's ~5 UI templates. | High, but **structural** effort, not 15× grind. |
| Telly encounter | A combat system | A spawner + a timed quiz popup. Clock-running is the only nuance. | Moderate. |
| Clock / scoring / ranks | Fiddly | Genuinely fiddly bookkeeping. Easy to get the pause rule wrong. | Moderate, get it right early. |
| Save / profiles | Boring | Boring and easy in Godot. Don't over-architect it. | Minimal. |
| Art / juice / audio | Where the fun is | A bottomless time sink that produces zero gameplay. | **Last. Strictly last.** |

**The trap:** starting with the side-scroller because it's the visible "game." You'll spend three weeks
on sprite animation and a camera and have *nothing playable*, because the thing that makes OutNumbered
a game — the deduction — isn't built. Build the brain first; it's playable with buttons.

**The other trap:** treating "15 puzzle types" as 15 separate programming tasks. It's really a handful
of **data-display templates** (bar graph, line graph, table, labeled-objects, slider/spinner) each
driven by a data Resource. Get the templating right once and the 15th puzzle costs you a `.tres` file,
not a new scene.

---

## 3. The one architectural principle: separate *simulation* from *presentation*

Draw a hard line through the project:

- **Simulation (model):** round state, the codes, the match rule, "is this solvable yet?", scoring,
  rank, difficulty config. **Pure GDScript. No nodes that draw anything. Testable from the console.**
- **Presentation (view):** the hallway, sprites, the Decoder screen, puzzle UIs, the clock display,
  particles, music.

The simulation must never reach into the view. The view reads the simulation and renders it; it sends
the simulation *intents* ("accuse room 3", "submit answer 42"). They talk through **signals** and a
small **state object**, never by one poking the other's internals.

Why this matters for *you specifically*: it means at every moment there is a clean, finished, testable
thing (the model) and a swappable thing (the view). You can throw away your entire side-scroller and
rebuild it without touching the game. That's what kills overwhelm — the scary part is small, done, and
walled off.

---

## 4. System map (the subsystems)

Nine subsystems. Each is independently buildable. Think of these as the "modules" you were missing.

1. **App Flow** — boot → menus → sign-in → game-type select → round → win/lose → level-up → repeat.
   A high-level state machine + scene switching.
2. **Profile/Save** — club members, lifetime score, rank. Trivial persistence.
3. **Round Controller** — owns ONE round's mutable state and the clock. The conductor.
4. **Deduction Model** — symbols, 4-symbol codes, match rules, solvability, accusation resolution.
   *Pure logic. The crown jewel.*
5. **Puzzle System** — 15 puzzle types as data + ~5 UI templates; produces a door-code symbol on success.
6. **World/Navigation** — 2 floors, rooms, elevators, rechargers, player movement.
7. **Encounters** — Telly spawn/attack/zap → timed secret-code drill; LiveWire; zapper + recharge.
8. **HUD/UI** — clock, energy bar, **Decoder** (notepad + Decide), calculator, help/options dialogs.
9. **Audio** — context music (title/hall/room), SFX.

Cross-cutting: **Difficulty/Config** (rank → level → problem rules), used by 5 and 7.

Dependency direction (who needs whom to exist first):

```
Deduction Model  ──┐
                   ├──> Round Controller ──> App Flow
Difficulty/Config ─┘            │
                                ├──> Puzzle System ──> HUD/Decoder
                                ├──> Encounters
                                └──> World/Navigation
Profile/Save ───────────────────────^ (read at boot, written on win)
Audio ── orthogonal, plug in last
```

Read that graph as your build order in miniature: **leaves first** (Deduction Model, Config), then the
Round Controller, then everything that hangs off it.

---

## 5. Godot construct mapping (the "Godot-thonic" part)

For each subsystem, the idiomatic Godot 4.x tool. Where there's a tempting wrong choice, I name it.

| Subsystem | Idiomatic Godot construct | Avoid |
|---|---|---|
| Global state (current profile, current round handle, signals) | **Autoload singletons**: `GameState`, `EventBus` (signal hub), `AudioManager`, `SceneSwitcher` | Passing references through 6 nodes; static vars everywhere |
| App Flow | A flow **state machine** (enum + `match`, or one node-per-state) driving `SceneSwitcher.change_scene()` | A god-script in the main scene `_process` with a wall of `if` |
| Cross-subsystem messaging | **Signals**, with a tiny `EventBus` autoload for truly global events (e.g. `door_code_found`, `telly_zapped`, `round_won`) | Direct `get_node("../../..")` chains |
| Deduction Model | Plain **`RefCounted`** classes (`Code`, `MatchRule`, `RoundModel`) with `class_name` — *not* `Node`. They don't belong in the tree. | Making the model a Node; baking logic into UI scripts |
| Symbols, puzzle defs, rank table, difficulty levels | **Custom `Resource` classes** (`.tres` files): `SymbolSet`, `PuzzleDefinition`, `RankTier`, `DifficultyLevel` | Hardcoding these as constants/dictionaries in code |
| Round Controller | A **Node** that owns the `RoundModel`, runs the clock via a `Timer` or accumulated `delta`, emits signals | Putting clock logic in `_process` of five different nodes |
| Puzzle System | A **base puzzle scene** (`PuzzleScreen`, a `Control`) + **scene inheritance** or composition for each template; each instance configured by a `PuzzleDefinition` Resource | A unique bespoke scene+script per all 15 with copy-pasted plumbing |
| Player | **`CharacterBody2D`** + a small movement state machine (`idle`/`walk`/`hop`/`zap`/`stunned`) | `AnimatedSprite2D` driving game logic; physics overkill for a flat floor |
| Rooms / doors / machines / elevators / rechargers | **`Area2D`** interaction zones; player presses the `interact` action when overlapping; each is its own **scene** placed in the level | Hard-coding positions and `if global_position.x > 412` checks |
| Telly & LiveWire | Each its own **scene** (`CharacterBody2D`/`Area2D`); spawn via a spawner node; states via enum machine; in a **group** (`"enemies"`) | One mega-enemy script with mode flags |
| Zapper / projectiles | `Area2D` projectile scenes; energy is an int on `GameState`/round; recharge = `interact` on a recharger Area2D | RayCast hacks; tracking energy in three places |
| HUD overlay (clock, energy) | **`CanvasLayer`** + `Control` nodes; subscribe to `EventBus`/round signals; update on signal, not every frame | Polling the model in `_process` |
| Decoder, calculator, puzzle UIs, menus | **`Control`** scenes (`VBoxContainer`/`GridContainer`); keyboard-navigable with `focus` + `ui_*` actions | Re-implementing focus/navigation by hand |
| Input | **Input Map actions** in Project Settings: `move_left`, `move_right`, `interact`, `jump`, `zap`, `decoder`, plus `ui_accept`/`ui_cancel` | `Input.is_key_pressed(KEY_LEFT)` scattered in scripts |
| Tuning values (speeds, spawn rates, clock ratio, bonuses) | **`@export`** vars on the relevant node, or a `GameConfig` Resource | Magic numbers inline |
| Animation / transitions | **`AnimationPlayer`** for sprite/cutscene; **`Tween`** for one-off UI motion | Manual `position += ...` in `_process` for tweenable things |
| Save/profiles | A `PlayerProfile` **Resource** saved with `ResourceSaver`/`ResourceLoader`, **or** `ConfigFile` for simple key/values, under `user://` | Inventing a serialization format; storing in the scene |
| Audio | **`AudioManager` autoload** with `AudioStreamPlayer`s per channel; crossfade with `Tween` on volume | A player node per scene that restarts music on every scene change |

### Why Resources are the lever for this game specifically

OutNumbered is fundamentally a **content/data game**: 15 puzzle types × 4 difficulty levels × number
ranges × formats × 8 ranks. If that combinatorial space lives in **code**, every tweak is a code change
and the complexity leaks everywhere — *this is exactly the "infinite choices" feeling you described.*

If it lives in **Resources**, the explosion is contained in data files the inspector edits for you:

- `SymbolSet.tres` — the pool of door symbols (phone, TV, lightning, star…) and their textures.
- `DifficultyLevel.tres` × 4 — allowed operations, number range, allowed formats, drills-per-capture,
  puzzles-per-room, match rule.
- `RankTier.tres` × 8 — name, score threshold, which `DifficultyLevel` it maps to.
- `PuzzleDefinition.tres` × 15 — which template renders it, its data schema, its question phrasings.

A `PuzzleGenerator` then takes `(PuzzleDefinition, DifficultyLevel)` and produces a concrete instance
(real numbers, the correct answer, the prompt string). **Your puzzle UI never knows about difficulty —
it just renders whatever the generator handed it.** That decoupling is the whole ballgame.

---

## 6. The genuinely tricky logic (design it deliberately, don't wing it)

Most of the project is routine. These three spots are where bugs and rework hide. Decide them on paper
before coding.

**(a) The Match function.** Two modes:
- *Ordered:* door code equals secret code position-for-position.
- *Unordered (Expert+):* door code is a permutation of the secret code (same multiset of symbols).

Write `MatchRule` as a strategy: a single method `matches(door_code, secret_code) -> bool`, with two
implementations. The rest of the game asks the rule; it never branches on difficulty itself.

**(b) Partial solvability — "can I accuse yet?"** This is the subtle one. You can solve before having
everything if the *known* information uniquely determines a room. Model it as a filter:

> Given the partial secret code (some symbols known) and whatever door codes you've found, compute the
> set of rooms **still consistent** with what's known under the current match rule. If exactly one room
> remains consistent **and** you've satisfied the game's gate (all door codes OR full secret code), the
> player may accuse.

Build this as a pure function `candidate_rooms(known_secret, found_door_codes, rule) -> Array[Room]`.
Test it in isolation with hand-built cases. The original game gates the *button* on "all door codes OR
full secret code," but the *certainty* can come earlier — keep those two notions separate in code
(`can_press_decide` vs `is_determined`).

**(c) The clock pause rule.** Room puzzles pause the clock; Telly drills don't. Put the clock on the
Round Controller with an explicit `running: bool`, and have exactly one place that flips it
(`pause_clock()`/`resume_clock()`), called on enter/exit of puzzle screens. Don't let five scenes each
fiddle the timer — that's how you get a clock that runs during a puzzle in one path and not another.

---

## 7. Build order (the anti-burnout spine)

This is the part to actually follow. Each milestone is **independently runnable** and ends in a thing you
can *see work*. The riskiest, most-core stuff is first, while motivation is highest. Presentation is last,
because it's swappable and bottomless.

**M0 — Skeleton (½ day).** Create the project. Set up the **Input Map** actions. Create empty autoloads
(`GameState`, `EventBus`, `SceneSwitcher`, `AudioManager`). Agree your **folder structure** (see §8). One
boot scene that prints "ready." *Win: it runs.*

**M1 — The brain, headless (1–2 days). THE important milestone.** No art, no scenes-with-pictures. Pure
GDScript:
- `Symbol`, `SymbolSet`, `Code` (4 symbols), `MatchRule` (ordered + unordered).
- `RoundModel`: picks the hideout room, generates 5 door codes + the secret code, tracks what's found.
- `candidate_rooms()` and `resolve_accusation()`.
- Drive it from a `_ready()` or a few debug buttons: "reveal door code N", "reveal secret symbol N",
  "accuse room K" → print win/lose. *Win: you can play the entire deduction in the console. This is the
  game. Everything after is making it nice.*

**M2 — Decoder UI + accusation (1–2 days).** A `Control` Decoder screen showing found door codes, the
partial secret code, the match rule, and a Decide flow. Wire fake "found a door code / found a symbol"
buttons to the model. *Win: you play OutNumbered's mind-game with a mouse/keyboard, no walking yet.*

**M3 — One real puzzle, then the framework (2–3 days).** Pick the easiest template (e.g. the
labeled-objects/price-tags puzzle). Build `PuzzleScreen` base, the `PuzzleDefinition` Resource, and the
`PuzzleGenerator`. On success → emit `door_code_found` → it lands in the Decoder. Then stub the other
templates (they can return a fixed answer for now). Add the **calculator** Control. *Win: solving a puzzle
feeds the brain.*

**M4 — The world (3–5 days).** Now the side-scroller, and keep it dumb: a flat floor, `CharacterBody2D`
left/right, `Area2D` doors/elevators/rechargers, two floors, the 5 rooms. Entering a room opens a puzzle
(M3); the elevator swaps floor; the recharger refills energy. *Win: you walk the station and rooms feed
the Decoder.*

**M5 — Encounters (2–4 days).** Telly spawner + attacks + zap-while-red → the timed drill that yields a
**secret-code** symbol (clock keeps running — wire the pause rule from §6c). LiveWire hazard. Zapper energy
+ recharge already exist from M4. *Win: both information sources (door codes AND secret code) are now
earned through play.*

**M6 — Round lifecycle & meta (2–3 days).** The clock counting 9:00→midnight, lose-on-midnight,
Energy/Time/Win bonuses, lifetime score, the 8 ranks, rank→difficulty mapping, level-up screen, and
`PlayerProfile` save/load. The App Flow state machine now ties menus → sign-in → game-type → round →
result together. *Win: a complete, replayable game with progression.*

**M7 — Customization & content fill (open-ended).** Implement the remaining puzzle templates for real.
Add the Customized Game / Drill-for-Skill modes (they're just different `DifficultyLevel`/config inputs —
cheap once §5's data-driven design holds). *Win: feature-complete.*

**M8 — Juice & audio (open-ended, strictly last).** Sprite animation, the classical tracks (title/hall/
room), SFX, transitions, particles, screen feel. *Win: it feels like 1990 in the best way.*

Notice M1–M3 contain the entire *game* and need essentially no art. By the time you touch sprites, you're
decorating something that already works. That ordering is the whole point.

---

## 8. Suggested project layout

```
res://
├─ autoload/            # GameState.gd, EventBus.gd, SceneSwitcher.gd, AudioManager.gd
├─ model/               # PURE logic, RefCounted, no Nodes: Code.gd, MatchRule.gd, RoundModel.gd ...
├─ data/                # Resources (.tres): symbols/, difficulty/, ranks/, puzzles/
│   └─ resource_defs/   # the custom Resource scripts (SymbolSet.gd, PuzzleDefinition.gd ...)
├─ flow/                # app state machine, menus, sign-in, game-type select, result/level-up screens
├─ world/               # level scenes, player/, enemies/ (telly/, livewire/), interactables/
├─ puzzles/             # PuzzleScreen base + template scenes + PuzzleGenerator.gd
├─ ui/                  # decoder/, calculator/, hud/, dialogs/
├─ audio/               # streams + bus layout
└─ tests/               # quick scripts that exercise model/ from the command line
```

Two rules that keep it sane: **`model/` may never `import`/reference anything in `world/` or `ui/`**, and
**data lives in `data/`, not in code**. If you find yourself typing puzzle numbers or rank thresholds into
a `.gd` file, stop and make it a Resource.

---

## 9. Scope discipline — cut this for your first playable

You don't need the whole 1990 feature set to have a *finished, real* game. A defensible MVP:

- **3 rooms** instead of 5 (less map, less content, same logic).
- **3–4 puzzle templates** instead of all 15 (the rest are content, added later).
- **One difficulty level**, ordered match rule only. (Unordered + ranks come in M6/M7.)
- **Telly only**, skip LiveWire at first.
- Placeholder rectangles for art through M6.

This MVP still exercises every architectural seam (model, puzzle pipeline, world, encounter, HUD, flow),
so nothing you build gets thrown away when you scale back up to full scope — you're adding *data and
content*, not re-architecting. That's the payoff of doing §3 and §5 properly.

---

## 10. Decisions to make before M1 (so you're not deciding mid-code)

- **Symbol set:** how many distinct door symbols exist in the pool? (The original uses a fixed icon set —
  phone, TV, lightning, star, etc. Pick ~8–12.)
- **Save format:** `PlayerProfile` Resource vs `ConfigFile`. For multiple named members with a few fields
  each, `ConfigFile` under `user://` is the lower-friction choice; a Resource is nicer if profiles grow.
- **Flow state machine style:** enum+`match` (simplest, fine for ~6 states) vs node-per-state (overkill
  here, but you may already know the pattern). Recommendation: enum+`match` until it hurts.
- **Clock implementation:** a `Timer` ticking game-minutes vs accumulating `delta`. Accumulated `delta`
  with one `running` flag is easiest to pause correctly.

None of these block M1's *model* work — but settling them now means M1 doesn't stall on a side-quest.

---

## 11. Quick reference — the rules, in numbers

- Round length: **9 real minutes** = 9:00 PM → midnight; **1 game-minute per 3 real seconds**.
- Rooms: **5** (Cartoon, Equipment, Sound, News, Game). Floors: **2**. Door code length: **4 symbols**.
- Puzzles per room: **3 machines, 2 can be active**; one active per room per round (two at Expert+).
- Puzzle types total: **15** (≈5 display templates). Room puzzles **pause** the clock.
- Telly drill length by rank: **4 → 6 → 8 → 10** problems. May miss **1** and still get the symbol; **2
  misses** = re-catch. Telly drills do **not** pause the clock.
- Ranks → score thresholds: Trainee 0 · Junior 5,000 · Senior 30,000 · Pro 60,000 · Expert 120,000 ·
  Master 200,000 · All-Star 300,000 · Champion 500,000.
- Rank → difficulty level: Trainee/Junior → L1 · Senior/Pro → L2 · Expert/Master → L3 · All-Star/Champion
  → L4. Match rule flips to **unordered at Expert**.
- End-round bonuses: **Energy** (zapper left) + **Time** (clock left) + **Win** (flat, scales with level).
- Accusation: **one guess**. Wrong or midnight = lose, lifetime score unchanged.
```
```

---

*Sources: Wikipedia (OutNumbered!), the GameFAQs walkthrough by DetroitDJ, and contemporary abandonware
descriptions. Where the original's exact value is unknown (e.g. precise bonus formulas), treat the number
as a tunable `@export`/Resource field rather than a fact to reverse-engineer.*
