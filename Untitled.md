```text
GLOBAL STATE
  state = gs_titles | gs_game
  gamestate = s_levelstart | s_playing | s_lostlife | s_levelcomplete | s_gameover
  player, entities[], particles[], intermissions[], ground[], layers[]
  groundx (world scroll position), cameray, lives, level, round

────────────────────────────────────────────────────────────────
_init()
  seed stars[]
  reset_titles()          -- gs_titles, start title music

_update60()               -- runs every frame
  input_update()
  if gs_titles → update_titles()
    game_update()           -- demo mode: game runs *behind* title screen
    on button press → game_reset() → gs_game
  else → game_update()
  transition:update()

_draw()
  if gs_titles → draw_titles()
    game_draw()             -- game visible behind title overlay
    logo, credits on top
  else → game_draw()
  transition:draw()

────────────────────────────────────────────────────────────────
game_reset()
  lives=3, level=levelstart*5
  player_create()
  game_resetlevel(advance=true)

game_resetlevel(advance)
  if advance → level++, pick sector slice from course data
  else       → rewind groundx to last checkpoint
  game_generate_level()   -- rebuild ground[] + spawn entities
  player_resetlevel()
  game_setstate(s_levelstart | s_playing)

game_generate_level()     -- THE WORLD BUILDER
  srand(17 + level + round*100)   -- deterministic per level
  ground = {}             -- per-pixel heightmap  ground[x].{y, origy, holedepth, slopedepth}
  
  for each pixel x in (5 sectors × sector_length):
    parse course action string at this x:
      "h" → arena_addhole()     -- authored crater
      "r" → rock_add()
      "m" → rock_add(size=0)    -- mine
      "1/2/3" → spawner_add()   -- flyer waves
      "b" → boulder_add()
      "t" → tank_add()
      "hs" → heatseeker_add()
      "p" → plant_add()
      ">/</-" → set slope direction
    compute y via seeded random walk (±undulation, clamped to slope)
    ground[x] = {y, origy, holedepth=0, slopedepth}
  
  set up background layers[] (stars, mountains or city)
  apply course color palette

────────────────────────────────────────────────────────────────
game_update()             -- per-frame game logic
  if intermission active → hand off entirely, return

  count active bombs/bullets
  
  for each entity: entity:update() / remove if inactive
  particles_update()
  
  match gamestate:
    s_levelstart  → wait 180 frames → s_playing
                    player_update() (for alignment on start platform)
    s_playing     → player_update()
                    groundspeed = player.speed + 0.5  (or 0 if dying)
                    arena_update()              -- scroll world
                    check level end → s_levelcomplete
    s_levelcomplete → queue int_levelclear intermission
    s_lostlife    → wait 15 frames → lives--
                    if lives==0 → s_gameover
                    else → game_resetlevel(advance=false)
    s_gameover    → play gameover music, wait → reset_titles()

game_draw()
  if intermission → intermission:draw(), return
  game_drawinternal():
    cls()
    arena_draw()                  -- stars, parallax layers, ground polygon
    for each entity (background z-order): e:draw()
    for each entity (foreground z-order): e:draw()
    player_draw()
    particles_draw()
    game_draw_scorepanel()        -- score, lives, time, A-E progress bar

────────────────────────────────────────────────────────────────
arena_update()            -- world scroll tick
  groundx += groundspeed
  check sector crossing → update checkpoint, play sfx
  scroll parallax layers at their respective speeds
  cameray = lerp(cameray, target_y_from_slope, 0.25)

arena_draw()
  stars_draw()
  draw 2 parallax layers (tiled, doubled for seamless scroll)
  for x in 0..127:
    sample ground[groundx + x]
    draw vertical line from surface to bottom (solid fill)
    if holedepth > 0: draw hole gap (skip fill, draw rim edges)

arena_addhole(x, size)    -- SAME function for authored + bomb craters
  lookup depths[] profile for size 1-4
  stamp depth values into ground[x].holedepth + lift ground[x].y

────────────────────────────────────────────────────────────────
ENTITY SYSTEM (flat array, duck-typed by .type field)
  entities[] contains: bullets, bombs, rocks, mines, boulders,
                        tanks, flyers, heatseekers, plants, spawners
  All share: {active, type, x, y, update(), draw()}
  Spawners emit flyer waves over time; flyers drop bombs;
  bombs call arena_addhole() on ground impact.

PLAYER
  player_update(): input → velocity → jump → fire bullets
    if bullet hits entity → score
    if entity/bomb hits player → ps_dying → game_setstate(s_lostlife)
  Bullets limited to maxplayerbullets (3), bombs to maxbombs (scales with round)
```
