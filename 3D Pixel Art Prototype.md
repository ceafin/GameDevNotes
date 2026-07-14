## 1. What those videos are actually doing (in Godot terms)

From the video titles + the resources they link / are inspired by:
- **Dylearn – “Recreating t3ssel8r style 3D pixel art in Godot”**  
    Rebuilds t3ssel8r’s Unity look in Godot: low-res internal render + outlines + toon shading + stable pixel-perfect camera.
- **“3D PixelArt Tutorial – Godot” and “Godot 3D píxelart – Shaders Updated!”**  
    Show how to:
    - Render 3D into a **SubViewport**.
    - Upscale it with **nearest filtering**.
    - Apply **post-process shaders** for pixelation and outlines.
- **t3ssel8r’s own “Creating a Scene for my 3D Pixel Art Game”** (Unity, but core ideas carry over):
    - Toon lighting, outlines using depth/normal textures, pixel-perfect camera with subpixel offset, low-res target. [David Holland](https://www.davidhol.land/articles/3d-pixel-art-rendering/)
- **David Holland’s “3D Pixel Art Rendering” article** (explicitly: Godot, inspired by t3ssel8r) lays out the same recipe:
    - Procedural outlines via depth + normals.
    - Camera snapped to a texel-aligned grid + screen-space shift to smooth motion.
    - Toon lighting + low-res render. [David Holland](https://www.davidhol.land/articles/3d-pixel-art-rendering/)
- **Merxon22’s article “Render 3D Models as Pixel Art (Godot)”** shows a clean, minimal implementation of the “SubViewport → Sprite2D → pixelation shader” technique, and we can pretty much lift that approach. [Medium](https://medium.com/%40merxon22/godot-shader-render-3d-models-as-pixel-art-4839e6528601)
- **Leopeltola’s 3D pixelart demo repo** shows how to do outlines/highlights on low-res 3D scenes in Godot 4, and notes the same thing:
	- use a low game resolution, and if you want hi-res UI, draw the game inside a SubViewport. [GitHub](https://github.com/leopeltola/Godot-3d-pixelart-demo)

So: we’ll build a **small Godot 4.5 project that does exactly that**.

---
## 2. Project settings: make Godot behave like a low-res console

1. **Set default window size** (just for testing):
    - Project → Project Settings → Display → Window:
        - Width: `1280`
        - Height: `720`
        - Stretch Mode: `viewport`
        - Stretch Aspect: `keep`
2. **Make everything “nearest” by default (no blurring):**
    - Project → Project Settings → Rendering → Textures:
        - `Default Texture Filter` → `Nearest`.
3. (Optional but nice for pixel art)
    - Project → Project Settings → Rendering → 2D:
        - Enable `Use Pixel Snap`.

These give you a good base where upscaling a low-res viewport looks crisp.

---
## 3. Scene layout for a pixelated 3D diorama

We’ll do this in two scenes:
- `World3D.tscn` – your 3D diorama + player + camera.
- `Main.tscn` – a UI/root scene that renders `World3D` through a **SubViewport** and displays it full-screen as a pixelated texture.

### 3.1 `World3D.tscn` (your diorama)

Create a new scene:

**Root**: `Node3D` named `World3D`

Children:
- `DirectionalLight3D`
- `MeshInstance3D` named `Ground`
    - Mesh: `PlaneMesh` (size e.g. 10×10)
- `CharacterBody3D` named `Player`
    - Child: `MeshInstance3D` (use a simple `BoxMesh`)
    - Child: `Node3D` named `CameraRig`
        - Child: `Camera3D`

Set `Camera3D`:
- Projection: `Perspective`
- FOV: something like `35` (narrow, toy-ish).
- Position: e.g. `Transform`:
    - Translation: `(0, 6, 6)`
    - Rotation X: around `-45°` (look down at the player).
- Or just use the gizmo and eyeball a ¾-top-down look.

Use **toon shading** to avoid smooth gradients:
- Click the `Ground` `MeshInstance3D` → `Material` → new `StandardMaterial3D`:
    - Shading → `Diffuse Mode: Toon`
    - Shading → `Specular Mode: Toon` or `Disabled`
- Do similarly for the `Player` mesh. [Medium](https://medium.com/%40merxon22/godot-shader-render-3d-models-as-pixel-art-4839e6528601)

Attach this script to `Player` as `player.gd`:

```gdscript
extends CharacterBody3D

const SPEED := 4.0
const GRAVITY := 9.8

func _physics_process(delta: float) -> void:
	var input_vec := Vector2(
		Input.get_action_strength("move_right") - Input.get_action_strength("move_left"),
		Input.get_action_strength("move_back") - Input.get_action_strength("move_forward")
	)
	
	var direction := Vector3.ZERO
	if input_vec.length() > 0.0:
		input_vec = input_vec.normalized()
		# map 2D input to world-space XZ (Z forward)
		direction = Vector3(input_vec.x, 0.0, input_vec.y)
		# face movement direction
		look_at(global_transform.origin + direction, Vector3.UP)
	
	velocity.x = direction.x * SPEED
	velocity.z = direction.z * SPEED
	
	# simple gravity
	if not is_on_floor():
		velocity.y -= GRAVITY * delta
	else:
		velocity.y = 0.0
	
	move_and_slide()
```

Add input actions in Project Settings → Input Map:
- `move_left`: A, Left
- `move_right`: D, Right
- `move_forward`: W, Up
- `move_back`: S, Down

That’s enough to walk a cube around a ground plane.

---
## 4. SubViewport + pixelated display (`Main.tscn`)

Now we’ll render `World3D` at a tiny resolution and show it scaled up.

Create a new scene:

**Root**: `Control` named `Main`

Children:
1. `SubViewport` named `WorldViewport`
    - Size: `320 x 180` (nice 16:9 low res).
    - `Disable 3D`: **off**
    - `Render Target → Update Mode`: `Always`
    - `Render Target → Clear Mode`: `Always`
    - `Rendering → 3D → MSAA`: `Disabled`
    - `Rendering → 3D → Use Occlusion Culling`: off (for now)
    - Instance your `World3D.tscn` as a child of this `SubViewport`.
2. `TextureRect` named `ViewportDisplay`
    - Layout → Full Rect (anchors to full window).
    - `Stretch Mode`: `Keep Aspect Centered`
    - `Expand`: on.

Attach a script to `Main` as `main.gd`:

```gdscript
extends Control

@onready var viewport: SubViewport = $WorldViewport
@onready var display: TextureRect = $ViewportDisplay

func _ready() -> void:
	display.texture = viewport.get_texture()
	# Make sure filtering is disabled on the canvas item
	display.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST

```

Run `Main.tscn` as your main scene (Project → Project Settings → Run → Main Scene).

You should now have:
- A 3D world.
- Rendered at 320×180.
- Upscaled to 1280×720 with crisp pixels.

This alone already gives you a “low-res 3D diorama” vibe.

---
## 5. Adding a pixelation shader (like the tutorials)

The SubViewport resolution is already low. But to:
- tweak “pixel size” independently, or
- implement the same technique as Merxon22,

you can add a **pixelation shader** on the `TextureRect`.
1. On `ViewportDisplay`, set:
    - `Material` → new `ShaderMaterial`
    - Click it → new Shader → type: `CanvasItem`.
2. Use this shader (adapted from Merxon22’s article): [Medium](https://medium.com/%40merxon22/godot-shader-render-3d-models-as-pixel-art-4839e6528601)

```c++
shader_type canvas_item;

uniform vec2 pixel_count = vec2(160.0, 90.0);

void fragment() {
	vec2 uv = UV;
	
	// snap UV to a coarse pixel grid
	uv *= pixel_count;
	uv = floor(uv);
	uv /= pixel_count;
	
	COLOR = texture(TEXTURE, uv);
}
```

- `pixel_count` is your “virtual resolution”.
    - For a chunky look: `160x90`.
    - For finer pixels: `320x180`, `400x225`, etc.

Now you have **two knobs**:
- `WorldViewport.size` – the actual render resolution (performance + base look).
- `pixel_count` – how “fat” the pixels look, regardless of window size.

---
## 6. Making the camera feel like Link’s Awakening

Link’s Awakening remake has:
- A fixed-ish, high, ¾ angle.
- Slight perspective.
- Very stable pixels (no shimmer).

You’ve already got the angle; now we’ll add **simple pixel snapping** to reduce shimmer.

Attach this script to your `CameraRig` (or directly to `Camera3D` if it’s independent) as `pixel_camera.gd`:

```gdscript
extends Node3D

# How many "screen pixels" per world unit.
# You'll tweak this by eye. Start with 16 and adjust.
@export var pixels_per_unit: float = 16.0

func _process(delta: float) -> void:
	# Snap the rig to a grid in world space.
	var pos := global_position
	pos.x = floor(pos.x * pixels_per_unit) / pixels_per_unit
	pos.y = floor(pos.y * pixels_per_unit) / pixels_per_unit
	pos.z = floor(pos.z * pixels_per_unit) / pixels_per_unit
	global_position = pos
```

Attach `CameraRig` as a child of `Player` so that:
- Player moves smoothly.
- CameraRig follows player (because it’s a child) but gets snapped to a grid.

This is a simplified version of the “pixel camera” described by David Holland and others: snap camera to a texel grid to prevent “pixel creep”. [David Holland](https://www.davidhol.land/articles/3d-pixel-art-rendering/)

If you want to go **hardcore accurate** later, the full technique is:
1. Snap camera position to pixel grid.
2. Compute the offset between snapped and unsnapped position.
3. Apply the offset back again in a screen-space shader to preserve smooth motion while keeping stable pixels. [David Holland](https://www.davidhol.land/articles/3d-pixel-art-rendering/)

But for a prototype, simple snapping is fine.

---
## 7. Optional: outlines and highlight shader (t3ssel8r-style polish)

The videos and their comment sections often point to:
- Depth + normal texture based outline shaders (1-pixel edges, convex highlights). [David Holland](https://www.davidhol.land/articles/3d-pixel-art-rendering/)
- Dedicated outline/highlight shaders like:
    - “3D Pixel art outline & highlight Shader (post-processing/object)” on Godot Shaders. [Godot Shaders](https://godotshaders.com/shader/3d-pixel-art-outline-highlight-post-processing-shader/)
    - The associated demo repo `Godot-3d-pixelart-demo`. [GitHub](https://github.com/leopeltola/Godot-3d-pixelart-demo)

The general recipe is:
1. Use **Forward+ renderer** and enable the depth/normal buffer.
2. Add a full-screen quad (or use Godot’s compositor) with a shader that:
    - Samples the scene color, depth, and normal textures.
    - Looks at up/down/left/right neighbors.
    - Draws dark outlines where depth/normal changes sharply.
    - Draws softer edge highlights on convex edges.

That’s overkill for a first prototype, but once your basic diorama and pixel camera are working, you can:
- Download the leopeltola repo. [GitHub](https://github.com/leopeltola/Godot-3d-pixelart-demo)
- Drop the provided `pixelart_stylizer.gdshader` into your project.
- Use it as a post-process material on a full-screen quad or via a compositor effect.

---
## 8. Checklist: you have a “3D pixel diorama” prototype when…

You can:
- Run `Main.tscn`.
- See a low-res 3D scene rendered into a SubViewport.
- That image is scaled up to your window with **nearest-neighbor** filtering.
- A simple toon-lit cube player walks around.
- The camera is at a fixed ¾ angle and snapping to a grid so pixels don’t shimmer badly.
- Optionally, a shader on the `TextureRect` gives you adjustable pixel size.

From here you can start replacing:
- The cube with your BurritoMan / Zelda-like hero.
- The plane with proper tiling low-poly geometry or heightfield terrain.
- Plain colors with carefully-painted pixel-art textures (keeping texture filter = Nearest).

If you want, next step we can:
- Add **depth-of-field-ish fake** to push the toy/diorama feeling.
- Design a **Celtic stone circle / túath village diorama** that matches your RPG’s vibe.
- Build a tiny “overworld room” in this style, not just a test ground.

