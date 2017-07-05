import commentjson
import yaml
import sys

try:
    with open('set_info') as data_file:
        setinfos = commentjson.load(data_file)
except Exception as ex:
    print "Unable to load file: set_info\nException information:\n" + str(ex.args)
    sys.exit("Unable to load file: set_info")
try:
    with open('cards_manual.yml') as data_file:
        manual_sets = yaml.load(data_file)
except Exception as ex:
    print "Unable to load file: cards_manual.yml\nException information:\n" + str(ex.args)
    sys.exit("Unable to load file: cards_manual.yml")
try:
    with open('cards_corrections.yml') as data_file:
        card_corrections = yaml.load(data_file)
except Exception as ex:
    print "Unable to load file: cards_corrections.yml\nException information:\n" + str(ex.args)
    sys.exit("Unable to load file: cards_corrections.yml")
try:
    with open('cards_delete.yml') as data_file:
        delete_cards = yaml.load(data_file)
except Exception as ex:
    print "Unable to load file: cards_delete.yml\nException information:\n" + str(ex.args)
    sys.exit("Unable to load file: cards_delete.yml")

print "Pre-flight: All input files loaded successfully."