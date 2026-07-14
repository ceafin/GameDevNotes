# Mega Man NES Clone: Architecture & Roadmap

**Engine:** Godot 4.6.3 / GDScript / VSCodium (Linux)
**Scope target:** MM1/MM2/MM3 mechanics, confirmed feature set below.
**APIs used:** target Godot 4.4+ features (typed loop vars, exported node refs). All valid on 4.6.3.
**v3 change:** FSM is now fully node-reference based. Transitions carry a `State` node reference (exported per state), not strings. No string dictionaries.
**v4 change:** Researched MM1-5 mechanics. Every mechanic not in core scope is now parked in Stretch goals with first-game attribution. Rush added there per request.
**v5 change:** Promoted 5 mechanics from stretch to core (item drops, Yoku blocks + moving platforms, weakness chart, password save). Corrected E-Tank carry cap. Added data-resource layer.
**v6 change:** Folded in `docs/MANUAL.md`'s Burrito Man/Burrito Supremo narrative. Charge shot and champion (weapon) powers are now **Supremo-only**, not always-on (overrides v1 of Locked Decision #1). Added `transform` to the Phase 0 input map. Weapon-select from the pause menu is **queue-only**, it never auto-transforms the player. See Locked Decisions #1 and #8.

> **How to use this doc:** Build top-to-bottom by phase. Do *not* build all systems at once. Finish the vertical slice (Phases 0-3) first: a Mega Man that runs, jumps, shoots, kills one enemy, and takes damage. Everything else bolts onto that.

---

## Correction / accuracy note

| Claim | Reality | Decision |
|---|---|---|
| Charge shot in MM1-3 | No. Debuted in **MM4** (1991) | Including anyway, your call |
| Slide | **MM3** only | Included |
| Rush (Coil/Jet/Marine) | MM3 | Excluded for now |
| E-Tanks | Debuted **MM2** | Included |
| Weapon switching in MM1-3 | Pause-menu only, no quick-cycle | Pause-menu core, cycle = stretch |
| Life/energy bar length | Commonly cited as **28 units** via disassembly | Tunable default, not treated as canon |

---

## Confirmed feature set

| Mechanic | In? | Notes |
|---|---|---|
| Charged buster shot | Yes | **2 tiers** (normal + full charge), charged shot counts toward the 3-cap. **Charging only works in Burrito Supremo**; base form fires normal shots only |
| Slide | Yes | MM3 dash-slide, own FSM state, **jump-cancellable** |
| Rush | No | Deferred |
| E-Tanks | Yes | Full health refill; carry 4 (MM2) / 9 (MM3-5); MM3+ persist through Game Over |
| Score | No | Dropped |
| On-screen buster cap = 3 | Yes | Live shots, **normal + charged combined**, hard limit |
| Variable jump height | Yes | Release jump early = shorter hop |
| Knockback + i-frames | Yes | On taking damage |
| Instant death (pits/spikes) | Yes | Ignores health entirely, bypasses i-frames |
| Weapon switching | Yes | **Pause-menu only** (authentic). Selecting a power **queues** it, no auto-transform. Powers only fire in Supremo. Quick-cycle = stretch goal |
| Enemy item drops | Yes | drop-table roll on death: health / weapon energy / 1-up / E-Tank |
| Weapon weakness chart | Yes | each boss weak to one weapon (`WeaponData` ref + damage multiplier) |
| Password save | Yes | code encodes bosses cleared + E-Tank count (MM2-5 grid style) |

---

## Phased roadmap

