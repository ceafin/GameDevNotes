# 'Gaiscígh Na Mórrígne' _(Working Title)_: Game Design Document & Player Manual

>  **Mór-Ríoghain** *(often anglicized as The Morrígan)* is a powerful and enigmatic goddess from Irish mythology. Her name translates from modern Irish as "Great Queen" or "Phantom Queen". She is primarily revered as a deity of war, destiny, prophecy, and sovereignty.

A top-down explore + party-battle RPG set in Irish myth, climaxing at the Second Battle of Mag Tuired.

**Source DNA:** Zelda: A Link to the Past (exploration) x Valkyrie Profile (gather-the-dead + roster tithe) x Indivisible (battle input model).

---
## 0. How to use this doc

- **Living document.** Two parts: **Part I** is the developer spec (GDD). **Part II** is the player-facing manual (old-school instruction booklet voice).
- **Title is a placeholder.** See Open Questions (§16) for candidates. Nothing is named yet.
- **Every design element is tagged** so myth-fact and invention never blur:

| Tag | Meaning |
|---|---|
| `[CANON]` | Faithful to the Mythological Cycle / Cath Maige Tuired |
| `[LICENSE]` | Deliberate deviation from myth, justified in-fiction |
| `[DESIGN]` | Pure game invention, no myth claim |
| `[OPEN]` | Not yet decided |

---
# PART I — GAME DESIGN DOCUMENT

## 1. Vision & pillars

**Pitch:** You play the Morrígan, chooser of the slain. You roam an Ireland sliding toward doom, mark fallen heroes for resurrection, forge them into a war-host, and spend them against a foretold apocalypse. Explore like ALttP; fight like Valkyrie Profile by way of Indivisible.

**Design pillars (in priority order):**

1. **The dead are a resource you both wield and surrender.** Recruiting, strengthening, and giving away champions is the spine of the game, not a side system.
2. **One combat system, entered many ways.** The overworld never deals damage; it only decides *when* and *on whose terms* a battle starts.
3. **A countdown you can feel.** The march to Mag Tuired is a clock, not a mood. Time is the scarce resource.
4. **Myth as mechanic, not skin.** The resurrection well, the muster, the four treasures, and Balor's eye are load-bearing systems, not decoration.

---

## 2. Build philosophy (from your Godot reference card)

Non-negotiable guardrails carried over from `godot-dev-reference.md`:

- **Build the dumb specific version first.** Structure crystallizes from repetition, never from a blank page.
- **Lift structure only when it hurts.** No autoload, bus, or persistent-root until a concrete wall demands it.
- **Grow from one verb.** A rectangle that fights beats a perfect plan.
- **Build order is NOT story order.** You build the vertical slice (§15) first and design Act 1 last.
- **Local stays local; only the genuinely global gets lifted out.**

> Everything in this doc is the *target*, not the build sequence. Read §15 before writing a line of code.

---

## 3. Player role: the Morrígan

- `[CANON]` The Morrígan incites and emboldens warriors and prophesies the slain. She is not a rank-and-file combatant in the battle line.
- `[DESIGN]` **In the overworld she MARKS prey; she never swings for damage.** The mark is the battle trigger.
- `[DESIGN]` **In battle she commands and emboldens; champions take the hits and do the killing.** She is never a targetable HP bar.
- `[DESIGN]` **No player-character handoff.** You are the Morrígan start to finish. The changing *roster* carries the generational shift (Nuada falls, Lugh rises), so there is no jarring PC swap.

---

## 4. Mode architecture

Two modes, cleanly separated. This separation is the whole reason the scope stays sane.

| Mode | Camera / feel | Does | Never does |
|---|---|---|---|
| **Explore** | Top-down, ALttP | Push, pull, interact, puzzle-solve, dialog, navigate, **mark enemies** | Deal combat damage |
| **Battle** | Dedicated side-on screen | All combat: 4-champion party fight | Platforming, traversal physics |

