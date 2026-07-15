# Godot Dev Reference Card

A tight reference for breaking down games, structuring code, and staying out of your own head. Target: **Godot 4.6.x, GDScript, static typing on.** Built from one principle repeated: **local things stay local; only the genuinely global gets lifted out — minimally, when the pain is real.**

---

## ⚠️ Your Two Traps (re-read these first)

You oscillate between two opposite mistakes. The middle path for both is **the tree**.

- **Trap A — over-building structure up front.** Designing the "perfect reusable foundation" on a blank page. You can't; you have no evidence yet what you'll need. The foundation *crystallizes from repetition* — write the dumb specific version 3x, then extract the pattern.
- **Trap B — collapsing all structure into one global thing.** God-object autoload, globalizing every variable, bus-for-everything. Looks tidy, is a tangle.
- **The rule for both:** build/lift structure *when you hit a concrete wall*, never preemptively. If you're doing it "for flexibility later," stop.

---

## Mindset

- **Godot IS your pre-built ecosystem** (your MERC2). Node tree = entity list. `_process`/`_physics_process` = tick loop. Signals = event system. Resources = data files. You add *content*, not scaffolding.
- **Rebuilding a built-in = the blank-page problem in disguise.** Both are "I built the foundation that already existed."
- **Use the built-in for the first pass, always.** Hand-roll *only* at a concrete wall the built-in can't clear. Never preemptively "for control."
- Don't decompose top-down. **Grow outward from one verb.**

---

## Decomposition Method

1. **Core loop = one sentence of verbs.** (Mega Man: "run, jump, shoot, take damage.")
2. **Get the first verb on screen.** A rectangle that moves beats a perfect plan.
3. **Each step must RUN before the next.** Never proceed on something that doesn't execute.
4. **Next step = the most boring missing piece** between now and the sentence being true. You only ever look at the next gap, never the whole tree.
5. **Loose coupling = small interfaces.** "Systems working together" is really: this thing has an `hp`, that thing deals damage, an overlap fires one event. That's the real engineering, not an illusion.

---

## Search the Noun (stop rebuilding these)

Before coding any mechanic, search the docs for the **noun** of what you want:

| Want | Use |
|---|---|
| Move with collision | `CharacterBody2D` + `move_and_slide()` (no args in 4.x — set the `velocity` property first) |
| On ground? | `is_on_floor()` |
| Overlap / hit detection | `Area2D` |
| One-shot move or ease (A → B, fixed duration) | `Tween` via `create_tween()` |
| Follow a MOVING target (camera, homing) | `Camera2D.position_smoothing_enabled`, or delta-based `lerp` / `move_toward` in `_process`. NOT a Tween. |
| Timing / delays | `Timer` (or `await get_tree().create_timer(t).timeout`) |
| Frame animation | `AnimatedSprite2D` / `AnimationPlayer` |
| State-driven animation | `AnimationTree` |
| Pathfinding | `NavigationAgent2D` / `NavigationAgent3D` |

**Tween vs lerp, the distinction that trips people up:**
- `Tween` = "go from where I am to X over N seconds," a *closed* animation. Restarting it every frame to chase a moving target is the wrong tool.
- Following something that keeps moving = per-frame smoothing. Use `Camera2D`'s built-in smoothing for cameras, or `pos = pos.lerp(target, weight)` / `move_toward` in `_process` for everything else. Hand-lerping here is correct, not a sin.

**Heuristic:** about to write math for a fixed A → B ease? Tween. Chasing a live target every frame? Smoothing, not Tween.

---

## Data Persistence

- **`change_scene_to_file()` frees only the current scene branch** (the old scene and all its children). The **root and autoloads survive.** Anything stored "in the level" or "on the player" node dies; autoload data does not.
- **The bucket line — ask per variable:** *Would this need to be true AFTER a scene change frees the current scene?*
  - **No → scene-local.** Enemy positions, projectiles, current HP (if refilled each stage), this level's pickups. Most variables. Leave them local.
  - **Yes → session-global.** Lives, score, unlocked weapons, equipped weapon, levels beaten.
- **Subtlety = the actual skill:** Mega Man *health* is scene-local, *lives* are session-global. Same kind of number, opposite bucket. Draw the line per-variable.
- **Session-global lives in an Autoload singleton** (Project Settings → Globals → Autoload). It sits under `/root`, above the current scene, never freed, reachable by its registered name. This is your persistent character struct.
- **"Persists" ≠ "persists across scenes."** A bullet persists for 2 seconds and is NOT global. Only scene-boundary-crossing data earns an autoload.

---

## Structure: Two Different Tools