| Phase | Goal | Key deliverable |
|---|---|---|
| 0 | Setup | project settings, input map, pixel snap, folder skeleton |
| 1 | Locomotion | `CharacterBody2D`, `MovementComponent`, run, variable jump, **then slide** |
| 2 | Buster | projectile + **charge shot**, 3-shot cap, collision layers |
| 3 | Combat loop | 1 enemy, hurtbox/hitbox, `HealthComponent`, knockback, i-frames (**Hurt state**), **enemy item drops (`DropTable`)** |
| 4 | Level + camera | `TileMapLayer`, **MM3 room/camera system**, ladders (**Climb state**), pit/spike death, **moving/conveyor platforms + Yoku blocks** |
| 5 | HUD | player health bar, weapon-energy bar, e-tank display |
| 6 | Boss | boss FSM, boss health bar, arena lock, **weakness-damage hook** |
| 7 | Weapon-get + pause menu | `WeaponData` resource, **Start/Pause weapon-select menu**, energy drain, **weapon weakness chart (`BossData`)** |
| 8 | Stage flow | checkpoints, respawn, lives, stage select, **password save** |
| 9 | Content + polish | more enemies/stages, sfx/music, screen transitions |
| S | Stretch (end) | quick-cycle weapon hotkeys (bumper/trigger), see Stretch goals |

---

## Folder structure

```
res://
├── autoload/       # GameState, EventBus, AudioManager, SceneManager
├── actors/
│   ├── player/
│   ├── enemies/
│   └── bosses/
├── components/     # MovementComponent, HealthComponent, Hurtbox, Hitbox, StateMachine, State
├── projectiles/
├── levels/         # stage scenes + Room nodes
├── ui/
├── weapons/        # WeaponData .tres resources
├── resources/      # EnemyData, BossData, DropTable, other custom Resources
└── assets/         # sprites, audio, fonts
```

---

## Autoloads (singletons)

| Autoload | Holds |
|---|---|
| `GameState` | lives, e-tanks, unlocked weapons, current stage, checkpoint |
| `EventBus` | global signals (`player_died`, `boss_defeated`, `weapon_changed`) |
| `AudioManager` | bgm + sfx playback |
| `SceneManager` | stage load, room/scene transitions |

Keep autoloads for state and global events only. Do not stuff gameplay logic here.

---

## Architecture: composition-first (no shared entity base), everything Node-based

Player and Enemy do **not** share a base class. Both are `CharacterBody2D` scenes composed from the **same Node-based component set**. Variety comes from data resources + state scripts, not inheritance.

```
CharacterBody2D
├── Player  (player.gd)  -> MovementComponent, HealthComponent, HurtboxComponent, StateMachine
└── Enemy   (enemy.gd)   -> MovementComponent, HealthComponent, HurtboxComponent, HitboxComponent, StateMachine
                             + EnemyData (.tres) for stats/behavior variance
```

**Only two sanctioned shallow bases** (genuine is-a, near-zero depth):

```
State (Node, class_name)        -> PlayerIdle, PlayerRun, ... , EnemyPatrol, ...
Projectile (Area2D, class_name) -> BusterShot, ChargedShot, (weapon shots)
```

**Components (all Node-based, attached as child nodes):**

| Component | Node type | Job |
|---|---|---|
| `MovementComponent` | Node | holds movement tunables + gravity helper, operates on a passed-in body |
| `HealthComponent` | Node | hp, `take_damage()`, `kill()`, emits `died` / `health_changed` |
| `HurtboxComponent` | Area2D | receives hits, routes to `HealthComponent` |
| `HitboxComponent` | Area2D | deals damage on overlap |
| `StateMachine` | Node | node-based FSM (see below) |

**Data resources (`.tres`, reference-based, no strings):**

| Resource | Holds |
|---|---|
| `WeaponData` | shot scene, damage, energy cost, palette |
| `BossData` | `weakness_weapon: WeaponData` ref + `weakness_multiplier: float` |
| `DropTable` | weighted pickup scenes + no-drop chance, rolled on enemy death |
| `EnemyData` | per-enemy stats and behavior variance |

Rule of thumb: shared **behavior/data** goes in a component or a `.tres` resource, never a new subclass.

---

## Player FSM (node-based, reference-wired)

Design rules:

