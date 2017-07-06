# -*- coding: utf-8 -*-
import requests
import re
import os
from lxml import html
import datetime
import json
import mtgs_scraper
import xml.dom.minidom


def correct_cards(mtgjson, manual_cards=[], card_corrections=[], delete_cards=[]):
    mtgjson2 = []
    for card in manual_cards:
        if 'manaCost' in card:
            card['manaCost'] = str(card['manaCost'])
        if 'number' in card:
            card['number'] = str(card['number'])
        if 'cmc' not in card:
            workingCMC = 0
            if 'manaCost' in card:
                stripCost = card['manaCost'].replace('{','').replace('}','')
                for manaSymbol in stripCost:
                    if manaSymbol.isdigit():
                        workingCMC += int(manaSymbol)
                    elif not manaSymbol == 'X':
                        workingCMC += 1
            card['cmc'] = workingCMC
        if 'types' not in card:
            card['types'] = []
            workingtypes = card['type']
            if ' - ' in workingtypes:
                workingtypes = card['type'].split(' - ')[0]
            card['types'] = workingtypes.replace('Legendary ', '').replace('Snow ', '') \
                .replace('Elite ', '').replace('Basic ', '').replace('World ', '').replace('Ongoing ', '') \
                .strip().split(' ')
        if 'subtypes' not in card:
            #            if '—' in card['type']:
            #                workingSubtypes = card['type'].split('—')[1].strip()
            if '-' in card['type']:
                workingSubtypes = card['type'].split('-')[1].strip()
            if workingSubtypes:
                card['subtypes'] = workingSubtypes.split(' ')
        colorMap = {
            "W": "White",
            "U": "Blue",
            "B": "Black",
            "R": "Red",
            "G": "Green"
        }
        if 'manaCost' in card:
            if 'text' in card and not 'Devoid' in card['text']:
                for letter in str(card['manaCost']):
                    if not letter.isdigit() and not letter == 'X':
                        if 'colorIdentity' in card:
                            if not letter in card['colorIdentity']:
                                card['colorIdentity'] += letter
                        else:
                            card['colorIdentity'] = [letter]
                        if 'colors' in card:
                            if not colorMap[letter] in card['colors']:
                                card['colors'].append(colorMap[letter])
                        else:
                            card['colors'] = [colorMap[letter]]
        if 'text' in card:
            for CID in colorMap:
                if '{' + CID + '}' in card['text']:
                    if 'colorIdentity' in card:
                        if not CID in card['colorIdentity']:
                            card['colorIdentity'] += CID
                    else:
                        card['colorIdentity'] = [CID]
    manual_added = []
    for card in mtgjson['cards']:
        isManual = False
        for manualCard in manual_cards:
            if card['name'] == manualCard['name']:
                mtgjson2.append(manualCard)
                manual_added.append(manualCard['name'] + " (overwritten)")
                isManual = True
        if not isManual and not card['name'] in delete_cards:
            mtgjson2.append(card)
    for manualCard in manual_cards:
        addManual = True
        for card in mtgjson['cards']:
            if manualCard['name'] == card['name']:
                addManual = False
        if addManual:
            mtgjson2.append(manualCard)
            manual_added.append(manualCard['name'])
    if manual_added != []:
        print "Manual Cards Added: " + str(manual_added).strip('[]')

    mtgjson = {"cards": mtgjson2}

    return mtgjson


