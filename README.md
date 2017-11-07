# Ultimate Deathmatch
Ultimate Deathmatch is a [Source.Python](https://github.com/Source-Python-Dev-Team/Source.Python) plugin.

Its goal is to provide an enriched [CSSDM](http://www.bailopan.net/cssdm/)-like experience, but written in [Python](https://www.python.org/) rather than [SourcePawn](https://wiki.alliedmods.net/Introduction_to_SourcePawn).

## Game Support
| Game | Status |
| ---- | ------ |
| Counter-Strike: Source | Tested |
| Counter-Strike: Global Offensive | Untested |

## Features
* Weapon Menu - accessible via the chat command **guns**
* Multiple inventories! See commit [a6dd66e](https://github.com/backraw/udm/commit/a6dd66e61a463d5ddd6c50ad8b49581eb6aa2d86) for details.
* Each inventory can hold either one or two weapons - easy primary/secondary only handling!
* Spawn Points
* Refill ammo after the reload animation has finished
* Admin Menu

Spawn points are loaded after a map change and on plugin load. The current map is evaluated and the corresponding data file ```../addons/source-python/data/plugins/udm/spawnpoints/<game_name>/<current_map>.json``` is being loaded, if it exists.
See [the spawnpoints folder for Counter-Strike: Source](https://github.com/backraw/udm/tree/master/addons/source-python/data/plugins/udm/spawnpoints/cstrike) for examples.

## The Admin Menu
The Admin menu is accessible to admins via the chat command **!udm** and currently provides the following functionality:
* Spawn Point Manager
	* Add: current location
	* Remove: current location
	* List: provide a list menu of all spawn points for the current map in a selectable enumerated format
	* Save: ```../addons/source-python/data/plugins/udm/spawnpoints/<game_name>/<current_map>.json```

### Adding an admin
Adding admins is quite simple using the following syntax: ```sp auth permission player add <userid> udm.admin```

1. Join your server
2. In any console - client or server - type **status** and make note of the value for your **userid** (e.g.: 2)
3. At the server console, type ```sp auth permission player add 2 udm.admin```
4. You should see a message like ```Granted permission "udm.admin" to <your player name>.```

You are good to go! For more information on managing admins, please refer to the [Source.Python Auth Configuration](http://wiki.sourcepython.com/general/config-auth.html) wiki page.

## Installation
1. [Install Source.Python](http://wiki.sourcepython.com/general/installation.html)
2. Download a release of this plugin (TODO: Add one...) and unzip its contents to the game server's root folder (e.g.: **cstrike** for Counter-Strike: Source, **csgo** for Counter-Strike: Global Offensive)
3. Put ```sp plugin load udm``` into your server configuration file (e.g.: **autoexec.cfg**) - this can be any file that gets read **after** a map has changed
4. Change the map

## Configuration File
The configuration file ```../cfg/source-python/udm.cfg``` gets created automatically after the plugin has loaded for the first time. The contents currently are the following:
```// Default Value: 0.0
// The delay after which the player gets equipped on spawn. Must be positive!
   udm_equip_delay 0.0


// Default Value: 1
// 0 = Off; 1 = Equip on spawn; 2 = Equip on spawn and after each detonation
   udm_equip_hegrenade 1


// Default Value: 2
// The respawn delay in seconds.
   udm_respawn_delay 2


// Default Value: 150
// The minimum distance players have to have between a spawn point for it to be
//   'safe'.
   udm_spawn_point_distance 150


// Default Value: 2
// The spawn protection delay in seconds.
   udm_spawn_protection_delay 2


// Default Value: "!udm"
// The chat command used to open the admin menu.
   udm_saycommand_admin "!udm"


// Default Value: "guns"
// The chat command used to open the weapons menu.
   udm_saycommand_guns "guns"
```

Be sure to reload the plugin after you have done any changes to that configuration via ```sp plugin reload udm``` or change the map.

### That's it!
