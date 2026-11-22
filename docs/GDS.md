# Game Design Specification (GDS): Untitled Rabbit Defense Game

**Working Titles:** Bunny Berserk / Field Defender / Rabid Defense
**Document Status:** Core Concept & Systems Architecture (v1.0)

## 1. High-Level Concept & Vision

- **Elevator Pitch:** A cute, colorful 3D top-down action-defense and base-building game. You play as a customizable rabbit living an idyllic life in a peaceful meadow until intruders (workmen, foxes, rabid dogs) invade. The rabbit snaps, arms up with DIY garden weaponry, rigs the field with underground pop-up turrets and minefields, and fights back to secure its territory and expand across an interconnected overworld.
- **Genre:** 3D Top-Down Action Tower Defense / Base-Builder / Resource Management.
- **Camera & Perspective:** Top-down isometric view with zoom control to watch the rabbit move across the field and oversee trap layouts and enemy lanes.
- **Art Style & Tone:** Cute, bright, stylized visuals (soft colors, bouncy animations) contrasted with chaotic, over-the-top cartoon combat (poof clouds, slapstick recoil, ragdoll physics).
- **Progression Model:** Permanent campaign progression. Clearing a field permanently liberates and saves it, turning it into an active resource hub before expanding to adjacent fields on a top-level map.

## 2. Core Gameplay Loop

```
[Peaceful Exploration & Farming]
        ➔ [Build Traps, Minefields & Burrow Turrets]
        ➔ [Trigger / Survive Intruder Waves]
        ➔ [Field Cleared & Saved]
        ➔ [Expand via Overworld Map]
```

- **Peaceful Prep Phase:** Explore the field, gather resources, tend to vegetable allotments, dig underground tunnel networks, and place surface traps and hidden hydraulic burrow turrets.
- **Wave Combat Phase:** Intruders breach the field perimeter. Control the rabbit directly in top-down twin-stick/action combat while automated defenses and traps thin out enemy lanes.
- **Liberation & Saving:** Defeating the final wave/boss secures the field permanently. Resources are stored, the burrow is upgraded, and adjacent fields unlock on the overworld map.

## 3. Player Character & Combat Mechanics

- **Customization (Start of Game):** Select fur color, coat patterns (Dutch, Lop-eared, Rex, Flemish Giant proportions), and tactical cosmetics (headbands, eye patches, armor vests).
- **Movement & Controls:** 360-degree top-down movement with a fast Burrow-Dash dodge mechanic to slip beneath attacks or traverse underground tunnel shortcuts across the field.
- **The "Lost It" (Rage) Meter:** Fills as enemies damage crops/defenses or as the rabbit deals damage. Activating it triggers a temporary frenzy state with increased speed, triple fire rate, and amplified melee/ranged damage.
- **Gear & Armor:** Craftable protective gear (e.g., colander helmets, acorn-shell chest plates) to survive heavy hits from predators and machinery.

## 4. Field Defenses & Underground Burrow Architecture

- **Surface Traps (Pre-Wave Setup):**
  - *Carrot C4 Minefields:* Buried explosives triggered by enemy proximity.
  - *Sticky Berry / Sap Patches:* Slows fast-moving predators like foxes and stray dogs.
  - *Bramble Hedges & Barricades:* Redirects enemy pathing into kill zones.
- **Raised Burrow Turrets:**
  - Built flush into the field soil during the peaceful phase (disguised as dirt mounds or flower patches).
  - When combat begins, hydraulic lifts raise the turrets out of the ground (e.g., Seed Gatling Guns, Acorn Mortars, Dandelion Poison Sprayers).
- **Underground Burrow Network:**
  - Players can enter their underground burrow between waves to access workbenches, weapon racks, and storage vaults.
  - Digging tunnel nodes across a field allows rapid point-to-point travel during chaotic waves.
  - Underground Silos: Building resource silos directly underneath surface turrets enables automatic mid-wave reloading.

## 5. Resources, Garden Allotments & Dietary Realism

Secured fields allow the rabbit to cultivate Allotment & Garden Vegetable Patches that generate passive and active resources over time. Resource roles strictly respect real-world rabbit dietary safety (toxic items are used strictly as ordnance/building materials, never food):