def error_check(mtgjson, card_corrections={}):
    errors = []
    for card in mtgjson['cards']:
        for key in card:
            if key == "":
                errors.append({"name": card['name'], "key": key, "value": ""})
        requiredKeys = ['name', 'type', 'types']
        for requiredKey in requiredKeys:
            if not requiredKey in card:
                errors.append(
                    {"name": card['name'], "key": key, "missing": True})
        if 'text' in card:
            card['text'] = card['text'].replace('<i>', '').replace(
                '</i>', '').replace('<em>', '').replace('</em', '').replace('(', '').replace('&bull;', u'•')
        if 'type' in card:
            if 'Planeswalker' in card['type']:
                if not 'loyalty' in card:
                    errors.append(
                        {"name": card['name'], "key": "loyalty", "value": ""})
                if not card['rarity'] == 'Mythic Rare':
                    errors.append(
                        {"name": card['name'], "key": "rarity", "value": card['rarity']})
                if not 'subtypes' in card:
                    errors.append({"name": card['name'], "key": "subtypes", "oldvalue": "",
                                   "newvalue": card['name'].split(" ")[0], "fixed": True})
                    if not card['name'].split(' ')[0] == 'Ob' and not card['name'].split(' ') == 'Nicol':
                        card["subtypes"] = card['name'].split(" ")[0]
                    else:
                        card["subtypes"] = card['name'].split(" ")[1]
                if not 'types' in card:
                    #errors.append({"name": card['name'], "key": "types", "fixed": True, "oldvalue": "", "newvalue": ["Planeswalker"]})
                    card['types'] = ["Planeswalker"]
                elif not "Planeswalker" in card['types']:
                    #errors.append({"name": card['name'], "key": "types", "fixed": True, "oldvalue": card['types'], "newvalue": card['types'] + ["Planeswalker"]})
                    card['types'].append("Planeswalker")
            if 'Creature' in card['type']:
                if not 'power' in card:
                    errors.append(
                        {"name": card['name'], "key": "power", "value": ""})
                if not 'toughness' in card:
                    errors.append(
                        {"name": card['name'], "key": "toughness", "value": ""})
                if not 'subtypes' in card:
                    errors.append(
                        {"name": card['name'], "key": "subtypes", "value": ""})
        if 'manaCost' in card:
            workingCMC = 0
            stripCost = card['manaCost'].replace('{', '').replace('}', '')
            for manaSymbol in stripCost:
                if manaSymbol.isdigit():
                    workingCMC += int(manaSymbol)
                elif not manaSymbol == 'X':
                    workingCMC += 1
            if not 'cmc' in card:
                errors.append(
                    {"name": card['name'], "key": "cmc", "value": ""})
            elif not card['cmc'] == workingCMC:
                errors.append({"name": card['name'], "key": "cmc", "oldvalue": card['cmc'],
                               "newvalue": workingCMC, "fixed": True, "match": card['manaCost']})
                card['cmc'] = workingCMC
        else:
            if 'type' in card and not 'land' in card['type'].lower():
                errors.append(
                    {"name": card['name'], "key": "manaCost", "value": ""})
        if not 'cmc' in card:
            errors.append({"name": card['name'], "key": "cmc", "value": ""})
        else:
            if not isinstance(card['cmc'], int):
                errors.append({"name": card['name'], "key": "cmc", "oldvalue": card['cmc'], "newvalue": int(
                    card['cmc']), "fixed": True})
                card['cmc'] = int(card['cmc'])
            else:
                if card['cmc'] > 0:
                    if not 'manaCost' in card:
                        errors.append(
                            {"name": card['name'], "key": "manaCost", "value": "", "match": card['cmc']})
                else:
                    if 'manaCost' in card:
                        errors.append(
                            {"name": card['name'], "key": "manaCost", "oldvalue": card['manaCost'], "fixed": True})
                        del card["manaCost"]
        if 'colors' in card:
            if not 'colorIdentity' in card:
                if 'text' in card:
                    if not 'devoid' in card['text'].lower():
                        errors.append(
                            {"name": card['name'], "key": "colorIdentity", "value": ""})
                else:
                    errors.append(
                        {"name": card['name'], "key": "colorIdentity", "value": ""})
        if 'colorIdentity' in card:
            if not 'colors' in card:
                # this one will false positive on emerge cards
                if not 'Land' in card['type'] and not 'Artifact' in card['type'] and not 'Eldrazi' in card['type']:
                    if 'text' in card:
                        if not 'emerge' in card['text'].lower() and not 'devoid' in card['text'].lower():
                            errors.append(
                                {"name": card['name'], "key": "colors", "value": ""})
                    else:
                        errors.append(
                            {"name": card['name'], "key": "colors", "value": ""})
                # if not 'Land' in card['type'] and not 'Artifact' in card['type'] and not 'Eldrazi' in card['type']:
                #    errors.append({"name": card['name'], "key": "colors", "value": ""})
        if not 'url' in card:
            errors.append({"name": card['name'], "key": "url", "value": ""})
        elif len(card['url']) < 10:
            errors.append({"name": card['name'], "key": "url", "value": ""})
        if not 'number' in card:
            errors.append({"name": card['name'], "key": "number", "value": ""})
        if not 'types' in card:
            errors.append({"name": card['name'], "key": "types", "value": ""})

    # we're going to loop through again and make sure split cards get paired
    for card in mtgjson['cards']:
        if 'layout' in card:
            if card['layout'] == 'split' or card['layout'] == 'meld' or card['layout'] == 'aftermath':
                if not 'names' in card:
                    errors.append(
                        {"name": card['name'], "key": "names", "value": ""})
                else:
                    for related_card_name in card['names']:
                        if related_card_name != card['name']:
                            related_card = False
                            for card2 in mtgjson['cards']:
                                if card2['name'] == related_card_name:
                                    related_card = card2
                            if not related_card:
                                errors.append(
                                    {"name": card['name'], "key": "names", "value": card['names']})
                            else:
                                if 'colors' in related_card:
                                    for color in related_card['colors']:
                                        if not 'colors' in card:
                                            card['colors'] = [color]
                                        elif not color in card['colors']:
                                            card['colors'].append(color)
                                if 'colorIdentity' in related_card:
                                    for colorIdentity in related_card['colorIdentity']:
                                        if not 'colorIdentity' in card:
                                            card['colorIdentity'] = [
                                                colorIdentity]
                                        elif not colorIdentity in card['colorIdentity']:
                                            card['colorIdentity'].append(
                                                colorIdentity)
                if 'number' in card:
                    if not 'a' in card['number'] and not 'b' in card['number'] and not 'c' in card['number']:
                        errors.append(
                            {"name": card['name'], "key": "number", "value": card['number']})

    for card in mtgjson['cards']:
        for cardCorrection in card_corrections:
            if card['name'] == cardCorrection:
                for correctionType in card_corrections[cardCorrection]:
                    # if not correctionType in card and correctionType not in :
                    #    sys.exit("Invalid correction for " + cardCorrection + " of type " + card)
                    if not correctionType == 'name':
                        if correctionType == 'img':
                            card['url'] = card_corrections[cardCorrection][correctionType]
                        else:
                            card[correctionType] = card_corrections[cardCorrection][correctionType]
                if 'name' in card_corrections[cardCorrection]:
                    card['name'] = card_corrections[cardCorrection]['name']

    return [mtgjson, errors]


