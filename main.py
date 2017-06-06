# -*- coding: utf-8 -*-
import spoilers
import sys
import os
import shutil
#import configparser
import json
#import urllib

presets = {
    "isfullspoil": True, #when full spoil comes around, we only want to use WOTC images
    "includeMasterpieces": True, #if the set has masterpieces, let's get those too
    "oldRSS": False #maybe MTGS hasn't updated their spoiler.rss but new cards have leaked
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
    #we can modify any of the variables from the set infos file or the presets above at runtime
    #works only for first-level variables currently (editing masterpieces
    #syntax is variable="new value"
    for setinfo in setinfos:
        if setinfo in argument.split("=")[0]:
            setinfos[setinfo] = argument.split("=")[1]
    for preset in presets:
        if preset in argument.split("=")[0]:
            presets[preset] = argument.split("=")[1]

def save_allsets(AllSets):
    #TODO Create AllSets.json for Oracle
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

def save_xml(xmlstring, outfile):
    with open(outfile,'w+') as xmlfile:
        xmlfile.write(xmlstring)

if __name__ == '__main__':
    AllSets = spoilers.get_allsets() #get AllSets from mtgjson
    if presets['oldRSS']:
        mtgs = {"cards":[]}
    else:
        mtgs = spoilers.scrape_mtgs('http://www.mtgsalvation.com/spoilers.rss') #scrape mtgs rss feed
        mtgs = spoilers.parse_mtgs(mtgs) #parse spoilers into mtgjson format
    mtgs = spoilers.correct_cards(mtgs, manual_cards, card_corrections, delete_cards) #fix using the fixfiles
    scryfall = spoilers.get_scryfall('https://api.scryfall.com/cards/search?q=++e:' + setinfos['setname'].lower())
    mtgs = spoilers.get_image_urls(mtgs, presets['isfullspoil'], setinfos['setname'], setinfos['setlongname'], setinfos['setsize']) #get images
    mtgjson = spoilers.smash_mtgs_scryfall(mtgs, scryfall)
    [mtgjson, errors] = spoilers.errorcheck(mtgjson) #check for errors where possible
    errorlog += errors
    spoilers.write_xml(mtgjson, setinfos['setname'], setinfos['setlongname'], setinfos['setreleasedate'])
    save_xml(spoilers.pretty_xml(setinfos['setname']), 'out/spoiler.xml')
    mtgs = spoilers.add_headers(mtgjson, setinfos)
    AllSets = spoilers.make_allsets(AllSets, mtgjson, setinfos['setname'])
    if 'masterpieces' in setinfos: #repeat all of the above for masterpieces
        #masterpieces aren't in the rss feed, so for the new cards, we'll go to their individual pages on mtgs
        #old cards will get their infos copied from mtgjson (including fields that may not apply like 'artist')
        #the images will still come from mtgs
        masterpieces = spoilers.make_masterpieces(setinfos['masterpieces'], AllSets, mtgjson)
        [masterpieces, errors] = spoilers.errorcheck(masterpieces)
        errorlog += errors
        spoilers.write_xml(masterpieces, setinfos['masterpieces']['setname'], setinfos['masterpieces']['setlongname'], setinfos['masterpieces']['setreleasedate'])
        AllSets = spoilers.make_allsets(AllSets, masterpieces, setinfos['masterpieces']['setname'])
        save_masterpieces(masterpieces)
    save_errorlog(errorlog)
    save_allsets(AllSets)
    save_setjson(mtgjson)
