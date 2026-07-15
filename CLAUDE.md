# Godot / GDScript Working Contract

Reusable across all Godot projects. This is a **behavioral contract**, not documentation — it governs how you work, not what the game is. The `.gd` files on disk are the source of truth for code; read them before acting on assumptions. Project-specific facts (dungeon layouts, item names, that project's exceptions to any rule below) live in `.claude/rules/` for that project. Running session state lives in that project's `MEMORY.md`.

One principle underlies almost every rule below: **local things stay local; only the genuinely global gets lifted out, minimally, when the pain is real.** When a rule below seems to conflict with a specific situation, resolve it toward that principle.

---

## 1. Working agreement

- **One small building block at a time.** Finish and verify a block before proposing the next. No long multi-step narratives dumped in one go.
- **Be constructively critical.** Never agree just to be amenable. Not every idea is a good one — say so, with reasons.
- **Design forks are the user's to decide.** When a real fork exists (two valid architectures, two valid node choices), present the options with tradeoffs and let the user choose. Do not silently pick one and build it.
- **No empty scaffolding.** Build a node, scene, autoload, or script only when the block that needs it actually arrives. Knowing something is coming later is not a reason to stub it now.

---

## 2. Mindset (read this before designing anything)

**Godot IS the pre-built ecosystem.** Node tree = entity list. `_process`/`_physics_process` = tick loop. Signals = event system. Resources = data files. You add *content*, not scaffolding. Rebuilding a built-in is the blank-page problem in disguise — both are "I built the foundation that already existed." Use the built-in for the first pass, always. Hand-roll *only* at a concrete wall the built-in can't clear — never preemptively "for control." Don't decompose top-down; grow outward from one verb.

### The two traps

You (the project owner) oscillate between two opposite mistakes. The middle path for both is **the tree**.

- **Trap A — over-building structure up front.** Designing the "perfect reusable foundation" on a blank page. There's no evidence yet for what's actually needed. The foundation *crystallizes from repetition*: write the dumb specific version 3x, then extract the pattern.
- **Trap B — collapsing all structure into one global thing.** God-object autoload, globalizing every variable, bus-for-everything. Looks tidy, is a tangle.
- **The rule for both:** build or lift structure *when you hit a concrete wall*, never preemptively. If a design choice is being justified as "for flexibility later," stop — that's Trap A talking.

### Decomposition method

1. **Core loop = one sentence of verbs.** (Mega Man: "run, jump, shoot, take damage.")
2. **Get the first verb on screen.** A rectangle that moves beats a perfect plan.
3. **Each step must RUN before the next.** Never proceed on something that doesn't execute.
4. **Next step = the most boring missing piece** between now and the sentence being true. Look only at the next gap, never the whole tree.
5. **Loose coupling = small interfaces.** "Systems working together" is really: this thing has an `hp`, that thing deals damage, an overlap fires one event. That is the real engineering.

---

## 3. Engine & version target

Target **Godot 4.6.x stable, GDScript 2.0** unless a project's own `.claude/rules/` says otherwise. Write only code valid for that version. When unsure whether an API, signature, or node exists in the target version, **say so and point to the docs — never invent one.**

Version-specific defaults (current as of 4.6, re-check this block on any engine upgrade):
- **Jolt** is the default 3D physics engine for new projects.
- Inverse kinematics is the `IKModifier3D` family (`TwoBoneIK3D`, `FABRIK3D`, `CCDIK`).
- `move_and_slide()` takes **no arguments** — set the `velocity` property first, then call it.

### Never emit Godot 3.x patterns

| 3.x (never write this) | 4.x (write this) |
|---|---|
| `export var` | `@export var` |
| `onready var` | `@onready var` |
| `yield(o, "s")` | `await o.s` |
| `connect("p", self, "_on")` | `node.p.connect(_on)` |
| `emit_signal("d")` | `d.emit()` |
| `KinematicBody2D`/`3D` | `CharacterBody2D`/`3D`; set `velocity`, then `move_and_slide()` with no args |
| `instance()` | `instantiate()` |
| `Spatial` | `Node3D` |
| `Reference` | `RefCounted` |
| `PoolXArray` | `PackedXArray` |
| `.empty()` | `.is_empty()` |
| `OS.get_ticks_msec()` | `Time.get_ticks_msec()` |
| `rad2deg` / `deg2rad` | `rad_to_deg` / `deg_to_rad` |
| `stepify` | `snapped` |
| `setget` | `get:` / `set:` blocks |
| `OS.window_*` | `DisplayServer.*` / `get_window()` |
| A `Tween` node | `create_tween()` — a `Tween` is never a node in 4.x |

Do not replicate an original game's technical workarounds just because the original did them that way (if porting/referencing another game's design) — do it the idiomatic Godot way.

