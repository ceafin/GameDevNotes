1. The Player: Moon Buggy (Kinematic/CharacterBody2D)

The "feel" of _Moon Patrol_ comes from its bouncy, sluggish suspension.

- **Three-Part Movement:** Implement a `CharacterBody2D` with three wheels. Use a "fake" suspension by oscillating the body's Y-offset relative to the wheels [1.2.1](https://www.retrorefurbs.com/moon-patrol-a-practical-example-of-how-to-get-good-at-classic-arcade-games/).
- **Input Logic:**
    - **Horizontal:** The buggy moves at a constant "base" speed. Left/Right inputs only add or subtract a small velocity modifier (it never fully stops) [1.3.6](https://www.arcade-museum.com/Videogame/moon-patrol).
    - **The Jump:** A fixed-height jump. Note that in the original, you cannot jump again for a split second after landing 1.2.1.
- **Dual Weapon System:** Map one "Fire" button to two different `instantiate()` calls:
    - **Vertical:** Fast-firing anti-air missiles (up to 4 on screen) 1.2.1.
    - **Horizontal:** A single, short-range projectile for rocks/tanks 1.2.1.

2. The Environment: Parallax & Level Design

This was one of the first games to use **Parallax Scrolling** [1.3.2](https://en.wikipedia.org/wiki/Moon_Patrol).

- **ParallaxBackground Node:** Use at least three layers:
    1. **Far:** Distant stars/galaxies (slowest).
    2. **Mid:** High mountains/hills [1.3.1](https://www.computerarcheology.com/Arcade/MoonPatrol/).
    3. **Near:** Moon craters and cityscapes (fastest).
- **The Checkpoint Map:** The game is divided into 26 segments (A to Z) [1.2.5](https://www.c64-wiki.com/wiki/Moon_Patrol).
    - **Dev Tip:** Don't build one giant level. Build a `LevelManager` that spawns hazards based on a JSON or Dictionary "course" file (e.g., `at_mark_B: spawn(rock)`). 

3. The Hazard AI (The "Attention List")

You need distinct behaviors for different `Area2D` or `CharacterBody2D` enemies:

- **Static Obstacles:** Craters (kill on contact), Rocks (can be shot/jumped), and Landmines [1.3.4](https://pixelatedarcade.com/games/moon-patrol).
- **Aerial UFOs:**
    - **Regular:** Float and fire downward beams [1.5.1](https://thatguywiththeglasses.fandom.com/wiki/Moon_Patrol).
    - **Crater-Makers:** Their bombs create new craters in the floor—this requires your ground to be dynamic or to use "hole" sprites [1.2.6](https://www.youtube.com/watch?v=imh9HMIbI1U).
- **Ground Threats:**
    - **Tanks:** Fire rockets horizontally [1.5.3](http://tips.retrogames.com/gamepage/mpatrol.html).
    - **Rocket Cars:** Zip in from behind; the player must jump over them [1.5.7](https://www.ataricompendium.com/archives/manuals/vcs/moon_patrol.pdf). 

4. Game Systems & UI

To make it "Itch-ready," you need the "Arcade Juice":

- **The Three-Light Warning:** Implement UI lights that blink when:
    1. UFOs are approaching.
    2. A minefield is ahead.
    3. An enemy is approaching from behind 1.2.6.
- **The Progress Bar:** A bottom-screen UI showing the letters A-Z and your current position [1.5.4](https://www.arcade-museum.com/manuals-videogames/M/Moon_Patrol_Instruction_Manual_163007101_Sep_1982.pdf).
- **Scoring:** Grant "Average Time" bonuses at every 5th letter (E, J, O, T, Z) 1.2.5. 

5. Technical Polish (Godot Specific)

- **CanvasLayer:** Keep your UI and "Warning Lights" on a separate `CanvasLayer` so they don't scroll with the moon.
- **CRT Shader:** Add a retro CRT shader to the `WorldEnvironment` or a screen-space `ColorRect` to give it that 1982 arcade feel.
- **Audio:** Use the Godot AudioStreamPlayer to loop the iconic funky bassline.

Would you like me to write a **GDScript snippet** for the buggy's unique "dual-fire" shooting mechanic?