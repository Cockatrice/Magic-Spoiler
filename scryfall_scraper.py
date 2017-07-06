# -*- coding: utf-8 -*-
import requests
import time


def get_scryfall(setUrl):
    #getUrl = 'https://api.scryfall.com/cards/search?q=++e:'
    #setUrl = getUrl + setname.lower()
    setDone = False
    scryfall = []

    while setDone == False:
        setcards = requests.get(setUrl)
        setcards = setcards.json()
        if setcards.has_key('data'):
            scryfall.append(setcards['data'])
        else:
            setDone = True
            # print setUrl
            # print setcards
            print 'No Scryfall data'
            scryfall = ['']
        time.sleep(.1)
        if setcards.has_key('has_more'):
            if setcards['has_more'] == True:
                setUrl = setcards['next_page']
            else:
                setDone = True
        else:
            setDone = True
    if not scryfall[0] == '':
        scryfall = convert_scryfall(scryfall[0])
        return {'cards': scryfall}
    else:
        return {'cards': []}


def convert_scryfall(scryfall):
    cards2 = []
    for card in scryfall:
        card2 = {}
        card2['cmc'] = int(card['cmc'])
        if card.has_key('mana_cost'):
            card2['manaCost'] = card['mana_cost'].replace(
                '{', '').replace('}', '')
        else:
            card2['manaCost'] = ''
        card2['name'] = card['name']
        card2['number'] = card['collector_number']
        card2['rarity'] = card['rarity'].replace(
            'mythic', 'mythic rare').title()
        if card.has_key('oracle_text'):
            card2['text'] = card['oracle_text'].replace(
                u"\u2014", '-').replace(u"\u2212", "-")
        else:
            card2['text'] = ''
        card2['url'] = card['image_uri']
        if not 'type_line' in card:
            card['type_line'] = 'Unknown'
        card2['type'] = card['type_line'].replace(u'—', '-')
        cardtypes = card['type_line'].split(u' — ')[0].replace('Legendary ', '').replace('Snow ', '')\
            .replace('Elite ', '').replace('Basic ', '').replace('World ', '').replace('Ongoing ', '')
        cardtypes = cardtypes.split(' ')
        if u' — ' in card['type_line']:
            cardsubtypes = card['type_line'].split(u' — ')[1]
            if ' ' in cardsubtypes:
                card2['subtypes'] = cardsubtypes.split(' ')
            else:
                card2['subtypes'] = [cardsubtypes]
        if 'Legendary' in card['type_line']:
            if card2.has_key('supertypes'):
                card2['supertypes'].append('Legendary')
            else:
                card2['supertypes'] = ['Legendary']
        if 'Snow' in card['type_line']:
            if card2.has_key('supertypes'):
                card2['supertypes'].append('Snow')
            else:
                card2['supertypes'] = ['Snow']
        if 'Elite' in card['type_line']:
            if card2.has_key('supertypes'):
                card2['supertypes'].append('Elite')
            else:
                card2['supertypes'] = ['Elite']
        if 'Basic' in card['type_line']:
            if card2.has_key('supertypes'):
                card2['supertypes'].append('Basic')
            else:
                card2['supertypes'] = ['Basic']
        if 'World' in card['type_line']:
            if card2.has_key('supertypes'):
                card2['supertypes'].append('World')
            else:
                card2['supertypes'] = ['World']
        if 'Ongoing' in card['type_line']:
            if card2.has_key('supertypes'):
                card2['supertypes'].append('Ongoing')
            else:
                card2['supertypes'] = ['Ongoing']
        card2['types'] = cardtypes
        if card.has_key('color_identity'):
            card2['colorIdentity'] = card['color_identity']
        if card.has_key('colors'):
            if not card['colors'] == []:
                card2['colors'] = []
                if 'W' in card['colors']:
                    card2['colors'].append("White")
                if 'U' in card['colors']:
                    card2['colors'].append("Blue")
                if 'B' in card['colors']:
                    card2['colors'].append("Black")
                if 'R' in card['colors']:
                    card2['colors'].append("Red")
                if 'G' in card['colors']:
                    card2['colors'].append("Green")
                #card2['colors'] = card['colors']
        if card.has_key('all_parts'):
            card2['names'] = []
            for partname in card['all_parts']:
                card2['names'].append(partname['name'])
        if card.has_key('power'):
            card2['power'] = card['power']
        if card.has_key('toughness'):
            card2['toughness'] = card['toughness']
        if card.has_key('layout'):
            if card['layout'] != 'normal':
                card2['layout'] = card['layout']
        if card.has_key('loyalty'):
            card2['loyalty'] = card['loyalty']
        if card.has_key('artist'):
            card2['artist'] = card['artist']
        # if card.has_key('source'):
        #    card2['source'] = card['source']
        # if card.has_key('rulings'):
        #    card2['rulings'] = card['rulings']
        if card.has_key('flavor_text'):
            card2['flavor'] = card['flavor_text']
        if card.has_key('multiverse_id'):
            card2['multiverseid'] = card['multiverse_id']

        cards2.append(card2)

    return cards2


def smash_mtgs_scryfall(mtgs, scryfall):
    for mtgscard in mtgs['cards']:
        cardFound = False
        for scryfallcard in scryfall['cards']:
            if scryfallcard['name'] == mtgscard['name']:
                for key in scryfallcard:
                    if key in mtgscard:
                        if not mtgscard[key] == scryfallcard[key]:
                            try:
                                print "%s's key %s\nMTGS    : %s\nScryfall: %s" % (mtgscard['name'], key, mtgscard[key], scryfallcard[key])
                            except:
                                print "Error printing Scryfall vs MTGS debug info for " + mtgscard['name']
                                pass
                cardFound = True
        if not cardFound:
            print "MTGS has card %s and Scryfall does not." % mtgscard['name']
    for scryfallcard in scryfall['cards']:
        cardFound = False
        for mtgscard in mtgs['cards']:
            if scryfallcard['name'] == mtgscard['name']:
                cardFound = True
        if not cardFound:
            print "Scryfall has card %s and MTGS does not." % scryfallcard['name']

    return mtgs
