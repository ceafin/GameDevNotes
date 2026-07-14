I'll create two Node-based Finite State Machines (FSMs) for a player character in Godot 4.5+. These FSMs will handle locomotion and 
actions, with proper interaction between them.

```gdscript
# LocomotionFSM.gd
extends Node

export var speed = 5.0
export var jump_force = 10.0
export var gravity = 10.0

var current_state = "Idle"
var is_paused = false

func _ready():
    # Initialize with Idle state
    current_state = "Idle"
    update_state()

func update_state():
    match current_state:
        "Idle":
            handle_idle()
        "Walk":
            handle_walk()
        "Run":
            handle_run()
        "Jump":
            handle_jump()
        "Fall":
            handle_fall()
        "Crouch":
            handle_crouch()

func handle_idle():
    # Default state - no movement
    pass

func handle_walk():
    # Handle walking movement
    pass

func handle_run():
    # Handle running movement
    pass

func handle_jump():
    # Handle jump mechanics
    pass

func handle_fall():
    # Handle falling physics
    pass

func handle_crouch():
    # Handle crouching
    pass

func pause_movement():
    is_paused = true
    current_state = "Paused"
    update_state()

func resume_movement():
    is_paused = false
    current
```

```gdscript
# ActionFSM.gd
extends Node

export var attack_cooldown = 1.0
export var item_use_cooldown = 2.0

var current_state = "Idle"
var is_paused = false
var action_timer = 0.0

func _ready():
    # Initialize with Idle state
    current_state = "Idle"
    update_state()

func update_state():
    match current_state:
        "Idle":
            handle_idle()
        "Attack":
            handle_attack()
        "UseItem":
            handle_use_item()
        "Block":
            handle_block()
        "Paused":
            handle_paused()

func handle_idle():
    # Default state - no action
    pass

func handle_attack():
    # Handle attack animation and cooldown
    pass

func handle_use_item():
    # Handle item use animation and cooldown
    pass

func handle_block():
    # Handle blocking animation
    pass

func handle_paused():
    # Handle paused state
    pass

func start_attack():
    if not is_paused:
        current_state = "Attack"
        action_timer = attack_cooldown
        update_state()

func start_use_item():
    if not is_paused:
        current_state = "UseItem"
        action_timer = item_use_cooldown
        update_state()

func pause_actions():
    is_paused = true
    current_state = "Paused"
    update_state()

func resume_actions():
    is_paused = false
    current_state = "Idle"
    update_state()
```

```gdscript
# Player.gd
extends Node

func _ready():
    # Connect signals for state transitions
    get_node("LocomotionFSM").connect("pause_movement", self, "_on_pause_movement")
    get_node("ActionFSM").connect("pause_actions", self, "_on_pause_actions")
    get_node("ActionFSM").connect("resume_actions", self, "_on_resume_actions")

func _on_pause_movement():
    get_node("ActionFSM").pause_actions()

func _on_pause_actions():
    get_node("LocomotionFSM").pause_movement()

func _on_resume_actions():
    get_node("LocomotionFSM").resume_movement()
    get_node("ActionFSM").resume_actions()
```

**Implementation Details:**

1. **State Structure:**
   - Locomotion FSM: Handles movement states (Idle, Walk, Run, Jump, Fall, Crouch)
   - Action FSM: Handles action states (Idle, Attack, UseItem, Block, Paused)

2. **State Transitions:**
   - When an action starts, it pauses the locomotion FSM
   - When an action finishes, it resumes the locomotion FSM
   - Both FSMs have separate pause/resume methods to handle state transitions

3. **Communication:**
   - The Player node acts as an intermediary to coordinate between FSMs
   - Signals are used to trigger state changes between FSMs

4. **Testing Requirements:**
   - Test locomotion while idle
   - Test movement while attacking
   - Test attack while moving
   - Test item use while moving
   - Test multiple actions in sequence
   - Test edge cases where actions interrupt movement

**Key Considerations:**
- The Action FSM should have priority over locomotion when an action is in progress
- Cooldown timers should prevent rapid consecutive actions
- The Player node should handle proper state transitions between FSMs
- Animation controllers should be integrated with these FSMs for visual feedback

Would you like me to provide the full implementation with animation integration and testing procedures?

