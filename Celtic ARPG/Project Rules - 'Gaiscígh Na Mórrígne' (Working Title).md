# Project Rules for a Celtic ARPG/JRPG 'Gaiscígh Na Mórrígne' _(Working Title)_

Durable, project-specific invariants for this game. Global Godot/GDScript rules and my working style live in `CLAUDE.md`; running state lives in `MEMORY.md`.

>  **Mór-Ríoghain** *(often anglicized as The Morrígan)* is a powerful and enigmatic goddess from Irish mythology. Her name translates from modern Irish as "Great Queen" or "Phantom Queen". She is primarily revered as a deity of war, destiny, prophecy, and sovereignty.
## What this is
Explore mode is 2D top-down in the mold of Zelda: Link's Awakening and Oracle of Seasons/Ages — faithful *feel*, modern *implementation*. Battle is a separate, dedicated screen: VP/Indivisible-style party combat. See `Game Design Document and Player Manual.md` for the full pillars; this file is just the technical invariants for Explore mode.

The player character is **The Morrígan**. `[DECISION LOCKED]` She is not a combatant in Explore mode — no sword, no HP, no hitbox. Her only verbs beyond movement/interaction are environmental (push, pull, interact, puzzle-solve, navigate) plus **mark**, which tags an enemy and triggers a battle rather than dealing damage. Combat itself resolves entirely on the dedicated battle screen, commanding up to 4 champions — that screen is separate architecture, not yet built, and is out of scope for this file (see "Not yet built," below).

`Nasc` (the directly-controlled Link-stand-in from the earlier prototypes) is **retired for this project** — the character and its sword/jump/dig kit are earmarked for a different, unrelated puzzle game instead. Any reference to `Nasc` elsewhere in this repo's Godot projects predates this decision; treat it as superseded, not current. The player body scene/class here is `morrigan.tscn` / `class_name Morrigan` (ASCII, no fada — GDScript identifiers don't take diacritics; the fada is fine in narrative text and asset names).

## Render & display (locked — re-verify integer scaling before changing)
- Base viewport **320×180** (20×11.25 tiles). Clean integer scale: 1080p ×6, 1440p ×8, 4K ×12.
- Stretch mode `viewport`, aspect `keep`. Default texture filter `Nearest`. Snap 2D Transforms to Pixel `on`.
- **16×16** tiles/sprites; large bosses composited from several 16×16 tiles.
- Fallback only if playtesting proves the view too tight: **384×216** — but this loses clean 1440p scaling. Do not switch preemptively.

## HUD & transitions (locked, Explore mode only)
- HUD floats over the playfield on a `CanvasLayer` (ALttP-style corner overlay). The full 320×180 is game world — no Game Boy ribbon/bar. Accepted tradeoff: 20×11 tiles is wider but shorter than ALttP; intentional widescreen feel.
- Room transitions are SNES-style framed/scrolling, not hard Game Boy cuts.
- The battle screen is a different mode entirely (see "Not yet built," below) and is not bound by this HUD treatment — its UI is undesigned.

## World & camera architecture (locked — do not revisit)
- One large `TileMapLayer` per zone. Zone files under `world/`. The tilemap is one contiguous map — not separate scenes per screen.
- Large cave zones work identically to the overworld (own `TileMapLayer`, same camera approach). Warp portals link an overworld zone and its cave counterpart.
- Camera is a `Camera2D` **sibling of the Morrígan** in the world scene (never a child of her body). **ALttP overworld-style free scroll**: updated in `_physics_process` (matches `move_and_slide` timestep — eliminates diagonal jitter); no position smoothing. Limits come from `CameraZone` sub-regions (see below); fallback is the tilemap used rect.
- **`CameraZone` (`class_name CameraZone extends Area2D`)** — place in world scenes to define camera limit rectangles for irregular overworld shapes. One `CollisionShape2D` child with a `RectangleShape2D`. Adds itself to group `camera_zones` in `_enter_tree`. `RoomCamera` connects to all zones at startup; smallest active zone wins when zones overlap. No zone active → tilemap fallback.
- **Warps are not camera events.** Doors, cave mouths, and zone portals are scene warps (fade → `change_scene_to_file()` → spawn the Morrígan at a named spawn point).
- **Marking is not a camera event either (for now).** Whatever happens visually when a battle triggers (a snap-cut, a wipe, a wind-up) is undesigned — don't invent it here; see "Not yet built."
- No `RemoteTransform2D` — not needed.

