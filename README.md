# Magic-Spoiler [![Gitter Chat](https://img.shields.io/gitter/room/Cockatrice/Magic-Spoiler.svg)](https://gitter.im/Cockatrice/Magic-Spoiler) #

Magic-Spoiler is a python script to scrape MTG Salvation, Scryfall, MythicSpoiler and Wizards.com to compile a cockatrice-friendly XML file and application ready, mtgjson formatted json files.

## Output [![Build Status](https://travis-ci.org/Cockatrice/Magic-Spoiler.svg?branch=master)](https://travis-ci.org/Cockatrice/Magic-Spoiler) ##
Just looking for XML or JSON files?  [They're in our files branch!](https://github.com/Cockatrice/Magic-Spoiler/tree/files)

## Errors ##
Noticed an error?  Check out our [Contributing file](https://github.com/Cockatrice/Magic-Spoiler/blob/master/.github/CONTRIBUTING.md) for information on how to help!

## Running ##

### Requirements ###
 * Python 2.7
 * Python Modules:
    requests==2.13.0
    feedparser
    lxml
    Pillow
    datetime

```
pip install -r requirements.txt
```

### Usage ###
 
```
$> python main.py
```

Outputs out/{SETCODE}.xml, out/MPS\_{SETCODE}.xml, out/{SETCODE}.json, out/{MPS\_{SETCODE}.json

errors are logged to out/errors.json

Add the set xml file to your `customsets` folder for Cockatrice.

When run by travis, uploads all files to [files branch](https://github.com/Cockatrice/Magic-Spoiler/tree/files)