---

## 4. Engine-first: search the noun before writing the system

Before coding any mechanic, search for the **noun** of what's wanted — do not hand-roll something Godot already ships.

| Want | Use |
|---|---|
| Move with collision | `CharacterBody2D` + `move_and_slide()` (no args in 4.x; set `velocity` first) |
| On ground? | `is_on_floor()` |
| Overlap / hit detection | `Area2D` + signals — not distance polling |
| One-shot move or ease (A → B, fixed duration) | `Tween` via `create_tween()` |
| Follow a MOVING target (camera, homing) | `Camera2D.position_smoothing_enabled`, or delta-based `lerp` / `move_toward` in `_process`. **NOT** a Tween. |
| Timing / delays | `Timer` node, or `await get_tree().create_timer(t).timeout` — never manual delta accumulation |
| Frame animation | `AnimatedSprite2D` / `AnimationPlayer` |
| State-driven / blended animation | `AnimationTree` |
| Pathfinding | `NavigationAgent2D` / `NavigationAgent3D` |
| Interpolation / juice | `create_tween()`, not per-frame lerp loops |
| Communication, one caster → many listeners | Signals up + `add_to_group()` / `get_tree().call_group()` for the many-listeners case — not a hand-built event bus |
| Data / config | Custom `Resource` subclasses with `@export`, not loose dicts/JSON |
| Save / load | `ResourceSaver` / `ResourceLoader`, `ConfigFile`, `FileAccess` |
| Global state | An autoload singleton (see §6) |

**Tween vs lerp, the distinction that trips people up:**
- `Tween` = "go from where I am to X over N seconds," a *closed* animation. Restarting it every frame to chase a moving target is the wrong tool.
- Following something that keeps moving = per-frame smoothing. Use `Camera2D`'s built-in smoothing for cameras, or `pos = pos.lerp(target, weight)` / `move_toward` in `_process` for everything else. Hand-lerping here is correct, not a sin.
- **Heuristic:** about to write math for a fixed A → B ease? Tween. Chasing a live target every frame? Smoothing, not Tween.

---

## 5. GDScript style

- **Strong typing, always.** Write out the type for every variable, parameter, and return, every time, unless something legitimately prevents it. Typed collections too (`Array[Enemy]`, `Dictionary[String, int]`).
- **`:=` is fine.** It is typed inference — the equivalent of C++ `auto`. Don't ban it; it's not a typing violation.
- **Annotate everything:** `func move(delta: float) -> void:`. A typed `Array[int]` behaves like `std::vector<int>`: type mismatches are caught at parse time where the compiler can see them.
- **No `$` node references scattered through logic.** Resolve a node once into an `@export` slot or an `@onready` var (`@onready var sprite: Sprite2D = $Sprite2D`), then reference that var thereafter.
- `class_name` only on infrastructure / reusable types, not on every leaf script — it pollutes the global namespace.
- Annotations to use: `@export`, `@export_range`, `@export_group`, `@onready`, `@tool`.
- `await` for anything time- or signal-based, not manual state flags.
- Built-in math (`move_toward`, `lerp`, `clamp`, `snapped`, vector ops) — don't reimplement it.
- `const` / `enum` over magic numbers and strings.
- **Naming:** `snake_case` funcs/vars, `PascalCase` classes & nodes, `CONSTANT_CASE` consts, leading `_` for private, past-tense signal names (`health_depleted`).
- Physics-affecting logic in `_physics_process`, frame logic in `_process`, input in `_input` / `_unhandled_input`.
- Use the in-editor debugger + remote scene tree for live runtime values. Stop debugging with `print()` like it's 1999.

