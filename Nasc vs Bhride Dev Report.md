# Comparative Analysis: finsceal-nasc vs. finsceal-bhride

Both projects are building the same thing: a 2D top-down action-adventure in the mold of Zelda: Link's Awakening. The player character is Nasc (a Link stand-in), movement is 8-directional with 4-cardinal sprite facing, and the game targets a pixel-art aesthetic with a 16×16 tile grid. They share the same spritesheet, the same input action names (`move_left/right/up/down`), and the same FSM-driven architecture for Nasc.

Where they diverge is in scope and design philosophy. **finsceal-nasc** is deliberately minimal — 9 files total — and prioritizes correctness and idiomatic Godot over features. **finsceal-bhride** is further along in feature scope — 29 files — and brings in a Command pattern, an equipment system, a UI, and several more FSM states. The gap creates a natural A/B test: the same game, two different architectural choices for every shared concept.

---

## Project At a Glance

|                             | finsceal-nasc              | finsceal-bhride                          |
| --------------------------- | -------------------------- | ---------------------------------------- |
| Viewport                    | 320×180                    | 400×224                                  |
| Renderer                    | GL Compatibility           | GL Compatibility                         |
| Physics interpolation       | off                        | on                                       |
| FSM states                  | Idle, Move                 | Idle, Walking, Jumping, Sword, Digging   |
| Input layer                 | direct poll in states      | Command pattern via InputHandler         |
| Equipment system            | none                       | 4-slot EquipmentManager + Item Resources |
| Camera                      | RoomCamera + CameraZone    | Camera2D child of Player (no logic)      |
| UI                          | none                       | Hearts, equipment display, pause menu    |
| Sound                       | none                       | SFX autoload                             |
| Untyped variables           | zero (enforced by warning) | several                                  |
| `class_name` on leaf states | no                         | yes (all of them)                        |

---

## Concept 1 — FSM Architecture

### nasc

`StateMachine` (`state_machine.gd`, `class_name StateMachine`) is a generic `Node` subclass. It knows nothing about Nasc. Any entity — an enemy, an NPC, a door — could use it without modification. Its three responsibilities are: wiring the `state_machine` back-reference onto every `State` child, disabling `_physics_process` until `start()` is called, and delegating `physics_update` to the current state each tick.

States are children of the `StateMachine` node. The base class (`state.gd`, `class_name State`) exposes `enter`, `exit`, and `physics_update` as virtual methods. Leaf states (no `class_name`) export whichever sibling states they need to reach: `idle.gd` exports `move_state: State`; `move.gd` exports `idle_state: State`. Wired in the Inspector. Nothing else.

### bhride

`NascFSM` (`nasc_fsm.gd`, `class_name NascFSM`) is permanently coupled to Nasc from line one. It `await owner.ready` in `_ready()`, asserts `owner is Nasc`, and stores `nasc: CharacterBody2D`. It also owns the `InputHandler` reference and calls `input_handler.get_command()` every physics frame.

States are still child nodes, but instead of exporting sibling references they emit a `finished` signal carrying a string name: `finished.emit(self, "walking")`. The FSM subscribes to every child's `finished` on startup and stores all states in `Dictionary states` keyed by the lowercased node name. Transitions are a string lookup: `states.get(new_state_name.to_lower())`.

### Winner: **nasc**

Four reasons, in order of importance.

**String keys vs. node references.** Bhride's `finished.emit(self, "walking")` is a string at the call site, a dictionary key at the receiver, and a lowercase comparison in between. A typo — `"Walkng"`, `"walk"`, `"Walking"` — fails silently: `states.get()` returns `null`, the guard `if !new_state: return` swallows it, and the FSM gets stuck in the current state with no error. Nasc's `transition_to(move_state)` is typed as `State` at both ends. It cannot be wrong at compile time, and a rename in the scene tree automatically updates the exported reference.

**Reusability.** `StateMachine` + `State` can be dropped onto any entity as-is. `NascFSM` + `NascState` cannot; they assert `owner is Nasc`. When the first enemy arrives, bhride will have to write a whole second FSM or break its coupling. Nasc's FSM works for enemies today.

**`move_and_slide()` location.** In nasc, states call `body.move_and_slide()` from within `physics_update`. Bhride centralizes this call in `NascFSM._physics_process` — one canonical location after all state logic runs. This is genuinely better than nasc's approach (see Concept 7), but it only works because the FSM is Nasc-specific. The reusability tradeoff costs this.

