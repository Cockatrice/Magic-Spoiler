import commentjson
import sys

try:
    with open('set_info') as data_file:
        setinfos = commentjson.load(data_file)
except Exception as ex:
    print "Unable to load file: set_info\nException information:\n" + str(ex.args)
    sys.exit("Unable to load file: set_info")
try:
    with open('cards_manual') as data_file:
        manual_sets = commentjson.load(data_file)
except Exception as ex:
    print "Unable to load file: cards_manual\nException information:\n" + str(ex.args)
    sys.exit("Unable to load file: cards_manual")
try:
    with open('cards_corrections') as data_file:
        card_corrections = commentjson.load(data_file)
except Exception as ex:
    print "Unable to load file: cards_corrections\nException information:\n" + str(ex.args)
    sys.exit("Unable to load file: cards_corrections")
try:
    with open('cards_delete') as data_file:
        delete_cards = commentjson.load(data_file)
except Exception as ex:
    print "Unable to load file: cards_delete\nException information:\n" + str(ex.args)
    sys.exit("Unable to load file: cards_delete")

print "Pre-flight: All input files loaded successfully."