### Project static-typing config (baseline for new projects)

| Setting | Value | Why |
|---|---|---|
| `untyped_declaration` | `2` (Error) | The keystone. Makes GDScript behave like C, not Python. Supercharges autocomplete. |
| `unsafe_*` (e.g. `unsafe_method_access`, `unsafe_property_access`, `unsafe_cast`) | `1` (Warn), not Error | Some unsafe ops (Dictionary access, `get_node`) are unavoidable. See them, don't let them block the build. |

Warning levels: `0 = Ignore`, `1 = Warn`, `2 = Error`. After editing warning settings: **restart the editor or re-save a script**, or the change won't apply.

---

## 6. Data & state architecture

- **`change_scene_to_file()` frees only the current scene branch** (the old scene and all its children). The **root and autoloads survive.** Anything stored "in the level" or "on the player" node dies; autoload data does not.
- **The bucket line, ask per variable:** *Would this need to be true AFTER a scene change frees the current scene?*
  - **No → scene-local.** Enemy positions, projectiles, current HP (if refilled each stage), this level's pickups. Most variables. Leave them local.
  - **Yes → session-global.** Lives, score, unlocked weapons, equipped weapon, levels beaten.
- **Subtlety is the actual skill:** e.g. Mega Man *health* is scene-local, *lives* are session-global. Same kind of number, opposite bucket. Draw the line per variable.
- **Session-global lives in an Autoload singleton** (`Project Settings → Globals → Autoload`). It sits under `/root`, above the current scene, never freed, reachable by its registered name. This is the persistent character struct.
- **"Persists" is not "persists across scenes."** A bullet persists for 2 seconds and is NOT global. Only scene-boundary-crossing data earns an autoload.

### Structure: two different tools — don't file them in the same drawer

- **Autoloads = DATA / services.** Global variables, audio. About 2–5 total (`GameState`, `AudioManager`, optional `SceneManager`, `Settings`). More than ~5 is a smell.
- **Persistent root scene = STRUCTURE.** A permanent `Main` node with a swappable child slot:
  ```
  Main (Node)              # never freed
  ├── CurrentLevel (Node)  # free children + instantiate new level here
  ├── HUD (CanvasLayer)    # persists across level swaps
  └── PauseMenu (CanvasLayer)
  ```
  Swap `CurrentLevel`'s children instead of calling `change_scene_to_file()`. HUD and menus stop flickering and rebuilding.
- **They collaborate:** `Main.load_level()` does the structural swap; it reads `GameState` to know *which* level.
- **Don't adopt the persistent root until it hurts** (HUD rebuilds, music restarts on every transition). A tiny prototype is fine with plain `change_scene_to_file()` + one `GameState`.

### Pause / menus

- `get_tree().paused = true` freezes the whole tree.
- Set the menu node's process mode so it stays alive while everything else freezes:
  - Inspector: **Process > Mode = When Paused**.
  - Code: `process_mode = Node.PROCESS_MODE_WHEN_PAUSED`.
- That is the built-in "everything stops except this UI."

---

## 7. Signals & communication

Built on one fact: **a parent knows its children; a child does not know its parent.**

- **Call down** = parent calls methods on children it holds references to. `enemy.take_damage(10)`, `hud.set_health(80)`. Not a compromise, it is correct. Stop feeling guilty about it.
- **Signal up** = child emits an event without knowing who listens. `died.emit()`. Keeps the child reusable in any scene.
- **Children never call up.** Welds them to a parent, kills reuse.
- **Siblings do not reference each other directly. The parent mediates.** Child A signals up, the parent hears it and calls down into child B. Only reach for shared global state when the thing really is shared *data* (see Tier 2 below), not just to avoid wiring the parent.
- Result: flow goes **up via signals → parent decides → down via calls.** A tree, not a web.
- For one-caster-to-many-listeners broadcast (not parent/child), prefer `add_to_group()` / `get_tree().call_group()` over a hand-built event bus.