**Self-start guard.** Nasc's `StateMachine` starts with `_physics_process` disabled. Nothing runs until the body explicitly calls `start()` from its own `_ready()`. This is the correct GDScript pattern: children's `_ready()` runs before parents', so if the FSM self-started in `_ready()` the body would not yet be ready. Bhride sidesteps this with `await owner.ready` throughout — which works but scatters async chains across six files (`nasc_fsm.gd`, `nasc_state.gd`, and all four state subclasses each call `await super._ready()`).

---

## Concept 2 — State Transition Mechanism

### nasc

Each leaf state exports a typed reference to every state it can reach:

```gdscript
# idle.gd
@export var move_state : State
# wired: NodePath("../Move")

state_machine.transition_to(move_state)  # direct call, typed node
```

`StateMachine.transition_to(next: State)` guards against null and self-transition, then
calls `exit()`/`enter()`.

### bhride

States emit a signal with a string payload:

```gdscript
# idle_state.gd
signal finished(acting_state: NascState, new_state_name: String)
finished.emit(self, "walking")

# nasc_fsm.gd
func _transition_to_next_state(acting_state, new_state_name):
    if acting_state != current_state: return
    var new_state = states.get(new_state_name.to_lower())
    if !new_state: return
    ...
```

### Winner: **nasc**

Already covered above under FSM Architecture, but worth isolating the one genuine advantage bhride's approach has: states don't need to know about each other. Bhride's `idle_state.gd` has no reference to `walking_state.gd`. In nasc's approach, a state with many outgoing edges needs many exported vars, and the Inspector must wire all of them. For a small state graph (2–5 states) this is negligible. At 10+ states with complex transition graphs it becomes a real burden.

That said, string fragility is a worse failure mode than Inspector wiring tedium. Silent stuck-state bugs are very hard to track down. The correct direction if you want to avoid Inspector wiring is to use an enum-keyed dictionary, not a string-keyed one:

```gdscript
enum State { IDLE, WALKING, JUMPING }
state_machine.transition_to(State.WALKING)
```

Neither project does this. Nasc's node-reference approach remains the safest of the options actually implemented.

---

## Concept 3 — Input Handling

### nasc

States poll `Input` directly inside `physics_update`:

```gdscript
# idle.gd
if Input.get_vector("move_left", "move_right", "move_up", "move_down") != Vector2.ZERO:
    state_machine.transition_to(move_state)

# move.gd
var direction: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")
body.velocity = direction * SPEED
```

No separation between "what did the player press" and "what does that mean in this state".

### bhride

`InputHandler` is a separate `Node` child of Nasc. Its one method, `get_command()`, runs each physics frame and returns a `Command` object. Priority order:
1. Discrete item actions (`is_action_just_pressed` on all four slots)
2. Continuous item actions (`is_action_pressed` on all four slots)
3. Movement

If no equipment manager is assigned, it falls through to movement/idle only. The FSM calls `input_handler.get_command()`, passes the command to `current_state.handle_command()`, and separately calls `current_state.physics_update(delta)`.

### Winner: **bhride** (for its own scope)

For the two-state nasc prototype, direct polling in states is perfectly adequate. The Command pattern is overkill for Idle ↔ Move.

For bhride's feature set — four item slots, items that create their own commands, states that need to know whether to accept a command — the separation is the right call. `FeatherItem.create_command()` returns a `JumpCommand`; `ShovelItem.create_command()` returns a `DigCommand`. The FSM and states don't know what items exist. Adding a new item means writing a new `Item` subclass and `Command` subclass; no FSM code changes.

The priority order in `InputHandler` (discrete → continuous → movement) is also important and having it in one place makes it auditable. Bhride correctly separates `is_action_just_pressed` for one-shot actions from `is_action_pressed` for held ones.

The one awkward spot: `InputHandler` needs the `EquipmentManager` reference, which is set via a property setter on Nasc that forwards to `InputHandler`. This setter silently does nothing if `input_handler` isn't ready yet. It works because Game uses `await get_tree().process_frame` before setting the equipment_manager, but it's easy to break without knowing why.

---

## Concept 4 — Player Body (Nasc.gd)

### nasc