def remove_corrected_errors(errorlog=[], card_corrections=[], print_fixed=False):
    errorlog2 = {}
    for error in errorlog:
        if not print_fixed:
            if 'fixed' in error and error['fixed'] == True:
                continue
        removeError = False
        for correction in card_corrections:
            for correction_type in card_corrections[correction]:
                if error['name'] == correction:
                    if error['key'] == correction_type:
                        removeError = True
        if not removeError:
            if not error['name'] in errorlog2:
                errorlog2[error['name']] = {}
            if not 'value' in error:
                error['value'] = ""
            errorlog2[error['name']][error['key']] = error['value']
    return errorlog2


def download_images(mtgjson, setcode):
    if not os.path.isdir('images/' + setcode):
        os.makedirs('images/' + setcode)
    if 'cards' in mtgjson:
        jsoncards = mtgjson['cards']
    else:
        jsoncards = mtgjson
    for card in jsoncards:
        if card['url']:
            if os.path.isfile('images/' + setcode + '/' + card['name'].replace(' // ', '') + '.jpg'):
                continue
            # print 'Downloading ' + card['url'] + ' to images/' + setcode + '/' + card['name'].replace(' // ','') + '.jpg'
            requests.get(card['url'], 'images/' + setcode +
                               '/' + card['name'].replace(' // ', '') + '.jpg')


