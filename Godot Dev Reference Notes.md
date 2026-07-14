# Godot Dev Reference Card

A tight reference for breaking down games, structuring code, and staying out of your own head. Built from one principle repeated: **local things stay local; only the genuinely global gets lifted out — minimally, when the pain is real.**

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
| Move with collision | `CharacterBody2D` + `move_and_slide()` |
| On ground? | `is_on_floor()` |
| Overlap / hit detection | `Area2D` |
| Smooth move / ease / follow | `Tween` (never lerp by hand) |
| Timing / delays | `Timer` |
| Frame animation | `AnimatedSprite2D` / `AnimationPlayer` |
| State-driven animation | `AnimationTree` |
| Pathfinding | `NavigationAgent` |

**Heuristic:** about to write math to move, ease, follow, overlap, or tick? → stop, there's a node for it.

---

## Data Persistence

- **`change_scene_to_file()` destroys the entire scene tree.** Anything stored "in the level" or "on the player" dies instantly.
- **The bucket line — ask per variable:** *Would this need to be true AFTER a scene change destroys everything?*
  - **No → scene-local.** Enemy positions, projectiles, current HP (if refilled each stage), this level's pickups. Most variables. Leave them local.
  - **Yes → session-global.** Lives, score, unlocked weapons, equipped weapon, levels beaten.
- **Subtlety = the actual skill:** Mega Man *health* is scene-local, *lives* are session-global. Same kind of number, opposite bucket. Draw the line per-variable.
- **Session-global lives in an Autoload singleton** (Project Settings → Globals → Autoload). It sits above the tree, never freed, reachable by name. This is your persistent char struct.
- **"Persists" ≠ "persists across scenes."** A bullet persists for 2 seconds and is NOT global. Only scene-boundary-crossing data earns an autoload.

---

## Structure: Two Different Tools

Don't file these in the same drawer — that's what made it feel like "autoloaders everywhere."

- **Autoloads = DATA / services.** Global variables, audio. ~2–5 total (`GameState`, `AudioManager`, optional `SceneManager`, `Settings`). More than ~5 = smell.
- **Persistent root scene = STRUCTURE.** A permanent `Main` node with a swappable child slot:
  ```
  Main (Node)              ← never freed
  ├── CurrentLevel (Node)  ← free children + instantiate new level here
  ├── HUD (CanvasLayer)    ← persists across level swaps
  └── PauseMenu (CanvasLayer)
  ```
  Swap `CurrentLevel`'s children instead of `change_scene_to_file()`. HUD/menu stop flickering and rebuilding.
- **They collaborate:** `Main.load_level()` does the structural swap; it reads `GameState` to know *which* level.
- **Don't adopt the persistent root until it hurts** (HUD rebuilds, music restarts). Tiny prototype = plain `change_scene_to_file()` + one `GameState` is fine.

---

## Pause / Menus

- `get_tree().paused = true` freezes the whole tree.
- Set the menu node's **`process_mode = "When Paused"`** so it stays alive while everything else freezes. That's the built-in "everything stops except this UI."

---

## Signals: "Signal Up, Call Down"

Based on one fact: **a parent knows its children; a child does not know its parent.**

- **Call down** = parent calls methods on children it holds references to. `enemy.take_damage(10)`, `hud.set_health(80)`. Not a compromise — correct. Stop feeling guilty.
- **Signal up** = child emits an event without knowing who listens. `died.emit()`. Keeps the child reusable in any scene.
- **Children never call up** (welds them to a parent → not reusable).
- **Siblings never reference each other.** HUD and player are siblings → they must not touch. They communicate via shared global state instead.
- Result: flow goes **up via signals → parent decides → down via calls.** A tree, not a web.

### Where to connect

- **Inspector** — both nodes live in the *same saved scene* and exist from the start (a menu's own button, a level's pre-placed door).
- **Code** — one side is spawned at runtime. Connect at the spawn site, same line as `add_child`:
  ```gdscript
  enemy.died.connect(_on_enemy_died)
  ```
  On `queue_free()`, Godot **auto-disconnects**. You don't manage connection lifetimes — they're born and die with the node.
- **Connect to the permanent thing, not the transient ones.** HUD connects to `GameState` once in `_ready()` and ignores the churn of spawning/dying objects entirely.

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
		score = value
		score_changed.emit(value)
```

HUD subscribes to `score_changed` once. Enemy and HUD never reference each other.

---

## Config / Typing (already in your project)

- **Static typing enforced:** `untyped_declaration = 2` (Error) — the keystone. Makes GDScript behave like C, not Python. Supercharges autocomplete.
- **`unsafe_*` = `1` (Warn), not Error** — some unsafe ops (Dictionary access, `get_node`) are unavoidable. See them, don't let them block the build.
- **`:=` is fine** (it's typed inference = C++ `auto`). Don't ban it.
- Annotate everything: `func move(delta: float) -> void:`. Typed `Array[int]` = `std::vector<int>`: errors caught at parse time.
- **Use the in-editor debugger + remote scene tree** (live runtime values). Stop debugging with `print()` like it's 1999.
- After editing warning settings: **restart editor or re-save a script** or they won't apply.

---

## The One-Line Summary

Local relationships handled locally (signal up / call down). Genuinely global state lifted into a small number of autoloads. Genuinely global events on a tiny bus. Structure swapped via a persistent root. Everything else stays in its scene and dies happily with it. **When in doubt: keep it local, build it dumb, lift it out only when it actually hurts.**