```gdscript
extends CharacterBody2D
class_name Nasc

@onready var state_machine: StateMachine = $StateMachine
@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
var last_direction: Vector2 = Vector2.DOWN

func _ready() -> void:
    state_machine.start()

static func cardinal(dir: Vector2) -> String:
    if abs(dir.x) > abs(dir.y):
        return "right" if dir.x > 0.0 else "left"
    return "down" if dir.y > 0.0 else "up"
```

Nasc's body is a thin data bus. It holds only what states need to share (`last_direction`, `sprite`), starts the FSM, and provides a static utility. States do everything else. Total: 15 lines.

### bhride

Nasc carries significantly more: `is_carrying`, `has_shield`, `jump_momentum`, `equipment_manager` (with a forwarding setter), `movement_speed`, `facing` (the current direction as a String), a constant `dirs: Dictionary` for Vector2→String lookup, a `blocks_actions()` query delegating to the FSM, `set_facing_direction()`, and `is_grounded()`. Total: 48 lines.

### Winner: **nasc**

Nasc's body is clean because it follows "body is a data bus, states are behavior". Every field on the body is there because multiple states need it. `last_direction` is read by both Idle (for `idle_<cardinal>` animation) and Move (for `walk_<cardinal>` animation and to persist direction between frames). The static `cardinal()` converts it to a String only at point of use.

Bhride's body has accumulated state that arguably belongs in states or components. `jump_momentum` is written by `JumpCommand.execute()`, read by `JumpingState.enter()`, then cleared by `JumpingState.exit()`. This works but couples three files through a shared mutable field. `movement_speed` is a constant that could live on the Move command or as a const in the state. `is_grounded()` always returns `true` (placeholder) — should be removed until the feature exists.

The `dirs` dictionary deserves special mention. It's used to convert a `Vector2` to a
direction String:

```gdscript
const dirs: Dictionary = { Vector2.DOWN: "down", Vector2.UP: "up", ... }
var facing: String = dirs[Vector2.DOWN]
```

This is fragile: the dictionary only has four exact entries, so any Vector2 not in the dict causes a runtime error. The `set_facing_direction()` guard (`is_equal_approx( input_dir.length_squared(), 1.0)`) prevents the crash by only updating facing for pure-cardinal inputs, but the underlying approach is riskier than nasc's `cardinal()` function, which handles any Vector2 by comparing axis magnitudes.

---

## Concept 5 — Facing Direction Tracking

### nasc

`last_direction: Vector2` stores the raw direction. It is only updated in Move state's
`physics_update`, and only when the player is actually pressing a direction:

```gdscript
# move.gd — diagonal resolution
if moving_h and not moving_v:
    body.last_direction = Vector2(-1.0 if Input.is_action_pressed("move_left") else 1.0, 0.0)
elif moving_v and not moving_h:
    body.last_direction = Vector2(0.0, -1.0 if Input.is_action_pressed("move_up") else 1.0)
else:
    # Diagonal: use last_direction's dominant axis to break the tie
    if abs(body.last_direction.x) >= abs(body.last_direction.y):
        body.last_direction = Vector2(...)
    else:
        body.last_direction = Vector2(...)
```

On a diagonal, the axis that was dominant last frame wins. This prevents the "moonwalk" bug (stale facing snapping on release) and removes up/down bias.

### bhride

`facing: String` on Nasc. Updated by `set_facing_direction()`:

```gdscript
func set_facing_direction() -> void:
    var input_dir = Vector2(Input.get_axis("move_left", "move_right"),
                            Input.get_axis("move_up", "move_down"))
    if input_dir != Vector2.ZERO:
        if is_equal_approx(input_dir.length_squared(), 1.0):
            facing = dirs[input_dir]
            if interaction_ray:
                interaction_ray.target_position = input_dir * 12
```

This only updates when `length_squared ≈ 1.0`, which for digital input means pure cardinals. Diagonals (length_squared ≈ 2.0 for keyboard) do not update facing. The facing String is then used directly in animation names: `nasc.animated_sprite_2d.play("walk_" + nasc.facing)`.

### Winner: **nasc**

Three advantages. First, storing direction as `Vector2` preserves numeric information for future use (hitbox placement, projectile direction, push force). Converting to String only at animation call-time is the right layer of abstraction. Bhride stores a String on the body and loses the vector.

Second, nasc's diagonal resolution is explicit and documented with a comment explaining the subtle invariant. Bhride's approach simply doesn't update facing on diagonals, which means the last facing before going diagonal sticks — that happens to produce the right result, but it's implicit behavior rather than deliberate logic.

