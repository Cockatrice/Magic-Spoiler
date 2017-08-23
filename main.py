# -*- coding: utf-8 -*-
import spoilers
import mtgs_scraper
import scryfall_scraper
import mythic_scraper
import wizards_scraper
import os
import json
import io
import sys
import verify_files
import requests
from lxml import etree

presets = {
    "isfullspoil": False,  # when full spoil comes around, we only want to use WOTC images
    "includeMasterpieces": True,  # if the set has masterpieces, let's get those too
    "oldRSS": False,  # maybe MTGS hasn't updated their spoiler.rss but new cards have leaked
    "dumpXML": False,  # let travis print XML for testing
    # only use Scryfall data (no mtgs for ANY sets)
    "scryfallOnly": False,
    "dumpErrors": True  # print the error log from out/errors.json
}

setinfos = verify_files.load_file('set_info.yml','yaml_multi')
manual_sets = verify_files.load_file('cards_manual.yml','yaml')
card_corrections = verify_files.load_file('cards_corrections.yml','yaml')
delete_cards = verify_files.load_file('cards_delete.yml','yaml')

errorlog = []

# TODO insert configparser to add config.ini file


def parseargs():
    for argument in sys.argv:
        for preset in presets:
            if argument.split('=')[0].lower().replace('-', '') == preset.lower():
                argvalue = argument.split('=')[1]
                if argvalue in ['true', 'True', 'T', 't']:
                    argvalue = True
                elif argvalue in ['false', 'False', 'F', 'f']:
                    argvalue = False
                presets[preset] = argvalue
                print "Setting preset " + preset + " to value " + str(argvalue)


def save_allsets(AllSets):
    with io.open('out/AllSets.json', 'w', encoding='utf8') as json_file:
        data = json.dumps(AllSets, ensure_ascii=False, encoding='utf8',
                          indent=2, sort_keys=True, separators=(',', ':'))
        json_file.write(unicode(data))


def save_masterpieces(masterpieces, setinfo):
    with open('out/' + setinfo['masterpieces']['code'] + '.json', 'w') as outfile:
        json.dump(masterpieces, outfile, sort_keys=True,
                  indent=2, separators=(',', ': '))


def save_setjson(mtgs, filename):
    with io.open('out/' + filename + '.json', 'w', encoding='utf8') as json_file:
        data = json.dumps(mtgs, ensure_ascii=False, encoding='utf8',
                          indent=2, sort_keys=True, separators=(',', ':'))
        json_file.write(unicode(data))


def save_errorlog(errorlog):
    with open('out/errors.json', 'w') as outfile:
        json.dump(errorlog, outfile, sort_keys=True,
                  indent=2, separators=(',', ': '))


def save_xml(xmlstring, outfile):
    if os.path.exists(outfile):
        append_or_write = 'w'
    else:
        append_or_write = 'w'
    with open(outfile, append_or_write) as xmlfile:
        xmlfile.write(xmlstring.encode('utf-8'))


def verify_xml(file, schema):
    try:
        schema_doc = etree.fromstring(schema)
    except Exception as e:
        print "XSD for " + file + " is invalid"
        print schema
        print e
        return False
    xml_schema = etree.XMLSchema(schema_doc)
    try:
        xml_doc = etree.parse(file)
    except Exception as e:
        print "XML file " + file + " is invalid"
        print e
        return False
    try:
        xml_schema.assert_(xml_doc)
    except:
        xsd_errors = xml_schema.error_log
        print "Errors validating XML file " + file + " against XSD:"
        for error in xsd_errors:
            print error
        sys.exit("Error: " + file + " does not pass Cockatrice XSD validation.")
        return False
    return True


