# -*- coding: utf-8 -*-
import requests
import time
from bs4 import BeautifulSoup as BS
from bs4 import Comment


# mtgjson is optional, will ignore cards found if passed
def get_mythic_cards(url='http://mythicspoiler.com/ixa/', mtgjson=False):
    cards = {'cards': []}
    r = requests.get(url)
    soup = BS(r.text, "html.parser")
    cardurls = soup.find_all('a', 'card')
    urllist = []
    for cardurl in cardurls:
        try:
            urllist.append(url + str(cardurl).split("href=\"")
                           [1].split('"><img')[0])
        except:
            pass
    if not mtgjson:
        for url in urllist:
            card = scrape_mythic_card_page(url)
            if card != '' and 'name' in card and card['name'] != '':
                cards['cards'].append(scrape_mythic_card_page(url))
            time.sleep(.5)
    else:
        for url in urllist:
            needsScraped = True
            for card in mtgjson['cards']:
                if card['name'].lower().replace(' ', '') in url:
                    needsScraped = False
            if needsScraped:
                card = scrape_mythic_card_page(url)
                if card != '' and 'name' in card and card['name'] != '':
                    mtgjson['cards'].append(card)
        cards = mtgjson

    return cards


def scrape_mythic_card_page(url):
    r = requests.get(url)

    soup = BS(r.text, "html.parser")

    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    card = {}

    for comment in comments:
        if comment == 'CARD NAME':
            card['name'] = comment.next_element.strip().replace('"', '')
        elif comment == 'MANA COST':
            try:
                card['manaCost'] = comment.next_element.strip().replace('"', '')
            except:
                pass
        elif comment == 'TYPE':
            card['type'] = comment.next_element.strip().replace('"', '')
        elif comment == 'CARD TEXT':
            buildText = ''
            for element in comment.next_elements:
                try:
                    if not element.strip() in ['CARD TEXT', 'FLAVOR TEXT', '']:
                        if buildText != '':
                            buildText += '\n'
                        buildText += element.strip()
                    if element.strip() == 'FLAVOR TEXT':
                        card['text'] = buildText
                        break
                except:
                    pass
        elif comment == 'Set Number':
            try:
                card['number'] = comment.next_element.strip()
            except:
                pass
        elif comment == 'P/T':
            try:
                if comment.next_element.strip().split('/')[0] != '':
                    card['power'] = comment.next_element.strip().split('/')[0]
                    card['toughness'] = comment.next_element.strip().split('/')[1]
            except:
                pass

    return card