- Every state is a **Node** (child of the `StateMachine` node).
- States reach their actor via **`owner`** (the actor scene root). No `get_parent()`.
- **Transitions carry a `State` node reference, not a string.** Each concrete state declares `@export var some_state: State` slots and emits the target node. Assign targets in the inspector by dragging sibling State nodes in.
- **No string dictionaries, no `state_name` literals, no `.to_lower()` lookups.**
- Constraint: the FSM must live *inside* the actor's own scene for `owner` to resolve to the actor. Do not instance the FSM as a separate detached scene.
- Only unavoidable strings left are Godot **input action names** (`"jump"`, `"move_left"`), which are a native Input API requirement. Centralize them as `const StringName` in an autoload later if you want zero loose strings.

**Trade-off (accept knowingly):** transition targets move from code strings into inspector-wired node refs. More drag-assign in the editor, but transitions are type-checked, refactor-safe, and click-navigable. A missing ref triggers a `push_warning`, not a silent typo.

**Scene tree:**

```
Player (CharacterBody2D)          # %-unique children marked "Access as Unique Name"
├── AnimatedSprite2D
├── CollisionShape2D
├── MovementComponent (Node)      %MovementComponent
├── HealthComponent (Node)        %HealthComponent
├── HurtboxComponent (Area2D)     %HurtboxComponent
└── StateMachine (Node)           %StateMachine   (@export initial_state -> Idle)
    ├── Idle (State)              # each concrete state exports its transition targets
    ├── Run (State)
    ├── Jump (State)
    ├── Fall (State)
    ├── Climb (State)
    ├── Slide (State)
    └── Hurt (State)
```

**States:**

| State | Enters from | Notes |
|---|---|---|
| Idle | Run, Fall(land) | can fire, can start charge |
| Run | Idle | can fire, can charge |
| Jump | Idle/Run/Slide | variable height, single jump |
| Fall | Jump, walk off ledge | |
| Climb | ladder contact + up/down | can fire horizontally only |
| Slide | Idle/Run + down+jump | short duration, low hitbox, locked direction |
| Hurt | any (on damage) | knockback, i-frame flash, input locked |

**State -> phase built:**

| State | Built in phase |
|---|---|
| Idle, Run, Jump, Fall | 1 |
| Slide | 1 |
| Hurt | 3 (needs combat) |
| Climb | 4 (needs ladders) |

**Slide exit rules (locked):**

| Trigger | Result |
|---|---|
| Jump pressed mid-slide | cancel to **Jump**, keep facing direction, normal jump velocity |
| Duration timer ends | Run if moving, else Idle |
| Hits wall | end slide early -> Idle/Run |
| Ceiling still overhead at timer end | stay in Slide until clear (avoid clipping into floor) |

**Variable jump:** on `jump` release while `velocity.y < 0`, cut upward velocity (e.g. halve it) inside the Jump state.

**Buster is an action layer, not a state.** Charging and firing happen *on top of* Idle/Run/Jump/Fall/Climb/Slide, driven by a separate charge timer. Do not make "Shoot" its own FSM state or you fight the locomotion states. **Form (Base/Supremo) is also an action layer, not a state**, toggled by `transform`; it gates whether charging/champion powers are available, it does not replace or branch the locomotion FSM.

---

## Camera / room system (MM3 style)

MM3 mixes free-scrolling rooms with locked single-screen rooms. Both are the *same* mechanism: a **Room** defines a rectangle, the camera clamps to it. Rooms may be **larger than one screen in either axis** (long horizontal corridors, tall vertical shafts, or both).

| Concept | Implementation |
|---|---|
| Room bounds | a `Room` node (or `Area2D`) storing a rect; **any size >= viewport** |
| Free-scroll room | rect larger than viewport, camera follows player clamped to rect |
| Locked screen | rect == viewport size, camera cannot move = screen is locked |
| Room transition (locked) | player crosses boundary -> **lock input, tween camera + limits to next room, resume** (classic MM scroll-pan) |
| Boss arena | one-screen room, close door on entry, disable exit until boss dead |