Don't file these in the same drawer — that's what made it feel like "autoloaders everywhere."

- **Autoloads = DATA / services.** Global variables, audio. ~2–5 total (`GameState`, `AudioManager`, optional `SceneManager`, `Settings`). More than ~5 = smell.
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

---

## Pause / Menus

- `get_tree().paused = true` freezes the whole tree.
- Set the menu node's process mode so it stays alive while everything else freezes:
  - Inspector: **Process > Mode = When Paused**.
  - Code: `process_mode = Node.PROCESS_MODE_WHEN_PAUSED`.
- That is the built-in "everything stops except this UI."

---

## Signals: "Signal Up, Call Down"

Based on one fact: **a parent knows its children; a child does not know its parent.**

- **Call down** = parent calls methods on children it holds references to. `enemy.take_damage(10)`, `hud.set_health(80)`. Not a compromise — correct. Stop feeling guilty.
- **Signal up** = child emits an event without knowing who listens. `died.emit()`. Keeps the child reusable in any scene.
- **Children never call up.** Welds them to a parent, kills reuse.
- **Siblings do not reference each other directly. The parent mediates.** Child A signals up, the parent hears it and calls down into child B. Only reach for shared global state when the thing really is shared *data* (see Tier 2), not just to avoid wiring the parent.
- Result: flow goes **up via signals → parent decides → down via calls.** A tree, not a web.

### Where to connect

| Situation | Connect via |
|---|---|
| Both nodes live in the *same saved scene* and exist from the start (a menu's own button, a level's pre-placed door) | **Inspector** |
| One side is spawned at runtime | **Code**, at the spawn site, same line as `add_child` |

```gdscript
enemy.died.connect(_on_enemy_died)
```
On `queue_free()`, Godot **auto-disconnects** when the node is actually freed. You do not manage connection lifetimes; they are born and die with the node.

**Connect to the permanent thing, not the transient ones.** The HUD connects to `GameState` once in `_ready()` and ignores the churn of spawning and dying objects entirely.

---

## Signal Architecture: The Three Tiers

For any two things that need to talk, ask in order:

1. **Does one own the other (parent/child)?** → **Tier 1: direct** signal-up / call-down. *Not the bus.* Putting parent/child traffic on a global bus is the #1 mistake.
2. **Is it really about a piece of shared state changing?** → **Tier 2: autoload data + a `_changed` signal.** Score, lives, equipped weapon. The signal is attached to the data it describes.
3. **Neither — a genuinely game-wide moment with no owner?** → **Tier 3: SignalBus, sparingly.** `player_died`, `game_paused`, `boss_defeated`. ~8 signals in a finished Zelda clone, not 80.

- **SignalBus-for-everything wasn't wrong because the game got big** — it was fine for Pong because Pong was small enough to hide that the bus eats the tree's directionality.
- Most interactions are Tier 1 or 2. The gate keeps the bus tiny automatically.

### Tier 2 pattern (data emits on change)

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

> Setter caveat: setters also run during scene load / init, before other nodes connect. If a listener must not miss the first value, have it read `GameState.score` in its own `_ready()` and *then* connect, rather than relying on the emit.

---

## Config / Typing (already in your project)

| Setting | Value | Why |
|---|---|---|
| `untyped_declaration` | `2` (Error) | The keystone. Makes GDScript behave like C, not Python. Supercharges autocomplete. |
| `unsafe_*` (e.g. `unsafe_method_access`, `unsafe_property_access`, `unsafe_cast`) | `1` (Warn), not Error | Some unsafe ops (Dictionary access, `get_node`) are unavoidable. See them, don't let them block the build. |

Warning levels: `0 = Ignore`, `1 = Warn`, `2 = Error`.

- **`:=` is fine.** It is typed inference, the equivalent of C++ `auto`. Don't ban it.
- **Annotate everything:** `func move(delta: float) -> void:`. A typed `Array[int]` behaves like `std::vector<int>`: type mismatches are caught at parse time where the compiler can see them.
- **Use `@export` and `@onready`** for inspector-editable fields and deferred node references. `@onready var sprite: Sprite2D = $Sprite2D`.
- **Use the in-editor debugger + remote scene tree** for live runtime values. Stop debugging with `print()` like it's 1999.
- After editing warning settings: **restart the editor or re-save a script**, or they won't apply.

---

## The One-Line Summary

Local relationships handled locally (signal up / call down). Genuinely global state lifted into a small number of autoloads. Genuinely global events on a tiny bus. Structure swapped via a persistent root. Everything else stays in its scene and dies happily with it. **When in doubt: keep it local, build it dumb, lift it out only when it actually hurts.**