def get_image_urls(mtgjson, isfullspoil, setname, setlongname, setSize=269, setinfo=False):
    IMAGES = 'http://magic.wizards.com/en/content/' + \
        setlongname.lower().replace(' ', '-') + '-cards'
    IMAGES2 = 'http://mythicspoiler.com/newspoilers.html'
    IMAGES3 = 'http://magic.wizards.com/en/articles/archive/card-image-gallery/' + \
        setlongname.lower().replace('of', '').replace('  ', ' ').replace(' ', '-')

    text = requests.get(IMAGES).text
    text2 = requests.get(IMAGES2).text
    text3 = requests.get(IMAGES3).text
    wotcpattern = r'<img alt="{}.*?" src="(?P<img>.*?\.png)"'
    wotcpattern2 = r'<img src="(?P<img>.*?\.png).*?alt="{}.*?"'
    mythicspoilerpattern = r' src="' + setname.lower() + '/cards/{}.*?.jpg">'
    WOTC = []
    for c in mtgjson['cards']:
        if 'names' in c:
            cardname = ' // '.join(c['names'])
        else:
            cardname = c['name']
        match = re.search(wotcpattern.format(
            cardname.replace('\'', '&rsquo;')), text, re.DOTALL)
        if match:
            c['url'] = match.groupdict()['img']
        else:
            match3 = re.search(wotcpattern2.format(
                cardname.replace('\'', '&rsquo;')), text3)
            if match3:
                c['url'] = match3.groupdict()['img']
            else:
                match4 = re.search(wotcpattern.format(
                    cardname.replace('\'', '&rsquo;')), text3, re.DOTALL)
                if match4:
                    c['url'] = match4.groupdict()['img']
                else:
                    match2 = re.search(mythicspoilerpattern.format(cardname.lower().replace(' // ', '').replace(
                        ' ', '').replace('&#x27;', '').replace('-', '').replace('\'', '').replace(',', '')), text2, re.DOTALL)
                    if match2 and not isfullspoil:
                        c['url'] = match2.group(0).replace(
                            ' src="', 'http://mythicspoiler.com/').replace('">', '')
                    pass
        if 'wizards.com' in c['url']:
            WOTC.append(c['name'])
    if setinfo:
        if 'mtgsurl' in setinfo and 'mtgscardpath' in setinfo:
            mtgsImages = mtgs_scraper.scrape_mtgs_images(
                setinfo['mtgsurl'], setinfo['mtgscardpath'], WOTC)
            for card in mtgjson['cards']:
                if card['name'] in mtgsImages:
                    if mtgsImages[card['name']]['url'] != '':
                        card['url'] = mtgsImages[card['name']]['url']

    for card in mtgjson['cards']:
        if len(str(card['url'])) < 10:
            print(card['name'] + ' has no image.')
    return mtgjson