**Transition style is locked (confirmed):** no hard cuts. Every room-to-room crossing does the classic pan with input frozen, regardless of room size.

**Camera2D settings for authentic feel:**

| Property | Value | Why |
|---|---|---|
| `position_smoothing_enabled` | `false` | NES camera is rigid, tracks player exactly |
| `limit_left/right/top/bottom` | set per active room | this is what produces scroll vs lock |
| `limit_smoothed` | `false` normally, `true` only during transitions | avoid drift |

Set the four `limit_*` values from the current room's rect. That single system gives you both behaviors with no branching.

---

## Charge shot design notes

| Aspect | Locked decision |
|---|---|
| Tiers | **2**: normal + full charge (no mid tier) |
| Form gate | **Charging only works in Burrito Supremo.** In base form, `shoot` always fires a normal (uncharged) `BusterShot`, no charge accumulation |
| Input | hold `shoot` (Supremo only), accumulate `charge_time`; release fires the reached tier |
| Firing | below threshold -> `BusterShot`, at/above -> `ChargedShot` |
| 3-shot cap | **normal + charged share one pool of 3 live shots**; a charged shot occupies one slot |
| Charge persistence | carries across Idle/Run/Jump/Fall/Climb/Slide |
| Charge cancel | entering **Hurt** cancels the charge (no auto-fire) |
| Visual | sprite flash/particles while charging (Phase 9 polish) |

Track charge + the live-shot count in the player script (or a small `BusterComponent`), not in the FSM. Simplest cap enforcement: each spawned shot connects its `tree_exited` back to a counter; block firing when count == 3.

---

## Use Godot-native, do not reinvent

| Need | Native tool | Do NOT build |
|---|---|---|
| Movement/collision | `CharacterBody2D` + `move_and_slide()` | custom physics loop |
| Moving platforms / conveyors | `AnimatableBody2D` (native moving-platform support in `move_and_slide`) | manual position hacks |
| Combat detection | `Area2D` hurtbox/hitbox + collision layers | manual AABB checks |
| Tilemaps | `TileMapLayer` (4.3+, replaces `TileMap`) | array maps |
| Animation | `AnimatedSprite2D` (`SpriteFrames`) | hand-rolled frame timers |
| Weapon/enemy data | custom `Resource` (`.tres`) | scattered dicts/JSON |
| Events | signals + `EventBus` | polling boolean flags |
| FSM transitions | exported `State` node refs | string-keyed state dictionaries |
| Type tagging | Groups + collision layers | string compares everywhere |
| Persistent state | autoload singleton | static globals scattered around |

---

## Abide by Godot best-practices, do not code with external conventions

The following Godot best-practices are not exhaustive, and these are the starting base line. When in doubt, double-check with Godot's own documentation or ask clarifying questions.

### GDScript Style & Conventions

