# Magic-Spoiler [![Gitter Chat](https://img.shields.io/gitter/room/Cockatrice/Magic-Spoiler.svg)](https://gitter.im/Cockatrice/Magic-Spoiler) #

Magic-Spoiler is a Python script to scrape <i>MTG Salvation</i>, <i>Scryfall</i>, <i>MythicSpoiler</i> and <i>Wizards</i> to compile<br>
XML files (Cockatrice formatted) and application-ready json files (mtgjson formatted) with information about spoiled cards from upcoming sets.

## Output [![Build Status](https://travis-ci.org/Cockatrice/Magic-Spoiler.svg?branch=master)](https://travis-ci.org/Cockatrice/Magic-Spoiler) ##
Just looking for XML or JSON files?  They are in our [`files` branch](https://github.com/Cockatrice/Magic-Spoiler/tree/files)! (A history of changes can be found [here](https://github.com/Cockatrice/Magic-Spoiler/commits/files))

When run by Travis, the script automatically updates the files and uploads new versions there.<br>
Travis CI is run daily on a cron job basis.

## Errors ##
Noticed an error?  Check out our [Contributing file](https://github.com/Cockatrice/Magic-Spoiler/blob/master/.github/CONTRIBUTING.md) for information on how to help!

## Running ##

### Requirements ###
 * Python 2.7
 * several Python Modules (see [requirements.txt](https://github.com/Cockatrice/Magic-Spoiler/blob/master/requirements.txt))

```
pip install -r requirements.txt
```

### Usage ###
 
```
$> python main.py
```

Outputs the following files to `out/` directory:<br>
`spoiler.xml`, `{SETCODE}.xml`, `MPS_{SETCODE}.xml`,<br>
`spoiler.json`, `{SETCODE}.json`, `MPS_{SETCODE}.json`

Errors are logged there as well (`errors.json`)

<br>

Add the desired <b>.xml</b> file to your <i>customsets</i> folder to make Cockatrice use it.