def write_xml(mtgjson, setname, setlongname, setreleasedate, split_cards=[]):
    if not os.path.isdir('out/'):
        os.makedirs('out/')
    cardsxml = open('out/' + setname + '.xml', 'w+')
    cardsxml.truncate()
    count = 0
    dfccount = 0
    newest = ''
    related = 0
    cardsxml.write("<?xml version='1.0' encoding='UTF-8'?>\n"
                   "<cockatrice_carddatabase version='3'>\n"
                   "<sets>\n<set>\n<name>"
                   + setname +
                   "</name>\n"
                   "<longname>"
                   + setlongname +
                   "</longname>\n"
                   "<settype>Expansion</settype>\n"
                   "<releasedate>"
                   + setreleasedate +
                   "</releasedate>\n"
                   "</set>\n"
                   "</sets>\n"
                   "<cards>\n")
    # print mtgjson
    for card in mtgjson["cards"]:
        for carda in split_cards:
            if card["name"] == split_cards[carda]:
                continue
        if count == 0:
            newest = card["name"]
        count += 1
        name = card["name"]
        if card.has_key("manaCost"):
            manacost = card["manaCost"].replace('{', '').replace('}', '')
        else:
            manacost = ""
        if card.has_key("power") or card.has_key("toughness"):
            if card["power"]:
                pt = str(card["power"]) + "/" + str(card["toughness"])
            else:
                pt = 0
        else:
            pt = 0
        if card.has_key("text"):
            text = card["text"]
        else:
            text = ""
        cardcmc = str(card['cmc'])
        cardtype = card["type"]
        if card.has_key("names"):
            if "layout" in card:
                if card['layout'] == 'split' or card['layout'] == 'aftermath':
                    if 'names' in card:
                        if card['name'] == card['names'][0]:
                            for jsoncard in mtgjson["cards"]:
                                if jsoncard['name'] == card['names'][1]:
                                    cardtype += " // " + jsoncard["type"]
                                    manacost += " // " + \
                                        (jsoncard["manaCost"]).replace(
                                            '{', '').replace('}', '')
                                    cardcmc += " // " + str(jsoncard["cmc"])
                                    text += "\n---\n" + jsoncard["text"]
                                    name += " // " + jsoncard['name']
                else:
                    print card["name"] + " has names, but layout != split"
            else:
                print card["name"] + " has multiple names and no 'layout' key"

        tablerow = "1"
        if "Land" in cardtype:
            tablerow = "0"
        elif "Sorcery" in cardtype:
            tablerow = "3"
        elif "Instant" in cardtype:
            tablerow = "3"
        elif "Creature" in cardtype:
            tablerow = "2"

        if 'number' in card:
            if 'b' in str(card['number']):
                if 'layout' in card:
                    if card['layout'] == 'split' or card['layout'] == 'aftermath':
                        # print "We're skipping " + card['name'] + " because it's the right side of a split card"
                        continue

        cardsxml.write("<card>\n")
        cardsxml.write("<name>" + name.encode('utf-8') + "</name>\n")
        cardsxml.write(
            '<set rarity="' + card['rarity'] + '" picURL="' + card["url"] + '">' + setname + '</set>\n')
        cardsxml.write(
            "<manacost>" + manacost.encode('utf-8') + "</manacost>\n")
        cardsxml.write("<cmc>" + cardcmc + "</cmc>\n")
        if card.has_key('colors'):
            colorTranslate = {
                "White": "W",
                "Blue": "U",
                "Black": "B",
                "Red": "R",
                "Green": "G"
            }
            for color in card['colors']:
                cardsxml.write(
                    '<color>' + colorTranslate[color] + '</color>\n')
        if name + ' enters the battlefield tapped' in text:
            cardsxml.write("<cipt>1</cipt>\n")
        cardsxml.write("<type>" + cardtype.encode('utf-8') + "</type>\n")
        if pt:
            cardsxml.write("<pt>" + pt + "</pt>\n")
        if card.has_key('loyalty'):
            cardsxml.write("<loyalty>" + str(card['loyalty']) + "</loyalty>\n")
        cardsxml.write("<tablerow>" + tablerow + "</tablerow>\n")
        cardsxml.write("<text>" + text.encode('utf-8') + "</text>\n")
        if related:
            #    for relatedname in related:
            cardsxml.write(
                "<related>" + related.encode('utf-8') + "</related>\n")
            related = ''

        cardsxml.write("</card>\n")

    cardsxml.write("</cards>\n</cockatrice_carddatabase>")

    print 'XML Stats for ' + setlongname
    print 'Total cards: ' + str(count)
    if dfccount > 0:
        print 'DFC: ' + str(dfccount)
    print 'Newest: ' + str(newest)
    print 'Runtime: ' + str(datetime.datetime.today().strftime('%H:%M')) + ' on ' + str(datetime.date.today())


