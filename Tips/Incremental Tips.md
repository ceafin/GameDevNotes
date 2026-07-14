# 1) Build features as _capabilities_, not branches

Treat every new mechanic as a plug-in module with a tiny contract, not a new `if/else` in Player.

**Interface (duck-typed)**

```gdscript
# res://interfaces/ability.gd
class_name IAbility
extends Resource

func can_activate(owner: Node) -> bool: return false
func activate(owner: Node) -> void: pass
func tick(owner: Node, dt: float) -> void: pass
func cancel(owner: Node) -> void: pass
```

**Data-driven ability resource**

```gdscript
# res://abilities/dash.gd
class_name DashAbility
extends IAbility

@export var speed := 350.0
@export var duration := 0.18

var t := 0.0

func can_activate(owner): return owner.is_on_floor() and t <= 0.0

func activate(owner):
	t = duration
	owner.velocity = owner.facing_dir * speed

func tick(owner, dt):
	if t > 0.0:
		t -= dt
		if t <= 0.0: cancel(owner)

func cancel(owner): owner.velocity = Vector2.ZERO
```

**Ability runner component**

```gdscript
# res://components/ability_runner.gd
class_name AbilityRunner
extends Node

@export var abilities: Array[IAbility] = [] var active: Array[IAbility] = []

func request(name: String, owner: Node) -> void:
	for a in abilities:
		if a.resource_path.get_file().get_basename() == name and a.can_activate(owner):
			a.activate(owner)
			active.append(a)

func _physics_process(dt):
	for a in active:
		a.tick(owner, dt)
	active = active.filter(func(a): return a.t > 0.0 if "t" in a else true)
```

Player just has an `AbilityRunner`. New mechanics = new `Resource` files, no Player rewrite.

# 2) Composition-first scenes

Prefer “lego” Nodes over inheritance. Typical player:

```bash
Player (CharacterBody2D)
  ├─ AbilityRunner
  ├─ HealthComponent
  ├─ Hurtbox
  ├─ Hitbox
  ├─ StateMachine   # optional (see §3)
  └─ Sprite/Anim
```

Each component owns exactly one concern. No component reaches into siblings directly; they talk via signals (next).

# 3) A tiny signal bus (decouple everything)
Create an autoloaded `SignalBus` and emit everything interesting.

```gdscript
# res://autoload/signal_bus.gd
extends Node

signal damage_applied(source, target, amount)
signal ability_used(user, ability_name)
signal state_changed(actor, from, to)
```

**Why**: Mechanics observe events they care about without hard references. Add/remove systems without touching emitters.
# 4) States as hot-swappable scripts
Use a script-only, node-light FSM. States don’t know the player; they get a typed handle.

```gdscript
# res://state/state.gd
class_name State
extends Resource

var sm
var actor

func enter(): pass
func exit(): pass
func physics(dt): pass

# res://state/walk.gd
class_name WalkState
extends State

@export var speed := 140.0

func physics(dt):
	actor.velocity.x = actor.input_axis * speed
	if actor.wants_jump(): sm.change("JumpState")
```

```gdscript
# res://components/state_machine.gd
class_name StateMachine
extends Node

@export var states: Dictionary = {}  # {"IdleState": preload(...).new(), ...}
var current: State

func setup(actor: Node):
	for s in states.values():
		s.sm = self
		s.actor = actor
	change("IdleState")

func change(name: String):
	if current: current.exit()
	current = states[name]
	current.enter()

func _physics_process(dt): if current: current.physics(dt)
```

States are `Resource`s → hot-reloadable and data-driven. New movement style? Add a state, don’t edit old ones.
# 5) Ports & Adapters (seams against Godot API churn)
Wrap external things (Input, RNG, Time, Save) behind thin ports.

```gdscript
# res://ports/input_port.gd
class_name InputPort
extends Node

func axis() -> float: return Input.get_action_strength("ui_right") - Input.get_action_strength("ui_left")
func pressed(action: String) -> bool: return Input.is_action_just_pressed(action)
```

Player depends on `InputPort` (exported NodePath). Tomorrow you swap to replay, AI, or network input by plugging a different adapter.
# 6) _Feature Arena_ workflow (kill rewrites early)
Before the mechanic touches your main game, build a 1-screen scene containing only:
- A floor, a dummy player prefab, one enemy prefab, a camera.
- A HUD readout for relevant variables.
- A record/replay button (serialize input) to reproduce bugs.

