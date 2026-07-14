#!/usr/bin/env python3
"""Generate a CSV matrix of games vs. game development mechanics."""
import csv
import io

# All mechanic columns (game-dev community terminology)
mechanics = [
    "Top-Down", "Side-View", "First-Person", "Third-Person", "Isometric",
    "Fixed Screen", "2D", "3D", "Pseudo-3D",
    "Side-Scrolling", "Vertical Scrolling", "Auto-Scrolling", "Screen-by-Screen",
    "Platformer", "Shooter/Shmup", "Puzzle", "Racing", "Fighting", "Beat 'em Up",
    "RPG", "Action-Adventure", "Real-Time Strategy (RTS)", "Simulation",
    "Rhythm", "Sports", "Point-and-Click Adventure", "Text Adventure",
    "Roguelike", "Sandbox", "Idle/Clicker", "Endless Runner", "Maze", "Pinball",
    "City Builder", "Life Simulation", "Management/Tycoon",
    "Rail Shooter", "Run-and-Gun", "Artillery", "FPS", "Educational",
    "Turn-Based", "Real-Time Combat", "Physics-Based", "Grid-Based",
    "Procedural Generation", "Level-Based", "Open World", "Metroidvania",
    "Dungeon Crawling", "Wave-Based",
    "Power-Ups", "Inventory Management", "Health System", "Lives System",
    "Score System", "Upgrade System", "Character Selection", "Collectibles",
    "Weapon Switching", "Ability Copying", "Equipment System", "Leveling/XP",
    "Magic/Spell System", "Party-Based", "Combo System",
    "Day-Night Cycle", "Destructible Terrain", "Fog of War", "Overworld Map",
    "Resource Gathering", "Base Building", "Economy System", "Crafting",
    "Dialog System", "NPC Interaction",
    "Local Multiplayer", "Co-op", "Online Multiplayer",
    "Projectile Combat", "Melee Combat", "Boss Battles", "Enemy AI/Pathfinding",
    "Save/Password System", "Timer/Time Limit", "Permadeath",
    "Random Encounters", "Secret Areas", "Mini-Games", "Multiple Endings",
    "Terrain Digging/Mining",
]

