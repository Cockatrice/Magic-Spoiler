# -*- coding: utf-8 -*-
import requests
from lxml import html
from PIL import Image


def scrape_fullspoil(url="http://magic.wizards.com/en/articles/archive/card-image-gallery/hour-devastation", setinfo={"setname": "HOU"}, showRarityColors=False, showFrameColors=False, manual_cards=[], delete_cards=[], split_cards=[]):
    if 'setlongname' in setinfo:
        url = 'http://magic.wizards.com/en/articles/archive/card-image-gallery/' + setinfo['setlongname'].lower().replace('of', '').replace(
            '  ', ' ').replace(' ', '-')
    page = requests.get(url)
    tree = html.fromstring(page.content)
    cards = []
    cardtree = tree.xpath('//*[@id="content-detail-page-of-an-article"]')
    for child in cardtree:
        cardElements = child.xpath('//*/p/img')
        cardcount = 0
        for cardElement in cardElements:
            card = {
                "name": cardElement.attrib['alt'].replace(u"\u2019", '\'').split(' /// ')[0],
                "img": cardElement.attrib['src']
            }
            card["url"] = card["img"]
            #card["cmc"] = 0
            #card["manaCost"] = ""
            #card["type"] = ""
            #card["types"] = []
            #card["text"] = ""
            #card["colorIdentity"] = [""]

            # if card['name'] in split_cards:
            #    card["names"] = [card['name'], split_cards[card['name']]]
            #    card["layout"] = "split"
            #notSplit = True
            # for backsplit in split_cards:
            #    if card['name'] == split_cards[backsplit]:
            #        notSplit = False
            # if not card['name'] in delete_cards:
            cards.append(card)
            cardcount += 1
    fullspoil = {"cards": cards}
    print "Spoil Gallery has " + str(cardcount) + " cards."
    download_images(fullspoil['cards'], setinfo['setname'])
    fullspoil = get_rarities_by_symbol(fullspoil, setinfo['setname'])
    fullspoil = get_mana_symbols(fullspoil, setinfo['setname'])
    #fullspoil = get_colors_by_frame(fullspoil, setinfo['setname'])
    return fullspoil


def get_rarities_by_symbol(fullspoil, setcode, split_cards=[]):
    symbolPixels = (240, 219, 242, 221)
    highVariance = 15
    colorAverages = {
        "Common": [30, 27, 28],
        "Uncommon": [121, 155, 169],
        "Rare": [166, 143, 80],
        "Mythic Rare": [201, 85, 14]
    }
    symbolCount = 0
    for card in fullspoil['cards']:
        try:
            cardImage = Image.open(
                'images/' + setcode + '/' + card['name'].replace(' // ', '') + '.jpg')
        except:
            continue
            pass
        if '//' in card['name']:
            setSymbol = cardImage.crop((240, 138, 242, 140))
        else:
            setSymbol = cardImage.crop(symbolPixels)
        cardHistogram = setSymbol.histogram()
        reds = cardHistogram[0:256]
        greens = cardHistogram[256:256 * 2]
        blues = cardHistogram[256 * 2: 256 * 3]
        reds = sum(i * w for i, w in enumerate(reds)) / sum(reds)
        greens = sum(i * w for i, w in enumerate(greens)) / sum(greens)
        blues = sum(i * w for i, w in enumerate(blues)) / sum(blues)
        variance = 768
        for color in colorAverages:
            colorVariance = 0
            colorVariance = colorVariance + \
                abs(colorAverages[color][0] - reds)
            colorVariance = colorVariance + \
                abs(colorAverages[color][1] - greens)
            colorVariance = colorVariance + \
                abs(colorAverages[color][2] - blues)
            if colorVariance < variance:
                variance = colorVariance
                card['rarity'] = color
        if variance > highVariance:
            # if a card isn't close to any of the colors, it's probably a planeswalker? make it mythic.
            print card['name'], 'has high variance of', variance, ', closest rarity is', card['rarity']
            card['rarity'] = "Mythic Rare"
            # print card['name'], '$', reds, greens, blues
            if symbolCount < 10:
                setSymbol.save(
                    'images/' + card['name'].replace(' // ', '') + '.symbol.jpg')
                symbolCount += 1
    return fullspoil


def get_colors_by_frame(fullspoil, setcode, split_cards={}):
    framePixels = (20, 11, 76, 16)
    highVariance = 10
    colorAverages = {
        "White": [231, 225, 200],
        "Blue": [103, 193, 230],
        "Black": [58, 61, 54],
        "Red": [221, 122, 101],
        "Green": [118, 165, 131],
        "Multicolor": [219, 200, 138],
        "Artifact": [141, 165, 173],
        "Colorless": [216, 197, 176],
    }
    symbolCount = 0
    for card in fullspoil['cards']:
        try:
            cardImage = Image.open(
                'images/' + setcode + '/' + card['name'].replace(' // ', '') + '.jpg')
        except:
            continue
            pass
        cardColor = cardImage.crop(framePixels)

        cardHistogram = cardColor.histogram()
        reds = cardHistogram[0:256]
        greens = cardHistogram[256:256 * 2]
        blues = cardHistogram[256 * 2: 256 * 3]
        reds = sum(i * w for i, w in enumerate(reds)) / sum(reds)
        greens = sum(i * w for i, w in enumerate(greens)) / sum(greens)
        blues = sum(i * w for i, w in enumerate(blues)) / sum(blues)
        variance = 768
        for color in colorAverages:
            colorVariance = 0
            colorVariance = colorVariance + \
                abs(colorAverages[color][0] - reds)
            colorVariance = colorVariance + \
                abs(colorAverages[color][1] - greens)
            colorVariance = colorVariance + \
                abs(colorAverages[color][2] - blues)
            if colorVariance < variance:
                variance = colorVariance
                card['colors'] = [color]
    return fullspoil