Keep these under `/lab/<feature_name>/*`. When the arena behaves, only then wire it into the real levels.
# 7) Three rings of code (stability zones)
- **Core (rarely changes):** movement, collision, health, save/load, signal bus, ports, serialization.
- **Extension (often changes):** abilities, weapons, enemy behaviors, loot tables (Resources).
- **Glue (throwaway):** level scripts, arena harnesses, debug UI.

You deliberately keep mechanics in the Extension ring so “new idea” ≠ “touch Core.”
# 8) Data > logic (Resources & JSON)
Put tunables in `Resource` assets:
- `EnemyConfig.tres`: hp, speed, contact_damage, loot table id.
- `WeaponConfig.tres`: rate, spread, projectile scene, stamina cost.
- `DropTable.tres`: array of `{scene, weight}`.

Your logic reads configs; swapping behavior = swapping data, not code.
# 9) A tiny “Damageable” contract (stop type spaghetti)

```gdscript
# res://interfaces/damageable.gd
class_name IDamageable
extends Resource
func apply_damage(amount: float, source := null) -> void: pass
```

Any node with `apply_damage()` is “damageable.” Hitboxes do:

```gdscript
if "apply_damage" in other:
	other.apply_damage(damage, self)
	SignalBus.emit_signal("damage_applied", self, other, damage)
```

Now anything can be a target (crates, bosses, shields) without inheritance chains.
# 10) Definition of Done (guards against “almost works”)
For each new mechanic/feature:
- Has a feature arena with a passing replay.
- Has at least one automated scene test (see below).
- Emits at least one useful signal to the bus.
- Tunables live in a Resource, not hardcoded.
- Docs: a 10-line README in `/docs/mechanics/<mechanic>.md` explaining inputs, signals, tunables.

# 11) Minimal automated test harness (Godot 4.x)
You don’t need a whole QA rig; a few headless checks save rewrites.

```gdscript
# res://tests/test_dash.gd
extends SceneTree

func _initialize():
	var scene = preload("res://lab/dash_arena.tscn").instantiate()
	root.add_child(scene)
	await get_tree().process_frame
	var p = scene.get_node("Player")
	# Simulate input port
	p.input.axis_override = 1.0
	p.ability_runner.request("dash", p)
	await get_tree().create_timer(0.2).timeout
	assert(p.velocity.length() < 1.0)  # dash stopped
	quit()
```

Run headless in CI or locally. It’s crude, but catches regressions.
# 12) Versioned prefab contracts (future-proof enemies)
When you know enemies will evolve, freeze a minimal contract:
- Must have `HealthComponent` with `died` signal.
- Must have `Hurtbox` Area2D with group `"hurtbox"`.
- Must implement optional `on_player_spotted(player)`.

Export a `PackedScene` where spawners only rely on this contract. Future enemies swap in without changing spawners.
# 13) Branching mechanics without branching code (selectors)
Use selectors that choose one of many strategies based on data/state.

```gdscript
# res://ai/target_selector.gd
class_name TargetSelector
extends Resource

@export_enum("Closest","LowestHP","Player") var mode := 0

func pick(src: Node, candidates: Array[Node]) -> Node:
	match mode:
		0: return candidates.min_by(func(n): return n.global_position.distance_to(src.global_position))
		1: return candidates.min_by(func(n): return n.health)
		_: return src.get_tree().get_first_node_in_group("player")
```

Changing “targeting logic” becomes a data change.

# 14) Tech debt budget (so scope doesn’t explode)
Keep a rolling TODO inside each component file:

```gdscript
# TECHDEBT: 
# - Replace manual cooldown with Timer node (low) 
# - Emit 'ability_used' with stamina cost (med) 
# - Move knockback to separate component (high)
```

Limit yourself to, say, 3 open items per component. If you hit 3, you must resolve one before adding another. This prevents silent rot.

# 15) Folder skeleton that scales

```gdscript
res://
	autoload/
	interfaces/
	ports/           # InputPort, TimePort, SavePort
	components/      # HealthComponent, AbilityRunner, StateMachine, Hitbox, Hurtbox
	abilities/       # *.tres/*.gd ability resources
	ai/              # selectors, behaviors
	data/            # DropTables, EnemyConfig, WeaponConfig
	entities/
		player/
		enemies/
		props/
		lab/             # feature arenas
	tests/
	docs/
```

---
# 0) The tiny mental model (5 lines to remember)
When you think “new feature,” think these five nouns:

**Thing → Interface → Runner → Arena → Signal**

- **Thing**: the behavior (dash, double jump, parry…)
- **Interface**: the minimum functions it must expose
- **Runner**: a small component on your actor that owns a list of “things”
- **Arena**: a 1-screen test scene where you try the thing in isolation
- **Signal**: an event you emit so other systems can react without tight coupling