**The trigger layer (how a battle starts):**

| Overworld event | Result | Precedent |
|---|---|---|
| Avoid the enemy | No fight, no souls | Chrono Trigger (visible field foes) `[CANON-game]` |
| **Mark it first** (Morrígan's strike) | Battle launches, party carries a **first-strike seed** | Paper Mario / Super Mario RPG first-strike |
| Enemy bumps you | Battle launches, **enemy** gets the seed | same, inverted |
| Story / dialog trigger | Same battle screen, scripted seed | JRPG set-piece |

- **One damage model, several doors in.** The slash is a *trigger*, not a hit. This is the single decision that keeps you at one combat system.
- **Trigger default is `[OPEN]`:** contact-based (touch = load battle) vs placed set-pieces (scripted). Likely a mix; pick the *default* and treat the other as the exception.

---

## 5. Combat system (battle mode)

`[DESIGN]` Indivisible's **input model** dropped onto a **dedicated battle screen** (Indivisible fought on the traversal terrain; you do not, which is actually simpler because the two modes never share physics).

| Element | Rule |
|---|---|
| Party size | 4 champions on screen, one per face button |
| Attacks | Press a champion's button to act; each has its own action bar / cooldown |
| Directional moves | Neutral / up (launch) / down (break), per champion |
| Defense | Hold a champion's button to block with timing; a clean block negates damage |
| Meter | Landing hits and clean blocks fills a shared gauge; full gauge = a **god-finisher** (Spear of Lugh, Dagda's club, etc.) |
| Morrígan | Off the HP grid; provides the **embolden / incite** layer (buffs, marks, finisher enablers) |
| Party config | **Menu-based, off-screen** (Chrono Trigger / VP style), not real-time swapping |

**Two independent axes you resolved (do not re-confuse them):**

- *Party config:* menu / off-screen `[chosen]` vs real-time like Link.
- *Roster persistence:* VP transfer-out `[chosen]` vs fixed cast. See §6.

**Confirmed Indivisible reference points** (verified): four members mapped to face buttons, send them singly or all at once; a charge meter fills on hits and blocks and unleashes finishers; explicitly VP-inspired row combat plus Skullgirls combo sensibility.

`[DESIGN]` **Champion weapon identity is where the Mechanics catalog's combat archetypes actually land.** With the Morrígan carrying no weapon-upgrade line of her own, the "Primary melee line," "Returning/stun weapon," "Shields & active defense," and "Elemental/magic projectiles" archetypes (`Base Collection in Theme.md` / `Base Collection Matrix.md` §A) are a ready-made pool of distinct per-champion kits rather than one shared player kit — e.g. one champion built around a Brigidine forged-weapon melee line, another around thrown ogham-stone stun tools, another around well-fire elemental projectiles. Assigning archetypes per champion also gives the 4-button battle roster mechanical variety for free, on top of the geasa identity layer from §6.

---

## 6. Roster & the Muster (the heavy system)

> **BUILD-ORDER FLAG:** This is the single heaviest system in the design and a `lift-it-when-it-hurts` system. It is **NOT** in the vertical slice. It only becomes possible once chapters exist.

The VP transfer loop, re-skinned to myth. Your champions are simultaneously your **army** and your **tax**.

| VP mechanic | This game | Myth basis |
|---|---|---|
| Collect souls of the slain | Morrígan marks the fallen; they rise as champions | `[CANON]` Morrígan as chooser of the slain |
| Materialize / heal at Valhalla | **Well of Sláine** hub, run by Dian Cécht + children | `[CANON]` Tipra Sláíne at Achad Abla |
| Periods (finite time per chapter) | **The omen / blight clock** counting to Mag Tuired | `[LICENSE]` the foretold battle is the deadline |
| Sacred Phase tithe (send 1 to 2 up) | **The Muster levy**: send champions "forward to the host" each act | `[CANON]` Lugh's muster roll-call |
| Sent einherjar leave until endgame | Levied champions leave the roster; **survivors return for Mag Tuired II** | `[CANON]` sent host marches back |
| Hero Value + trait requirements | Worthiness gate on who satisfies the levy | `[DESIGN]` |
| Evaluation → ending + rewards | **War-effort variable** → final-battle difficulty + ending branch | `[DESIGN]` |
| Materialize Points economy | Well output + **Airmed's herbs** crafting | `[CANON]` 365 herbs from Miach's grave |

**The cost of avoidance (the important nuance):**

- VP **never** punishes dodging a single fight directly. There is no nag meter.
- The cost is **deferred and structural**: combat is the only forge for worthy champions, and the levy comes due every act. Avoid everything → weak levy → war-effort craters → harder climax and worse ending.
- `[DESIGN-RULE]` **Do NOT build a crude "you avoided too much" penalty counter.** Copy VP's indirection. The clock plus the mandatory levy do the work.

`[DESIGN]` **The unmarked and the unclaimed dead have somewhere to go, diegetically.** Every fallen warrior the Morrígan doesn't choose doesn't just vanish from the fiction — the Bestiary already has the right creatures for this: **Sluagh** (soul-stealing host of the restless, unforgiven dead) and **Battle-Mist Wraiths / Scáth Catha** (ghosts bound to old battlefields) are the visible fate of the fallen she passed over. They can populate the fields and old battlegrounds as ambient overworld threats — a quiet, worldbuilt answer to "what happens to strength you didn't earn" instead of a UI counter, and a visual tell that reinforces the clock without narrating it.

**Permanent loss (myth-grounded):**

- `[CANON]` The Well cannot heal decapitation or destroyed brain/spine. `[DESIGN]` Use this as the diegetic rule for **permadeath**: certain deaths are beyond the Well, and levied champions can die "at the front" and never return (VP: sent einherjar can die in Valhalla).

**Known failure mode + mitigations:**

- Players bond with a strong champion, then are forced to give them away and fight on with weaklings.
- Mitigate with: a **large cast**, **survivors-return-at-the-end**, and clear signalling of *why* the levy matters. `[OPEN]` exact release-valve tuning.

**Fomorian sabotage (escalation, free from myth):**

- `[CANON]` The Fomorian Octriallach has every man cast a stone to bury the Well under a cairn. `[DESIGN]` Your resurrection hub becomes an **attackable objective** late-game: sabotage throttles or halts recruitment during the climax.

**Champion geasa (binding the roster to myth):** `[DESIGN]` `[OPEN — build-order: same as the rest of §6, not in the vertical slice]` The Mechanics doc's geasa system (taboo-obligations that grant power when kept, ruin when broken — see `Base Collection Matrix.md` §E) was originally scoped as trinkets the player-character wears. With the Morrígan off the HP grid and never fighting directly, it fits the roster better than it fits her: **bind geasa to individual champions instead.** A champion carries their own taboo as part of their identity and battle-screen kit — Cú Chulainn's own dog-geis is a ready-made template (`[CANON hook]`, buff vs. hounds, taboo against harming them), and this gives every recruit a distinct build-defining hook beyond raw stats, which directly helps the "known failure mode" above: a champion you're about to lose to the levy is easier to let go of if their geis made them mechanically unique, not just numerically strong.

---

## 7. Progression economy

| Source | Feeds |
|---|---|
| Battle spoils | Champion strength, materialize resource |
| **Well of Sláine** (Dian Cécht) | Resurrect + heal + strengthen |
| **Airmed's herbs** | Crafting / upgrade tree (`[CANON]` 365 herbs, one per joint/sinew) |
| **Forge trio** Goibniu, Credne, Luchta | Weapon crafting + battlefield resupply `[CANON]` |

`[LICENSE]` **Brigid's patronage lives here, not on the four treasures.** She's a real Tuatha Dé Danann figure (goddess of smithcraft, healing, and poetry) with no seat at the table in §13's cast yet — rather than inventing her a scene appearance, fold her in as the blessing behind the mechanical shape of this economy: the Well of Sláine's healing rites and Airmed's herb-craft can diegetically invoke her fire and wells alongside Dian Cécht's and Airmed's own work, without touching their `[CANON]` roles. This also validates the tech: the Mechanics Matrix's shrine-offering stat-growth pattern and its well-coin/barter dual-currency pattern are already the right technical shape for this table — nothing new needs designing there, just building.

---

## 8. Story structure (three acts)

`[LICENSE]` The two battles of Mag Tuired are split to bookend the game. Most of the "middle" is already chronologically between the battles in the source; only the four-treasures quest is relocated inward.

| | Act 1: First Battle | Act 2: The Long Middle | Act 3: Second Battle |
|---|---|---|---|
| Enemy | Fir Bolg (Sreng) | Bres's regime + Fomorian tribute | Fomorians (Balor) |
| World | Living land only | Otherworld / sídhe opens | The battlefield |
| Boss | Sreng (duel) | Tribute-collectors / mini-bosses | Balor (eye timing) |
| Emotional beat | Win the war, lose your king | Arm saga + Miach mercy choice | Nuada dies; Lugh's sling wins it |

- **Break 1→2 = downturn** `[CANON]`: the battle is won but Nuada loses his arm and thus his kingship (a king must be whole), and the tyrant Bres rises.
- **Break 2→3 = upswing** `[CANON]`: Nuada healed and restored, Lugh arrives, the host is mustered.
- **Four-treasures relocation justification** `[LICENSE]`: under Bres's misrule the treasures decayed or were paid to the Fomorians as tribute, so Act 2 recovers them. Causality stays tight.

**Chapter breakdown (VP-style periods per chapter):**

| Chapter | Content | Role |
|---|---|---|
| Ch 0 | Fir Bolg prologue: Sreng, Nuada loses the arm | Tutorial |
| Ch 1 to 3 | Bres's misrule; blight climbs; recover the four cities/treasures; craft-gods join | Body of Act 2 |
| Ch 4 to 5 | Lugh arrives; the muster; Well goes live; Fomorians sabotage the Well | Act 2 → 3 pivot |
| Ch 6 | Cath Maige Tuired II: Balor | Climax |

---

## 9. Overworld: four cities = four dungeons

`[CANON]` The Tuatha Dé came from four cities, each with a sage and a treasure. This is a ready-made ALttP "collect the set, then prove worthy" structure (pendants → treasures).

| City | Sage | Treasure | `[DESIGN]` gate function |
|---|---|---|---|
| Falias | Morfesa | Lia Fáil (Stone of Destiny) | Reveals true / kingly paths |
| Gorias | Esras | Spear of Lugh | Ranged pierce tool |
| Findias | Uscias | Sword of Nuada (Claíomh Solais) | Light / reveal + cut-through |
| Murias | Semias | Dagda's Cauldron | Heal / life resource |

**Naming reconciliation (resolves a conflict with the Mechanics doc):** `Base Collection Matrix.md` independently proposed a "relics of Bríd" flavor for the generic keys/MacGuffins archetype, written before this four-treasures structure existed. `[CANON]` **The four treasures keep their real names** — Lia Fáil, Spear of Lugh, Sword of Nuada, Dagda's Cauldron. They are not renamed to Brigid relics; that would trade specific, load-bearing mythology (pillar 4) for a generic patron-goddess skin. Brigid's patronage is rescoped to the systems that were actually still unnamed — see §7's note on the Well of Sláine and shrine-offering economy, and §6's note on champion geasa.

`[DESIGN]` **The treasures already are the Morrígan's traversal/puzzle-gating kit, not a separate item list.** Cross-referencing the Mechanics catalog's boots/lifting-gear/water-traversal/grapple archetypes: those still belong to her (she still pushes, pulls, and navigates puzzles in Explore mode), and the four treasures' `[DESIGN] gate function` column already reads like exactly that toolkit — Lia Fáil for hidden/kingly paths, the Spear for ranged switches, the Sword for light-and-cut gates, the Cauldron as a resource gate. No new gear needs inventing; the four treasures are the ALttP-style item progression, reskinned. Champion weapon archetypes (melee lines, shields, elemental projectiles) are a separate pool — see §5's note.

---

## 10. Two-world overlay `[DESIGN]` `[OPEN-flavor]`

- One overlay axis only (avoid inventing a third mechanic). Same map, two states, swap to solve overworld gates.
- **Flavor choice not finalized:** living land vs sídhe/Otherworld, OR pre-blight vs Fomorian-blighted. Pick one.
- Opens in Act 2 (the sages and treasures live across the overlay).

---

## 11. Branching & endings

`[DESIGN]` VP-style A/B/C outcomes tied to **multiple variables**, not one meter:

| Variable | Set by | Affects |
|---|---|---|
| **Miach spared?** | Prevent Dian Cécht's jealousy `[CANON hook]` | Well quality; Nuada's arm state |
| **Nuada alive at climax?** | War-effort + player choices | Who leads; ending tone (canonically he dies to Balor) |
| **Muster strength vs Well sabotage** | Levy quality + how hard the Well is defended | Whether Mag Tuired is winnable cleanly |

---

## 12. The climax: Cath Maige Tuired II

`[CANON]` The battle has built-in phases; use them directly.

1. **Attrition war.** Goibniu's forge + Dian Cécht's Well give you the edge, until the Fomorians sabotage both (Octriallach's stones; Goibniu targeted).
2. **Balor opens the eye.** Its gaze withers what it sees. Canonically the lid is so heavy it needs several men to lift, so **telegraph it heavily** (a long, dread wind-up).
3. **Lugh's sling finisher.** A stone drives the eye back through Balor's skull so its gaze destroys the Fomorian host behind him. `[DESIGN]` The final input is a **timing / aim finisher, not a DPS check.**

---

## 13. Cast & roles (master table)

| Figure | Role in game | First appears | Tag |
|---|---|---|---|
| **The Morrígan** | Player character; inciter; marks prey; evaluator | Ch 0 | `[CANON]` |
| **Badb** | The Morrígan's own triad-aspect (with Macha) — myth-confirmed; in-game role (mirror/foil, recruitable champion, or narrative-only) not yet decided | not yet decided | `[CANON]` myth basis, `[OPEN]` usage |
| **Nuada** | Act 1 anchor champion; king to keep alive; arm saga; dies to Balor | Ch 0 | `[CANON]` |
| **Lugh** | Joins Act 2, spearheads Act 3; sling-finisher; Dian Cécht's grandson | Ch 4 | `[CANON]` |
| **Dian Cécht** | Runs the Well (recruit/heal/strengthen hub); jealousy subplot; Lugh's grandfather | Ch 1 | `[CANON]` |
| **Miach** | Regrows Nuada's arm; murdered by Dian Cécht = **moral branch** | Ch 2 to 3 | `[CANON]` |
| **Airmed** | 365-herb crafting/upgrade tree; mourns Miach | Ch 2 to 3 | `[CANON]` |
| **Bres** | Act 1→2 antagonist; misrule brings the Fomorians | Ch 1 | `[CANON]` |
| **Sreng** | Prologue duel (cuts Nuada's arm); optional rematch | Ch 0 | `[CANON]` |
| **Balor** | Final boss; the eye | Ch 6 | `[CANON]` |
| **Goibniu / Credne / Luchta** | Forge trio: weapon crafting + battlefield resupply | Ch 1 to 3 | `[CANON]` |
| **The Dagda** | Heavy party member; captured-under-Bres beat; harp utility; cauldron | Ch 2 to 3 | `[CANON]` |
| **Ogma** | Champion; sidequest to recover the sword Orna | Ch 2 to 3 | `[CANON]` |

---

## 14. Godot architecture (your conventions)

**Toolchain:** Godot 4.6+, GDScript (version-tied), VSCodium + godot-tools (LSP), Git/GitHub, Kubuntu 26 LTS. Static typing enforced (`untyped_declaration = 2`), `unsafe_* = 1` (warn).

**Autoloads = DATA / services (keep to ~2 to 5):**

| Autoload | Holds |
|---|---|
| `GameState` | Session-global: war-effort, act/chapter, levy record, unlocked treasures, endings flags |
| `AudioManager` | Music/SFX |
| `MusterState` `[later]` | Roster, hero-values, who has been levied, who survives |
| `BlightClock` `[later]` | The omen/period counter |
| `SceneManager` `[optional]` | Structural level swap |

> The muster/clock autoloads are Act-structure systems. Do not create them for the slice.

**Persistent root scene = STRUCTURE (adopt only when HUD/music start rebuilding):**

```
Main (Node)                 <- never freed
├── CurrentWorld (Node)     <- explore scenes swap here
├── BattleLayer (Node)      <- battle scene instantiated here on trigger
├── HUD (CanvasLayer)       <- persists across swaps
└── PauseMenu (CanvasLayer) <- process_mode = When Paused
```

**Signal three tiers, applied here:**

| Tier | Use | Examples |
|---|---|---|
| 1: direct (signal-up / call-down) | Parent/child that own each other | battle screen → `champion.take_damage()`; `champion.died` up to the battle controller |
| 2: autoload data + `_changed` | Shared state | `GameState.war_effort_changed`, `BlightClock.period_advanced`, `MusterState.roster_changed` |
| 3: SignalBus (sparingly, ~8 total) | Genuinely game-wide moments, no owner | `battle_started`, `battle_won`, `champion_levied`, `well_sabotaged`, `boss_defeated` |

**The spine to get right first:** the **mode-switch handoff**. Overworld mark freezes the world, records which enemy seeded the battle and the first-strike side, loads the battle scene, resolves, returns with state changed (enemy gone, souls gained). Everything else hangs off this.

---

## 15. Vertical slice (BUILD THIS FIRST)

**One verb proven: recruit a fallen champion, then deploy them.**

Contains, and nothing more:

- Overworld **mark** → **trigger** → battle screen → **return** with state changed.
- **One** commanded battle: Morrígan + 3 champions, button-per-champion, block timing, meter → one god-finisher.
- Placeholder art (rectangles are fine).

**Explicitly EXCLUDED from the slice:**

- No overworld combat (mark is a trigger, never damage).
- No two-world overlay.
- No four cities / dungeons.
- No muster / levy / clock / evaluation / endings.
- No crafting economy.

**Success test:** is the trigger → battle → return loop fun with rectangles? If not, no amount of Ireland saves it. Prove the loop, then grow outward.

---

## 16. Open questions / unresolved

| # | Question | Status |
|---|---|---|
| 1 | **Game title.** Candidates: *Chooser of the Slain*, *The Morrígan's Muster*, *Well of the Slain*, *Cath* (working). All `[suggestions]`, none chosen. | `[OPEN]` |
| 2 | Battle-control scheme specifics for a commander-not-combatant Morrígan | `[OPEN]` |
| 3 | Two-world flavor: sídhe/Otherworld vs blight-overlay | `[OPEN]` |
| 4 | Tithe-resentment release valve (exact design) | `[OPEN]` |
| 5 | Trigger default: contact vs placed set-piece mix ratio | `[OPEN]` |
| 6 | "Silent when resurrected" as optional flavor (NOT myth-supported; invention only) | `[OPEN]` |
| 7 | Badb's exact in-game role — mirror/foil to the Morrígan, a recruitable champion, or purely narrative | `[OPEN]` |

---

## 17. Scope reality check

- **Full game as specified is multi-year.** Four dungeons + two-world overworld + party combat + a recruitment/tithe sim + branching endings is a large project.
- **The muster/transfer system is the heaviest and riskiest part.** Beautiful thematically, real work mechanically, with a known player-frustration failure mode. Respect its weight; build it late.
- **Discipline:** build order ≠ story order. Slice first (§15). Design Act 1 last. Lift each big system only at a concrete wall.

---
---

# PART II — PLAYER INSTRUCTION MANUAL

*(Booklet voice. Spoiler-light. Written as if printed for the player.)*

## The story so far

Ireland stands between two doom-battles. The Tuatha Dé Danann won the first at a terrible price: their king Nuada lost his sword-arm and, by the old law, his crown. A tyrant rules in his place, and out on the black water the Fomorians gather. A greater battle is foretold on the plain of Mag Tuired, and it is coming whether you are ready or not.

You are the **Morrígan**, chooser of the slain. You cannot win this war with your own hands. You win it with the dead.

## Who you are

You walk the land alone. You do not draw a blade against roaming foes. Instead you **mark** them, and you gather the fallen who are worthy, and you send a host to the front. Your gift is not the killing blow. It is choosing who fights, and steeling them to do it.

## Your world (exploring)

Roam top-down. Push, pull, solve, talk, open the way. Enemies wander the field in plain sight.

- **Mark an enemy first** and the battle begins on *your* terms (your champions strike first).
- **Let one reach you** and it begins on *its* terms.
- **Walk around it** and there is no battle, and no souls gained. Fights are a choice, but the ones you skip are strength you never earned.

## The battle line

When a battle starts, the view shifts and your four champions stand ready, one to each button.

- Tap a champion's button to strike. Each acts on their own rhythm.
- Chain strikes together to fill the **war-gauge**. Full, it unleashes a **god-finisher**.
- **Hold** to guard; time it well and the blow is turned aside.
- You, the Morrígan, do not bleed here. You embolden. Your marks and incitements are the edge your champions carry.

## The Well of Sláine

Bring the worthy dead to the Well. Dian Cécht and his kin chant them whole again, and they rise to serve. Herbs gathered in your travels (Airmed's craft) make them stronger. But mark this well: some wounds are past the Well's reach. Not everyone can be brought back.

## The Muster

The host at the front is always hungry. Each stage of the war, you must **send champions forward**, and once sent they leave your side. The strongest you give may not return. Give too few, or give the weak, and the war turns against you where you cannot see it. This is the hardest law of your office: the dead you raise are not yours to keep.

## The omens

Doom keeps time. Every journey, every delve, every summoning spends the days you have before Mag Tuired. You cannot dawdle and you cannot grind forever. Move with purpose.

## Your champions (spoiler-light)

- **Nuada** — the wronged king; keep him whole, keep him alive.
- **Lugh** — the many-skilled; arrives when the host is nearly ready, and ends the war.
- **The Dagda** — vast and heavy; his club and his cauldron turn a battle.
- **Ogma** — the champion; recover his lost sword and he is yours.
- ...and more fall along the way. Choose them well.

## Old advice

- A fight you can win but choose to skip is strength you gave away.
- Guard is not weakness. A turned blow is a free strike.
- Do not grow too fond. You will have to give them up.

## Controls (quick reference)

| Context | Input | Action |
|---|---|---|
| Explore | Move | Walk |
| Explore | Interact | Push / pull / talk / open |
| Explore | Mark | Tag an enemy, start a battle on your terms |
| Battle | Champion buttons (x4) | Strike / hold to guard |
| Battle | Up + button | Launcher |
| Battle | Down + button | Breaker |
| Battle | Finisher | Spend the full war-gauge |
| Menus | Party | Configure the four you take in |
| Menus | Well | Resurrect, heal, strengthen |
| Menus | Muster | Send champions forward |

---

*End of document. This is a living reference; update tags and Open Questions as decisions land.*