# (Game, Year, Platform, Complexity, Scope, Combined, [list of mechanics])
games_data = [
    ("Pong", 1972, "Arcade", 0.5, 0.5, 1,
     ["Side-View", "2D", "Fixed Screen", "Sports", "Real-Time Combat",
      "Score System", "Local Multiplayer"]),

    ("Breakout", 1976, "Arcade", 0.5, 0.5, 1,
     ["Side-View", "2D", "Fixed Screen", "Puzzle", "Physics-Based",
      "Score System", "Level-Based"]),

    ("Chrome Dinosaur Game", 2014, "Web Browser", 0.5, 0.5, 1,
     ["Side-View", "2D", "Endless Runner", "Auto-Scrolling", "Score System"]),

    ("Blockade (Snake)", 1976, "Arcade", 1, 0.5, 1.5,
     ["Top-Down", "2D", "Fixed Screen", "Grid-Based", "Score System"]),

    ("Gorillas.bas", 1990, "MS-DOS", 1, 0.5, 1.5,
     ["Side-View", "2D", "Fixed Screen", "Artillery", "Turn-Based",
      "Physics-Based", "Score System", "Local Multiplayer",
      "Destructible Terrain"]),

    ("Number Munchers", 1986, "Apple II", 1, 1, 2,
     ["Top-Down", "2D", "Fixed Screen", "Educational", "Grid-Based",
      "Level-Based", "Lives System", "Score System", "Enemy AI/Pathfinding"]),

    ("Snail Maze", 1986, "Sega Master System", 1, 1, 2,
     ["Top-Down", "2D", "Maze", "Level-Based", "Timer/Time Limit"]),

    ("Cookie Clicker", 2013, "PC", 1, 1, 2,
     ["2D", "Idle/Clicker", "Upgrade System", "Economy System"]),

    ("Flappy Bird", 2013, "Mobile", 1, 1, 2,
     ["Side-View", "2D", "Endless Runner", "Auto-Scrolling", "Score System"]),

    ("Jetpack Joyride", 2011, "Mobile", 1, 1.5, 2.5,
     ["Side-View", "2D", "Endless Runner", "Auto-Scrolling", "Power-Ups",
      "Collectibles", "Upgrade System", "Score System"]),

    ("Spacewar!", 1962, "PDP-1", 1.5, 1, 2.5,
     ["Top-Down", "2D", "Fixed Screen", "Shooter/Shmup", "Physics-Based",
      "Projectile Combat", "Local Multiplayer"]),

    ("Asteroids", 1979, "Arcade", 1.5, 1, 2.5,
     ["Top-Down", "2D", "Fixed Screen", "Shooter/Shmup", "Physics-Based",
      "Projectile Combat", "Score System", "Lives System"]),

    ("Dr. Mario", 1990, "NES", 1.5, 1, 2.5,
     ["Side-View", "2D", "Fixed Screen", "Puzzle", "Level-Based",
      "Score System", "Local Multiplayer"]),

    ("Minesweeper", 1990, "Windows", 1.5, 1, 2.5,
     ["Top-Down", "2D", "Fixed Screen", "Puzzle", "Grid-Based"]),

    ("Bejeweled", 2000, "Web Browser", 1.5, 1, 2.5,
     ["Top-Down", "2D", "Fixed Screen", "Puzzle", "Grid-Based",
      "Score System"]),

    ("Doodle Jump", 2009, "Mobile", 1.5, 1, 2.5,
     ["Side-View", "2D", "Vertical Scrolling", "Auto-Scrolling", "Platformer",
      "Endless Runner", "Power-Ups", "Score System",
      "Procedural Generation"]),

    ("Missile Command", 1980, "Arcade", 1.5, 1.5, 3,
     ["Top-Down", "2D", "Fixed Screen", "Shooter/Shmup", "Wave-Based",
      "Score System", "Projectile Combat"]),

    ("Aldo's Adventure", 1987, "DOS", 1.5, 1.5, 3,
     ["Side-View", "2D", "Platformer", "Level-Based", "Collectibles",
      "Score System", "Lives System"]),

    ("Guitar Hero", 2005, "Console", 1.5, 1.5, 3,
     ["2D", "Rhythm", "Score System", "Level-Based", "Local Multiplayer",
      "Combo System"]),

    ("Maze War", 1974, "Imlac PDS-1", 2, 1, 3,
     ["First-Person", "3D", "Maze", "Shooter/Shmup", "Local Multiplayer",
      "Projectile Combat"]),

    ("Indy 500", 1977, "Atari 2600", 2, 1, 3,
     ["Top-Down", "2D", "Racing", "Score System", "Local Multiplayer"]),

    ("Lunar Lander", 1979, "Arcade", 2, 1, 3,
     ["Side-View", "2D", "Simulation", "Physics-Based", "Score System"]),

    ("Zork", 1980, "PDP-10", 2, 1, 3,
     ["Text Adventure", "Puzzle", "Inventory Management",
      "Save/Password System"]),

    ("Tetris", 1984, "Elektronika 60", 2, 1, 3,
     ["Side-View", "2D", "Fixed Screen", "Puzzle", "Score System",
      "Level-Based"]),

    ("Space Invaders", 1978, "Arcade", 1.5, 2, 3.5,
     ["Side-View", "2D", "Fixed Screen", "Shooter/Shmup", "Wave-Based",
      "Score System", "Lives System", "Projectile Combat",
      "Enemy AI/Pathfinding"]),

    ("Frogger", 1981, "Arcade", 1.5, 2, 3.5,
     ["Top-Down", "2D", "Fixed Screen", "Puzzle", "Grid-Based",
      "Score System", "Lives System", "Timer/Time Limit", "Level-Based"]),

    ("Moon Patrol", 1982, "Arcade", 1.5, 2, 3.5,
     ["Side-View", "2D", "Side-Scrolling", "Auto-Scrolling", "Shooter/Shmup",
      "Platformer", "Score System", "Projectile Combat"]),

    ("Super Solvers: Midnight Rescue!", 1989, "DOS", 1.5, 2, 3.5,
     ["Side-View", "2D", "Platformer", "Educational", "Puzzle",
      "Collectibles", "Timer/Time Limit"]),

    ("Super Solvers: OutNumbered!", 1990, "DOS", 1.5, 2, 3.5,
     ["Side-View", "2D", "Platformer", "Educational", "Puzzle",
      "Collectibles", "Timer/Time Limit"]),

    ("Tic-Tac-Toe", 1950, "Custom Hardware", 2, 1.5, 3.5,
     ["Top-Down", "2D", "Fixed Screen", "Puzzle", "Turn-Based", "Grid-Based",
      "Enemy AI/Pathfinding", "Local Multiplayer"]),

    ("Conway's Game of Life", 1970, "Mainframe", 2, 1.5, 3.5,
     ["Top-Down", "2D", "Simulation", "Grid-Based", "Sandbox"]),

    ("Pac-Man", 1980, "Arcade", 2, 1.5, 3.5,
     ["Top-Down", "2D", "Fixed Screen", "Maze", "Power-Ups", "Score System",
      "Lives System", "Collectibles", "Enemy AI/Pathfinding", "Level-Based"]),

    ("Donkey Kong", 1981, "Arcade", 2, 1.5, 3.5,
     ["Side-View", "2D", "Fixed Screen", "Platformer", "Score System",
      "Lives System", "Level-Based", "Enemy AI/Pathfinding"]),

    ("Rogue", 1980, "Unix", 2.5, 1, 3.5,
     ["Top-Down", "2D", "Roguelike", "RPG", "Turn-Based", "Grid-Based",
      "Procedural Generation", "Dungeon Crawling", "Permadeath",
      "Inventory Management", "Health System", "Melee Combat",
      "Leveling/XP", "Equipment System"]),

    ("River Raid", 1982, "Atari 2600", 2, 2, 4,
     ["Top-Down", "2D", "Vertical Scrolling", "Shooter/Shmup", "Score System",
      "Lives System", "Projectile Combat", "Procedural Generation"]),

    ("Super Mario Bros.", 1985, "NES", 2, 2, 4,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Power-Ups",
      "Level-Based", "Lives System", "Score System", "Collectibles",
      "Secret Areas", "Enemy AI/Pathfinding"]),

    ("Bubble Bobble", 1986, "Arcade", 2, 2, 4,
     ["Side-View", "2D", "Fixed Screen", "Platformer", "Power-Ups",
      "Co-op", "Collectibles", "Score System", "Level-Based",
      "Local Multiplayer", "Projectile Combat", "Boss Battles"]),

    ("StarGoose!", 1988, "Amiga", 2, 2, 4,
     ["Top-Down", "2D", "Vertical Scrolling", "Shooter/Shmup", "Power-Ups",
      "Score System", "Projectile Combat", "Lives System"]),

    ("Kirby's Dream Land", 1992, "Game Boy", 2, 2, 4,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Ability Copying",
      "Health System", "Lives System", "Boss Battles", "Level-Based"]),

    ("Kirby's Pinball Land", 1993, "Game Boy", 2, 2, 4,
     ["Side-View", "2D", "Pinball", "Physics-Based", "Score System",
      "Boss Battles", "Level-Based"]),

    ("Peggle", 2007, "PC", 2, 2, 4,
     ["Side-View", "2D", "Fixed Screen", "Puzzle", "Physics-Based",
      "Score System", "Level-Based", "Power-Ups"]),

    ("Line Rider", 2006, "PC", 3, 1, 4,
     ["Side-View", "2D", "Sandbox", "Physics-Based", "Simulation"]),

    ("Super Mario Bros. 2", 1988, "NES", 2, 2.5, 4.5,
     ["Side-View", "2D", "Side-Scrolling", "Vertical Scrolling", "Platformer",
      "Character Selection", "Level-Based", "Lives System", "Boss Battles",
      "Collectibles", "Enemy AI/Pathfinding"]),

    ("DuckTales", 1989, "NES", 2, 2.5, 4.5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Level-Based",
      "Collectibles", "Boss Battles", "Lives System", "Health System"]),

    ("Chip 'n Dale: Rescue Rangers", 1990, "NES", 2, 2.5, 4.5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Co-op",
      "Level-Based", "Boss Battles", "Lives System", "Health System",
      "Local Multiplayer", "Projectile Combat"]),

    ("Super Mario Land 2: 6 Golden Coins", 1992, "Game Boy", 2, 2.5, 4.5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Power-Ups",
      "Overworld Map", "Level-Based", "Lives System", "Boss Battles",
      "Collectibles", "Save/Password System", "Secret Areas"]),

    ("Dig Dug", 1982, "Arcade", 2.5, 2, 4.5,
     ["Side-View", "2D", "Fixed Screen", "Puzzle", "Level-Based",
      "Score System", "Lives System", "Enemy AI/Pathfinding",
      "Terrain Digging/Mining", "Projectile Combat"]),

    ("Tiny Wings", 2011, "Mobile", 2.5, 2, 4.5,
     ["Side-View", "2D", "Auto-Scrolling", "Physics-Based", "Score System",
      "Procedural Generation", "Endless Runner"]),

    ("The Legend of Zelda", 1986, "Famicom Disk System", 2, 3, 5,
     ["Top-Down", "2D", "Screen-by-Screen", "Action-Adventure", "Open World",
      "Inventory Management", "Dungeon Crawling", "Puzzle", "Health System",
      "Boss Battles", "Power-Ups", "Collectibles", "Save/Password System",
      "Projectile Combat", "Melee Combat", "Secret Areas",
      "NPC Interaction", "Enemy AI/Pathfinding"]),

    ("Castlevania", 1986, "Famicom Disk System", 2.5, 2.5, 5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Melee Combat",
      "Level-Based", "Health System", "Lives System", "Score System",
      "Boss Battles", "Collectibles", "Power-Ups", "Weapon Switching",
      "Enemy AI/Pathfinding"]),

    ("Contra", 1987, "Arcade", 2.5, 2.5, 5,
     ["Side-View", "2D", "Side-Scrolling", "Run-and-Gun", "Platformer",
      "Co-op", "Power-Ups", "Level-Based", "Lives System", "Boss Battles",
      "Local Multiplayer", "Projectile Combat", "Enemy AI/Pathfinding"]),

    ("Mega Man", 1987, "NES", 2.5, 2.5, 5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Run-and-Gun",
      "Ability Copying", "Health System", "Lives System", "Boss Battles",
      "Level-Based", "Projectile Combat", "Weapon Switching",
      "Enemy AI/Pathfinding"]),

    ("The Goonies II", 1987, "NES", 2.5, 2.5, 5,
     ["Side-View", "First-Person", "2D", "Action-Adventure", "Platformer",
      "Metroidvania", "Inventory Management", "Puzzle", "Health System",
      "Lives System", "NPC Interaction", "Melee Combat", "Projectile Combat",
      "Weapon Switching", "Save/Password System", "Open World"]),

    ("Metroid II: Return of Samus", 1991, "Game Boy", 2.5, 2.5, 5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Metroidvania",
      "Power-Ups", "Health System", "Boss Battles", "Projectile Combat",
      "Save/Password System", "Enemy AI/Pathfinding"]),

    ("Full Tilt Pinball", 1995, "PC", 2.5, 2.5, 5,
     ["Side-View", "2D", "Pinball", "Physics-Based", "Score System",
      "Level-Based", "Local Multiplayer"]),

    ("Hill Climb Racing", 2012, "Mobile", 2.5, 2.5, 5,
     ["Side-View", "2D", "Racing", "Physics-Based", "Upgrade System",
      "Collectibles", "Economy System"]),

    ("(Super) Motherload", 2013, "Adobe Flash", 2.5, 2.5, 5,
     ["Side-View", "2D", "Upgrade System", "Resource Gathering",
      "Economy System", "Terrain Digging/Mining", "Crafting",
      "Save/Password System"]),

    ("Marble Madness", 1984, "Arcade", 3, 2, 5,
     ["Isometric", "2D", "Pseudo-3D", "Racing", "Physics-Based",
      "Timer/Time Limit", "Level-Based", "Score System",
      "Local Multiplayer", "Enemy AI/Pathfinding"]),

    ("Pitfall!", 1982, "Atari 2600", 2.5, 3, 5.5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Score System",
      "Lives System", "Timer/Time Limit", "Collectibles"]),

    ("Mario Bros.", 1983, "Arcade", 2.5, 3, 5.5,
     ["Side-View", "2D", "Fixed Screen", "Platformer", "Co-op",
      "Wave-Based", "Score System", "Lives System", "Local Multiplayer",
      "Enemy AI/Pathfinding"]),

    ("Metroid", 1986, "Famicom Disk System", 2.5, 3, 5.5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Metroidvania",
      "Power-Ups", "Health System", "Boss Battles", "Projectile Combat",
      "Save/Password System", "Secret Areas", "Enemy AI/Pathfinding"]),

    ("Rampage", 1986, "Arcade", 2.5, 3, 5.5,
     ["Side-View", "2D", "Beat 'em Up", "Co-op", "Health System",
      "Score System", "Level-Based", "Destructible Terrain",
      "Local Multiplayer", "Character Selection", "Melee Combat"]),

    ("Castlevania II: Simon's Quest", 1987, "Famicom Disk System", 2.5, 3, 5.5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Action-Adventure",
      "RPG", "Open World", "Melee Combat", "Inventory Management",
      "NPC Interaction", "Day-Night Cycle", "Health System", "Lives System",
      "Leveling/XP", "Save/Password System", "Weapon Switching",
      "Economy System"]),

    ("Zelda II: The Adventure of Link", 1987, "Famicom Disk System", 2.5, 3, 5.5,
     ["Side-View", "Top-Down", "2D", "Platformer", "Action-Adventure", "RPG",
      "Melee Combat", "Magic/Spell System", "Leveling/XP", "Lives System",
      "Health System", "Overworld Map", "Dungeon Crawling", "NPC Interaction",
      "Boss Battles", "Random Encounters", "Save/Password System",
      "Enemy AI/Pathfinding"]),

    ("Mega Man 2", 1988, "NES", 2.5, 3, 5.5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Run-and-Gun",
      "Ability Copying", "Health System", "Lives System", "Boss Battles",
      "Level-Based", "Projectile Combat", "Weapon Switching",
      "Enemy AI/Pathfinding", "Save/Password System"]),

    ("The Guardian Legend", 1988, "NES", 2.5, 3, 5.5,
     ["Top-Down", "2D", "Vertical Scrolling", "Screen-by-Screen",
      "Action-Adventure", "Shooter/Shmup", "Power-Ups", "Health System",
      "Boss Battles", "Weapon Switching", "Projectile Combat",
      "Save/Password System", "NPC Interaction", "Enemy AI/Pathfinding"]),

    ("Teenage Mutant Ninja Turtles", 1989, "NES", 2.5, 3, 5.5,
     ["Side-View", "Top-Down", "2D", "Side-Scrolling", "Platformer",
      "Action-Adventure", "Character Selection", "Melee Combat",
      "Health System", "Lives System", "Level-Based",
      "Enemy AI/Pathfinding"]),

    ("Mega Man 3", 1990, "NES", 2.5, 3, 5.5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Run-and-Gun",
      "Ability Copying", "Health System", "Lives System", "Boss Battles",
      "Level-Based", "Projectile Combat", "Weapon Switching",
      "Enemy AI/Pathfinding", "Save/Password System"]),

    ("StarTropics", 1990, "NES", 2.5, 3, 5.5,
     ["Top-Down", "2D", "Action-Adventure", "Grid-Based", "Puzzle",
      "Dungeon Crawling", "Health System", "Lives System", "NPC Interaction",
      "Melee Combat", "Projectile Combat", "Boss Battles", "Level-Based",
      "Save/Password System", "Enemy AI/Pathfinding"]),

    ("Sonic the Hedgehog", 1991, "Sega Genesis", 2.5, 3, 5.5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Physics-Based",
      "Power-Ups", "Collectibles", "Boss Battles", "Level-Based",
      "Lives System", "Score System", "Secret Areas",
      "Enemy AI/Pathfinding"]),

    ("Mega Man X", 1993, "SNES", 2.5, 3, 5.5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Run-and-Gun",
      "Ability Copying", "Health System", "Lives System", "Boss Battles",
      "Level-Based", "Projectile Combat", "Weapon Switching",
      "Upgrade System", "Secret Areas", "Enemy AI/Pathfinding",
      "Save/Password System"]),

    ("Super Mario Bros. 3", 1988, "NES", 2.5, 3.5, 6,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Power-Ups",
      "Overworld Map", "Level-Based", "Lives System", "Score System",
      "Collectibles", "Boss Battles", "Inventory Management", "Mini-Games",
      "Secret Areas", "Enemy AI/Pathfinding"]),

    ("Super Mario World", 1990, "SNES", 2.5, 3.5, 6,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Power-Ups",
      "Overworld Map", "Level-Based", "Lives System", "Score System",
      "Collectibles", "Boss Battles", "Save/Password System",
      "Secret Areas", "Enemy AI/Pathfinding"]),

    ("Kirby's Adventure", 1993, "NES", 2.5, 3.5, 6,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Ability Copying",
      "Health System", "Lives System", "Boss Battles", "Level-Based",
      "Overworld Map", "Mini-Games", "Save/Password System",
      "Enemy AI/Pathfinding"]),

    ("The Legend of Zelda: Link's Awakening", 1993, "Game Boy", 2.5, 3.5, 6,
     ["Top-Down", "Side-View", "2D", "Screen-by-Screen", "Action-Adventure",
      "Dungeon Crawling", "Puzzle", "Inventory Management", "Health System",
      "Boss Battles", "Collectibles", "NPC Interaction", "Dialog System",
      "Save/Password System", "Melee Combat", "Projectile Combat",
      "Secret Areas", "Mini-Games", "Enemy AI/Pathfinding"]),

    ("Donkey Kong Country", 1994, "SNES", 2.5, 3.5, 6,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Co-op",
      "Character Selection", "Collectibles", "Boss Battles", "Overworld Map",
      "Level-Based", "Lives System", "Save/Password System", "Secret Areas",
      "Local Multiplayer", "Enemy AI/Pathfinding"]),

    ("The Legend of Zelda: Oracle of Ages", 2001, "Game Boy Color", 2.5, 3.5, 6,
     ["Top-Down", "2D", "Screen-by-Screen", "Action-Adventure",
      "Dungeon Crawling", "Puzzle", "Inventory Management", "Health System",
      "Boss Battles", "NPC Interaction", "Save/Password System",
      "Melee Combat", "Projectile Combat", "Secret Areas",
      "Enemy AI/Pathfinding"]),

    ("The Legend of Zelda: Oracle of Seasons", 2001, "Game Boy Color", 2.5, 3.5, 6,
     ["Top-Down", "2D", "Screen-by-Screen", "Action-Adventure",
      "Dungeon Crawling", "Puzzle", "Inventory Management", "Health System",
      "Boss Battles", "NPC Interaction", "Save/Password System",
      "Melee Combat", "Projectile Combat", "Secret Areas",
      "Enemy AI/Pathfinding"]),

    ("Zaxxon", 1981, "Arcade", 3, 3, 6,
     ["Isometric", "2D", "Pseudo-3D", "Shooter/Shmup", "Auto-Scrolling",
      "Score System", "Lives System", "Projectile Combat",
      "Enemy AI/Pathfinding"]),

    ("Lemmings", 1991, "Amiga", 3, 3, 6,
     ["Side-View", "2D", "Puzzle", "Simulation", "Level-Based",
      "Timer/Time Limit", "Enemy AI/Pathfinding"]),

    ("Worms", 1995, "Amiga", 3, 3, 6,
     ["Side-View", "2D", "Artillery", "Turn-Based", "Physics-Based",
      "Destructible Terrain", "Weapon Switching", "Health System",
      "Local Multiplayer", "Projectile Combat"]),

    ("Minecraft", 2009, "PC", 4, 2, 6,
     ["First-Person", "3D", "Sandbox", "Open World", "Crafting",
      "Resource Gathering", "Health System", "Inventory Management",
      "Day-Night Cycle", "Procedural Generation", "Melee Combat",
      "Projectile Combat", "Enemy AI/Pathfinding", "Online Multiplayer",
      "Co-op", "Local Multiplayer", "Save/Password System",
      "Terrain Digging/Mining"]),

    ("Final Fantasy", 1987, "NES", 3, 3.5, 6.5,
     ["Top-Down", "2D", "RPG", "Turn-Based", "Random Encounters",
      "Party-Based", "Magic/Spell System", "Inventory Management",
      "Equipment System", "Health System", "Leveling/XP", "Overworld Map",
      "Dungeon Crawling", "Boss Battles", "NPC Interaction",
      "Economy System", "Save/Password System", "Character Selection"]),

    ("Super Metroid", 1994, "SNES", 3, 3.5, 6.5,
     ["Side-View", "2D", "Side-Scrolling", "Platformer", "Metroidvania",
      "Power-Ups", "Health System", "Boss Battles", "Projectile Combat",
      "Save/Password System", "Secret Areas", "Enemy AI/Pathfinding"]),

    ("Harvest Moon", 1996, "SNES", 3, 3.5, 6.5,
     ["Top-Down", "2D", "Simulation", "Life Simulation", "Economy System",
      "NPC Interaction", "Day-Night Cycle", "Resource Gathering",
      "Save/Password System", "Timer/Time Limit"]),

    ("Pokémon Red and Blue", 1996, "Game Boy", 3.5, 3, 6.5,
     ["Top-Down", "2D", "RPG", "Turn-Based", "Random Encounters",
      "Party-Based", "Inventory Management", "Leveling/XP", "Health System",
      "Overworld Map", "NPC Interaction", "Economy System", "Boss Battles",
      "Collectibles", "Save/Password System", "Enemy AI/Pathfinding"]),

    ("Super Smash Bros.", 1999, "Nintendo 64", 3.5, 3, 6.5,
     ["Side-View", "3D", "Fighting", "Platformer", "Character Selection",
      "Power-Ups", "Health System", "Local Multiplayer", "Melee Combat",
      "Projectile Combat", "Level-Based"]),

    ("Luigi's Mansion", 2001, "GameCube", 3.5, 3, 6.5,
     ["Third-Person", "3D", "Action-Adventure", "Puzzle", "Health System",
      "Boss Battles", "Collectibles", "Save/Password System",
      "Enemy AI/Pathfinding"]),

    ("Super Monkey Ball", 2001, "GameCube", 3.5, 3, 6.5,
     ["Third-Person", "3D", "Puzzle", "Physics-Based", "Timer/Time Limit",
      "Level-Based", "Local Multiplayer", "Mini-Games", "Score System"]),

    ("The Legend of Zelda: A Link to the Past", 1991, "SNES", 3, 4, 7,
     ["Top-Down", "2D", "Action-Adventure", "Dungeon Crawling", "Puzzle",
      "Inventory Management", "Health System", "Boss Battles", "Power-Ups",
      "Collectibles", "NPC Interaction", "Save/Password System",
      "Melee Combat", "Projectile Combat", "Secret Areas", "Open World",
      "Overworld Map", "Enemy AI/Pathfinding", "Magic/Spell System"]),

    ("Breath of Fire II", 1994, "SNES", 3, 4, 7,
     ["Top-Down", "2D", "RPG", "Turn-Based", "Random Encounters",
      "Party-Based", "Magic/Spell System", "Inventory Management",
      "Equipment System", "Health System", "Leveling/XP", "Overworld Map",
      "Dungeon Crawling", "Boss Battles", "NPC Interaction",
      "Economy System", "Save/Password System", "Base Building"]),

    ("Maniac Mansion", 1987, "Commodore 64", 3.5, 3.5, 7,
     ["Side-View", "2D", "Point-and-Click Adventure", "Puzzle",
      "Inventory Management", "Character Selection", "Dialog System",
      "Save/Password System"]),

    ("Prince of Persia", 1989, "Apple II", 3.5, 3.5, 7,
     ["Side-View", "2D", "Platformer", "Melee Combat", "Health System",
      "Timer/Time Limit", "Level-Based", "Puzzle", "Physics-Based"]),

    ("Super Mario Kart", 1992, "SNES", 3.5, 3.5, 7,
     ["Third-Person", "2D", "Pseudo-3D", "Racing", "Power-Ups",
      "Character Selection", "Level-Based", "Local Multiplayer",
      "Projectile Combat", "Enemy AI/Pathfinding"]),

    ("Doom", 1993, "DOS", 3.5, 3.5, 7,
     ["First-Person", "Pseudo-3D", "FPS", "Weapon Switching",
      "Health System", "Level-Based", "Enemy AI/Pathfinding", "Boss Battles",
      "Projectile Combat", "Secret Areas", "Local Multiplayer"]),

    ("Crash Bandicoot", 1996, "PlayStation", 3.5, 3.5, 7,
     ["Third-Person", "3D", "Platformer", "Level-Based", "Collectibles",
      "Boss Battles", "Lives System", "Health System",
      "Save/Password System", "Overworld Map", "Secret Areas",
      "Enemy AI/Pathfinding"]),

    ("Final Fantasy Crystal Chronicles", 2003, "GameCube", 3.5, 3.5, 7,
     ["Top-Down", "3D", "RPG", "Action-Adventure", "Real-Time Combat",
      "Co-op", "Dungeon Crawling", "Magic/Spell System",
      "Equipment System", "Health System", "Boss Battles", "Collectibles",
      "Crafting", "Local Multiplayer", "Save/Password System"]),

    ("Quake", 1996, "DOS", 4, 3, 7,
     ["First-Person", "3D", "FPS", "Weapon Switching", "Health System",
      "Level-Based", "Enemy AI/Pathfinding", "Boss Battles",
      "Projectile Combat", "Secret Areas", "Local Multiplayer",
      "Online Multiplayer"]),

    ("Portal", 2007, "PC", 4, 3, 7,
     ["First-Person", "3D", "Puzzle", "FPS", "Physics-Based", "Level-Based",
      "Save/Password System"]),

    ("Rocket League", 2015, "Console; PC", 4.5, 2.5, 7,
     ["Third-Person", "3D", "Sports", "Racing", "Physics-Based",
      "Online Multiplayer", "Local Multiplayer"]),

    ("EarthBound", 1994, "SNES", 3, 4.5, 7.5,
     ["Top-Down", "2D", "RPG", "Turn-Based", "Party-Based",
      "Magic/Spell System", "Inventory Management", "Equipment System",
      "Health System", "Leveling/XP", "Overworld Map", "Boss Battles",
      "NPC Interaction", "Dialog System", "Economy System",
      "Save/Password System", "Enemy AI/Pathfinding"]),

    ("Secret of Mana", 1993, "SNES", 3.5, 4, 7.5,
     ["Top-Down", "2D", "RPG", "Action-Adventure", "Real-Time Combat",
      "Co-op", "Party-Based", "Magic/Spell System", "Weapon Switching",
      "Health System", "Leveling/XP", "Boss Battles", "Overworld Map",
      "NPC Interaction", "Save/Password System", "Local Multiplayer",
      "Melee Combat", "Enemy AI/Pathfinding"]),

    ("Star Fox", 1993, "SNES", 3.5, 4, 7.5,
     ["Third-Person", "3D", "Pseudo-3D", "Rail Shooter", "Projectile Combat",
      "Health System", "Boss Battles", "Score System", "Level-Based",
      "Enemy AI/Pathfinding"]),

    ("Doom II: Hell on Earth", 1994, "DOS", 3.5, 4, 7.5,
     ["First-Person", "Pseudo-3D", "FPS", "Weapon Switching",
      "Health System", "Level-Based", "Enemy AI/Pathfinding", "Boss Battles",
      "Projectile Combat", "Secret Areas", "Local Multiplayer"]),

    ("Pikmin", 2001, "GameCube", 4, 3.5, 7.5,
     ["Third-Person", "3D", "Real-Time Strategy (RTS)", "Puzzle",
      "Timer/Time Limit", "Resource Gathering", "Health System",
      "Boss Battles", "Save/Password System", "Enemy AI/Pathfinding"]),

    ("Double Dragon", 1987, "Arcade", 3.5, 4.5, 8,
     ["Side-View", "2D", "Side-Scrolling", "Beat 'em Up", "Co-op",
      "Melee Combat", "Health System", "Lives System", "Level-Based",
      "Boss Battles", "Score System", "Local Multiplayer",
      "Weapon Switching", "Enemy AI/Pathfinding"]),

    ("Animal Crossing", 2001, "Nintendo 64", 3.5, 4.5, 8,
     ["Top-Down", "3D", "Life Simulation", "Sandbox", "Day-Night Cycle",
      "NPC Interaction", "Collectibles", "Economy System",
      "Save/Password System", "Dialog System"]),

    ("The Secret of Monkey Island", 1990, "DOS", 4, 4, 8,
     ["Side-View", "2D", "Point-and-Click Adventure", "Puzzle",
      "Inventory Management", "Dialog System", "Save/Password System",
      "NPC Interaction"]),

    ("Day of the Tentacle", 1993, "DOS", 4, 4, 8,
     ["Side-View", "2D", "Point-and-Click Adventure", "Puzzle",
      "Inventory Management", "Dialog System", "Character Selection",
      "Save/Password System", "NPC Interaction"]),

    ("Chrono Trigger", 1995, "SNES", 3.5, 5, 8.5,
     ["Top-Down", "2D", "RPG", "Turn-Based", "Party-Based",
      "Magic/Spell System", "Inventory Management", "Equipment System",
      "Health System", "Leveling/XP", "Overworld Map", "Boss Battles",
      "NPC Interaction", "Dialog System", "Economy System",
      "Save/Password System", "Multiple Endings", "Combo System",
      "Enemy AI/Pathfinding"]),

    ("Diablo", 1996, "Windows", 3.5, 5, 8.5,
     ["Isometric", "2D", "RPG", "Action-Adventure", "Real-Time Combat",
      "Dungeon Crawling", "Procedural Generation", "Inventory Management",
      "Equipment System", "Health System", "Leveling/XP", "Boss Battles",
      "Magic/Spell System", "Economy System", "Melee Combat",
      "Projectile Combat", "Online Multiplayer", "Character Selection",
      "Save/Password System", "Enemy AI/Pathfinding"]),

    ("Warcraft: Orcs & Humans", 1994, "DOS", 4.5, 4, 8.5,
     ["Top-Down", "2D", "Real-Time Strategy (RTS)", "Base Building",
      "Resource Gathering", "Fog of War", "Level-Based",
      "Local Multiplayer", "Enemy AI/Pathfinding", "Projectile Combat",
      "Melee Combat", "Save/Password System"]),

    ("Super Mario 64", 1996, "Nintendo 64", 4.5, 4, 8.5,
     ["Third-Person", "3D", "Platformer", "Open World", "Collectibles",
      "Power-Ups", "Health System", "Lives System", "Boss Battles",
      "Save/Password System", "Secret Areas", "Enemy AI/Pathfinding"]),

    ("SimCity", 1989, "Amiga", 5, 3.5, 8.5,
     ["Top-Down", "2D", "City Builder", "Simulation", "Sandbox",
      "Economy System", "Save/Password System"]),

    ("Final Fantasy VIII", 1999, "PlayStation", 4, 5, 9,
     ["Top-Down", "3D", "RPG", "Turn-Based", "Party-Based",
      "Magic/Spell System", "Inventory Management", "Equipment System",
      "Health System", "Leveling/XP", "Overworld Map", "Boss Battles",
      "NPC Interaction", "Dialog System", "Economy System",
      "Save/Password System", "Mini-Games", "Enemy AI/Pathfinding"]),

    ("The Legend of Zelda: Ocarina of Time", 1998, "Nintendo 64", 4.5, 4.5, 9,
     ["Third-Person", "3D", "Action-Adventure", "Dungeon Crawling",
      "Puzzle", "Inventory Management", "Health System", "Boss Battles",
      "Collectibles", "NPC Interaction", "Dialog System",
      "Save/Password System", "Melee Combat", "Projectile Combat",
      "Secret Areas", "Open World", "Overworld Map",
      "Enemy AI/Pathfinding", "Day-Night Cycle", "Mini-Games",
      "Weapon Switching"]),

    ("Metroid Prime", 2002, "GameCube", 4.5, 4.5, 9,
     ["First-Person", "3D", "FPS", "Metroidvania", "Power-Ups",
      "Health System", "Boss Battles", "Projectile Combat",
      "Save/Password System", "Secret Areas", "Puzzle",
      "Enemy AI/Pathfinding"]),

    ("The Legend of Zelda: The Wind Waker", 2002, "GameCube", 4.5, 4.5, 9,
     ["Third-Person", "3D", "Action-Adventure", "Open World",
      "Dungeon Crawling", "Puzzle", "Inventory Management", "Health System",
      "Boss Battles", "Collectibles", "NPC Interaction", "Dialog System",
      "Save/Password System", "Melee Combat", "Projectile Combat",
      "Secret Areas", "Day-Night Cycle", "Enemy AI/Pathfinding",
      "Weapon Switching"]),

    ("SimCity 2000", 1993, "Macintosh", 5, 4, 9,
     ["Isometric", "2D", "City Builder", "Simulation", "Sandbox",
      "Economy System", "Save/Password System"]),

    ("Gran Turismo", 1997, "Console", 5, 4, 9,
     ["Third-Person", "3D", "Racing", "Simulation", "Physics-Based",
      "Level-Based", "Economy System", "Upgrade System", "Collectibles",
      "Save/Password System", "Enemy AI/Pathfinding"]),

    ("FTL: Faster Than Light", 2012, "PC", 4.5, 5, 9.5,
     ["Top-Down", "2D", "Roguelike", "Real-Time Combat",
      "Procedural Generation", "Permadeath", "Resource Gathering",
      "Upgrade System", "Weapon Switching", "Health System", "Boss Battles",
      "Random Encounters", "Save/Password System",
      "Enemy AI/Pathfinding"]),

    ("SimCity 3000", 1999, "Windows", 5, 4.5, 9.5,
     ["Isometric", "2D", "City Builder", "Simulation", "Sandbox",
      "Economy System", "Save/Password System"]),

    ("Dune II: The Building of a Dynasty", 1992, "DOS", 5, 5, 10,
     ["Top-Down", "2D", "Real-Time Strategy (RTS)", "Base Building",
      "Resource Gathering", "Fog of War", "Level-Based",
      "Enemy AI/Pathfinding", "Projectile Combat",
      "Save/Password System"]),

    ("Command & Conquer", 1995, "DOS", 5, 5, 10,
     ["Top-Down", "2D", "Real-Time Strategy (RTS)", "Base Building",
      "Resource Gathering", "Fog of War", "Level-Based",
      "Local Multiplayer", "Enemy AI/Pathfinding", "Projectile Combat",
      "Save/Password System"]),

    ("Warcraft II: Tides of Darkness", 1995, "DOS", 5, 5, 10,
     ["Top-Down", "2D", "Real-Time Strategy (RTS)", "Base Building",
      "Resource Gathering", "Fog of War", "Level-Based",
      "Local Multiplayer", "Online Multiplayer", "Enemy AI/Pathfinding",
      "Projectile Combat", "Melee Combat", "Save/Password System"]),

    ("StarCraft", 1998, "Windows", 5, 5, 10,
     ["Top-Down", "2D", "Isometric", "Real-Time Strategy (RTS)",
      "Base Building", "Resource Gathering", "Fog of War", "Level-Based",
      "Local Multiplayer", "Online Multiplayer", "Enemy AI/Pathfinding",
      "Projectile Combat", "Melee Combat", "Save/Password System"]),

    ("Age of Empires II: The Age of Kings", 1999, "Windows", 5, 5, 10,
     ["Isometric", "2D", "Real-Time Strategy (RTS)", "Base Building",
      "Resource Gathering", "Fog of War", "Level-Based",
      "Local Multiplayer", "Online Multiplayer", "Enemy AI/Pathfinding",
      "Projectile Combat", "Melee Combat", "Save/Password System",
      "Upgrade System"]),

    ("EverQuest", 1999, "Windows", 5, 5, 10,
     ["First-Person", "Third-Person", "3D", "RPG", "Real-Time Combat",
      "Online Multiplayer", "Party-Based", "Magic/Spell System",
      "Inventory Management", "Equipment System", "Health System",
      "Leveling/XP", "Open World", "Dungeon Crawling", "Boss Battles",
      "NPC Interaction", "Economy System", "Save/Password System",
      "Melee Combat", "Projectile Combat", "Enemy AI/Pathfinding"]),

    ("Roller Coaster Tycoon", 1999, "PC", 5, 5, 10,
     ["Isometric", "2D", "Management/Tycoon", "Simulation", "Sandbox",
      "Economy System", "Save/Password System", "Enemy AI/Pathfinding"]),

    ("The Sims", 2000, "Windows", 5, 5, 10,
     ["Isometric", "3D", "Life Simulation", "Simulation", "Sandbox",
      "Economy System", "NPC Interaction", "Save/Password System",
      "Enemy AI/Pathfinding"]),
]


def main():
    header = ["Game", "Year", "Platform", "Complexity", "Scope",
              "Combined Score"] + mechanics

    rows = []
    for name, year, platform, complexity, scope, combined, game_mechs in games_data:
        row = [name, year, platform, complexity, scope, combined]
        for m in mechanics:
            row.append("X" if m in game_mechs else "")
        rows.append(row)

    with open("/home/ceafin/Documents/GameDevNotes/Game Mechanics Matrix.csv",
              "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)

    print(f"Generated matrix: {len(rows)} games × {len(mechanics)} mechanics")
    # Verify no typos in mechanic names
    all_used = set()
    for _, _, _, _, _, _, game_mechs in games_data:
        for m in game_mechs:
            all_used.add(m)
    unknown = all_used - set(mechanics)
    if unknown:
        print(f"WARNING: Unknown mechanics used: {unknown}")
    unused = set(mechanics) - all_used
    if unused:
        print(f"INFO: Unused mechanic columns: {unused}")


if __name__ == "__main__":
    main()
