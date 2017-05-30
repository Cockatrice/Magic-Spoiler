# -*- coding: utf-8 -*-
import spoilers
import sys
#import configparser
import json
#import urllib

presets = {
    "isfullspoil": True,
    "includeMasterpieces": True
}

with open('set_info.json') as data_file:
    setinfos = json.load(data_file)

with open('cards_manual.json') as data_file:
    manual_cards = json.load(data_file)
    manual_cards = manual_cards['cards']

with open('cards_corrections.json') as data_file:
    card_corrections = json.load(data_file)

with open('cards_delete.json') as data_file:
    delete_cards = json.load(data_file)

errorlog = []

#TODO insert configparser to add config.ini file

for argument in sys.argv:
    for setinfo in setinfos:
        if setinfo in argument.split("=")[0]:
            setinfos[setinfo] = argument.split("=")[0]
    for preset in presets:
        if preset in argument.split("=")[0]:
            presets[preset] = argument.split("=")[1]

def save_allsets(AllSets):
    print "Saving AllSets"

def save_masterpieces(masterpieces):
    with open('out/' + setinfos['masterpieces']['setname'] + '.json', 'w') as outfile:
        json.dump(masterpieces, outfile, sort_keys=True, indent=2, separators=(',', ': '))

def save_setjson(mtgs):
    with open('out/' + setinfos['setname'] + '.json', 'w') as outfile:
        json.dump(mtgs, outfile, sort_keys=True, indent=2, separators=(',', ': '))

def save_errorlog(errorlog):
    fixederrors = []
    unfixederrors = []
    for error in errorlog:
        if 'fixed' in error:
            fixederrors.append(error)
        else:
            unfixederrors.append(error)
    errorlog = {"unfixed": unfixederrors, "fixed": fixederrors}
    with open('out/errors.json', 'w') as outfile:
        json.dump(errorlog, outfile, sort_keys=True, indent=2, separators=(',', ': '))

if __name__ == '__main__':
    AllSets = spoilers.get_allsets()
    mtgs = spoilers.scrape_mtgs('http://www.mtgsalvation.com/spoilers.rss')
    mtgs = spoilers.parse_mtgs(mtgs)
    mtgs = spoilers.correct_cards(mtgs, manual_cards, card_corrections, delete_cards)
    #errorlog.append(temperror)
    #scryfall = spoilers.get_scryfall('https://api.scryfall.com/cards/search?q=++e:' + setinfos['setname'].lower())
    mtgs = spoilers.get_image_urls(mtgs, presets['isfullspoil'], setinfos['setname'], setinfos['setlongname'], setinfos['setsize'])
    #errorlog.append(temperror)
    [mtgs, errors] = spoilers.errorcheck(mtgs)
    errorlog += errors
    spoilers.write_xml(mtgs, setinfos['setname'], setinfos['setlongname'], setinfos['setreleasedate'])
    mtgs = spoilers.add_headers(mtgs, setinfos)
    AllSets = spoilers.make_allsets(AllSets, mtgs, setinfos['setname'])
    if 'masterpieces' in setinfos:
        masterpieces = spoilers.make_masterpieces(setinfos['masterpieces'], AllSets, mtgs)
        [masterpieces, errors] = spoilers.errorcheck(masterpieces)
        errorlog += errors
        #errorlog.append(temperror)
        spoilers.write_xml(masterpieces, setinfos['masterpieces']['setname'], setinfos['masterpieces']['setlongname'], setinfos['masterpieces']['setreleasedate'])
        AllSets = spoilers.make_allsets(AllSets, masterpieces, setinfos['masterpieces']['setname'])
        save_masterpieces(masterpieces)
    save_errorlog(errorlog)
    save_allsets(AllSets)
    save_setjson(mtgs)

#outline
#set variables
#open files
#enable/disable features
#call spoilers
#save files
