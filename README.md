# SpoilerSeason #

SpoilerSeason is a python script to scrape MTGS, Scryfall, and Wizards.com to compile a cockatrice-friendly XML file as well as json files.

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
