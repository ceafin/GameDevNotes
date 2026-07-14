# Cloning the Super Solvers Series in Godot 4.6
**Context:** 2D edutainment clone of *Midnight Rescue!* (reading) and *OutNumbered!* (math), Godot 4.6+ / GDScript.
**Rules:** when responding be terse and concise but not mean, prefer tables and bulleted lists, style in breadcrumbs not lectures.

---
## Features of Focus
- The two games deduce **different subjects**. *Midnight Rescue!* = "which of 5 **robots** is Morty?", evidence = **photographed robot features**. *OutNumbered!* = "which **room** is Morty in?", evidence = **room patterns revealed by solving that room's math**. Same *abstract* deduction engine, **different candidate domain and a different investigation modality**. Swapping only the question type does **not** get you OutNumbered!. (§3, §6)
- Two orthogonal things differ: (a) the **clue source** and (b) the **candidate investigator**. They are separate roles; one log collapsed them into a single provider. (§6)
- Both originals use exactly **4 clues / patterns** per round. Set `clues_required = 4`.
- Robot feature assignments are **randomized per round** ("for that particular session"). Keep robot **identity** (name/sprite) static; assign the **profile per round**. Doc 2's split is the correct one. (§4)
- `get()` returns `null` for an *un-photographed* slot, so this **eliminates candidates you simply haven't investigated yet**. Eliminate only on a **contradiction** (`profile.has(slot) and profile[slot] != clue`). (§5)
- Confirmed: rounds run 9:00 PM → midnight, 9 real minutes = 540 s (1 game-minute per 3 real-seconds). Keep it.
- Sources say only "a plethora of articles." Treat the exact count as unknown; don't hard-code a number into your content plan.
- Confirmed: the originals mixed invented diary entries with **excerpts from real literary works**. Many classics are public-domain, but you still owe grade-leveling work write/curate your own.
- Everything else from both logs (Type Object = Resource, Flyweight, Signals, Autoload, node-FSM-only-where-warranted, no-ECS, TileMapLayer, `.tres` dev / `.res` release, Resource-caching gotcha, solver-first build order) is correct and carried forward below.

---
## 1. Engine & tooling reality check (verified)

