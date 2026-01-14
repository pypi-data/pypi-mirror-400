"""
Utility functions for basic uses.
"""
import json
import os
import sys
import uuid
import shutil
from dataclasses import asdict
from json import load, dump, loads, dumps
from math import ceil, log2

from numpy import ndarray

from .bases.parts.baseinteractablepart import BaseInteractablePart
from .blueprint import Blueprint


def load_blueprint(name: str):
    """Load a blueprint from a path file (normally a blueprint.json).

    Args:
        name (str): Name of the blueprint to load.

    Returns:
        Blueprint: The loaded blueprint.
    """
    with open(get_blueprint_path(name)) as fp:
        return Blueprint(**load(fp))


def save_blueprint(name: str, bp: Blueprint):
    """Save a blueprint to a file (normally a blueprint.json).

    Args:
        name (str): Name of the new blueprint.
        bp (Blueprint): The blueprint to be saved.
    """
    with open(get_blueprint_path(name), "w") as fp:
        return dump(asdict(bp), fp, sort_keys=True, separators=(',', ':'))


def load_blueprint_from_string(str: str):
    """Load a blueprint from a json string.

    Args:
        str (str): The string to be loaded.

    Returns:
        Blueprint: The loaded blueprint.
    """
    return Blueprint(**loads(str))


def dump_string_from_blueprint(bp: Blueprint):
    """Dump a blueprint into a json-formatted string.

    Args:
        bp (Blueprint): The blueprint to be dumped.

    Returns:
        str: The json-formatted string.
    """
    return dumps(asdict(bp), sort_keys=True, separators=(',', ':'))


def connect(_from, _to, *, parallel=True):
    """Connect interactable parts together, recursively.

    Args:
        _from (Any): Must be an instance of BaseInteractablePart or a subclass.
        Also it can be any nested iterable of instances (list of parts, list of lists of parts, etc).
        _to (Any): Must be an instance of BaseInteractablePart or a subclass.
        Also it can be any nested iterable of instances (list of parts, list of lists of parts, etc).
        parallel (bool, optional): Defines the behaviour of the connections in the following way:

        With parallel=False, everything connects to everything:
            from1 🔀 to1

            from2 🔀 to2

        With parallel=True, every row is connected respectively:
            from1 → to1

            from2 → to2

        Also, if the dimensions does not match it tries to adapt (many to one, one to many, etc)

        Defaults to True.
    """
    if isinstance(_from, BaseInteractablePart) and isinstance(_to, BaseInteractablePart):
        _from.connect(_to)
        return
    # Try connect things row-by-row if possible (one to one, one to many, many to many)
    if parallel:
        # Assume both are sequence of parts
        if not isinstance(_from, BaseInteractablePart) and not isinstance(_to, BaseInteractablePart):
            for subfrom, subto in zip(_from, _to):
                connect(subfrom, subto, parallel=parallel)
        # Assume _from is a sequence of parts
        elif not isinstance(_from, BaseInteractablePart):
            for subfrom in _from:
                connect(subfrom, _to, parallel=parallel)
        else:                                               # Assume _to is a sequence of parts
            for subto in _to:
                connect(_from, subto, parallel=parallel)
    else:           # Just connect everything to everything lol
        # Assume both are sequence of parts
        if not isinstance(_from, BaseInteractablePart) and not isinstance(_to, BaseInteractablePart):
            for subfrom in _from:
                for subto in _to:
                    connect(subfrom, subto, parallel=parallel)
        # Assume _from is a sequence of parts
        elif not isinstance(_from, BaseInteractablePart):
            for subfrom in _from:
                connect(subfrom, _to, parallel=parallel)
        else:                                               # Assume _to is a sequence of parts
            for subto in _to:
                connect(_from, subto, parallel=parallel)


def get_bits_required(number: int | float):
    """Calculates how many bits are required to store this number.

    Args:
        number (int | float): The target number.
    """
    return ceil(log2(number))


def num_to_bit_list(number: int, bit_length: int):
    """Converts a number to a numpy array of its bits.

    Args:
        number (int): The number to convert.
        bit_length (int): The number of bits the list will have.
    """
    output = ndarray(bit_length, dtype=bool)
    for b in range(bit_length):
        output[b] = bool((number >> b) & 1)
    return output


