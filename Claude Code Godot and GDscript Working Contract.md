Reusable across all my Godot projects. This is a behavioral contract, not
documentation. The `.gd` files on disk are the source of truth for code — read
them. Project-specific facts live in `.claude/rules/`; running session state
lives in `MEMORY.md`.

## Working agreement
- **One small building block at a time.** Finish and verify a block before
  proposing the next. No long multi-step narratives.
- **Be constructively critical.** Never agree just to be amenable. Not every idea
  is a good one — say so, with reasons.
- **Design forks are mine to decide.** When a real fork exists, present the
  options with tradeoffs and let me choose. Do not silently pick one and build it.
- **No empty scaffolding.** Build a node, scene, or script only when the block
  that needs it actually arrives. Knowing something is coming is not a reason to
  stub it now.

## Comments & docs
- Wrap larger comment blocks in Unicode box-drawing frames (`─ │ ┌ ┐ └ ┘`).
- Document every script, function, member, and signal with Godot `##`
  documentation comments so the editor's built-in Help generates from them. Use
  the doc tags (`[br]`, `[code]`, `@tutorial`) where they help.

## Engine & version
Target **Godot 4.6.x stable, GDScript 2.0** unless a project's rules say
otherwise. Write only code valid for that version. When unsure an API, signature,
or node exists in the target version, say so and point to the docs — never invent
one. Version-specific defaults (currently 4.6): Jolt is the default 3D physics for
new projects; inverse kinematics is the `IKModifier3D` family (`TwoBoneIK3D`,
`FABRIK3D`, `CCDIK`). Re-check this block on any engine upgrade.

### Never emit Godot 3.x patterns
- `export var` → `@export var`; `onready var` → `@onready var`
- `yield(o,"s")` → `await o.s`
- `connect("p", self, "_on")` → `node.p.connect(_on)`; `emit_signal("d")` → `d.emit()`
- `KinematicBody2D/3D` → `CharacterBody2D/3D`; set `velocity`, then
  `move_and_slide()` with no args
- `instance()` → `instantiate()`; `Spatial` → `Node3D`; `Reference` → `RefCounted`
- `PoolXArray` → `PackedXArray`; `.empty()` → `.is_empty()`
- `OS.get_ticks_msec()` → `Time.get_ticks_msec()`; `rad2deg`/`deg2rad` →
  `rad_to_deg`/`deg_to_rad`; `stepify` → `snapped`
- `setget` → `get:`/`set:` blocks; `OS.window_*` → `DisplayServer.*` / `get_window()`
- A `Tween` comes from `create_tween()`, not a node

## Godot-thonic: engine first
Before writing a system, use the built-in:
- Timing → `Timer` node or `await get_tree().create_timer(t).timeout`, not manual
  delta accumulation
- Interpolation / juice → `create_tween()`, not per-frame lerp loops
- Animation → `AnimationPlayer`; blended or state-driven → `AnimationTree`
- Detection → `Area2D/3D` + signals, not distance polling
- Movement / collision → `CharacterBody2D/3D.move_and_slide()` /
  `move_and_collide()`, not custom collision math
- Communication → signals up, direct calls down; many listeners → groups
  (`add_to_group`, `get_tree().call_group`), not a hand-built event bus
- Data / config → custom `Resource` classes with `@export`, not loose dicts/JSON
- Save / load → `ResourceSaver`/`ResourceLoader`, `ConfigFile`, `FileAccess`
- Global state → an autoload singleton

Do not replicate an original game's technical workarounds just because the
original did them that way — do it the idiomatic Godot way.

## GDScript style
- **Strong typing, always.** Write out the type for every variable, parameter,
  and return, every time, unless something legitimately prevents it. Typed
  collections too (`Array[Enemy]`, `Dictionary[String, int]`).
- **No `$` node references.** Resolve a node once into an `@export` slot or an
  `@onready` var; reference that var thereafter. Avoid scattering `$Path` literals
  through logic.
- `class_name` only on infrastructure / reusable types, not on every leaf script
  (it pollutes the global namespace).
- Annotations: `@export`, `@export_range`, `@onready`, `@tool`, `@export_group`.
- `await` for anything time- or signal-based, not manual state flags.
- Built-in math (`move_toward`, `lerp`, `clamp`, `snapped`, vector ops) — don't
  reimplement it.
- `const` / `enum` over magic numbers and strings.
- Naming: `snake_case` funcs/vars, `PascalCase` classes & nodes, `CONSTANT_CASE`
  consts, leading `_` for private, past-tense signal names (`health_depleted`).
- Physics-affecting logic in `_physics_process`, frame logic in `_process`, input
  in `_input` / `_unhandled_input`.

## Composition & restraint
- Composition over inheritance: behaviour from child nodes/components, not deep
  class trees.
- No manager classes, abstraction layers, or event buses until a real second
  caller exists. Signals + groups cover most of it.
- Child nodes reach their owning body via `owner` or an exported reference — never
  `get_parent()` chains or tree-crawling.

## Output contract
For any script, state which node it attaches to and the children/exports it
assumes — a `.gd` file is meaningless without its scene context. If a native node
does the job better than a script, say so first. Flag any API you are not certain
exists in the target version.

## Session continuity
At the start of a session, read `MEMORY.md` at the repo root if present — it is
the running state; read it before acting. At the end of a completed building
block, append a short dated entry: what changed, any decisions locked, and the
current verified state. Keep it concise — durable rules belong in `.claude/rules/`,
not in the log.