Third, `dirs[input_dir]` is a dictionary lookup with a runtime crash failure mode. `Nasc.cardinal(dir)` is a function with `abs()` comparisons — it handles any Vector2 safely and correctly.

---

## Concept 6 — Animation Management

### nasc

Eight clips: `idle_down`, `idle_up`, `idle_left`, `idle_right`, `walk_down`, `walk_up`, `walk_left`, `walk_right`. Idle state plays the appropriate idle clip in `enter()`. Move state plays the walk clip in `physics_update` after updating `last_direction`. All clips loop. Simple.

### bhride

Forty-four clips covering: `walk`, `walk_s1` (shield 1), `walk_s2` (shield 2), `carry`, `dig`, `jump`, `slash`, `pull`, `push`, `shield1`, `shield2`, `swim`, `throw`, `underwater`, `holdup_onehand`, `holdup_twohands` — all four cardinals for directional ones.

"Idle" is not a separate set of clips — it's achieved by playing the walk animation and
calling `.pause()`:

```gdscript
# idle_state.gd
func enter() -> void:
    nasc.velocity = Vector2.ZERO
    nasc.animated_sprite_2d.play("walk_" + nasc.facing)
    nasc.animated_sprite_2d.pause()
```

States pick variants based on runtime state:

```gdscript
# walking_state.gd
func _sync_animation() -> void:
    var anim: String
    if nasc.is_carrying:
        anim = "carry_" + nasc.facing
    elif nasc.has_shield == Nasc.SHIELD_1:
        anim = "walk_s1_" + nasc.facing
    elif nasc.has_shield == Nasc.SHIELD_2:
        anim = "walk_s2_" + nasc.facing
    else:
        anim = "walk_" + nasc.facing
    if nasc.animated_sprite_2d.animation != anim:
        nasc.animated_sprite_2d.play(anim)
```

The guard `if animation != anim` prevents restarting the same animation on every frame.

### Winner: **nasc for simplicity, bhride for completeness**

The "idle = walk paused" approach in bhride is actually clever — it matches what the original Game Boy game did and saves maintaining separate idle clip sets for every variant (you'd need `idle_s1_down`, `idle_carry_down`, etc. otherwise). The paused-walk frame shows the correct pose without extra art.

The `_sync_animation()` guard is good practice. Nasc's states play the animation on every state entry but don't re-guard on every frame in Move — that's acceptable since the animation only changes when `last_direction` changes and a new state entry implies a new animation. For performance-sensitive games the guard becomes important; bhride has it right.

Bhride's animation library is dramatically richer, which shows more work has gone into the art pipeline. The approach of string-concatenating the cardinal suffix onto a prefix is identical in both projects and is the right pattern.

---

## Concept 7 — Where `move_and_slide()` Lives

### nasc

Both states call `body.move_and_slide()` themselves, inside their `physics_update`:

```gdscript
# idle.gd
func physics_update(_delta: float) -> void:
    var body: Nasc = owner as Nasc
    body.velocity = Vector2.ZERO
    body.move_and_slide()
    ...

# move.gd
func physics_update(_delta: float) -> void:
    ...
    body.velocity = direction * SPEED
    body.move_and_slide()
```

Every state is responsible for calling it.

### bhride

`NascFSM._physics_process` calls `nasc.move_and_slide()` once, after all state logic:

```gdscript
func _physics_process(delta: float) -> void:
    var command = input_handler.get_command()
    current_state.handle_command(command)
    current_state.physics_update(delta)
    nasc.move_and_slide()  # one canonical call
```

States set velocity; the FSM applies it.

### Winner: **bhride**

One call site is better than N call sites. With nasc's approach, every new state must remember to call `move_and_slide()`. Forgetting it in a blocking state (sword, dig, jump) causes the character to float or ignore momentum — a subtle bug. Bhride's centralized call means a new state that only needs to set velocity and nothing else still gets physics applied automatically.

The tradeoff is that the centralized call is only possible because `NascFSM` is Nasc-specific. A generic `StateMachine` can't call `move_and_slide()` on its owner without knowing the owner is a `CharacterBody2D`. This is one area where bhride's tighter coupling pays off. If nasc moved `move_and_slide()` to the body's `_physics_process`, it would achieve the same benefit while keeping the FSM generic.

---

## Concept 8 — Scene Hierarchy

### nasc (`nasc.tscn`)

```
Nasc (CharacterBody2D)
├── AnimatedSprite2D        ← offset (0, -8)
├── CollisionShape2D        ← offset (0, -2), horizontal CapsuleShape2D
└── StateMachine (Node)
    ├── Idle (Node)         ← exports: move_state → ../Move
    └── Move (Node)         ← exports: idle_state → ../Idle
```

### bhride (`nasc.tscn`)

```
Nasc (CharacterBody2D)
├── InputHandler (Node)
├── FSM (Node)
│   ├── Idle (Node)
│   ├── Walking (Node)
│   ├── Jumping (Node)
│   ├── Digging (Node)
│   └── Sword (Node)
├── CollisionShape2D        ← offset (0, -0.5), RectangleShape2D(10×7)
├── AnimatedSprite2D        ← offset (0, -4)
└── InteractionRay (RayCast2D)
```

### bhride (`game.tscn`)

```
Game (Node)
├── EquipmentManager (Node)
├── World (Node2D)
│   ├── Overworld (TileMapLayer)
│   └── Player (Nasc)
│       └── Camera2D          ← child of Player, no scripted tracking
└── CanvasLayer (process_mode = ALWAYS)
    └── UI
```

### Winner: **nasc for camera placement**

Bhride's Nasc scene is richer in features, appropriately so. `InteractionRay` (a `RayCast2D`) pointing in the facing direction is a smart addition for examining objects — nasc doesn't have this yet.

The critical mistake in bhride is in `game.tscn`: **Camera2D is a child of Player**. This makes the camera follow Nasc automatically but eliminates the ability to do anything interesting with the camera later: cutscenes, panning to reveal an enemy, lag zones, screen-scroll-to-edge behaviors, sub-region limit overrides. The camera is hardwired to Nasc's position with no controllable offset or limits.

Nasc's CLAUDE.md explicitly locks this: "Camera is a Camera2D sibling of Nasc in the world scene (never a child of Nasc)". The right pattern is a sibling camera that tracks the target in `_physics_process`. Bhride will have to restructure the scene hierarchy when it needs any camera behavior beyond "follow player".

---

## Concept 9 — Collision Shape

### nasc

`CapsuleShape2D` (radius 2.0, height 16.0), rotated 90° so it lies horizontal, at `position (0, -2)`. This is the "feet footprint" — a very narrow horizontal oval that sits just below the sprite's center, selling the 3/4 overhead perspective (the character's head overlaps walls above; their feet stop movement).