### Where to connect

| Situation | Connect via |
|---|---|
| Both nodes live in the *same saved scene* and exist from the start (a menu's own button, a level's pre-placed door) | **Inspector** |
| One side is spawned at runtime | **Code**, at the spawn site, same line as `add_child` |

```gdscript
enemy.died.connect(_on_enemy_died)
```
On `queue_free()`, Godot **auto-disconnects** when the node is actually freed. Connection lifetimes are not manually managed; they are born and die with the node.

**Connect to the permanent thing, not the transient ones.** The HUD connects to `GameState` once in `_ready()` and ignores the churn of spawning and dying objects entirely.

### Signal architecture: the three tiers

For any two things that need to talk, ask in order:

1. **Does one own the other (parent/child)?** → **Tier 1: direct** signal-up / call-down. *Not the bus.* Putting parent/child traffic on a global bus is the number-one mistake.
2. **Is it really about a piece of shared state changing?** → **Tier 2: autoload data + a `_changed` signal.** Score, lives, equipped weapon. The signal is attached to the data it describes.
3. **Neither, a genuinely game-wide moment with no owner?** → **Tier 3: SignalBus, sparingly.** `player_died`, `game_paused`, `boss_defeated`. About 8 signals in a finished game, not 80.

SignalBus-for-everything is not wrong *because the game got big* — it's fine for a tiny prototype *because* the prototype is small enough to hide that the bus eats the tree's directionality. Most interactions are Tier 1 or 2; the gate above keeps the bus tiny automatically.

**Tier 2 pattern (data emits on change):**

```gdscript
# GameState.gd (autoload)
extends Node

signal score_changed(new_score: int)

var score: int = 0:
	set(value):
		if value == score:   # skip redundant emits
			return
		score = value
		score_changed.emit(value)
```

HUD subscribes to `score_changed` once. Enemy and HUD never reference each other.

> **Setter caveat:** setters also run during scene load / init, before other nodes connect. If a listener must not miss the first value, have it read `GameState.score` in its own `_ready()` and *then* connect, rather than relying on the emit.

---

## 8. Composition & restraint

- Composition over inheritance: behavior comes from child nodes/components, not deep class trees.
- No manager classes, abstraction layers, or event buses until a **real second caller** exists. Signals + groups cover most of it. (This is Trap A from §2 applied to code structure specifically.)
- Child nodes reach their owning body via `owner` or an exported reference — never `get_parent()` chains or tree-crawling.

---

## 9. Comments & documentation

- Wrap larger comment blocks in Unicode box-drawing frames (`─ │ ┌ ┐ └ ┘`).
- Document every script, function, member, and signal with Godot `##` documentation comments so the editor's built-in Help panel generates from them. Use the doc tags (`[br]`, `[code]`, `@tutorial`) where they help.

---

## 10. Output contract

For any script, state which node it attaches to and the children/exports it assumes — a `.gd` file is meaningless without its scene context. If a native node does the job better than a script, say so first, before writing the script. Flag any API you are not certain exists in the target version rather than guessing.

---

## 11. Session continuity

At the start of a session, read `MEMORY.md` at the repo root if present — it is the running state; read it before acting. At the end of a completed building block, append a short dated entry: what changed, any decisions locked, and the current verified state. Keep it concise — durable rules belong in `.claude/rules/`, not in the log.

---

## 12. One-line summary

Local relationships handled locally (signal up / call down). Genuinely global state lifted into a small number of autoloads. Genuinely global events on a tiny bus. Structure swapped via a persistent root. Everything else stays in its scene and dies happily with it. Strong typing and idiomatic 4.x APIs throughout, one small verified block at a time. **When in doubt: keep it local, build it dumb, lift it out only when it actually hurts.**
