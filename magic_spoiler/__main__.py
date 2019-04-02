"""
Handle Scryfall Spoilers
"""
import contextvars
import datetime
import pathlib
import time
from typing import IO, Any, Dict, List, Tuple, Union

import requests
import requests_cache
from lxml import etree

SCRYFALL_SET_URL: str = "https://api.scryfall.com/sets/{}"
SESSION: contextvars.ContextVar = contextvars.ContextVar("SESSION_SCRYFALL")
SPOILER_SETS: contextvars.ContextVar = contextvars.ContextVar("SPOILER_SETS")


def __get_session() -> Union[requests.Session, Any]:
    """
    Get the session for downloading content
    :return: Session
    """
    requests_cache.install_cache(
        cache_name="scryfall_cache", backend="sqlite", expire_after=7200  # 2 hours
    )

    if not SESSION.get(None):
        SESSION.set(requests.Session())
    return SESSION.get()


def json_download(scryfall_url: str) -> Dict[str, Any]:
    """
    Get the data from Scryfall in JSON format using our secret keys
    :param scryfall_url: URL to json_download JSON data from
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
    set_content: Dict[str, Any] = json_download(SCRYFALL_SET_URL.format(set_code))
    if set_content["object"] == "error":
        print("API download failed for {}: {}".format(set_code, set_content))
        return []

    spoiler_cards = []
    download_url = set_content["search_uri"]

    page_downloaded: int = 1
    while download_url:
        page_downloaded += 1

        cards = json_download(download_url)
        if cards["object"] == "error":
            print("Set {} has no cards, skipping".format(set_code))
            break

        for card in cards["data"]:
            spoiler_cards.append(card)

        if not cards.get("has_more"):
            break

        download_url = cards["next_page"]

    return sorted(spoiler_cards, key=lambda c: (c["name"], c["collector_number"]))


def build_types(sf_card: Dict[str, Any]) -> Tuple[List[str], str, List[str]]:
    """
    Build the super, type, and sub-types of a given card
    :param sf_card: Scryfall card
    :return: Tuple of types
    """
    all_super_types = ["Legendary", "Snow", "Elite", "Basic", "World", "Ongoing"]

    # return values
    super_types: List[str] = []
    sub_types: List[str] = []

    type_line = sf_card["type_line"]

    if u"—" in type_line:
        card_subs = type_line.split(u"—")[1].strip()
        sub_types = card_subs.split(" ") if " " in card_subs else [card_subs]

    for card_type in all_super_types:
        if card_type in type_line:
            super_types.append(card_type)

    types: str = type_line.split(u"—")[0]
    for card_type in all_super_types:
        types = types.replace(card_type, "")

    return super_types, types, sub_types


def scryfall2mtgjson(scryfall_cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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


def open_header(card_xml_file: IO[Any]) -> None:
    """
    Add the header data to the XML file
    :param card_xml_file: Card file path
    """
    card_xml_file.write(
        "<?xml version='1.0' encoding='UTF-8'?>\n"
        + "<cockatrice_carddatabase version='4'>\n"
        + "<!--\nCreated At: "
        + datetime.datetime.utcnow().strftime("%a, %b %d %Y, %H:%M:%S")
        + " (UTC)"
        + "\nCreated By: Magic-Spoiler project @ https://github.com/Cockatrice/Magic-Spoiler\n-->\n"
        + "<sets>\n"
    )


def fill_header_sets(card_xml_file: IO[Any], set_obj: Dict[str, str]) -> None:
    """
    Add header data for set files
    :param card_xml_file: Card file path
    :param set_code: Set code
    :param set_name: Set name
    :param release_date: Release Date
    """
    card_xml_file.write(
        "<set>\n<name>" + set_obj["code"] + "</name>\n"
        "<longname>" + set_obj["name"] + "</longname>\n"
        "<settype>Expansion</settype>\n"
        "<releasedate>" + set_obj["released_at"] + "</releasedate>\n"
        "</set>\n"
    )


def close_header(card_xml_file: IO[Any]) -> None:
    """
    Add closing data to files
    :param card_xml_file: Card file path
    """
    card_xml_file.write("</sets>\n<cards>\n")


def close_xml_file(card_xml_file: IO[Any]) -> None:
    """
    Add final touch to files to validate them,
    then pretty them
    :param card_xml_file: Card file path
    """
    card_xml_file.write("</cards>\n</cockatrice_carddatabase>\n")
    card_xml_file.close()

    # Make the files pretty
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.parse(card_xml_file.name, parser).getroot()
    with pathlib.Path(card_xml_file.name).open("wb") as f:
        f.write(etree.tostring(root, pretty_print=True))


def write_cards(
    card_xml_file: Any, trice_dict: List[Dict[str, Any]], set_code: str
) -> None:
    """
    Given a list of cards, write the cards to an output file
    :param card_xml_file: Output file to write to
    :param trice_dict: List of cards
    :param set_code: Set code
    """
    for card in trice_dict:
        if "names" in card.keys() and card["names"]:
            if "layout" in card and card["layout"] != "double-faced":
                if card["name"] == card["names"][1]:
                    continue

        set_name = card["name"]

        if "mana_cost" in card.keys():
            mana_cost = card["mana_cost"].replace("{", "").replace("}", "")
        else:
            mana_cost = ""

        if "power" in card.keys() or "toughness" in card.keys():
            if card["power"]:
                pow_tough = str(card["power"]) + "/" + str(card["toughness"])
            else:
                pow_tough = ""
        else:
            pow_tough = ""

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
                        pass
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

        if pow_tough:
            card_xml_file.write("<pt>" + pow_tough + "</pt>\n")

        if "loyalty" in card.keys():
            card_xml_file.write("<loyalty>" + str(card["loyalty"]) + "</loyalty>\n")
        card_xml_file.write("<tablerow>" + table_row + "</tablerow>\n")
        card_xml_file.write("<text>" + text + "</text>\n")
        card_xml_file.write("</card>\n")


def write_spoilers_xml(trice_dicts: Dict[str, List[Dict[str, Any]]]) -> None:
    """
    Write the spoiler.xml file
    :param trice_dicts: Dict of dict entries
    """
    pathlib.Path("../out").mkdir(exist_ok=True)
    card_xml_file = pathlib.Path("../out/spoiler.xml").open("w")

    # Fill in set headers
    open_header(card_xml_file)
    for value in SPOILER_SETS.get():
        fill_header_sets(card_xml_file, value)
    close_header(card_xml_file)

    # Write in all the cards
    for value in SPOILER_SETS.get():
        try:
            write_cards(card_xml_file, trice_dicts[value["code"]], value["code"])
        except KeyError:
            print("Skipping " + value["code"])

    close_xml_file(card_xml_file)


def write_set_xml(trice_dict: List[Dict[str, Any]], set_obj: Dict[str, str]) -> None:
    """
    Write out a single magic set to XML format
    :param trice_dict: Cards to print
    :param set_obj: Set object
    """
    if not trice_dict:
        return

    pathlib.Path("../out").mkdir(exist_ok=True)
    card_xml_file = pathlib.Path("../out/{}.xml".format(set_obj["code"])).open("w")

    open_header(card_xml_file)
    fill_header_sets(card_xml_file, set_obj)
    close_header(card_xml_file)
    write_cards(card_xml_file, trice_dict, set_obj["code"])
    close_xml_file(card_xml_file)


def get_spoiler_sets() -> List[Dict[str, str]]:
    """
    Download Sf sets and mark spoiler sets
    :return: Spoiler sets
    """
    sf_sets = json_download("https://api.scryfall.com/sets/")
    if sf_sets["object"] == "error":
        print("Unable to download SF correctly: {}".format(sf_sets))
        return []

    spoiler_sets = []
    for sf_set in sf_sets["data"]:
        if sf_set["released_at"] >= time.strftime("%Y-%m-%d %H:%M:%S"):
            if sf_set["set_type"] != "token":
                sf_set["code"] = sf_set["code"].upper()
                spoiler_sets.append(sf_set)

    return spoiler_sets


def main() -> None:
    """
    Main dispatch thread
    """
    # Determine what sets have spoiler data
    SPOILER_SETS.set(get_spoiler_sets())

    spoiler_xml = {}
    for set_info in SPOILER_SETS.get():
        print("Handling {}".format(set_info["code"]))

        cards = download_scryfall_set(set_info["code"])
        trice_dict = scryfall2mtgjson(cards)

        # Write SET.xml
        write_set_xml(trice_dict, set_info)

        # Save for spoiler.xml
        spoiler_xml[set_info["code"]] = trice_dict

    # Write out the spoiler.xml file
    write_spoilers_xml(spoiler_xml)


if __name__ == "__main__":
    main()