## Player, FSM & component architecture (do not silently break)
- **Body is the scene root.** `move_and_slide()` moves the body's own transform; a wrapper `Node2D` root would cause position/physics drift. Do not reintroduce one.
- **Collision box is at the feet, narrower than the sprite** — a horizontal `CapsuleShape2D` (rotated 90°). Sells the 3/4 overhead view (head overlaps walls above, feet stop movement). Do not "fix" it to match full sprite bounds.
- **`class_name` only on infrastructure** (`Morrigan`, `State`, `StateMachine`), never on leaf states — leaf export slots are typed as the base `State`.
- **FSM transitions are node references, not strings.** `transition_to(next: State)` takes the `State` node directly; each leaf exports its reachable states, wired in the Inspector. No dictionary or string lookup. (This pattern beat the string/signal alternative tried in an earlier prototype on every axis that mattered — keep it.)
- **`StateMachine` never self-starts.** Its `_ready()` only wires refs and disables physics; the owning body calls `start()` from its own `_ready()` once its resources are ready. Any body using `StateMachine` follows this pattern.
- **Keep the StateMachine guards:** null-`initial_state` → disable physics + `push_error`; self-transition (`next == current_state`) → no-op (avoids spurious `exit()`/`enter()` once `enter()` runs timers/VFX).
- FSM and components are orthogonal and both used. FSM = what the Morrígan is *doing now* (idle/move, later mark). Components = *capabilities* — for her body that's things like an interaction/mark-range detector (`Area2D`), **not** a health component or a hurtbox/hitbox: she takes no damage and deals none in Explore mode, so don't build those for her. (A generic `hurtbox`/`hitbox` component may still make sense later for *champions* on the battle screen — that's separate architecture, not this body.) Build each component only when its block arrives.
- **A state is a mode that changes what inputs MEAN — not every verb is a state.** Marking an enemy, or pushing/pulling an object, is an action from within Move/Idle — it doesn't change what other inputs mean, so it doesn't need its own state. Don't node-ify every verb.

## Established naming
- Input actions: `move_left`, `move_right`, `move_up`, `move_down`. A `mark` action is planned but not yet mapped — add it when the mark verb is actually built, not before.
- Animation clips: `idle_<cardinal>` / `walk_<cardinal>`, cardinal ∈ `down/up/left/right`. `Morrigan.cardinal(dir) -> String` picks the cardinal by dominant axis.

## Script roles (target shape — see disk-reconciliation note below)
- `morrigan.gd` (`class_name Morrigan`): thin body. Holds `@onready` refs to its sprite and state machine, `var last_direction: Vector2` (default `Vector2.DOWN`), and the static `cardinal()` helper. States drive `velocity`.
- `state.gd` (`class_name State`): base; holds `state_machine` ref + virtuals (`enter`/`exit`/`physics_update`). Faction-agnostic on purpose — no target/aggro.
- `state_machine.gd` (`class_name StateMachine`): wires refs and disables physics in `_ready()`; `start()` launches the initial state and enables physics; `transition_to(next: State)` switches by node reference.
- `idle.gd` / `move.gd`: leaf states (no `class_name`). Idle zeroes velocity and plays `idle_<cardinal>`; Move drives the body, updates `last_direction`, plays `walk_<cardinal>`.
- **Disk-reconciliation note:** the existing Godot prototype(s) currently have these scripts under the name `nasc.gd`/`Nasc`/`nasc.tscn`, built before this decision. `.gd` files on disk are still the source of truth for what code *currently does* — this section describes the target shape to rename/migrate toward, not a claim about what's on disk today. Do the rename as its own deliberate pass, not incidentally while building something else.

## Not yet built (do not invent details here)
The battle screen and the mode-switch that connects it to Explore are the next real architecture milestone (per the GDD's vertical slice), and neither exists yet. Specifically undesigned: the mark→trigger→battle handoff, the battle scene and its 4-champion combat, battle-screen camera/rendering treatment, and any transition VFX between modes. When that work starts, it gets its own rules here — don't pre-build scaffolding for it now.