### bhride

`RectangleShape2D` (size 10×7), at `position (0, -0.5)`. Also a small, flat shape at the feet.

### Winner: **nasc**

Both are doing the correct thing (small footprint hitbox, not full-sprite-bounds), which matters. A rotated `CapsuleShape2D` is slightly better for sliding along walls — the curved ends reduce corner snagging. A rectangle's flat edges catch on adjacent tile corners in ways a capsule avoids. For a top-down game with lots of wall hugging, capsule wins.

---

## Concept 10 — FSM Start Timing / `_ready()` Contract

### nasc

`StateMachine._ready()`:
1. Disables `_physics_process`
2. Iterates children, sets `child.state_machine = self` on every `State`
3. Checks `initial_state != null`, emits `push_error` if null
4. **Does not start.** Physics is off, no state is active.

`Nasc._ready()`:
1. Calls `state_machine.start()`
2. `start()` sets `current_state`, calls `current_state.enter()`, enables physics.

States can safely access `owner as Nasc` in `enter()` because by the time `start()` is called, the entire `Nasc` node is ready.

### bhride

`NascFSM._ready()`:
```gdscript
await owner.ready
nasc = owner as Nasc
assert(nasc != null, ...)
for child_state in get_children():
    ...
    child_state.finished.connect(_transition_to_next_state)
var starting_state = initial_state if initial_state != null else get_child(0)
if starting_state and starting_state is NascState:
    starting_state.enter()
    current_state = starting_state
```

`NascState._ready()`:
```gdscript
await owner.ready
nasc = owner as Nasc
```

`NascIdleState._ready()`:
```gdscript
await super._ready()
```
(four state files repeat this)

### Winner: **nasc**

`await owner.ready` scattered across six files is noise. The pattern works but it means any state's `enter()` that runs during initialization must be careful not to assume the `await` has resolved. It also means six separate deferred continuations are scheduled and resumed, making execution order hard to trace.