def write_combined_xml(mtgjson, setinfos):
    if not os.path.isdir('out/'):
        os.makedirs('out/')
    cardsxml = open('out/spoiler.xml', 'w+')
    cardsxml.truncate()
    cardsxml.write("<?xml version='1.0' encoding='UTF-8'?>\n"
                   "<cockatrice_carddatabase version='3'>\n")
    cardsxml.write("<!--\n    created (UTC): " + datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y")
                   + "\n    by: Magic-Spoiler project @ https://github.com/Cockatrice/Magic-Spoiler\n    -->\n")
    cardsxml.write("<sets>\n")
    for setcode in mtgjson:
        setobj = mtgjson[setcode]
        if 'cards' in setobj and len(setobj['cards']) > 0:
            cardsxml.write("<set>\n<name>"
                           + setcode +
                           "</name>\n"
                           "<longname>"
                           + setobj['name'] +
                           "</longname>\n"
                           "<settype>"
                           + setobj['type'].title() +
                           "</settype>\n"
                           "<releasedate>"
                           + setobj['releaseDate'] +
                           "</releasedate>\n"
                           "</set>\n")
    cardsxml.write(
        "</sets>\n"
        "<cards>\n")
    count = 0
    dfccount = 0
    newest = ''
    related = 0
    for setcode in mtgjson:
        setobj = mtgjson[setcode]
        for card in setobj["cards"]:
            if 'layout' in card and (card['layout'] == 'split' or card['layout'] == 'aftermath'):
                if 'b' in card["number"]:
                    continue
            if count == 0:
                newest = card["name"]
            count += 1
            name = card["name"]
            if card.has_key("manaCost"):
                manacost = card["manaCost"].replace('{', '').replace('}', '')
            else:
                manacost = ""
            if card.has_key("power") or card.has_key("toughness"):
                if card["power"]:
                    pt = str(card["power"]) + "/" + str(card["toughness"])
                else:
                    pt = 0
            else:
                pt = 0
            if card.has_key("text"):
                text = card["text"]
            else:
                text = ""
            cardcmc = str(card['cmc'])
            cardtype = card["type"]
            if card.has_key("names"):
                if "layout" in card:
                    if card["layout"] != 'split' and card["layout"] != 'aftermath':
                        if len(card["names"]) > 1:
                            if card["names"][0] == card["name"]:
                                related = card["names"][1]
                                text += '\n\n(Related: ' + \
                                    card["names"][1] + ')'
                                dfccount += 1
                            elif card['names'][1] == card['name']:
                                related = card["names"][0]
                                text += '\n\n(Related: ' + \
                                    card["names"][0] + ')'
                    else:
                        for cardb in setobj['cards']:
                            if cardb['name'] == card["names"][1]:
                                cardtype += " // " + cardb['type']
                                manacost += " // " + \
                                    (cardb["manaCost"]).replace(
                                        '{', '').replace('}', '')
                                cardcmc += " // " + str(cardb["cmc"])
                                text += "\n---\n" + cardb["text"]
                                name += " // " + cardb['name']
                else:
                    print card["name"] + " has multiple names and no 'layout' key"

            tablerow = "1"
            if "Land" in cardtype:
                tablerow = "0"
            elif "Sorcery" in cardtype:
                tablerow = "3"
            elif "Instant" in cardtype:
                tablerow = "3"
            elif "Creature" in cardtype:
                tablerow = "2"

            if 'number' in card:
                if 'b' in card['number']:
                    if 'layout' in card:
                        if card['layout'] == 'split' or card['layout'] == 'aftermath':
                            # print "We're skipping " + card['name'] + " because it's the right side of a split card"
                            continue

            cardsxml.write("<card>\n")
            cardsxml.write("<name>" + name.encode('utf-8') + "</name>\n")
            cardsxml.write(
                '<set rarity="' + card['rarity'] + '" picURL="' + card["url"] + '">' + setcode + '</set>\n')
            cardsxml.write(
                "<manacost>" + manacost.encode('utf-8') + "</manacost>\n")
            cardsxml.write("<cmc>" + cardcmc + "</cmc>\n")
            if card.has_key('colors'):
                colorTranslate = {
                    "White": "W",
                    "Blue": "U",
                    "Black": "B",
                    "Red": "R",
                    "Green": "G"
                }
                for color in card['colors']:
                    cardsxml.write(
                        '<color>' + colorTranslate[color] + '</color>\n')
            if name + ' enters the battlefield tapped' in text:
                cardsxml.write("<cipt>1</cipt>\n")
            cardsxml.write("<type>" + cardtype.encode('utf-8') + "</type>\n")
            if pt:
                cardsxml.write("<pt>" + pt + "</pt>\n")
            if card.has_key('loyalty'):
                cardsxml.write(
                    "<loyalty>" + str(card['loyalty']) + "</loyalty>\n")
            cardsxml.write("<tablerow>" + tablerow + "</tablerow>\n")
            cardsxml.write("<text>" + text.encode('utf-8') + "</text>\n")
            if related:
                #    for relatedname in related:
                cardsxml.write(
                    "<related>" + related.encode('utf-8') + "</related>\n")
                related = ''

            cardsxml.write("</card>\n")

    cardsxml.write("</cards>\n</cockatrice_carddatabase>")

    print 'XML COMBINED STATS'
    print 'Total cards: ' + str(count)
    if dfccount > 0:
        print 'DFC: ' + str(dfccount)
    print 'Newest: ' + str(newest)
    print 'Runtime: ' + str(datetime.datetime.today().strftime('%H:%M')) + ' on ' + str(datetime.date.today())