def load_vdf(file):
    """Converts a steam vdf file to a python dict.

    Args:
        file (str): path to file.

    Returns:
        Dict: vdf as Dict.
    """
    temp = "{"
    with open(file,"r") as vdf:
        for line in vdf.readlines():
            temp += line.strip("		").strip("\n").replace('"		"', '":"')
    temp = temp.replace('"{','":{')
    temp = temp.replace('}"', '},"')
    temp = temp.replace('"""', '=_=')
    temp = temp.replace('""', '","')
    temp = temp.replace('=_=', '"","')
    temp+="}"
    return loads(temp)


def find_game(steam_path):
    """Tries to find the Scrap Mechanic path.

    Args:
        steam_path (str): Path to Steam.

    Returns:
        str: Path to Scrap Mechanic folder.
    """
    if os.path.isdir(steam_path):
        vdf = load_vdf(fr"{steam_path}/config/libraryfolders.vdf")
        for library in vdf["libraryfolders"]:
            if "387990" in vdf["libraryfolders"][library]["apps"].keys():
                if os.path.isdir(fr"{vdf["libraryfolders"][library]["path"]}/steamapps/common/Scrap Mechanic"):
                    return fr"{vdf["libraryfolders"][library]["path"]}/steamapps/common/Scrap Mechanic"
    return None


def find_blueprint_folder(steam_path,appdata_path):
    """Tries to find the path to blueprint folder.

    Args:
        steam_path (str): Path to Steam.
        appdata_path (str): Path to appdata/roaming.

    Returns:
        str: Path to Scrap Mechanic blueprint folder.
    """
    if os.path.isdir(fr"{steam_path}/userdata/"):
        steam_active_user = None
        users = os.listdir(fr"{steam_path}/userdata/")
        if len(users) == 1:
            steam_active_user = users[0]
        else:
            time = 0
            for user in users:
                if time < os.path.getmtime(fr"{steam_path}/userdata/{user}/config/licensecache"):
                    time = os.path.getmtime(fr"{steam_path}/userdata/{user}/config/licensecache")
                    steam_active_user = user
        if os.path.isdir(fr"{steam_path}/userdata/{steam_active_user}/387990"):
            vdf = load_vdf(fr"{steam_path}/userdata/{steam_active_user}/387990/remotecache.vdf")
            keys = vdf["387990"].keys()
            for key in keys:
                if key.startswith("Axolot Games"):
                    return f"{appdata_path}/{key.split("Blueprints")[0]}Blueprints/"
    return None


def get_paths():
    """Tries to find all paths related to ScrapMechanic.

    Returns:
        blueprint_path (str): Path to the current steam users blueprint folder from root.
        game_path (str): Path to ScrapMechanic game files.
    """
    if sys.platform == "linux":
        linux_user = os.getcwd().split("/")[2]
        if os.path.isdir(f"/home/{linux_user}/snap/steam/common/.local/share/Steam/steamapps/"):
            steam_path = f"/home/{linux_user}/snap/steam/common/.local/share/Steam"
            game_path = find_game(steam_path)
            if os.path.isdir(f"{steam_path}/steamapps/compatdata/387990/pfx/drive_c/"):
                drive = f"{steam_path}/steamapps/compatdata/387990/pfx/drive_c/"
                if os.path.isdir(f"{drive}users/steamuser/AppData/Roaming"):
                    appdata_path = f"{drive}users/steamuser/AppData/Roaming"
                    blueprint_path = find_blueprint_folder(steam_path, appdata_path)
                    return blueprint_path, game_path

        if os.path.isdir(f"/home/{linux_user}/.var/app/com.valvesoftware.Steam/data/Steam/steamapps"):
            #print("installer:", "flathub")
            steam_path = f"/home/{linux_user}/.var/app/com.valvesoftware.Steam/data/Steam"
            game_path = find_game(steam_path)
            if os.path.isdir(f"{steam_path}/steamapps/compatdata/387990/pfx/drive_c/"):
                drive = f"{steam_path}/steamapps/compatdata/387990/pfx/drive_c/"
                if os.path.isdir(f"{drive}users/steamuser/AppData/Roaming"):
                    appdata_path = f"{drive}users/steamuser/AppData/Roaming"
                    blueprint_path = find_blueprint_folder(steam_path, appdata_path)
                    return blueprint_path, game_path

        return None, None

    elif sys.platform == "win32":
        import winreg
        key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam")
        steam_path = winreg.QueryValueEx(key, 'InstallPath')[0]
        winreg.CloseKey(key)
        game_path = find_game(steam_path)
        appdata_path = os.getenv("APPDATA")
        blueprint_path = find_blueprint_folder(steam_path, appdata_path).replace("/", "\\")
        return blueprint_path, game_path

    else:
        return None, None