Nasc's approach consolidates initialization into one point: the body's `_ready()`. When `start()` runs, the whole tree is provably ready. The `push_error` guard for missing `initial_state` is a nice touch — it surfaces misconfiguration at startup rather than letting it NRE later.

---

## Concept 11 — Code Quality and GDScript Typing

### nasc

- Strong typing on every variable, parameter, and return value — enforced by `gdscript/warnings/untyped_declaration=2` in project.godot (warnings become errors)
- `##` documentation comments on all scripts and public functions
- `class_name` only on infrastructure (`Nasc`, `State`, `StateMachine`) — leaf states have no `class_name`
- No `$` node-path literals in logic — all `@onready` vars
- `const SPEED: float = 64.0` in Move state — correct use of const
- Box-drawing comment frames for structural sections (`# ─── Zone wiring ───`)
- Zero debug prints

### bhride

- Typing is inconsistent. Examples of untyped declarations:
  - `NascFSM`: `var starting_state = initial_state if ...` (no type)
  - `NascFSM`: `for child_state in get_children():` (untyped loop var)
  - `InputHandler`: `var item = equipment_manager.get_equipped_item(slot_name)` (no type)
  - `EquipmentManager`: `var states: Dictionary = {}` (no type params; should be `Dictionary[String, NascState]`)
  - `EquipmentManager`: `for slot_name in [...]` (loop var untyped)
- `#` single-line comments, not `##` doc comments — editor Help won't generate from them
- `class_name` on every class including all leaf states: `NascIdleState`, `NascWalkingState`, `NascJumpingState`, `NascSwordState`, `NascDiggingState`. This pollutes the global namespace — every time Godot parses the project, these class names are registered globally. They cannot conflict with other files' class names.
- Debug `print()` statements left in `game.gd` (`print("Pulling down the pause menu!")`, `print("Rolling up the pause menu!")`)
- `motion_mode = 1` on bhride's Nasc (Floating mode). This may be intentional — Floating mode doesn't apply gravity — but it's undocumented and unexpected for a top-down 2D character

### Winner: **nasc** (by a significant margin)

Nasc enforces typing at the build level. Bhride's inconsistent typing creates the exact class of bugs that type checking prevents: passing the wrong thing to a function, indexing a dictionary with a key of the wrong shape, iterating over `Variant`s. The untyped `starting_state` in `NascFSM._ready()` is a particularly bad example — if `get_child(0)` returns a non-`NascState` node (say, a debug helper added as the first child), the code proceeds without catching it.

`class_name` on leaf states is a real quality issue. Each registered class name takes memory and parse time, but more importantly it's a scope decision: you're saying "NascIdleState is a type the entire project needs to know about." Nothing outside nasc's FSM ever needs to refer to `NascIdleState` by name. Keeping leaf states anonymous (no `class_name`) means they can be freely renamed, duplicated, or removed without affecting anything else. Nasc's project rules explicitly lock this.

---

## Concept 12 — Equipment and Item System (bhride only)

Bhride implements a Zelda-style 4-slot equipment system that nasc has not yet built.

`Item` extends `Resource` — the correct Godot primitive for data objects that can be saved, inspected, and serialized. The base class defines `create_command(nasc) -> Command` and `can_use(nasc) -> bool`. Concrete items override these:

```gdscript
# feather_item.gd
func create_command(nasc: Nasc) -> Command:
    return JumpCommand.new(nasc.velocity)

func can_use(nasc: Nasc) -> bool:
    return nasc.is_grounded()
```

`EquipmentManager` is a `Node` that holds four named slots and an inventory array. It emits `slot_changed` when a slot is modified. The UI subscribes to this signal and redraws. The `InputHandler` queries the manager each frame to know what commands to create.

This is a well-structured data pipeline: item press → InputHandler asks manager → manager returns Item → item creates Command → FSM passes Command to current state → state decides whether to accept and transition.

The `is_continuous: bool` flag on `Item` and `Command` is important: it separates "hold sword button" from "tap feather button". `InputHandler` checks `just_pressed` for discrete items and `pressed` for continuous ones. The sword uses `is_continuous = true` because holding the button after the slash animation ends triggers a spin attack.

**What works:** The Command pattern fully decouples item types from the FSM. A new item means a new `Item` subclass and a new `Command` subclass. The FSM and states need no modification.

**What doesn't work yet:** `EquipmentManager._ready()` hardcodes all items:

```gdscript
inventory.append(SwordItem.new())
inventory.append(ShovelItem.new())
inventory.append(FeatherItem.new())
equip_item("slot_south", inventory[0])
```

This is explicitly noted with a comment. The correct long-term approach is a saved `Resource` or `ConfigFile` that describes the player's inventory. But as a prototype harness it's fine.

**No equivalent in nasc.** This concept cannot be compared.

---

## Concept 13 — Camera System (nasc only)

Nasc implements the full camera architecture described in its project rules. Bhride has a Camera2D node parented to Nasc with no scripted logic.

### `RoomCamera extends Camera2D`

Tracks target in physics time (matching `move_and_slide`'s timestep), which eliminates the diagonal jitter that appears when a camera updates in `_process` (60hz) but the character moves in `_physics_process` (physics ticks, default 60hz but not guaranteed to align). Setting `global_position = target.global_position` directly (no smoothing) gives the crisp, instantaneous camera feel of classic 16-bit Zelda.

Camera limits are set via `limit_left/top/right/bottom` on `Camera2D`, computed from whichever source is active.

### `CameraZone extends Area2D`

Each zone is an `Area2D` with a `CollisionShape2D` (`RectangleShape2D`). Zones add themselves to the group `"camera_zones"` in `_enter_tree`. `RoomCamera` connects to all zones' `body_entered`/`body_exited` signals at startup. When Nasc enters a zone, that zone's rect becomes the camera limits. When multiple zones overlap (at region borders), the smallest-area zone wins — tighter corridors always override open areas. When no zone is active, the camera falls back to the tilemap's used-rect.

This is clean Godot: `Area2D` + signals for detection, groups for loose coupling between zones and camera, tilemap as fallback data source. The "smallest area wins" rule is a simple, robust policy for an irregular overworld shape.

**No equivalent in bhride.** This concept cannot be compared. Bhride will need something like this when it implements camera limits.

---

## Concept 14 — Pause Menu and UI (bhride only)

Bhride's `UI` (extends `Control`) implements:

- **Heart display:** `hearts: float` property with a setter that iterates the heart grid and assigns `HEART_FULL`, `HEART_PART`, or `HEART_EMPTY` textures reactively. A setter-based reactive property is the right Godot pattern for this — no polling.

- **Equipment display:** `@onready` refs to four `TextureRect` nodes for each button slot. `_refresh_equipment_display()` fetches each slot from `EquipmentManager` and sets the texture. Called when `equipment_manager` is assigned (via setter) and on `slot_changed` signal. Clean.

- **Pause menu:** The UI panel slides down from off-screen on "start" press:

```gdscript
func enter_pause_menu() -> void:
    get_tree().paused = not get_tree().paused  # pause first
    var tween = create_tween()
    SFX.play(LA_PAUSE_MENU_OPEN)
    tween.tween_property(self, "global_position", OPENED_POSITION, 0.5)
         .set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_IN_OUT)

func exit_pause_menu() -> void:
    var tween = create_tween()
    SFX.play(LA_PAUSE_MENU_CLOSE)
    tween.tween_property(self, "global_position", CLOSED_POSITION, 0.2)
         .set_trans(Tween.TRANS_EXPO).set_ease(Tween.EASE_OUT)
    await tween.finished
    get_tree().paused = not get_tree().paused  # unpause after animation
```

Open: QUART ease (accelerates, feels deliberate). Close: EXPO ease + faster (snappy rollup). Unpausing happens after the animation, not before — so the game doesn't resume while the menu is still visible. This sequencing is correct.

One issue: `enter_pause_menu()` toggles `get_tree().paused` but pauses first. If the game is already paused for another reason (shouldn't happen yet, but future-proofing matters), this inverts the state. Using `get_tree().paused = true` and `= false` explicitly would be safer than toggling.

`UIInventorySelector` is a menu cursor that can `move_to()` a target position with a tween, or `snap_to()` without. The `AnimationPlayer`-driven pulse effect (scale 1.0 → 1.1 → 1.0, modulate fading) is a good use of `AnimationPlayer` for visual polish.

**No equivalent in nasc.** This concept cannot be compared.

---

## Concept 15 — Sound Effects Autoload (bhride only)

```gdscript
# sound_effects_player.gd — autoloaded as SFX
extends Node

func play(stream: AudioStream) -> void:
    var audio: AudioStreamPlayer = AudioStreamPlayer.new()
    audio.stream = stream
    audio.finished.connect(audio.queue_free)
    add_child(audio)
    audio.play()
```

Fire-and-forget: create a new `AudioStreamPlayer`, connect its `finished` signal to `queue_free()`, play it. No reference retained. Overlapping sounds work correctly because each call creates an independent player. The node cleans itself up.

This is the idiomatic Godot pattern for one-shot audio and it's done correctly. Preloaded streams (`const LA_PAUSE_MENU_OPEN = preload(...)`) avoid runtime disk reads.

**No equivalent in nasc.** This concept cannot be compared.

---

## Concept 16 — Viewport and Project Configuration

### nasc

- Viewport: 320×180 (20×11.25 tiles at 16px). Integer-scales to 1080p ×6, 1440p ×8, 4K ×12.
- `snap_2d_transforms_to_pixel = true` — prevents sub-pixel drift on sprite movement.
- `gdscript/warnings/untyped_declaration=2` — untyped vars are errors.
- No input configured for gamepad.

### bhride

- Viewport: 400×224 (25×14 tiles). Approximately a Game Boy Advance aspect ratio.
- Physics interpolation enabled (`common/physics_interpolation=true`) — smooths rendering between physics ticks when display FPS > physics FPS.
- Full input map including four face buttons, bumpers, triggers, select, start, and both sticks mapped to gamepad buttons — ready for actual controller use.
- Layer names defined: Player, Enemies, Environment, Items, Overworld.

### Winner: **nasc for viewport purity, bhride for input completeness**

320×180 is a more principled choice — it integer-scales cleanly to every common resolution without letterboxing. 400×224 doesn't scale as cleanly (800×448 at 2× fits in a window, but 1200×672 at 3× doesn't fit in a 1080p screen).

However, bhride's full gamepad input map and physics layer names show more completeness in project setup. Physics interpolation is a good call for a game with a physics-driven character — it makes movement visually smoother on high-refresh displays.

---

## Summary: Which Project Made Better Decisions?

| Concept | Winner | Margin |
|---|---|---|
| FSM Architecture | **nasc** | Significant |
| State Transition Mechanism | **nasc** | Significant |
| Input Handling | **bhride** (scoped) | Moderate |
| Player Body Design | **nasc** | Moderate |
| Facing Direction Tracking | **nasc** | Moderate |
| Animation Approach | **Tie** | — |
| `move_and_slide()` Placement | **bhride** | Moderate |
| Scene Hierarchy | **nasc** (camera) | Significant |
| Collision Shape | **nasc** | Minor |
| FSM Start Timing | **nasc** | Moderate |
| Code Quality / Typing | **nasc** | Significant |
| `class_name` Policy | **nasc** | Moderate |

**finsceal-nasc** wins the majority of shared architectural decisions. Its FSM is generic and reusable, its transitions are type-safe, its typing is consistent and enforced, its camera placement is correct, and its player body is lean. These are structural decisions that become expensive to undo as a project grows.

**finsceal-bhride** is ahead in feature scope and gets two genuine wins: centralizing `move_and_slide()` in the FSM, and separating input from state logic via the Command pattern. Both of these are ideas worth pulling into nasc. Its equipment system, UI, audio, and animation library also represent real progress that nasc has yet to build.

The highest-priority fixes for bhride — if it continues as a project — are:

1. **Camera2D must move out of Player's hierarchy.** It will need to become a sibling with scripted tracking before any camera logic (limits, pan, cutscenes) is possible.

2. **Replace string-based state transitions with a type-safe alternative.** Node references (nasc's approach) or an enum-keyed dictionary. String keys with silent fallback are a bug waiting to happen.

3. **Enforce untyped-declaration warnings.** The inconsistent typing will cause runtime errors that strong typing would catch at parse time.

4. **Remove `class_name` from all leaf state files.** `NascIdleState` etc. should be anonymous. Nothing outside the FSM references them by name.

The highest-priority lessons nasc should adopt from bhride:

1. **Call `move_and_slide()` once, in the FSM or in the body's `_physics_process`.** Not in each state. States should set velocity; the body or FSM applies it.

2. **Use the Command pattern when items arrive.** The item-creates-command pipeline is clean and extensible. Don't wire item behavior directly into state `physics_update`.

3. **`InteractionRay` in the Nasc scene.** A `RayCast2D` pointing in the facing direction is the right way to implement object interaction (picking up pots, reading signs, talking to NPCs). Bhride has this; nasc doesn't yet.
