import yaml
import sys

def load_file(input_file, lib_to_use):
    try:
        with open(input_file) as data_file:
            if lib_to_use == 'yaml':
                output_file = yaml.safe_load(data_file)
            elif lib_to_use == 'yaml_multi':
                output_file = []
                for doc in yaml.safe_load_all(data_file):
                    output_file.append(doc)
            return output_file
    except Exception as ex:
        print "Unable to load file: " + input_file + "\nException information:\n" + str(ex.args)
        sys.exit("Unable to load file: " + input_file)

if __name__ == '__main__':
    setinfos = load_file('set_info.yml','yaml_multi')
    manual_sets = load_file('cards_manual.yml','yaml')
    card_corrections = load_file('cards_corrections.yml','yaml')
    delete_cards = load_file('cards_delete.yml','yaml')

    print "Pre-flight: All input files loaded successfully."