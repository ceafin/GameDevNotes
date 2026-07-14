# OutNumbered! — Build Roadmap & Where to Start

Companion to `outnumbered_godot_architecture.md`. That doc is the *why*; this is the *do-this-next*.
Tick the boxes. Each milestone ends in something you can run and see work.

> **The one rule:** build the deduction brain first (M1), with no art. The walking-around game is
> presentation you layer on later. Never start with sprites.

---

## ▶ Start here — your literal first session (~2 hours)

Do exactly these, in order. The goal is to touch the real core on day one and end with a thing that runs.

- [ ] Install **Godot 4.6+**, create the project, set up the folder structure from §8 of the architecture doc
      (just make the empty folders: `model/`, `data/`, `flow/`, `world/`, `puzzles/`, `ui/`, `audio/`, `autoload/`, `tests/`).
- [ ] **Project Settings → Input Map:** add actions `move_left`, `move_right`, `interact`, `jump`, `zap`, `decoder`.
      (You won't use most yet — defining them now stops you hardcoding keys later.)
- [ ] Create four **empty autoload scripts** and register them in Project Settings → Autoload:
      `GameState`, `EventBus`, `SceneSwitcher`, `AudioManager`. Each can be a bare `extends Node` for now.
- [ ] In `model/`, write `Code.gd`: a `RefCounted` with `class_name Code`, holding an array of 4 symbol IDs,
      plus a `_to_string()` so you can print it. **No Node, no scene — pure logic.**
- [ ] In `tests/`, write a 10-line script that makes two `Code`s and prints them. Run it.

**Done when:** the test prints two codes to the console. That's it. You've started, and you started in the
right place — the model — not in a swamp of art.

---

## Dependency order (what must exist before what)

Read this top-to-bottom: it's roughly the order things get built. **Leaves (no dependencies) first.**

| Subsystem | Must exist first | Built in | Why it sits here |
|---|---|---|---|
| **Deduction Model** | *(nothing — pure logic)* | **M1** | It's the actual game. Build and test it before anything can render. |
| **Difficulty / Config** | *(nothing — just data Resources)* | M1 (basic) → M7 (full) | Leaf data. The model and puzzles read it; it reads nothing. |
| **Round Controller** | Deduction Model, Config | M1 (lite) → M6 (clock+meta) | The conductor. Owns one round's state and the clock. |
| **Decoder / HUD** | Round Controller (reads the model) | M2 (Decoder) → M6 (clock+energy) | A view onto the model. Needs the model to exist to show anything. |
| **Puzzle System** | Round Controller, Config | M3 | Produces door codes → feeds the Decoder. Needs the round to feed. |
| **World / Navigation** | Round Controller, Puzzle System | M4 | Walking is just a *delivery mechanism* for puzzles and encounters. |
| **Encounters (Telly/LiveWire)** | World, Round Controller, Config | M5 | Lives in the world; delivers secret-code symbols to the model. |
| **Profile / Save** | *(nothing — read at boot, written on win)* | M6 | Boring and standalone. No reason to do it early. |
| **App Flow** | basically everything above | M6 | The glue that ties menus → round → result. Glue comes after parts. |
| **Audio** | *(orthogonal)* | M8 | Plugs into anything, depends on nothing, adds zero gameplay. Last. |

The shape to notice: the **leaves are the core** (Deduction Model, Config). The visible stuff
(World, Audio) is downstream and swappable. That inversion — core-first, visible-last — is the
anti-burnout structure.

---

## Milestone roadmap

Effort estimates assume hobby pace and will vary. The point isn't the numbers — it's that **every
milestone is independently runnable** and the scary/core parts come while motivation is high.

### ☐ M0 — Skeleton — *½ day*
*(This is the "Start here" session above.)*
- [ ] Project, folders, Input Map, four empty autoloads, one boot scene that runs.
- **Done when:** the project launches and prints "ready."

### ☐ M1 — The brain, headless — *1–2 days* ⭐ **the milestone that matters**
No art. No scenes that draw. Pure GDScript in `model/`.
- [ ] `Symbol` / `SymbolSet` (the pool of ~8–12 door icons, IDs only for now).
- [ ] `Code` (4 symbols) — already started in M0.
- [ ] `MatchRule` with two implementations: **ordered** and **unordered** (same method signature).
- [ ] `RoundModel`: pick the hideout room, generate 5 door codes + the secret code, track what's "found."
- [ ] `candidate_rooms(known_secret, found_door_codes, rule)` — the partial-solve filter (§6 of arch doc).
- [ ] `resolve_accusation(room)` → win / lose.
- [ ] Drive it all from debug buttons or `_ready()`: reveal a door code, reveal a secret symbol, accuse.
- **Done when:** you can play the entire deduction in the console and it correctly says win/lose,
      including the "solvable early" cases. **This is the game. Everything after is making it nice.**

### ☐ M2 — Decoder UI + accusation — *1–2 days*
- [ ] A `Control` Decoder screen: shows found door codes, the partial secret code, the current match rule.
- [ ] The Decide flow (pick a room → confirm → calls `resolve_accusation`).
- [ ] Temporary "found a door code" / "found a secret symbol" buttons wired to the model.
- **Done when:** you play OutNumbered's mind-game with mouse/keyboard. Still no walking.

### ☐ M3 — One real puzzle, then the framework — *2–3 days*
- [ ] Build `PuzzleScreen` (base `Control`) + the `PuzzleDefinition` Resource + `PuzzleGenerator`.
- [ ] Implement **one** template fully (suggest the labeled-objects / price-tags puzzle — simplest).
- [ ] On correct answer → emit `door_code_found` → it lands in the Decoder.
- [ ] Add the **calculator** Control (press `=` between operations, like the original).
- [ ] Stub the other templates (return a fixed correct answer for now).
- **Done when:** solving a puzzle feeds a real door code into the Decoder.

### ☐ M4 — The world — *3–5 days*
Keep it dumb: flat floor, no platforming.
- [ ] `CharacterBody2D` player: left/right + a hop, driven by the Input Map.
- [ ] `Area2D` interactables: room doors, elevators, recharge machines (each its own scene).
- [ ] Two floors; elevator swaps them; entering a room opens an M3 puzzle; recharger refills energy.
- **Done when:** you walk the station, enter rooms, and rooms feed the Decoder.

### ☐ M5 — Encounters — *2–4 days*
- [ ] Telly: spawner + roaming + attacks + "zap while red" → triggers a **timed** secret-code drill.
- [ ] The drill yields one secret-code symbol into the model; **clock keeps running** (wire §6c pause rule).
- [ ] LiveWire floor hazard (jump or zap).
- **Done when:** both information sources — door codes *and* the secret code — are earned through play.

### ☐ M6 — Round lifecycle & meta — *2–3 days*
- [ ] The clock: 9:00 PM → midnight, 1 game-min per 3 real sec, lose on midnight.
- [ ] End-round bonuses (Energy / Time / Win) + lifetime score.
- [ ] The 8 ranks + rank→difficulty mapping + level-up screen (match rule flips to unordered at Expert).
- [ ] `PlayerProfile` save/load (`ConfigFile` under `user://` is the low-friction choice).
- [ ] App Flow state machine: menus → sign-in → game-type select → round → result → repeat.
- **Done when:** a complete, replayable game with progression that persists between launches.

### ☐ M7 — Customization & content fill — *open-ended*
- [ ] Implement the remaining puzzle templates for real (data + UI, no new architecture).
- [ ] Customized Game / Drill-for-Skill modes (just different Config inputs — cheap if §5 held).
- **Done when:** feature-complete vs the original's scope.

### ☐ M8 — Juice & audio — *open-ended, strictly last*
- [ ] Sprite animation, transitions, particles, screen feel.
- [ ] The classical tracks (title / hall / room) + SFX via `AudioManager`.
- **Done when:** it feels like 1990 in the best way.

---

## If you only have a weekend before you lose steam

The minimum that proves the concept to yourself and is genuinely *playable*:

- [ ] **M0 + M1 + M2.** That's the whole deduction game, playable with buttons, no art, no walking.

If that's fun to click through, the rest is worth building. If it isn't, you've learned that in a weekend
instead of after three weeks of sprite work — which is exactly the outcome the build order is designed to
give you.
