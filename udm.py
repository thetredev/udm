from entities.hooks import Entity
from events import Event
from events.hooks import PreEvent
from listeners import OnEntityCreated
from listeners.tick import Delay
from players.entity import Player

from weapons.constants import WeaponSlot


player_weapons = {
    WeaponSlot.PRIMARY: "ak47",
    WeaponSlot.SECONDARY: "deagle",
    WeaponSlot.GRENADE: "hegrenade",
    WeaponSlot.KNIFE: True,
    WeaponSlot.C4: False
}


def player_equip_weapon(player: Player, *slots: list[WeaponSlot]):
    """Equip the player with the weapon configured for `slot`."""
    for slot in slots:
        replacement = player_weapons[slot]

        if replacement is None:
            return

        classname = f"weapon_{replacement}"
        Delay(0.00000001, player.give_named_item, (classname,))


@PreEvent("player_spawn")
def pre_player_spawn(game_event):
    player = Player.from_userid(game_event.get_int("userid"))

    if player.dead:
        return

    for weapon in player.weapons(is_filters=("primary", "secondary")):
        weapon.remove()


@Event("player_spawn")
def player_spawn(game_event):
    player = Player.from_userid(game_event.get_int("userid"))

    if player.dead:
        return

    player_equip_weapon(player,
        WeaponSlot.SECONDARY,
        WeaponSlot.PRIMARY,
        WeaponSlot.GRENADE
    )


# TODO: dependent on config
WEAPON_SLOTS_TO_REMOVE = [
    WeaponSlot.C4, WeaponSlot.KNIFE
]

WEAPON_CLASSNAMES_TO_REMOVE = [
    f"weapon_{slot.name.lower()}" for slot in WEAPON_SLOTS_TO_REMOVE
]


@OnEntityCreated
def on_entity_created(base_entity):
    if base_entity.classname not in WEAPON_CLASSNAMES_TO_REMOVE:
        return

    weapon_name = base_entity.classname.removeprefix("weapon_")
    weapon_slot = WeaponSlot[weapon_name.upper()]

    if player_weapons[weapon_slot]:
        return

    print(f"removing {base_entity.classname}")
    base_entity.remove()