| Resource | Category | Gameplay Function & Purpose |
|---|---|---|
| Timothy Hay & Dandelions | Consumables / Health | Restores rabbit health and boosts stamina/speed (safe rabbit diet). |
| Carrots & Berries | Special Ammo & Traps | Powers Carrot Rocket Launchers, C4 Carrot Mines, and sticky berry slow-traps. |
| Acorns & Pinecones | Heavy Ordnance & Armor | Used strictly as heavy mortar shells, fragmentation grenades, and turret armor plating (never eaten). |
| Garden Scrap & Nails | Tech & Hydraulics | Scavenged metal used to build hydraulic turret lifts, electric fences, and weapon upgrades. |

## 6. Enemies, Intruders & Raid Mechanics

- **Enemy Tiers:**
  - *Tier 1 (Pests):* Stray rabid dogs, aggressive cats, crows (aerial units).
  - *Tier 2 (Predators):* Foxes, badgers, owls.
  - *Tier 3 (Human & Mechanical Threats):* Construction workmen, surveyors, lawn-mowing crews, and mini-boss vehicles (skid steers, ride-on mowers).
- **Allotment Raiding (Single-Player):** Intruders actively target vegetable patches as well as the main burrow. If foxes or workmen steal crops and escape off-map, stored yields for that field are reduced.
- **Overworld Map:** A stylized top-level map connecting distinct zones (e.g., The Starting Meadow, The Farmer's Allotment, The Suburb Backyard, The Construction Site). Players travel freely between liberated fields to collect harvests and upgrade defenses.

## 7. Future Roadmap / Backlog (Post-MVP)

- **Asynchronous Multiplayer Raids (Clash of Clans Style):**
  - Players design and fortify their own custom field layouts, allotment placements, and hidden burrow turret networks.
  - Other players deploy wave squads (fox packs, stray dogs, workmen) to raid rival fields and loot surface granaries/scrap piles, while underground bunker vaults protect a core percentage of the defender's resources.

## 8. Suggested Starting Points for Next Session

- **Weapon & Turret Crafting Tree:** Exact recipes, damage types, and upgrade tiers for handheld weapons and pop-up turrets.
- **First 3 Campaign Fields:** Level layouts, wave compositions, and boss mechanics for the opening zones.
- **Technical & Engine Scope:** Target game engine (Unity / Unreal / Godot), 3D asset pipeline, and grid vs. free-placement building rules.

---

## 9. Review Notes & Open Questions (v1.0 review)

### Open design questions
1. **Fail state is undefined.** What happens when a wave is lost: burrow destroyed, field reset, resource penalty, or wave retry?
2. **"Permanently liberated" vs. "upgrade defenses" there.** Either liberated fields are truly safe (passive income only) or they suffer occasional smaller counter-raids. Pick one.
3. **Why hide turrets?** Proposal: enemies path around *visible* defenses, so concealed turrets enable ambushes.
4. **Mazing rules.** Can players fully block paths? How do enemies respond (e.g., chew through hedges)? Recommendation: grid placement.
5. **Turret ammo.** Silos only matter if turrets are ammo-limited. Recommendation for MVP: unlimited ammo.
6. **Burrow-Dash vs. tunnel network overlap.** Consider merging: the dash goes underground only at dug tunnel nodes.
7. **Aerial enemies** (crows, owls) bypass traps and mazing; define which turrets can hit air.
8. **Defeat presentation.** Pets and humans ragdolling may clash with the cute audience and the age rating. Proposal: poof-cloud and flee off-map.
9. **Customization wording.** Lop, Rex and Flemish Giant are breeds (body/ear/coat), not patterns; Dutch is a pattern. Split into body type × coat × pattern.

### Proposed MVP / vertical slice
- One meadow, ~10 waves, ride-on mower boss.
- Rabbit with one weapon, Burrow-Dash and Rage meter.
- 3 traps (Carrot C4, sap patch, bramble hedge), 2 pop-up turrets (Seed Gatling, Acorn Mortar).
- 4 enemies: dog, crow, fox, workman.
- One crop patch with crop-thief raiding.
- Deferred: tunnels, silos, overworld, armor crafting, multiplayer. Store field layouts as data from day one.

### Missing sections
Target platform and input (gamepad / mouse & keyboard), audience and age rating, session length, business model.

## 10. Prototype Tech

- **Prototype platform:** HTML / browser (three.js).
- **3D asset format:** `.glb` (binary glTF 2.0) with embedded textures. See `assets/models/README.md`.