- **Godot 4.6 is real and current.** 4.6 stable ~late Jan 2026; current patch **4.6.3** (May 2026); 4.7 in development. Your toolchain (v4.6+) is fine.
- **Typed dictionaries** (`Dictionary[K, V]`) landed in **4.4** — available to you.
- **Nested typed collections are still NOT supported** in 4.6 (`Array[Array[X]]`, `Dictionary[K, Array[V]]`). Official docs confirm. Keep collections **one level deep**, or wrap the inner collection in a Resource/class.
  - ⚠️ Live 4.6.1 bug (#116947): iterating a typed `Dictionary` whose **values are typed Arrays** can hard-crash with no error. Another reason to wrap nested data in a Resource instead of `Dictionary[K, Array]`.
- **`TileMap` is deprecated** (since 4.3). Use **`TileMapLayer`** — one node per layer, all sharing one `TileSet`. (Note the unchanged ±32768 per-layer coordinate clamp; chunk huge worlds.)

---
## 2. Critical framing (before any code)

- **Model the deduction first; movement is secondary.** The real game is constraint-elimination (Guess-Who / Mastermind), not platforming. The in-game **notepad** cross-references clues vs investigated candidate facts to eliminate non-matches. Get this data right and the rest is plumbing.
- **One *deduction engine*, two *candidate domains*.** Architect a generic solver over "candidates, each with a profile across N slots; a hidden target; clues that reveal target slots; investigation that reveals candidate slots; win when the match is unique." Robots-vs-rooms then becomes **data + two small strategies**, not two codebases. (This is the corrected version of the old "one engine" claim — see §0.1, §6.)
- **Reading vs math content are modeled differently.** Reading passages are finite, hand-authored → **Resources** (`.tres`). Math problems are effectively infinite → **procedural generators**, never hundreds of `.tres`. Same `Question` base, two subclasses.
- **Resources = authored data, NOT mutable runtime state.** Godot **caches Resources and shares them by reference**; mutating a loaded `.tres` at runtime mutates the canonical copy for everything (and can get written back to source in-editor). So: *static catalog* = Resources; *live round/save state* = `resource.duplicate(true)` or plain `RefCounted` / `Dictionary`.
- **Don't reach for an ECS addon.** Godot's node tree *is* composition. Bolting on a GDScript ECS fights the engine. Likewise resist FSM-everything: a chest needs a `bool`, not a state machine. Reserve FSMs for the player and henchman AI.
- **Don't clone the IP.** Mechanics aren't copyrightable; "Morty Maxwell," "Shady Glen," "Master of Mischief," the named robots (Buffo/Lectro/Pogo/Rollo/Turbo, Telly), the sprites, and the passages are. Use original or genuinely public-domain text and original art.

---
## 3. Verified facts about the two games (so your data model is faithful)

| Fact | *Midnight Rescue!* (1989, reading) | *OutNumbered!* (1990, math) |
|---|---|---|
| Setting | Shady Glen **School** | Shady Glen **TV station** |
| **Deduce** | which of **5 robots** Morty hides in | which **room** Morty hides in |
| Candidate profile = | robot **features** (held items, worn items e.g. necklace, speech bubble) | room **pattern** (a set of pattern facts) |
| How you learn a **candidate** fact | **photograph** a roaming robot (each photo reveals one more part) | **solve that room's math puzzle** |
| How you earn a **clue** (target fact) | answer a **reading MCQ** at a triangular envelope | **zap Telly** (the henchman) → answer a **math challenge** |
| Clues per round | **4** | **4** patterns |
| Clock | 9:00 PM → midnight, **540 s** real (1 game-min / 3 s) | same |
| Henchmen | Buffo, Lectro, Pogo, Rollo, Turbo; crash = −45 s or −1 film; some carry clues | Telly / LiveWire; same hazard role |
| Tool | camera (photograph **and** zap-defend) | remote/zapper |
| Win | accuse the right robot before midnight; **one guess** | accuse the right room; one guess |
| Partial-info win | possible **with all photos + some clues, OR all clues + one fully-photographed match** (see §5) | analogous |
The headline correction lives in rows 2–5: the **candidate** (robot vs room) and the **investigation modality** (photograph vs solve-the-room) differ. The clue-source also differs (reading MCQ vs Telly-math). That's **two** pluggable seams, not one.

---
## 4. Data model — concern → Godot construct

| Concern | Construct | Why |
|---|---|---|
| Robot/room **identity** (name, art) — static catalog | **Custom `Resource` + `class_name` + `@export`** (Type Object) | type-safe, inspector-editable, `.tres` is VCS-friendly |
| **Attribute values** ("owl", "rubber nose", a room pattern token) | **one `.tres` per value** (Flyweight) | shared by reference; cheap to compare by identity |
| Profile **slots** (which axes exist) | `StringName` keys or an `enum` | int/StringName compare, no typos |
| A candidate's **per-round profile** | `Dictionary[StringName, AttributeValue]` (one level deep) | randomized each round → never bake into identity (§0.5) |
| Reading passage + its MCQs | `Resource` holding `Array[Question]` | sub-resources nest cleanly |
| Math question | **generator**, runtime-built | infinite content; never author these |
| Round definition (culprit, rank, profiles) | `Resource` (authored) **or** built by a `RoundFactory` (generated) | designer-tuned vs infinite — your call (§10) |
| **Live round state / save** | `duplicate(true)`'d Resource **or** `RefCounted` / autoload `Dictionary` | avoid shared-reference mutation |
| Rank / difficulty scaling | separate `Resource` | keep "photos required", robot speed, clue-density knobs out of robots/questions |
| "All robots in this room" | **Groups** | tag + iterate without hard refs |
| Spawn points | **`Marker2D`** (in a group) | data-light placement |
| Envelope / room trigger | **`Area2D`** holding a `Passage`/puzzle ref | built-in overlap detection |
| Robots, projectiles, envelopes | **`PackedScene`** instancing (Prototype) | one `.tscn`, many instances |
| Sprites / animation | `@export var frames: SpriteFrames` on the identity Resource | Flyweight art across spawns |

> ⚠️ Nested typed collections unsupported (§1). `Array[Dictionary]` and `Dictionary[StringName, AttributeValue]` are each one level — fine. `Dictionary[StringName, Array[X]]` is **not** — wrap it.

### Authored Resources (catalog)

```gdscript
# attribute_value.gd — Flyweight: one .tres per concrete value
class_name AttributeValue extends Resource
@export var id: StringName          # &"owl", &"necklace", &"pattern_red"
@export var slot: StringName        # &"wearing", &"holding", &"saying", &"pattern_a"...
@export var label: String
@export var icon: Texture2D

# candidate_def.gd — static identity ONLY (robot OR room); no per-round features here
class_name CandidateDef extends Resource
@export var id: StringName
@export var display_name: String
@export var frames: SpriteFrames    # robot art; for rooms, a thumbnail/marker

# question.gd — polymorphic base (Strategy); same in both games
class_name Question extends Resource
@export var prompt: String
func is_correct(_answer: Variant) -> bool: return false   # override

# reading_question.gd
class_name ReadingQuestion extends Question
@export var choices: PackedStringArray
@export var correct_index: int
func is_correct(a: Variant) -> bool: return int(a) == correct_index

# math_question.gd — usually generated, not authored
class_name MathQuestion extends Question
@export var answer: int             # OutNumbered! is integer arithmetic
func is_correct(a: Variant) -> bool: return int(a) == answer

# passage.gd — reading content + glossary + its questions
class_name Passage extends Resource
@export_multiline var body: String
@export var hard_words: Dictionary  # { "word": "definition" }  (one level)
@export var questions: Array[Question]

# round_config.gd — authored OR produced by RoundFactory
class_name RoundConfig extends Resource
@export var time_limit_sec: int = 540        # 9 min — verified
@export var film: int = 10                    # camera shots (tune; not source-confirmed)
@export var clues_required: int = 4           # CORRECTED from 3
@export var candidates: Array[CandidateDef]
@export var profiles: Array[Dictionary]       # parallel to candidates: { slot: AttributeValue }
@export var target_index: int                 # which candidate is Morty
```

> Parallel arrays (`candidates[]` / `profiles[]`) are fragile but keep the nesting one level deep. If you prefer safety over flatness, wrap each `{candidate, profile}` pair in a tiny `Resource` and store `Array[RoundEntry]`.

---
## 5. The deduction core — the actual game (corrected solver)

```gdscript
# deduction.gd — generic constraint elimination over candidates (robots OR rooms)
# target_facts : slot -> AttributeValue   the culprit is KNOWN to have (from clues)
# investigated : candidate_id -> { slot -> AttributeValue }  (photos / room puzzles)

# A candidate is ruled out ONLY by a contradiction with a fact we actually know.
func is_possible(profile: Dictionary, target_facts: Dictionary) -> bool:
    for slot in target_facts:
        if profile.has(slot) and profile[slot] != target_facts[slot]:
            return false                      # known feature contradicts a clue
    return true                               # consistent (or simply not yet investigated)

func possible(investigated: Dictionary, target_facts: Dictionary) -> Array:
    var out: Array = []
    for id in investigated:
        if is_possible(investigated[id], target_facts):
            out.append(id)
    return out
```

**Why `profile.has(slot)` matters (the fix to Doc 2's bug):** a candidate you have only *partly* investigated must stay POSSIBLE for the slots you haven't seen. The old `p.get(slot) != clue` test treated "unknown" as "mismatch" and wrongly eliminated under-photographed candidates.

**Certainty** — faithful to how the original lets you win on partial info:

```gdscript
# Solvable when exactly one candidate remains possible,
# OR all clue slots are known AND one candidate matches every clue.
# The latter relies on RoundFactory guaranteeing exactly ONE full match (§10).
func solved_id(investigated: Dictionary, target_facts: Dictionary,
               all_clue_slots_known: bool) -> Variant:
    var poss := possible(investigated, target_facts)
    if poss.size() == 1:
        return poss[0]                        # "all photos + few clues" → unique survivor
    if all_clue_slots_known:
        for id in investigated:
            var prof: Dictionary = investigated[id]
            var full := true
            for slot in target_facts:
                if prof.get(slot) != target_facts[slot]:
                    full = false; break
            if full:
                return id                     # "all clues + one full match" → it's Morty
    return null                               # not yet determinable
```

This reproduces both win paths the original documents: *all photographs + one clue that only one robot satisfies*, and *all clues + a single fully-photographed robot that matches them all*. **Invariant the round generator must uphold:** exactly one candidate fully matches all clue facts (otherwise the second branch is unsound).

Clue card model (carried from Doc 2, kept): `{ slot, value, kind }` where `kind ∈ {REAL, DUMMY, DUPLICATE}` — dummies/taunts (henchman lines) add no fact.

---
## 6. The two pluggable seams (what actually makes it BOTH games)

The old logs had **one** seam (the question type). There are **two** orthogonal ones:

| Role | What it yields | *Midnight Rescue!* | *OutNumbered!* |
|---|---|---|---|
| **ClueSource** | one **target** fact (about Morty) | answer a **reading MCQ** at an envelope | **zap Telly** → answer a **math** challenge |
| **Investigator** | one **candidate** fact (a slot of one candidate's profile) | **photograph** a roaming robot | **solve a room's math** puzzle → that room's pattern slot |

Note the asymmetry the single-provider model hides: in *OutNumbered!* **math fills both roles** (Telly-math earns clues; room-math investigates rooms), whereas in *Midnight Rescue!* the roles split across **two modalities** (reading earns clues; camera investigates robots).

```gdscript
# clue_source.gd — returns a target fact on success, else null
class_name ClueSource extends RefCounted
func try_clue(answer: Variant) -> AttributeValue: return null      # override

# investigator.gd — returns the candidate facts newly revealed
class_name Investigator extends RefCounted
func investigate(candidate_id: StringName) -> Dictionary: return {} # { slot: value }
```

- `ReadingClueSource` (MCQ) / `MathClueSource` (Telly) implement `try_clue`.
- `CameraInvestigator` (photo reveals one slot per shot) / `RoomMathInvestigator` (correct answer reveals the room's slot) implement `investigate`.
- Swap the **pair**, not just one — that's the ~80–90% reuse, honestly accounted for.

---
## 7. Game Programming Patterns → Godot-native form

GDQuest's own point: Godot gives you Singleton, Observer, Flyweight, Prototype, Component **for free** — don't hand-roll them.

| Nystrom pattern                 | Godot-native form                                                                                      | Use here for                                   |
| ------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------- |
| **Type Object**                 | custom `Resource`                                                                                      | candidates, questions, ranks, attribute values |
| **Flyweight**                   | shared `Resource` / `SpriteFrames`                                                                     | attribute `.tres`, robot art across spawns     |
| **Observer**                    | Signals / a `SignalBus` autoload; Resources also emit `changed` via `emit_changed()` (auto-refresh UI) | clue-gained, photo-taken, time-out             |
| **Singleton / Service Locator** | Autoload                                                                                               | `GameState`, `CaseManager`, `SignalBus`        |
| **State**                       | node-based FSM (`enter/exit/update`) — only at ~4+ states; below that, `enum` + `match`                | player, henchman AI **only**                   |
| **Strategy**                    | polymorphic `Resource` (`Question`) + the two seams in §6                                              | reading↔math, the only differing parts         |
| **Prototype**                   | `PackedScene` instancing                                                                               | robots, projectiles, envelopes                 |
| **Component**                   | node composition                                                                                       | camera, hurtbox, mover (avoid ECS addons)      |
| **Update Method**               | `_process` / `_physics_process`                                                                        | movement, the clock                            |

---
## 8. Scene-tree & autoload skeleton

```
Autoloads (live under /root, ABOVE the main scene — they ARE in the tree):
  SignalBus.gd · GameState.gd · CaseManager.gd

Main (Node)
├─ GameClock (Node)        → pauses while Notebook / Reading open
├─ World (Node2D)
│   └─ Room*.tscn          → TileMapLayer (floor) + TileMapLayer (walls)
│                            Spawn (Marker2D, group "spawns")
│                            Envelope (Area2D) → holds a Passage / room puzzle
├─ Player (CharacterBody2D)
│   ├─ StateMachine        → Idle / Run / Aim
│   └─ Camera-tool         (photograph ↔ zap)
├─ Robot.tscn (CharacterBody2D, group "robots")
│   └─ StateMachine        → Patrol / Attack / Flee(after photo)
└─ UI (CanvasLayer)
    ├─ HUD                 (clock, film, score)
    ├─ ReadingView         (passage + Hard-Words popup + MCQ)   ← Midnight Rescue
    ├─ MathView            (Telly challenge / room puzzle)       ← OutNumbered!
    ├─ Notebook            (clues ✓ / candidate grid) ← reads GameState signals
    └─ AccusationView      (pick candidate → GameState.solved_id())
```

> Correction to Doc 2's diagram: autoloads are **not** children of `Main`; the engine adds them under the SceneTree **root**, before your main scene loads. They're in the tree, just not under `Main`.

```gdscript
# game_state.gd — Autoload (runtime state; NOT a shared .tres)
extends Node
signal clue_added(value: AttributeValue)
signal candidate_investigated(id: StringName, slot: StringName, value: AttributeValue)
signal time_changed(sec: int)

var target_facts: Dictionary = {}    # slot -> AttributeValue   (clues)
var investigated: Dictionary = {}    # candidate_id -> { slot: AttributeValue }
var score: int = 0
```

---
## 9. Build order (de-risk the deduction core first)

1. **Resources + the solver in isolation** — unit-test `is_possible` / `solved_id` with fake data and both partial-info win cases. No engine UI yet.
2. **Notebook UI** bound to `GameState` signals — no movement yet.
3. **ClueSource path:** `ReadingView` → correct answer → `add_clue()` (one target fact).
4. **Investigator path:** player + camera + one robot → photo writes one candidate slot.
5. **World:** `TileMapLayer` rooms, `GameClock`, henchman attacks (−45 s / −film), scoring, accusation.
6. **Fork to OutNumbered!:** swap the §6 **pair** — `MathClueSource` (Telly) + `RoomMathInvestigator` (room puzzles), candidate domain = rooms. Reuses the solver, notepad, clock, scoring untouched.

---
## 10. Open decisions to make yourself (don't let me pick blindly)

- **Authored vs generated rounds.** Authored `.tres` per round = hand-tuned, finite. A **`RoundFactory`** = infinite content but must **guarantee a unique solution** (exactly one candidate matches all 4 clue facts) — that's the hard part, and §5's second win-branch depends on it. Generation is more work; decide based on how much content you'll hand-author.
- **Save format.** A dedicated `SaveData` Resource you `ResourceSaver.save()` is more Godot-thonic but **couples saves to class layout** — version it, or you'll break old saves on refactor. JSON is uglier but layout-tolerant. (Also a faithful "lifetime score across playthroughs" lives here.)
- **`.tres` vs `.res`.** `.tres` (text) while developing — diff-able, VCS-friendly. `.res` (binary) for release — smaller/faster but **not hand-editable**.
- **Profile axis taxonomy.** Sources confirm *examples* (held items, worn items like a necklace, speech bubbles) but not a definitive closed list, and rounds surface **4** clue facts. Pick your own slot vocabulary; the solver doesn't care how many slots exist.

---
## 11. Reference breadcrumbs (verified live, 2026-06-17)

| Topic | Link |
|---|---|
| Custom Resources | `https://docs.godotengine.org/en/stable/tutorials/scripting/resources.html` |
| Typed dictionaries (4.4+) + nested-collection limitation | `https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_basics.html` |
| Saving games / `ResourceSaver` | `https://docs.godotengine.org/en/stable/tutorials/io/saving_games.html` |
| Singletons (Autoload) | `https://docs.godotengine.org/en/stable/tutorials/scripting/singletons_autoload.html` |
| Groups | `https://docs.godotengine.org/en/stable/tutorials/scripting/groups.html` |
| TileMapLayer (class ref) | `https://docs.godotengine.org/en/stable/classes/class_tilemaplayer.html` |
| Best practices / project organization | `https://docs.godotengine.org/en/stable/tutorials/best_practices/` |
| GDQuest — Finite State Machine | `https://www.gdquest.com/tutorial/godot/design-patterns/finite-state-machine/` |
| GDQuest — Strategy | `https://www.gdquest.com/tutorial/godot/design-patterns/strategy/` |
| GDQuest — design-patterns index + demo repo | `https://www.gdquest.com/tutorial/godot/design-patterns/` · `https://github.com/gdquest-demos/godot-design-patterns` |
| Game Programming Patterns (Nystrom, free) | `https://gameprogrammingpatterns.com` |
### Sources for the game-design facts (§3)
- *Midnight Rescue!* — Wikipedia; Internet Archive item page; GameFAQs walkthrough (4-clue rule, 9-min/540 s clock, partial-info win cases); Grokipedia (notepad cross-referencing, triangular envelopes, photographed held-items/speech).
- *OutNumbered!* — Wikipedia (deduce-the-**room**, room patterns via math, zap-Telly clues, 4 patterns); MobyGames; Kotaku (room-by-room math, LiveWire).

---