def generate_blocks(path):
    pass


def make_new_blueprint(name, blueprint = None, description="#{STEAM_WORKSHOP_NO_DESCRIPTION}", Image=None):
    """Will make a new blueprint folder in the directory of path.

    Args:
        name (str): Name of the new blueprint.
        blueprint (Blueprint, optional): Blueprint to be saved.
            If None, an empty blueprint is created.
        description (str, optional): Description of the new blueprint.
            Defaults to "#{STEAM_WORKSHOP_NO_DESCRIPTION}".
        Image (Image, optional): Image used as the blueprint icon.
            If None, the sm_blueprint_icon is used. Defaults to None.

    Returns:
        blueprint_uuid (str): The uuid of the new blueprint folder.
    """
    path = get_paths()[0]
    if find_blueprint(name) is not None:
        print("blueprint already exists")
        return find_blueprint(name)
    id = uuid.uuid4()
    while id in os.listdir(path):
        id = uuid.uuid4()
    blueprint_path = path + str(id)
    os.mkdir(blueprint_path)

    if Image is None:
        shutil.copy(__file__[:-8]+"icon.png",blueprint_path)
    elif os.path.isfile(Image):
        shutil.copy(Image, blueprint_path)
    else:
        shutil.copy(__file__[:-8] + "icon.png", blueprint_path)

    with open(blueprint_path+"/description.json","w") as discrip:
        discrip.write(dumps({"description": description,
                                "localId": str(id),
                                "name": name,
                                "type": "Blueprint",
                                "version": 0},indent=4))

    if blueprint is not None:
        blueprint = Blueprint()
    save_blueprint(name,blueprint)
    return str(id)


def find_blueprint(name):
    """loops though path and opens descriptions to check blueprint name.

    Args:
        path (str): Path to the main blueprint folder.
        name (str): Name of the blueprint.

    Returns:
        blueprint_uuid (str): The uuid of the new blueprint folder.
    """
    path = get_paths()[0]
    for bp in os.listdir(path):
        if os.path.exists(path+bp+"/description.json"):
            with open(path+bp+"/description.json","r") as discrip:
                discrip = loads(discrip.read())
                if name  == discrip["name"]:
                    return bp
    return None

def list_blueprints():
    """loops though path and opens descriptions to check blueprint names.

    Returns:
        BlueprintList: ([str]): List of blueprint names.

    """
    path = get_paths()[0]
    bplist = []
    for bp in os.listdir(path):
        if os.path.exists(path+bp+"/description.json"):
            with open(path+bp+"/description.json","r") as discrip:
                discrip = loads(discrip.read())
                bplist.append(discrip["name"])
    return bplist


def get_blueprint_path(name):
    """gets the full path of blueprint.json from blueprint name.

    Args:
        name (str): Name of the blueprint.

    Returns:
        BlueprintPath: (str): full path of blueprint.json.

    """
    path = get_paths()[0]
    bp = find_blueprint(name)
    return f"{path}{bp}/blueprint.json"

def delete_blueprint(name):
    """deletes a blueprints whole folder!

    Args:
        name (str): Name of the blueprint.

    """
    path = get_paths()[0]
    if find_blueprint(name) is not None:
        bp = path+"/"+find_blueprint(name)
        if input(f'are you sure you want to delete blueprint {name}? Type "yes" or "no".' ) == "yes":
            for file in os.listdir(bp):
                os.remove(bp+"/"+file)
            os.rmdir(bp)