- **Use snake_case** for file names, variable names, and function names.
- **Use PascalCase** for class names and node types.
- **Use UPPER_CASE** for constants and enums.
- **Prepend an underscore `_`** to private variables and private functions.
- **Use tabs, not spaces, for indentation** (official style guide). Code blocks below show spaces only because markdown cannot render tabs reliably.
- **Put `class_name` on its own line, above `extends`** (official style-guide order).
- **Leverage strong, static typing, even when type is "obvious" still strongly type** (e.g., `var health : int = 100`) to catch bugs early and improve auto-complete.
- **Use integer-native math functions** (`maxi`, `mini`, `clampi`) for typed ints, and float variants (`maxf`, `minf`, `clampf`) for floats.
- **Prefer Node references over strings** for anything the engine can hold as a Node (states, targets, spawn points). Reserve strings for genuine text and unavoidable native APIs (input actions, groups).
- **Utilize whitespace** for all syntax. Where it does not break syntax expectations, be whitespace "friendly" and try not to bunch everything together (no one-line `func x(): pass`).
- [[1](https://gdquest.gitbook.io/gdquests-guidelines/godot-gdscript-guidelines), [2](https://www.youtube.com/watch?v=USIbT81VFVg), [3](https://simondalvai.org/blog/godot-static-typing/), [4](https://www.beep.blog/2024-02-14-gdscript-typing/), [5](https://docs.godotengine.org/en/4.3/tutorials/scripting/gdscript/gdscript_styleguide.html)]

### Node & Scene Management

- **"Signal up, method down"**: Call methods directly on children; use signals to communicate with parent nodes.
- **Use variables to reference Node Paths** Store a dollar-sign node path into a variable, and utilize the variable, instead of directly using dollar-sign paths in code.
- **Use `%` Unique Node Names** only for internal scene referencing instead of rigid, absolute NodePaths.
- **Instantiate scenes dynamically** using `preload()` for assets known at compile-time to avoid runtime stutter.
- **Free nodes safely** using `queue_free()` instead of `free()` to avoid crashing from active processing.
- [[1](https://www.youtube.com/watch?v=LWcTQZ-NaXs), [2](https://www.facebook.com/groups/godotengine/posts/3445018298968073/), [3](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_basics.html)]

### Performance & Engine Data

- **Cache node references** using the `@onready` keyword to avoid repetitive `get_node()` lookups.
- **Keep `_process` lightweight**: Move physics calculations to `_physics_process` and heavy logic to threads or signals.
- **Utilize native types**: Use built-in math functions (`clamp`, `lerp`, `remap`) and optimized data containers (`PackedByteArray`, `Vector2i`).
- **Use Custom Resources** (`Resource`) to store game data, item stats, and configurations instead of heavy Nodes or JSONs.
- **Avoid shims/hacks for performance**: Only use things like `await` and `process_frame` when absolutely necessary, never to create a hack around race conditions or more appropriate coding architectures. Use them only when extra-appropriate.
- **Avoid "fancy" code tricks**: Things like ternary operators and lambdas are completely acceptable; however, avoid them for more clearer-human-readable code conventions. Use them only when extra-appropriate.
- [[1](https://www.kodeco.com/43227199-using-and-creating-resources-in-godot-4/page/2)]

### Architecture

- **Use Composition and Inheritance**: use proper data structures and conventions to minimize parallel unique similar objects/etc.
- **Keep scripts modular**: One script should handle one specific responsibility (Composition over Inheritance).
- **Avoid `get_parent()`**: High coupling to a parent breaks scene reusability and isolation. Use them only when extra-appropriate.
- **Use Autoloads (Singletons) Appropriately**: Restrict them to global managers like audio, saving, or scene transitions, or any appropriately scoped artifacts that need to exist in a super position outside of scenes or inter-scene.

---

## Phase 0 setup checklist

| Setting | Value |
|---|---|
| Rendering > Textures > Default Texture Filter | **Nearest** |
| Display > Window > Viewport width/height | **256 x 240** (NES framebuffer) |
| Display > Window > Stretch Mode | **canvas_items** |
| Display > Window > Stretch Aspect | **keep** |
| Physics > Common > Physics Ticks per Second | **60** |
| Snap 2D Transforms/Vertices to Pixel | **On** (both) |

**Input Map (core):** `move_left`, `move_right`, `move_up`, `move_down`, `jump`, `shoot`, `transform`, `pause`

**Input Map (stretch, end of project):** `weapon_cycle_left`, `weapon_cycle_right` (bumper/trigger)

**Tunables:** put `run_speed`, `jump_velocity`, `gravity`, `slide_speed`, `slide_time`, `charge_time` as `@export` vars. Never hardcode. Tune to feel. Frame-exact ROM constants exist via TAS/disassembly communities if you later want authenticity; I will not hand you numbers I cannot verify. All numbers in the samples below are placeholders.

---

## Starter code patterns

Indentation shown as spaces for markdown; **use tabs in-editor**.

**State machine (`components/state_machine.gd`), pure node references, zero strings:**

```gdscript
class_name StateMachine
extends Node

@export var initial_state: State

var current_state: State

func _ready() -> void:
	for child: Node in get_children():
		if child is State:
			child.transitioned.connect(_on_transitioned)
	if initial_state:
		current_state = initial_state
		current_state.enter()

func _process(delta: float) -> void:
	if current_state:
		current_state.update(delta)

func _physics_process(delta: float) -> void:
	if current_state:
		current_state.physics_update(delta)

func _on_transitioned(new_state: State) -> void:
	if new_state == null:
		push_warning("StateMachine: transition target is null. Check exported state refs in the inspector.")
		return
	if new_state == current_state:
		return
	if current_state:
		current_state.exit()
	new_state.enter()
	current_state = new_state
```

**Base state (`components/state.gd`), emits a `State` node, not a string:**

```gdscript
class_name State
extends Node

# States reach their actor via `owner` (the actor scene root).
# Concrete states declare their own `@export var target: State` slots
# and emit the target node. No strings, no lookups.

signal transitioned(new_state: State)

func enter() -> void:
	pass

func exit() -> void:
	pass

func update(_delta: float) -> void:
	pass

func physics_update(_delta: float) -> void:
	pass
```

**Movement component (`components/movement_component.gd`):**

```gdscript
class_name MovementComponent
extends Node

@export var run_speed: float = 90.0
@export var acceleration: float = 1200.0
@export var gravity: float = 640.0
@export var max_fall_speed: float = 300.0
@export var jump_velocity: float = -240.0   # up is negative y
@export var slide_speed: float = 160.0
@export var slide_time: float = 0.35

func apply_gravity(body: CharacterBody2D, delta: float) -> void:
	if not body.is_on_floor():
		body.velocity.y = minf(body.velocity.y + gravity * delta, max_fall_speed)
```

**Health component (`components/health_component.gd`):**

```gdscript
class_name HealthComponent
extends Node

signal died
signal health_changed(current: int, max_value: int)

@export var max_health: int = 28   # commonly cited via disassembly; tunable, not canon

var current_health: int

func _ready() -> void:
	current_health = max_health

func take_damage(amount: int) -> void:
	current_health = maxi(current_health - amount, 0)
	health_changed.emit(current_health, max_health)
	if current_health == 0:
		died.emit()

func heal(amount: int) -> void:
	current_health = mini(current_health + amount, max_health)
	health_changed.emit(current_health, max_health)

func kill() -> void:
	# Instant death (pits/spikes). Bypasses i-frames and knockback.
	current_health = 0
	health_changed.emit(current_health, max_health)
	died.emit()
```

**Player (`actors/player/player.gd`), exposes cached component refs for states:**

```gdscript
class_name Player
extends CharacterBody2D

@onready var movement: MovementComponent = %MovementComponent
@onready var health: HealthComponent = %HealthComponent
@onready var state_machine: StateMachine = %StateMachine
```

**Example state (`actors/player/states/player_run.gd`), transitions via exported node refs:**

```gdscript
class_name PlayerRun
extends State

@export var idle_state: State
@export var jump_state: State
@export var fall_state: State

func physics_update(delta: float) -> void:
	var player: Player = owner as Player
	var dir: float = Input.get_axis("move_left", "move_right")
	player.velocity.x = dir * player.movement.run_speed
	player.movement.apply_gravity(player, delta)
	player.move_and_slide()
	if not player.is_on_floor():
		transitioned.emit(fall_state)
	elif Input.is_action_just_pressed("jump"):
		transitioned.emit(jump_state)
	elif dir == 0.0:
		transitioned.emit(idle_state)
```

---

## Locked design decisions

| # | Decision | Affects |
|---|---|---|
| 1 | Charge = 2 tiers; charged shot counts as 1 of the 3 live shots (shared pool). **Supersedes v1: charging only works in Burrito Supremo, base form fires normal shots only** | buster logic, cap counter |
| 2 | Slide is jump-cancellable (keeps facing dir, normal jump velocity) | Slide state exit |
| 3 | Camera = classic locked scroll-pan transitions; rooms may exceed one screen in either axis | room/camera code |
| 4 | No shared Player/Enemy base; both compose from the same Node components | actor scenes |
| 5 | Weapon switch = pause-menu only (authentic); quick-cycle hotkeys deferred to end-of-project stretch | input map, UI |
| 6 | FSM states reach the actor via `owner`; FSM must live inside the actor scene | Phase 1 wiring |
| 7 | FSM transitions carry exported `State` node refs, not strings; no string dictionaries or `state_name` literals | StateMachine, all states |
| 8 | Base/Supremo transform (`transform` input action) is a form toggle, not an FSM state. Champion (weapon) powers only fire in Supremo. Selecting a power from the pause menu **queues** it; it does not auto-transform the player | input map, Player, weapon-select UI, Phase 2/7 buster + weapon logic |

---

## Stretch goals (parked, not in core scope)

Researched across MM1-5. Everything in the phased roadmap above is core. The tables below are every MM1-5 mechanic **not** yet in core, parked here per request. "First game" = where it debuted. Five mechanics were promoted to core this round (see note at the end of this section).

### Support items & companions

| Item | First game | Does |
|---|---|---|
| Rush (Coil / Jet / Marine) | MM3 | dog transforms into springboard / auto-forward jet / submarine; each energy-limited |
| Eddie ("Flip-Top") | MM4 | appears in set rooms, drops one random item (health, ammo, 1-up, or E-Tank) |
| Beat | MM5 | bird ally; unlock by collecting 8 letters spelling MEGAMANV across stages; auto-attacks nearest enemy and drains its own gauge; disables buster charging while active |
| Super Arrow | MM5 | fire a ridable forward-moving platform (Item-2-like) |
| Items 1 / 2 / 3 | MM2 | rising / forward-moving / wall-climbing platforms (pre-Rush traversal set) |
| Magnet Beam | MM1 | creates temporary solid platforms to bridge gaps |
| Wire + Balloon adaptors | MM4 | hidden stage-found mobility tools (grapple-up / rising balloon) |

### Combat & progression systems

| Mechanic | First game | Does |
|---|---|---|
| Weapon block-break / hidden paths | MM1 | specific weapons destroy blocks to open passages |
| Off-screen enemy respawn | MM1 | enemies respawn when their spawn point scrolls off then back into view |

### Content structures

| Structure | First game | Does |
|---|---|---|
| Wily-fortress refight room | MM1 | teleporter hub to re-fight all 8 Robot Masters before the final boss |
| Doc Robot refight stages | MM3 | mid-game stages that re-run earlier bosses with new patterns |
| Proto Man / Break Man | MM3 | recurring rival mini-boss and story appearances |

### Level gimmicks & hazards (movement-model changers, deferred)

| Gimmick | Example source | Does |
|---|---|---|
| Slippery ice floors | MM1 Ice Man | reduced friction, momentum carry |
| Water / buoyancy | MM4 Dive Man, MM5 Wave Man | higher jump arcs, slower descent while submerged |
| Wind gusts | MM2 Air Man | horizontal push force applied to the player |
| Crushers / spike presses | MM1+ | timed instant-death hazards |

### Dev quality-of-life (non-gameplay)

| Goal | Notes |
|---|---|
| Quick-cycle weapon hotkeys | bumper / trigger; MM4+ style, not authentic to MM1-3 |
| Centralize input action names | `const StringName` autoload to remove loose input strings |

**Promoted to core this round:** enemy item drops (P3), Yoku blocks + moving/conveyor platforms (P4), weakness-damage hook (P6), weapon weakness chart (P7), password save (P8). Ice, water, wind, and crushers stay stretch because they change the movement model, which touches `MovementComponent`.

**Next:** pick a phase and I will give you the concrete node tree plus the full scripts for it.


