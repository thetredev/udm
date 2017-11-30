# Ultimate Deathmatch
Ultimate Deathmatch is a [Source.Python](https://github.com/Source-Python-Dev-Team/Source.Python) plugin.

Its goal is to provide an enriched [CSSDM](http://www.bailopan.net/cssdm/)-like experience, but written in [Python](https://www.python.org/) rather than [SourcePawn](https://wiki.alliedmods.net/Introduction_to_SourcePawn).
See it as the version of CSSDM I always wanted.

### Game Support
| Game | Status |
| ---- | ------ |
| Counter-Strike: Source | Stable |
| Counter-Strike: Global Offensive | Stable |

See the [issues list](https://github.com/backraw/udm/issues) for current bugs.

### Features
* [Restrict the amount of times a player can join a different team](https://github.com/backraw/udm/commit/74b9bf689fab6c1e347a38a84715273871b2dfef) (prevent spawn spamming)
* Weapon Menus - accessible via the chat command ```guns```
* Buy anywhere for CS:GO - Open up the buy menu anywhere on the map, like in standard CS:GO Deathmatch mode
* Multiple inventories! See commit [a6dd66e](https://github.com/backraw/udm/commit/a6dd66e61a463d5ddd6c50ad8b49581eb6aa2d86) for details.
* Each inventory can hold either one or two weapons - easy primary/secondary only handling!
* Admin Menu - accessible via the chat command ```!udm```
* [Spawn Points](https://github.com/backraw/udm/tree/master/addons/source-python/data/plugins/udm/spawnpoints) - manageable in game via the Admin menu
* Damage Protection (timed on spawn, but indefinitely when using the Admin menu)
* Refill ammo after the reload animation has finished - even if [the reload button has not been pressed](https://github.com/backraw/udm/commit/19ea391fb6900a3d6497e7ea7b091bf1fea9ea76)
* Refill clip after a player killed an enemy with a headshot
* Noblock (see the config file below)
* Give back High Explosive grenade (4 options - see the config file below)
* Restore the killer's health to 100HP if they killed an enemy with the knife (see the config file below)

Check out the tech demo: https://www.youtube.com/watch?v=srTt0N0AakQ

## Weapon Menus
Have a look at [the ```guns``` command screenshots](https://github.com/backraw/udm/tree/master/screenshots/guns) for CS: GO. You can have an unlimited amount of
inventories and switch between them:

```
# Edit or equip the first inventory
guns 1

# The first inventory is now selected and the player will spawn with those weapons.
# The command guns without any argument will now default to inventory 1.

# Edit the first inventory
guns


# Edit or equip the second inventory
guns 2

# The command guns without any argument will now default to inventory 2.
guns

# ...
```

### Inventories
As mentioned earlier, you can decide whether you only want one weapon in an inventory.

For CS: Source you will want to select ```0``` and for CS: GO ```9``` as the primary or secondary option.
If you choose no weapons at all, random weapons will be activated for you as long as you have not
chosen any weapons for your current inventory.

You can always enable random weapons via ```guns 0```. This will **not** remove any of your inventories.
Disable them by choosing an inventory via ```guns``` or ```guns <inventory>```.

## Admin Menu
Have a look at [the ```!udm``` command screenshots](https://github.com/backraw/udm/tree/master/screenshots/admin) for CS: GO. As soon as you open up the Admin menu, you will lose all your current weapons, but *godmode* will be enabled for you
until you close the menu. Currently only the Spawn Points Manager is implemented: you can manage your spawn points in game!

### Adding an admin
Adding admins is quite simple using the following syntax: ```sp auth permission player add <userid> udm.admin```

1. Join your server
2. In any console - client or server - type ```status``` and make note of the value for your **userid** (i.e.: 2)
3. At the server console, type ```sp auth permission player add 2 udm.admin```
4. You should see a message like **Granted permission "udm.admin" to \<your player name\>.**

You are good to go! For more information on managing admins, please refer to the [Source.Python Auth Configuration](http://wiki.sourcepython.com/general/config-auth.html) wiki page.

## Installation
1. [Install Source.Python](http://wiki.sourcepython.com/general/installation.html): Build #620 is required for this plugin
2. Download [the latest UDM release](https://github.com/backraw/udm/releases/tag/v1.5.2) and unzip its contents to the game server's root folder (i.e.: **cstrike** for Counter-Strike: Source, **csgo** for Counter-Strike: Global Offensive)
3. Put ```sp plugin load udm``` into your server configuration file (i.e.: **autoexec.cfg**) - this can be any file that gets read **after** a map has changed
4. Change the map

## Configuration File
The configuration file ```../cfg/source-python/udm.cfg``` will automatically be created for you after the plugin has loaded for the first time:
```
// ----------------------------------
//    * General
// ----------------------------------

// Default Value: 2
// The respawn delay in seconds.
   udm_respawn_delay 2


// Default Value: 1
// Enable or disable non-blocking mode for players.
   udm_enable_noblock 1


// Default Value: 2
// The spawn protection delay in seconds.
   udm_spawn_protection_delay 2


// Default Value: 1
// Refill the killer's clip if they killed an enemy with a headshot.
   udm_refill_clip_on_headshot 1


// Default Value: 1
// Restore the killer's health to 100HP if they killed an enemy with the knife.
   udm_restore_health_on_knife_kill 1


// Default Value: 150
// The minimum distance players have to have between a spawn point for it to be
//   'safe'.
   udm_spawn_point_distance 150


// Default Value: 2
// The maximum amount of times a players are allowed to change their team per
//   round.
   udm_team_changes_per_round 2


// Default Value: 1.5
// The time in minutes a player who exceeded the maximum team change count has
//   to wait until they can choose ateam again.
   udm_team_changes_reset_delay 1.5

// ----------------------------------
//    * Chat Commands
// ----------------------------------

// Default Value: "!udm"
// The chat command used to open the admin menu.
   udm_saycommand_admin "!udm"


// Default Value: "guns"
// The chat command used to open the weapons menu.
   udm_saycommand_guns "guns"

// ----------------------------------
//    * High Explosive Grenade
// ----------------------------------

// Options
//   * 0 = Off
//   * 1 = Equip on spawn
//   * 2 = Equip on spawn and on each HE grenade kill
//   * 3 = Equip on spawn and after each detonation
// Default Value: 2
// High Explosive grenade behaviour
   udm_equip_hegrenade 2
```

Be sure to reload the plugin via ```sp plugin reload udm``` after you have done any changes to that configuration file.

## Enable or disable weapons for players to choose
Open [the weapon data file for the game](https://github.com/backraw/udm/tree/master/addons/source-python/data/plugins/udm/weapons).
You can disable weapons by commenting them:
```
...
glock = "Glock 18"
usp_silencer = "USP-S"
# deagle = "Desert Eagle"
...
```
This would disable the weapon Desert Eagle. To re-enable it remove the comment:
```
...
glock = "Glock 18"
usp_silencer = "USP-S"
deagle = "Desert Eagle"
...
```
Be sure to reload the plugin via ```sp plugin reload udm``` after you have done any changes to the INI file.

## Enjoy!