if __name__ == '__main__':
    parseargs()
    AllSets = spoilers.get_allsets()  # get AllSets from mtgjson
    combinedjson = {}
    for setinfo in setinfos:
        if setinfo['code'] in AllSets:
            print "Found " +setinfo['code']+ " set from set_info.yml in MTGJSON, not adding it"
            continue
        if presets['oldRSS'] or 'noRSS' in setinfo and setinfo['noRSS']:
            mtgs = {"cards": []}
        else:
            mtgs = mtgs_scraper.scrape_mtgs(
                'http://www.mtgsalvation.com/spoilers.rss')  # scrape mtgs rss feed
            mtgs = mtgs_scraper.parse_mtgs(mtgs, setinfo=setinfo)  # parse spoilers into mtgjson format
        if not setinfo['code'] in manual_sets:
            manual_cards = ['']
        else:
            manual_cards = manual_sets[setinfo['code']]
        mtgs = spoilers.correct_cards(
            mtgs, manual_cards, card_corrections, delete_cards['delete'])  # fix using the fixfiles
        mtgjson = spoilers.get_image_urls(
            mtgs, presets['isfullspoil'], setinfo['code'], setinfo['name'], setinfo['size'], setinfo)  # get images
        if presets['scryfallOnly'] or 'scryfallOnly' in setinfo and setinfo['scryfallOnly']:
            scryfall = scryfall_scraper.get_scryfall(
                'https://api.scryfall.com/cards/search?q=++e:' + setinfo['code'].lower())
            mtgjson = scryfall #_scraper.smash_mtgs_scryfall(mtgs, scryfall)
        if 'fullSpoil' in setinfo and setinfo['fullSpoil']:
            wotc = wizards_scraper.scrape_fullspoil('', setinfo)
            wizards_scraper.smash_fullspoil(mtgjson, wotc)
        [mtgjson, errors] = spoilers.error_check(
            mtgjson, card_corrections)  # check for errors where possible
        errorlog += errors
        spoilers.write_xml(
            mtgjson, setinfo['code'], setinfo['name'], setinfo['releaseDate'])
        #save_xml(spoilers.pretty_xml(setinfo['code']), 'out/spoiler.xml')
        mtgjson = spoilers.add_headers(mtgjson, setinfo)
        AllSets = spoilers.make_allsets(AllSets, mtgjson, setinfo['code'])
        if 'masterpieces' in setinfo:  # repeat all of the above for masterpieces
            # masterpieces aren't in the rss feed, so for the new cards, we'll go to their individual pages on mtgs
            # old cards will get their infos copied from mtgjson (including fields that may not apply like 'artist')
            # the images will still come from mtgs
            masterpieces = spoilers.make_masterpieces(
                setinfo['masterpieces'], AllSets, mtgjson)
            [masterpieces, errors] = spoilers.error_check(masterpieces)
            errorlog += errors
            spoilers.write_xml(masterpieces, setinfo['masterpieces']['code'],
                               setinfo['masterpieces']['name'], setinfo['masterpieces']['releaseDate'])
            AllSets = spoilers.make_allsets(
                AllSets, masterpieces, setinfo['masterpieces']['code'])
            save_masterpieces(masterpieces, setinfo)
            save_xml(spoilers.pretty_xml('out/' + setinfo['masterpieces']['code'] + '.xml'), 'out/' + setinfo['masterpieces']['code'] + '.xml')
            combinedjson[setinfo['masterpieces']['code']] = masterpieces
        save_setjson(mtgjson, setinfo['code'])
        save_xml(spoilers.pretty_xml('out/' + setinfo['code'] + '.xml'), 'out/' + setinfo['code'] + '.xml')
        combinedjson[setinfo['code']] = mtgjson
    save_setjson(combinedjson, 'spoiler')
    spoilers.write_combined_xml(combinedjson, setinfos)
    save_xml(spoilers.pretty_xml('out/spoiler.xml'), 'out/spoiler.xml')
    cockatrice_xsd = requests.get('https://raw.githubusercontent.com/Cockatrice/Cockatrice/master/doc/cards.xsd').text
    if verify_xml('out/spoiler.xml', cockatrice_xsd):  # check if our XML passes Cockatrice's XSD
        print 'spoiler.xml passes Cockatrice XSD verification'
    else:
        print 'spoiler.xml fails Cockatrice XSD verification'
    errorlog = spoilers.remove_corrected_errors(errorlog, card_corrections)
    save_errorlog(errorlog)
    save_allsets(AllSets)
    # save_setjson(mtgjson)
    if presets['dumpXML']:
        print '<!----- DUMPING SPOILER.XML -----!>'
        with open('out/spoiler.xml', 'r') as xmlfile:
            print xmlfile.read()
        print '<!-----    END XML DUMP     -----!>'
    if presets['dumpErrors']:
        if errorlog != {}:
            print '//----- DUMPING ERROR LOG -----'
            print json.dumps(errorlog, ensure_ascii=False, encoding='utf8', indent=2, sort_keys=True, separators=(',', ':'))
            print '//-----   END ERROR LOG   -----'
        else:
            print "No Detected Errors!"
