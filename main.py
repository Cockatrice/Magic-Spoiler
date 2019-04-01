import datetime
import pathlib
import sys

import contextvars
from typing import Dict, Any, List, Union, Tuple

import requests
import requests_cache
import yaml

# Scryfall API for downloading spoiler sets
SCRYFALL_SET_URL: str = "https://api.scryfall.com/sets/{}"

# Downloader sessions for header consistency
SESSION: contextvars.ContextVar = contextvars.ContextVar("SESSION_SCRYFALL")


def load_yaml_file(
    input_file: str, lib_to_use: str = "yaml"
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Load a yaml file from system
    :param input_file: File to open
    :param lib_to_use: Open format
    :return: Loaded file
    """
    try:
        with pathlib.Path(input_file).open("r") as f:
            if lib_to_use == "yaml":
                return yaml.safe_load(f)
            else:
                return [of for of in yaml.safe_load_all(f)]
    except Exception as ex:
        print("Unable to load {}: {}".format(input_file, ex.args))
        sys.exit(2)


# File containing all spoiler set details
SET_INFO_FILE: List[Dict[str, Any]] = load_yaml_file("set_info.yml", "yaml_multi")


def __get_session() -> requests.Session:
    """
    Get the session for downloading content
    :return: Session
    """
    requests_cache.install_cache(
        cache_name="scryfall_cache", backend="sqlite", expire_after=604800  # 1 week
    )

    if not SESSION.get(None):
        SESSION.set(requests.Session())
    return SESSION.get()


def __download(scryfall_url: str) -> Dict[str, Any]:
    """
    Get the data from Scryfall in JSON format using our secret keys
    :param scryfall_url: URL to __download JSON data from
    :return: JSON object of the Scryfall data
    """
    session = __get_session()
    response: Any = session.get(url=scryfall_url, timeout=5.0)
    request_api_json: Dict[str, Any] = response.json()
    print("Downloaded: {} (Cache = {})".format(scryfall_url, response.from_cache))
    return request_api_json


def download_scryfall_set(set_code: str) -> List[Dict[str, Any]]:
    """
    Download a set from scryfall in entirety
    :param set_code: Set code
    :return: Card list
    """
    set_content: Dict[str, Any] = __download(SCRYFALL_SET_URL.format(set_code))
    if set_content["object"] == "error":
        print("API download failed for {}: {}".format(set_code, set_content))
        return []

    spoiler_cards = []
    download_url = set_content["search_uri"]

    page_downloaded: int = 1
    while download_url:
        page_downloaded += 1

        cards = __download(download_url)
        if cards["object"] == "error":
            print("Error downloading {0}: {1}".format(set_code, cards))
            break

        for card in cards["data"]:
            spoiler_cards.append(card)

        if not cards.get("has_more"):
            break

        download_url = cards["next_page"]

    return sorted(spoiler_cards, key=lambda c: (c["name"], c["collector_number"]))


def build_types(sf_card: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
    """
    Build the super, type, and sub-types of a given card
    :param sf_card: Scryfall card
    :return: Tuple of types
    """
    all_super_types = ["Legendary", "Snow", "Elite", "Basic", "World", "Ongoing"]

    # return values
    super_types, types, sub_types = [], [], []

    type_line = sf_card["type_line"]

    if u"—" in type_line:
        card_subs = type_line.split(u"—")[1].strip()
        sub_types = card_subs.split(" ") if " " in card_subs else [card_subs]

    for card_type in all_super_types:
        if card_type in type_line:
            super_types.append(card_type)

    types = type_line.split(u"—")[0]
    for card_type in all_super_types:
        types = types.replace(card_type, "")

    return super_types, types, sub_types


def convert_scryfall(scryfall_cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert SF cards to MTGJSON format for dispatching
    :param scryfall_cards: List of Scryfall cards
    :return: MTGJSON card list
    """
    trice_cards = []

    composed_sf_cards = []

    # Handle split/transform cards
    for sf_card in scryfall_cards:
        if "layout" in sf_card.keys():
            if sf_card["layout"] in ["transform", "split"]:
                # Make a copy for zoning
                combined_sides = sf_card.copy()
                del combined_sides["card_faces"]

                # Quick pointers
                face_0 = sf_card["card_faces"][0]
                face_1 = sf_card["card_faces"][1]

                # Update data for the combined
                combined_sides["layout"] = "double-faced"
                combined_sides["names"] = [face_0["name"], face_1["name"]]

                # Re-structure two cards into singletons
                front_side = {**combined_sides, **face_0}
                back_side = {**combined_sides, **face_1}

                # Uniquify them
                front_side["collector_number"] += "a"
                back_side["collector_number"] += "b"

                # And continue on our journey
                composed_sf_cards.extend([front_side, back_side])
            else:
                composed_sf_cards.append(sf_card)

    # Build trice cards from SF cards
    for sf_card in composed_sf_cards:
        super_types, types, sub_types = build_types(sf_card)

        trice_card = {
            "cmc": sf_card["cmc"],
            "names": sf_card.get("names", None),
            "mana_cost": sf_card.get("mana_cost", ""),
            "name": sf_card["name"],
            "number": sf_card["collector_number"],
            "rarity": sf_card["rarity"].replace("mythic", "mythic rare").title(),
            "text": sf_card.get("oracle_text", ""),
            "url": sf_card["image_uris"].get("normal", None),
            "type": sf_card.get("type_line", "Unknown").replace(u"—", "-"),
            "colorIdentity": sf_card.get("color_identity", None),
            "colors": sf_card["colors"],
            "power": sf_card.get("power", None),
            "toughness": sf_card.get("toughness", None),
            "layout": sf_card["layout"].replace("normal", ""),
            "loyalty": sf_card.get("loyalty", None),
            "artist": sf_card.get("artist", ""),
            "flavor": sf_card.get("flavor_text", None),
            "multiverseId": sf_card.get("multiverse_id", None),
            "superTypes": super_types,
            "types": types,
            "subTypes": sub_types,
        }
        trice_cards.append(trice_card)

    return trice_cards


def open_header(card_xml_file) -> None:
    """
    Add the header data to the XML file
    :param card_xml_file: Card file path
    """
    card_xml_file.write(
        "<?xml version='1.0' encoding='UTF-8'?>\n"
        "<cockatrice_carddatabase version='4'>\n"
        "<!--\ncreated: "
        + datetime.datetime.utcnow().strftime("%a, %b %d %Y, %H:%M:%S")
        + " (UTC)"
        + "\nby: Magic-Spoiler project @ https://github.com/Cockatrice/Magic-Spoiler\n-->\n"
        "<sets>\n"
    )


def fill_header_sets(card_xml_file, set_code, set_name, release_date) -> None:
    """
    Add header data for set files
    :param card_xml_file: Card file path
    :param set_code: Set code
    :param set_name: Set name
    :param release_date: Release Date
    """
    card_xml_file.write(
        "<set>\n<name>" + set_code + "</name>\n"
        "<longname>" + set_name + "</longname>\n"
        "<settype>Expansion</settype>\n"
        "<releasedate>" + release_date + "</releasedate>\n"
        "</set>\n"
    )


def close_header(card_xml_file) -> None:
    """
    Add closing data to files
    :param card_xml_file: Card file path
    """
    card_xml_file.write("</sets>\n<cards>\n")


def close_xml_file(card_xml_file) -> None:
    """
    Add final touch to files to validate them
    :param card_xml_file: Card file path
    """
    card_xml_file.write("</cards>\n</cockatrice_carddatabase>\n")


def write_cards(
    card_xml_file: Any, trice_dict: List[Dict[str, Any]], set_code: str
) -> None:
    """
    Given a list of cards, write the cards to an output file
    :param card_xml_file: Output file to write to
    :param trice_dict: List of cards
    :param set_code: Set code
    """
    count = 0
    related = 0

    for card in trice_dict:
        if "names" in card.keys() and card["names"]:
            if "layout" in card and card["layout"] != "double-faced":
                if card["name"] == card["names"][1]:
                    continue

        count += 1
        set_name = card["name"]

        if "mana_cost" in card.keys():
            mana_cost = card["mana_cost"].replace("{", "").replace("}", "")
        else:
            mana_cost = ""

        if "power" in card.keys() or "toughness" in card.keys():
            if card["power"]:
                pt = str(card["power"]) + "/" + str(card["toughness"])
            else:
                pt = 0
        else:
            pt = 0

        if "text" in card.keys():
            text = card["text"]
        else:
            text = ""

        card_cmc = str(card["cmc"])
        card_type = card["type"]
        if "names" in card.keys():
            if "layout" in card:
                if card["layout"] == "split" or card["layout"] == "aftermath":
                    if "names" in card:
                        if card["name"] == card["names"][0]:
                            for json_card in trice_dict:
                                if json_card["name"] == card["names"][1]:
                                    card_type += " // " + json_card["type"]
                                    new_mc = ""
                                    if "mana_cost" in json_card:
                                        new_mc = json_card["mana_cost"]
                                    mana_cost += " // " + new_mc.replace(
                                        "{", ""
                                    ).replace("}", "")
                                    card_cmc += " // " + str(json_card["cmc"])
                                    text += "\n---\n" + json_card["text"]
                                    set_name += " // " + json_card["name"]
                elif card["layout"] == "double-faced":
                    if "names" not in card.keys():
                        print(card["name"] + ' is double-faced but no "names" key')
                    else:
                        for dfc_name in card["names"]:
                            if dfc_name != card["name"]:
                                related = dfc_name
                else:
                    print(
                        card["name"]
                        + " has names, but layout != split, aftermath, or double-faced"
                    )
            else:
                print(card["name"] + " has multiple names and no 'layout' key")

        table_row = "1"
        if "Land" in card_type:
            table_row = "0"
        elif "Sorcery" in card_type:
            table_row = "3"
        elif "Instant" in card_type:
            table_row = "3"
        elif "Creature" in card_type:
            table_row = "2"

        if "number" in card:
            if "b" in str(card["number"]):
                if "layout" in card:
                    if card["layout"] == "split" or card["layout"] == "aftermath":
                        continue

        card_xml_file.write("<card>\n")
        card_xml_file.write("<name>" + set_name + "</name>\n")
        card_xml_file.write(
            '<set rarity="'
            + str(card["rarity"])
            + '" picURL="'
            + str(card["url"])
            + '">'
            + str(set_code)
            + "</set>\n"
        )
        card_xml_file.write("<manacost>" + mana_cost + "</manacost>\n")
        card_xml_file.write("<cmc>" + card_cmc + "</cmc>\n")

        if "colors" in card.keys():
            for color in card["colors"]:
                card_xml_file.write("<color>" + str(color) + "</color>\n")

        if set_name + " enters the battlefield tapped" in text:
            card_xml_file.write("<cipt>1</cipt>\n")

        card_xml_file.write("<type>" + card_type + "</type>\n")

        if pt:
            card_xml_file.write("<pt>" + pt + "</pt>\n")

        if "loyalty" in card.keys():
            card_xml_file.write("<loyalty>" + str(card["loyalty"]) + "</loyalty>\n")
        card_xml_file.write("<tablerow>" + table_row + "</tablerow>\n")
        card_xml_file.write("<text>" + text + "</text>\n")

        if related:
            card_xml_file.write("<related>" + related + "</related>\n")
            related = ""

        card_xml_file.write("</card>\n")


def write_spoilers_xml(trice_dicts) -> None:
    """
    Write the spoiler.xml file
    :param trice_dicts: Dict of entries
    """
    pathlib.Path("out").mkdir(exist_ok=True)
    card_xml_file = pathlib.Path("out/spoiler.xml").open("w")

    # Fill in set headers
    open_header(card_xml_file)
    for value in SET_INFO_FILE:
        fill_header_sets(
            card_xml_file, value["code"], value["name"], value["releaseDate"]
        )
    close_header(card_xml_file)

    # Write in all the cards
    for value in SET_INFO_FILE:
        try:
            write_cards(card_xml_file, trice_dicts[value["code"]], value["code"])
        except KeyError:
            print("Skipping " + value["code"])

    close_xml_file(card_xml_file)


def write_set_xml(
    trice_dict: List[Dict[str, Any]], set_code: str, set_name: str, release_date: str
) -> None:
    """
    Write out a single magic set to XML format
    :param trice_dict: Cards to print
    :param set_code: Set code
    :param set_name: Set name
    :param release_date: Set release date
    """
    if not trice_dict:
        return

    pathlib.Path("out").mkdir(exist_ok=True)
    card_xml_file = pathlib.Path("out/{}.xml".format(set_code)).open("w")

    open_header(card_xml_file)
    fill_header_sets(card_xml_file, set_code, set_name, release_date)
    close_header(card_xml_file)
    write_cards(card_xml_file, trice_dict, set_code)
    close_xml_file(card_xml_file)


def main() -> None:
    """
    Main dispatch thread
    """
    spoiler_xml = {}
    for set_info in SET_INFO_FILE:
        print("Handling {}".format(set_info["code"]))

        if not set_info["scryfallOnly"]:
            continue

        cards = download_scryfall_set(set_info["code"])
        trice_dict = convert_scryfall(cards)

        # Write SET.xml
        write_set_xml(
            trice_dict, set_info["code"], set_info["name"], set_info["releaseDate"]
        )

        # Save for spoiler.xml
        spoiler_xml[set_info["code"]] = trice_dict

    # Write out the spoiler.xml file
    write_spoilers_xml(spoiler_xml)


if __name__ == "__main__":
    main()
