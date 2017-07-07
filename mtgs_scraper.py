# -*- coding: utf-8 -*-
import requests
import feedparser
import re
import sys
import time
from lxml import html


def scrape_mtgs(url):
    return requests.get(url, headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'Expires': 'Thu, 01 Jan 1970 00:00:00 GMT'}).text


def parse_mtgs(mtgs, manual_cards=[], card_corrections=[], delete_cards=[], related_cards=[], setinfo={"mtgsurl": ""}):
    mtgs = mtgs.replace('utf-16', 'utf-8')
    patterns = ['<b>Name:</b> <b>(?P<name>.*?)<',
                'Cost: (?P<cost>[X]*\d{0,2}[XWUBRGC]*?)<',
                'Type: (?P<type>.*?)<',
                'Pow/Tgh: (?P<pow>.*?)<',
                'Rules Text: (?P<rules>.*?)<br /',
                'Rarity: (?P<rarity>.*?)<',
                'Set Number: #(?P<setnumber>.*?)/'
                ]
    d = feedparser.parse(mtgs)

    cards = []
    for entry in d.items()[5][1]:
        card = dict(cost='', cmc='', img='', pow='', name='', rules='', type='',
                    color='', altname='', colorIdentity='', colorArray=[], colorIdentityArray=[], setnumber='', rarity='')
        summary = entry['summary']
        for pattern in patterns:
            match = re.search(pattern, summary, re.MULTILINE | re.DOTALL)
            if match:
                dg = match.groupdict()
                card[dg.items()[0][0]] = dg.items()[0][1]
        cards.append(card)

    gallery_list = list_mtgs_gallery(setinfo['mtgsurl'])
    for card in cards:
        if card['name'] not in gallery_list:
            print "Removing card scraped from MTGS RSS but not in their gallery: " + card['name']
            cards.remove(card)

    # if we didn't find any cards, let's bail out to prevent overwriting good data
    count = 0
    for card in cards:
        count = count + 1
    if count < 1:
        sys.exit("No cards found, exiting to prevent file overwrite")

    cards2 = []
    for card in cards:
        if 'rules' in card:
            htmltags = re.compile(r'<.*?>')
            card['rules'] = htmltags.sub('', card['rules'])
        if '//' in card['name'] or 'Aftermath' in card['rules']:
            print 'Splitting up Aftermath card ' + card['name']
            card1 = card.copy()
            card2 = dict(cost='', cmc='', img='', pow='', name='', rules='', type='',
                         color='', altname='', colorIdentity='', colorArray=[], colorIdentityArray=[], setnumber='', rarity='')
            if '//' in card['name']:
                card['name'] = card['name'].replace(' // ', '//')
                card1['name'] = card['name'].split('//')[0]
                card2["name"] = card['name'].split('//')[1]
            else:
                card1['name'] = card['name']
                card2["name"] = card['rules'].split(
                    '\n\n')[1].strip().split(' {')[0]
            card1['rules'] = card['rules'].split('\n\n')[0].strip()
            card2["rules"] = "Aftermath" + card['rules'].split('Aftermath')[1]
            card2['cost'] = re.findall(
                r'{.*}', card['rules'])[0].replace('{', '').replace('}', '').upper()
            card2['type'] = re.findall(
                r'}\n.*\n', card['rules'])[0].replace('}', '').replace('\n', '')
            if 'setnumber' in card:
                card1['setnumber'] = card['setnumber'] + 'a'
                card2['setnumber'] = card['setnumber'] + 'b'
            if 'rarity' in card:
                card2['rarity'] = card['rarity']
            card1['layout'] = 'aftermath'
            card2['layout'] = 'aftermath'
            card1['names'] = [card1['name'], card2['name']]
            card2['names'] = [card1['name'], card2['name']]
            cards2.append(card1)
            cards2.append(card2)
        else:
            cards2.append(card)
    cards = cards2

    for card in cards:
        card['name'] = card['name'].replace('&#x27;', '\'')
        card['rules'] = card['rules'].replace('&#x27;', '\'') \
            .replace('&lt;i&gt;', '') \
            .replace('&lt;/i&gt;', '') \
            .replace('&quot;', '"') \
            .replace('blkocking', 'blocking')\
            .replace('&amp;bull;', u'•')\
            .replace('&bull;', u'•')\
            .replace('comes into the', 'enters the')\
            .replace('threeor', 'three or')\
            .replace('[i]', '')\
            .replace('[/i]', '')\
            .replace('Lawlwss', 'Lawless')\
            .replace('Costner', "Counter")
        card['type'] = card['type'].replace('  ', ' ')\
            .replace('Crature', 'Creature')

        if card['type'][-1] == ' ':
            card['type'] = card['type'][:-1]

        if 'cost' in card and len(card['cost']) > 0:
            workingCMC = 0
            stripCost = card['cost'].replace('{', '').replace('}', '')
            for manaSymbol in stripCost:
                if manaSymbol.isdigit():
                    workingCMC += int(manaSymbol)
                elif not manaSymbol == 'X':
                    workingCMC += 1
            card['cmc'] = workingCMC

        for c in 'WUBRG':  # figure out card's color
            if c not in card['colorIdentity']:
                if c in card['cost']:
                    card['color'] += c
                    card['colorIdentity'] += c
                if (c + '}') in card['rules'] or (str.lower(c) + '}') in card['rules']:
                    if not (c in card['colorIdentity']):
                        card['colorIdentity'] += c

    cleanedcards = []
    for card in cards:  # let's remove any cards that are named in delete_cards array
        if not card['name'] in delete_cards:
            cleanedcards.append(card)
    cards = cleanedcards

    cardarray = []
    for card in cards:
        dupe = False
        for dupecheck in cardarray:
            if dupecheck['name'] == card['name']:
                dupe = True
        if dupe == True:
            continue
        for cid in card['colorIdentity']:
            card['colorIdentityArray'].append(cid)
        if 'W' in card['color']:
            card['colorArray'].append('White')
        if 'U' in card['color']:
            card['colorArray'].append('Blue')
        if 'B' in card['color']:
            card['colorArray'].append('Black')
        if 'R' in card['color']:
            card['colorArray'].append('Red')
        if 'G' in card['color']:
            card['colorArray'].append('Green')
        cardpower = ''
        cardtoughness = ''
        if len(card['pow'].split('/')) > 1:
            cardpower = card['pow'].split('/')[0]
            cardtoughness = card['pow'].split('/')[1]
        cardnames = []
        cardnumber = card['setnumber'].lstrip('0')
        if card['name'] in related_cards:
            cardnames.append(card['name'])
            cardnames.append(related_cards[card['name']])
            cardnumber += 'a'
            card['layout'] = 'double-faced'
        for namematch in related_cards:
            if card['name'] == related_cards[namematch]:
                card['layout'] = 'double-faced'
                cardnames.append(namematch)
                if not card['name'] in cardnames:
                    cardnames.append(card['name'])
                    cardnumber += 'b'
        cardnames = []

        if 'number' in card:
            if 'b' in card['number'] or 'a' in card['number']:
                if not 'layout' in card:
                    print card['name'] + " has a a/b number but no 'layout'"
        card['type'] = card['type'].replace('instant', 'Instant').replace(
            'sorcery', 'Sorcery').replace('creature', 'Creature')
        if '-' in card['type']:
            subtype = card['type'].split(' - ')[1].strip()
        else:
            subtype = False
        if subtype:
            subtypes = subtype.split(' ')
        else:
            subtypes = False
        if card['cmc'] == '':
            card['cmc'] = 0
        cardjson = {}
        #cardjson["id"] = hashlib.sha1(code + card['name'] + str(card['name']).lower()).hexdigest()
        cardjson["cmc"] = card['cmc']
        cardjson["manaCost"] = card['cost']
        cardjson["name"] = card['name']
        cardjson["number"] = cardnumber
        # not sure if mtgjson has a list of acceptable rarities, but my application does
        # so we'll warn me but continue to write a non-standard rarity (timeshifted?)
        # may force 'special' in the future
        if card['rarity'] not in ['Mythic Rare', 'Rare', 'Uncommon', 'Common', 'Special', 'Basic Land']:
            #errors.append({"name": card['name'], "key": "rarity", "value": card['rarity']})
            print card['name'] + ' has rarity = ' + card['rarity']
        if subtypes:
            cardjson['subtypes'] = subtypes
        cardjson["rarity"] = card['rarity']
        cardjson["text"] = card['rules']
        cardjson["type"] = card['type']

        workingtypes = card['type']
        if ' - ' in workingtypes:
            workingtypes = card['type'].split(' - ')[0]
        cardjson['types'] = workingtypes.replace('Legendary ', '').replace('Snow ', '')\
            .replace('Elite ', '').replace('Basic ', '').replace('World ', '').replace('Ongoing ', '')\
            .strip().split(' ')
        cardjson["url"] = card['img']

        # optional fields
        if len(card['colorIdentityArray']) > 0:
            cardjson["colorIdentity"] = card['colorIdentityArray']
        if len(card['colorArray']) > 0:
            cardjson["colors"] = card['colorArray']
        if len(cardnames) > 1:
            cardjson["names"] = cardnames
        if 'names' in card:
            cardjson['names'] = card['names']
        if cardpower or cardpower == '0':
            cardjson["power"] = cardpower
            cardjson["toughness"] = cardtoughness
        if card.has_key('loyalty'):
            cardjson["loyalty"] = card['loyalty']
        if card.has_key('layout'):
            cardjson["layout"] = card['layout']

        cardarray.append(cardjson)

    return {"cards": cardarray}


def scrape_mtgs_images(url='http://www.mtgsalvation.com/spoilers/183-hour-of-devastation', mtgscardurl='http://www.mtgsalvation.com/cards/hour-of-devastation/', exemptlist=[]):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    cards = {}
    cardstree = tree.xpath('//*[contains(@class, "log-card")]')
    for child in cardstree:
        if child.text in exemptlist:
            continue
        childurl = mtgscardurl + child.attrib['data-card-id'] + '-' + child.text.replace(
            ' ', '-').replace("'", "").replace(',', '').replace('-//', '')
        cardpage = requests.get(childurl)
        tree = html.fromstring(cardpage.content)
        cardtree = tree.xpath('//img[contains(@class, "card-spoiler-image")]')
        try:
            cardurl = cardtree[0].attrib['src']
        except:
            cardurl = ''
            pass
        cards[child.text] = {
            "url": cardurl
        }
        time.sleep(.2)
    return cards


def list_mtgs_gallery(url=''):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    cards = []
    cardstree = tree.xpath('//*[contains(@class, "log-card")]')
    for child in cardstree:
        cards.append(child.text)
    return cards