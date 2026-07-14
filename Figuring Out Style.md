**Link’s Awakening (Switch) diorama camera + the crunchy pixel look of that screenshot.**  

## The style you’re aiming for (in Godot terms)

What you want is basically:
1. **Tiny diorama worlds**
    - Simple low-poly meshes (blocks, wedges, pillared ruins, trees).
    - Each “screen” is a small self-contained scene (like LA’s little room-sized chunks).
2. **Tilted, toy-box camera (Link’s Awakening-ish)**
    - Camera high above, angled down.
    - Often _orthographic_ or very low FOV to avoid distortion.
    - Optional depth-of-field blur for the tilt-shift vibe.
3. **Pixelated output**
    - Render the 3D scene at a low resolution in a `SubViewport`.
    - Scale that up to window size using nearest-neighbor filtering.
    - Small textures / flat colors to keep it crisp.

All of that you can absolutely do in Godot 4.5 with GDScript and primitives.

---
### Stage 1 – One static shrine diorama (no gameplay)

**Goal:** Recreate something _vaguely like_ the screenshot: a walled grass room with a little shrine in the middle, viewed from a nice camera angle and pixelated.
**What to build**
Scene `ShrineWorld3D.tscn` (root: `Node3D`):
- `DirectionalLight3D`
- `Camera3D`
- `MeshInstance3D` – ground (BoxMesh scaled flat, grassy material).
- 4–6 `MeshInstance3D` pillars (BoxMeshes scaled tall).
- 4 wall segments around the edges.
- A simple “altar” in the middle (stacked boxes / cylinders).
- A couple of “bushes” (squashed spheres or boxes with green color).

**Camera setup (LA-style-ish)**
- Select `Camera3D`:
    - Projection: **Orthogonal** (in Inspector) – this gives you that board-game look.
    - Size: something like `8–12` (you’ll tweak based on world size).
    - Position: `x = 0, y = 12, z = 8` (ballpark).
    - Rotation:
        - X ≈ **-55°** (looking down).
        - Y ≈ **45°** (so corners face camera).
- Optional: on the camera, enable **DOF** later for tilt-shift:
    - `Dof Blur Near/Far` with a small `Depth of Field` region around the altar.
    - Not required for first pass; focus on composition.

**Pixel viewport setup**
Make a separate main scene `Main.tscn`:
- Root: `Control` → name `Main`.
- Child: `SubViewport` → `GameViewport`
    - Size: Width `320`, Height `180` (or similar).
    - `Update Mode: Always`.
    - Instance `ShrineWorld3D.tscn` _into_ this SubViewport.
- Child: `TextureRect` → `GameView`
    - Texture: drag `GameViewport` into it.
    - `Expand: On`.
    - `Stretch Mode: STRETCH_SCALE`.
    - `Stretch Aspect: KEEP_CENTERED` or `KEEP_ASPECT_COVERED`.

In **Project Settings**:
- `Rendering > Textures > Default Texture Filter = Nearest`.

---
### Stage 2 – Make it playable: one hero walking around

**Goal:** You can walk a little character around that single shrine room under this camera.

**What to add**

In `ShrineWorld3D.tscn`:
- Add `CharacterBody3D` → `Player`.
    - Child: `MeshInstance3D` with a BoxMesh (temporary hero).
    - Collision: `CollisionShape3D` (capsule or box).

Attach something like:

```gdscript
extends CharacterBody3D

const SPEED := 4.0
const GRAVITY := 20.0

func _physics_process(delta):
var input_dir := Vector2.ZERO

if Input.is_action_pressed("ui_up"):
	input_dir.y -= 1
if Input.is_action_pressed("ui_down"):
	input_dir.y += 1
if Input.is_action_pressed("ui_left"):
	input_dir.x -= 1
if Input.is_action_pressed("ui_right"):
	input_dir.x += 1

input_dir = input_dir.normalized()

# Screen-up is world -Z, screen-right is +X
var direction = Vector3(
	input_dir.x,
	0,
	input_dir.y
)

velocity.x = direction.x * SPEED
velocity.z = direction.z * SPEED

if not is_on_floor():
	velocity.y -= GRAVITY * delta
else:
	velocity.y = 0.0

move_and_slide()
```

Add colliders to your walls/pillars so the player bumps into things properly.

**Camera**

For now keep it **fixed**, toy-box style (like LA’s outdoor screens). You can later experiment with slightly following the player within bounds.

**Stage success when:**  
You can run around that one shrine room and it feels like a little plastic-toy Zelda screen, but pixely.

---
### Stage 3 – Multiple “screens” with smooth transitions

Now we lean into the Link’s Awakening screen-by-screen overworld.

**Goal:** Have 2–4 adjacent dioramas and slide the camera (or swap scenes) when the player steps off an edge.

**Option A – One big world, moving camera**
- Build 2–4 shrine-like areas in one large `World3D`, laid out on a grid.
- Define “screen centers” (Markers or Position3D nodes).
- Keep the **orthographic camera**, but lerp it between screen centers when the player crosses a threshold.

Pseudo-logic on some `WorldController` script:

```gdscript
@onready var camera := $GameCamera
var target_position: Vector3

func _ready():
	target_position = camera.global_position

func _process(delta):
	camera.global_position = camera.global_position.lerp(target_position, 5.0 * delta)

func go_to_screen(center: Vector3):
	target_position = center
```

Trigger `go_to_screen()` when the player crosses a boundary Area3D.

**Option B – Each screen is its own scene**
- Make `ShrineWorld3D`, `ForestWorld3D`, `CliffWorld3D`, etc.
- A lightweight `WorldManager` in 2D/UI land swaps which one is instanced into the SubViewport.
- Doors/edges signal the manager: “load scene X, spawn player at entrance Y”.

Either way you’re practicing:
- Chunking the world like LA.
- Keeping the camera as a diorama viewer rather than a free follower.

---
### Stage 4 – Interactions & “toy” feeling

Now we add the Zelda-y verb set:

**Goal:** You can interact with diorama bits: open a chest, flip a switch, get a key, open a gate.

Pieces to add (all very re-usable):
- `Interactable.gd` base:
    - Uses an `Area3D` to detect when the player is in range.
    - Shows a “Press A / E” prompt via a 2D UI.
    - On button press, calls `interact()` on the object (or emits a signal).
- Concrete interactables:
    - Chest that plays an open animation & gives an item.
    - Door that opens if you have a key.
    - Pedestal where you can place a thing.
- Simple inventory singleton (`GlobalInventory.gd`) to track keys & items.

This is where your previous FSM and component habit shines; it’s the same ideas in 3D.

---
### Stage 5 – Enemies & combat (first dungeon room)

Finally, bring in danger:

**Goal:** A single room with 1–2 enemy types you can defeat.

- `Enemy.tscn`:
    - `CharacterBody3D` + mesh + collider.
    - Simple AI:
        - Idle/wander until player in radius.
        - Move toward player and occasionally attack.
- `HealthComponent.gd` used by both player & enemies.
- Player sword attack:
    - A `Area3D` in front of the hero that’s enabled during a few frames of an attack animation.