You’ll repeat this loop forever.

---
# 1) 90-minute bootstrap from blank project (click-by-click)

### A. Create folders (2 min)

```gdscript
res://
	autoload/
	interfaces/
	components/
	abilities/
	entities/player/
	lab/
```

### B. Add a SignalBus autoload (3 min)
1. Create **autoload/signal_bus.gd**

```gdscript
extends Node
signal ability_used(user, ability_name)
```

2. Project Settings → Autoload → Add `signal_bus.gd` as **SignalBus** (Singleton).

### C. Make an Ability interface (3 min)

**interfaces/ability.gd**

```gdscript
class_name IAbility
extends Resource

func name() -> String: return "Ability"
func can_activate(owner: Node) -> bool: return true
func activate(owner: Node) -> void: pass
func tick(owner: Node, dt: float) -> void: pass
func is_active() -> bool: return false
func cancel(owner: Node) -> void: pass
```

### D. Make the AbilityRunner (5 min)

**components/ability_runner.gd**

```gdscript
class_name AbilityRunner
extends Node

@export var abilities: Array[IAbility] = []
var _active: Array[IAbility] = []

func request(ability_name: String, owner: Node) -> void:
	for a in abilities:
		if a.name() == ability_name and a.can_activate(owner):
			a.activate(owner)
			_active.append(a)
			SignalBus.emit_signal("ability_used", owner, ability_name)

func _physics_process(dt: float) -> void:
	if owner == null: return
	for a in _active:
		a.tick(owner, dt)
	_active = _active.filter(func(a): return a.is_active())

```

> You just created the seam: new mechanics = new `Resource` files. The runner never changes.
### E. Minimal Player (10 min)
1. New scene: **CharacterBody2D** → name it `Player`.
2. Add children:
    - `AbilityRunner` (Node) → attach **components/ability_runner.gd**
    - `Sprite2D` (any placeholder)
    - `CollisionShape2D` (Box)
3. Attach **entities/player/player.gd**:

```gdscript
extends CharacterBody2D

@export var speed := 140.0
@onready var abilities := $AbilityRunner

var _input_dir := 0.0
var facing := Vector2.RIGHT

func _ready():
	set_physics_process(true)

func _physics_process(dt):
	_input_dir = Input.get_action_strength("ui_right") - Input.get_action_strength("ui_left")
	velocity.x = _input_dir * speed
	if _input_dir != 0: facing = Vector2.RIGHT if _input_dir > 0 else Vector2.LEFT
	move_and_slide()
	
	if Input.is_action_just_pressed("ui_accept"):
		abilities.request("Dash", self)
```

4. Project Settings → Input Map:
    - `ui_left`, `ui_right` (arrow keys default)
    - `ui_accept` (Space/Enter)

### F. First ability: Dash (10 min)

**abilities/dash.gd**

```gdscript
class_name DashAbility
extends IAbility

@export var speed := 360.0
@export var duration := 0.18
var _t := 0.0

func name() -> String: return "Dash"
func can_activate(owner) -> bool: return _t <= 0.0
func activate(owner):
	_t = duration
	owner.velocity = owner.facing * speed

func tick(owner, dt):
	if _t > 0.0:
		_t -= dt
		if _t <= 0.0:
			cancel(owner)

func is_active() -> bool: return _t > 0.0
func cancel(owner): owner.velocity = Vector2.ZERO
```

In the editor: select Player → AbilityRunner → add element to **abilities** → pick `DashAbility` (create new resource).
### G. Build your first “arena” (10 min)
1. New scene: **Node2D** → name `lab/dash_arena.tscn`.
2. Add `TileMap` (or a `StaticBody2D+CollisionShape2D`) as floor.
3. Instance `Player.tscn`.
4. Add a `Camera2D` current=true.

Run _this_ arena scene (not the whole game). Press Space → player dashes. You have a sandpit now.
### H. Prove composability: add a second ability without editing Player (10 min)

**abilities/double_jump.gd**

```gdscript
class_name DoubleJumpAbility
extends IAbility
@export var impulse := -280.0
@export var max_jumps := 1
var _jumps_left := 0

func name() -> String:
return "DoubleJump"

func can_activate(owner) -> bool:
	if owner.is_on_floor(): _jumps_left = max_jumps
	return not owner.is_on_floor() and _jumps_left > 0

func activate(owner):
	_jumps_left -= 1
	owner.velocity.y = impulse

func tick(owner, dt): pass
func is_active() -> bool: return false

```