def get_mana_symbols(fullspoil={}, setcode="HOU", split_cards=[]):
    manaBoxes = [(234, 23, 244, 33), (220, 23, 230, 33),
                 (206, 23, 216, 33), (192, 23, 202, 33), (178, 23, 188, 33)]
    highVariance = 0
    colorAverages = {
        "W": [126, 123, 110],
        "U": [115, 140, 151],
        "B": [105, 99, 98],
        "R": [120, 89, 77],
        "G": [65, 78, 69],
        "1": [162, 156, 154],
        "2": [155, 148, 147],
        "3": [160, 153, 152],
        "4": [149, 143, 141],
        "5": [155, 149, 147],
        "6": [151, 145, 143],
        "7": [169, 163, 161],
        "X": [160, 154, 152]
    }
    for card in fullspoil['cards']:
        try:
            cardImage = Image.open(
                'images/' + setcode + '/' + card['name'].replace(' // ', '') + '.jpg')
        except:
            continue
            pass
        card['manaCost'] = ""
        for manaBox in manaBoxes:
            manaSymbol = cardImage.crop(manaBox)
            cardHistogram = manaSymbol.histogram()
            reds = cardHistogram[0:256]
            greens = cardHistogram[256:256 * 2]
            blues = cardHistogram[256 * 2: 256 * 3]
            reds = sum(i * w for i, w in enumerate(reds)) / sum(reds)
            greens = sum(i * w for i, w in enumerate(greens)) / sum(greens)
            blues = sum(i * w for i, w in enumerate(blues)) / sum(blues)
            variance = 768
            for color in colorAverages:
                colorVariance = 0
                colorVariance = colorVariance + \
                    abs(colorAverages[color][0] - reds)
                colorVariance = colorVariance + \
                    abs(colorAverages[color][1] - greens)
                colorVariance = colorVariance + \
                    abs(colorAverages[color][2] - blues)
                if colorVariance < variance:
                    variance = colorVariance
                    closestColor = color
            if variance < 10:
                # if card['name'] in ["Mirage Mirror", "Uncage the Menagerie", "Torment of Hailfire"]:
                #    print card['name'] + " " + str(reds) + " " + str(greens) + " " + str(blues)
                if closestColor in ["2", "5"]:
                    twoVSfive = (
                        manaBox[0] + 1, manaBox[1] + 4, manaBox[2] - 5, manaBox[3] - 2)
                    manaSymbol = cardImage.crop(twoVSfive)
                    cardHistogram = manaSymbol.histogram()
                    reds = cardHistogram[0:256]
                    greens = cardHistogram[256:256 * 2]
                    blues = cardHistogram[256 * 2: 256 * 3]
                    reds = sum(
                        i * w for i, w in enumerate(reds)) / sum(reds)
                    greens = sum(
                        i * w for i, w in enumerate(greens)) / sum(greens)
                    blues = sum(
                        i * w for i, w in enumerate(blues)) / sum(blues)
                    variance = 768
                    colorVariance = 0
                    colorVariance = colorVariance + abs(175 - reds)
                    colorVariance = colorVariance + abs(168 - greens)
                    colorVariance = colorVariance + abs(166 - blues)
                    if colorVariance < 10:
                        closestColor = "2"
                    elif colorVariance > 110 and colorVariance < 120:
                        closestColor = "5"
                    else:
                        continue
                card['manaCost'] = closestColor + card['manaCost']
    return fullspoil


def smash_fullspoil(mtgjson, fullspoil):
    different_keys = {}
    for mtgjson_card in mtgjson['cards']:
        for fullspoil_card in fullspoil['cards']:
            if mtgjson_card['name'] == fullspoil_card['name']:
                for key in fullspoil_card:
                    if key in mtgjson_card:
                        if mtgjson_card[key] != fullspoil_card[key] and key != 'colors':
                            if not fullspoil_card['name'] in different_keys:
                                different_keys[fullspoil_card['name']] = {
                                    key: fullspoil_card[key]}
                            else:
                                different_keys[fullspoil_card['name']
                                               ][key] = fullspoil_card[key]
    for fullspoil_card in fullspoil['cards']:
        WOTC_only = []
        match = False
        for mtgjson_card in mtgjson['cards']:
            if mtgjson_card['name'] == fullspoil_card['name']:
                match = True
        if not match:
            WOTC_only.append(fullspoil_card['name'])
    if len(WOTC_only) > 0:
        print "WOTC only cards: "
        print WOTC_only
    print different_keys