def pretty_xml(infile):
    # or xml.dom.minidom.parseString(xml_string)
    prettyxml = xml.dom.minidom.parse(infile)
    pretty_xml_as_string = prettyxml.toprettyxml(newl='')
    return pretty_xml_as_string


def make_allsets(AllSets, mtgjson, setname):
    AllSets[setname] = mtgjson
    return AllSets


def scrape_masterpieces(url='http://www.mtgsalvation.com/spoilers/181-amonkhet-invocations', mtgscardurl='http://www.mtgsalvation.com/cards/amonkhet-invocations/'):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    cards = []
    cardstree = tree.xpath('//*[contains(@class, "log-card")]')
    for child in cardstree:
        childurl = mtgscardurl + \
            child.attrib['data-card-id'] + '-' + child.text.replace(' ', '-')
        cardpage = requests.get(childurl)
        tree = html.fromstring(cardpage.content)
        cardtree = tree.xpath('//img[contains(@class, "card-spoiler-image")]')
        try:
            cardurl = cardtree[0].attrib['src']
        except:
            cardurl = ''
            pass
        card = {
            "name": child.text,
            "url": cardurl
        }
        cards.append(card)
    return cards


def make_masterpieces(headers, AllSets, spoil):
    masterpieces = scrape_masterpieces(
        headers['mtgsurl'], headers['mtgscardpath'])
    masterpieces2 = []
    for masterpiece in masterpieces:
        matched = False
        if headers['setname'] in AllSets:
            for oldMasterpiece in AllSets[headers['setname']]['cards']:
                if masterpiece['name'] == oldMasterpiece['name']:
                    matched = True
        for set in AllSets:
            if not matched:
                for oldcard in AllSets[set]['cards']:
                    if oldcard['name'] == masterpiece['name'] and not matched:
                        mixcard = oldcard
                        mixcard['url'] = masterpiece['url']
                        mixcard['rarity'] = 'Mythic Rare'
                        masterpieces2.append(mixcard)
                        matched = True
                        break
        for spoilcard in spoil['cards']:
            if not matched:
                if spoilcard['name'] == masterpiece['name']:
                    mixcard = spoilcard
                    mixcard['rarity'] = 'Mythic Rare'
                    mixcard['url'] = masterpiece['url']
                    masterpieces2.append(mixcard)
                    matched = True
                    break
        if not matched:
            print "We couldn't find a card object to assign the data to for masterpiece " + masterpiece['name']
            masterpieces2.append(masterpiece)
    mpsjson = {
        "name": headers['setlongname'],
        "alternativeNames": headers['alternativeNames'],
        "code": headers['setname'],
        "releaseDate": headers['setreleasedate'],
        "border": "black",
        "type": "masterpiece",
        "cards": masterpieces2
    }
    return mpsjson


def set_has_cards(setinfo, manual_cards, mtgjson):
    if setinfo['setname'] in manual_cards or setinfo['setname'] in mtgjson:
        return True
    for card in manual_cards['cards']:
        if set in card:
            if set == setinfo['setname']:
                return True


def get_allsets():
    headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko / 20071127 Firefox / 2.0.0.11'}
    json_file = requests.get('http://mtgjson.com/json/AllSets.json', headers=headers)
    AllSets = json.loads(json_file.text)
    return AllSets


def add_headers(mtgjson, setinfos):
    mtgjson2 = {
        "border": "black",
        "code": setinfos['setname'],
        "name": setinfos['setlongname'],
        "releaseDate": setinfos['setreleasedate'],
        "type": setinfos['settype'],
        "cards": mtgjson['cards']
    }
    if not 'noBooster' in setinfos:
        mtgjson2['booster'] = [
                [
                    "rare",
                    "mythic rare"
                ],
            "uncommon",
            "uncommon",
            "uncommon",
            "common",
            "common",
            "common",
            "common",
            "common",
            "common",
            "common",
            "common",
            "common",
            "common",
            "land",
            "marketing"
        ],
    if 'blockname' in setinfos:
        mtgjson2['block'] = setinfos['blockname']
    return mtgjson2