- Add it to AbilityRunner’s `abilities`.
- Map another input (e.g., `ui_select`) and call `abilities.request("DoubleJump", self)` on press, **or** reuse `ui_accept` temporarily.
- Run the _arena_ again. Notice: you didn’t touch Player logic or Dash.
That’s the core loop. You can now add abilities forever.

---
# 2) “When do I use what?” (cheat sheet)
- **Ability (Resource + Runner)**  
    Use when behavior is triggered and can be active/inactive (dash, parry, cloak, aim-mode, charge-shot).  
    ✅ Plug-and-play per actor, tunable via exported vars, easy to test in arenas.
- **State (Resource + StateMachine component)**  
    Use when _exactly one_ mode should own movement/inputs at a time (Idle/Walk/Jump/Climb/Ladder/Swim).  
    ✅ Prevents spaghetti if/else; transitions explicit; per-state code stays tiny.
- **Component (Node with one job)**  
    Use for cross-cutting systems (Health, Hitbox/Hurtbox, Stamina, Inventory).  
    ✅ Reusable across Player, Enemies, Props.
- **SignalBus (autoload)**  
    Use whenever something interesting happens that _others might care about later_.  
    ✅ Decouple today; future UI/FX/analytics listen without refactors.
- **Arena**  
    Use for any new mechanic or tricky bug.  
    ✅ Short feedback loop, safe to experiment, record/replay possible later.

Quick rule:  
If it’s **triggered** → Ability.  
If it’s **always on but mutually exclusive** → State.  
If it’s **a property or system** → Component.  
If others might **react** → Signal.  
If you’re **unsure** → build an Arena first.

---
# 3) Add-a-mechanic exercise (30–45 min)
Goal: add a **Stamina** system that gates Dash & DoubleJump **without editing the abilities’ code**.
1. Make a **components/stamina.gd**

```gdscript
class_name StaminaComponent
extends Node

@export var max_stamina := 100.0
@export var regen_rate := 25.0
var value := 0.0

func _ready(): value = max_stamina
func _physics_process(dt): value = min(max_stamina, value + regen_rate * dt)
func try_spend(cost: float) -> bool:
	if value >= cost:
		value -= cost
		return true
	return false
```

2. Add it to `Player` as child **Stamina**.
3. Make a **gate** adapter that sits between Player and AbilityRunner, so Player stays dumb: **components/ability_gate.gd**

```gdscript
class_name AbilityGate
extends Node
@export var runner_path : NodePath
@export var stamina_path : NodePath
@export var costs := { "Dash": 20.0, "DoubleJump": 15.0 }

@onready var runner : AbilityRunner = get_node(runner_path)
@onready var stamina : StaminaComponent = get_node(stamina_path)

func request(name: String, owner: Node) -> void:
	var cost = costs.get(name, 0.0)
	if cost <= 0.0 or stamina.try_spend(cost):
		runner.request(name, owner)
```

4. Wire it:
- Add `AbilityGate` to Player, set `runner_path` → `AbilityRunner`, `stamina_path` → `Stamina`.
- In `player.gd` replace `abilities.request("Dash", self)` with:

```gdscript
$AbilityGate.request("Dash", self)
```

Done. You gated abilities without editing the abilities. That’s composability in action.

---
# 4) “I still freeze at a blank editor” — a tiny routine
Use this 6-step ritual every time you add a feature:
1. **Say it in one sentence**: “Player performs a short burst forward with a cooldown.”
2. **Pick the shape**: Ability, State, Component? (Dash → Ability)
3. **Define the 3 methods**: `can_activate`, `activate`, `tick` (+ any tunables)
4. **Create an arena**: floor, player prefab, camera.
5. **Add 1 debug readout**: Label that shows key numbers (stamina, timers).
6. **Ship the minimum signal**: `SignalBus.ability_used(user, name)`.
If you cannot do step 1 in one sentence, the feature is too big—split it.

---
# 5) Micro “Definition of Done” for any mechanic
- It runs in its own **lab scene**.
- Tunables are **export vars** on a Resource or Component.
- It emits at least one **bus signal** (or you decided it doesn’t need one).
- You added a **note** in `docs/mechanics/<name>.md` with inputs & tunables (5–10 lines).
- You didn’t change Player internals (only plugged things together).

---
# 6) Your next 2 hours (actionable checklist)
-  Make the folder skeleton & SignalBus.
-  Build `Player` + `AbilityRunner`.
-  Implement `DashAbility` + `DoubleJumpAbility`.
-  Create `lab/dash_arena.tscn` and confirm both work.
-  Add `StaminaComponent` + `AbilityGate` and confirm gating works.
-  Add a `Label` that shows stamina so you can see feedback.