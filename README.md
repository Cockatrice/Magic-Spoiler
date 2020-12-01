[![](https://img.shields.io/badge/dynamic/xml.svg?label=Currently%20included%20sets&colorB=lightgrey&url=https%3A%2F%2Fraw.githubusercontent.com%2FCockatrice%2FMagic-Spoiler%2Ffiles%2Fspoiler.xml&query=%2F%2Flongname)](https://github.com/Cockatrice/Magic-Spoiler/blob/files/spoiler.xml)
[![](https://img.shields.io/badge/dynamic/xml.svg?label=Release%20dates&colorB=lightgrey&url=https%3A%2F%2Fraw.githubusercontent.com%2FCockatrice%2FMagic-Spoiler%2Ffiles%2Fspoiler.xml&query=%2F%2Freleasedate)](https://github.com/Cockatrice/Magic-Spoiler/blob/files/spoiler.xml)
[![](https://img.shields.io/badge/dynamic/xml.svg?label=Included%20cards&colorB=lightgrey&url=https%3A%2F%2Fraw.githubusercontent.com%2FCockatrice%2FMagic-Spoiler%2Ffiles%2Fspoiler.xml&query=count(%2F%2Fcard))](https://github.com/Cockatrice/Magic-Spoiler/blob/files/spoiler.xml)

<br>

# Magic-Spoiler [![Discord](https://img.shields.io/discord/314987288398659595?label=Discord&logo=discord&logoColor=white)](https://discord.gg/3Z9yzmA) [![Gitter Chat](https://img.shields.io/gitter/room/Cockatrice/Magic-Spoiler)](https://gitter.im/Cockatrice/Magic-Spoiler) #

Magic-Spoiler is a Python script to scrape <i>[Scryfall](https://scryfall.com)</i> to compile XML files (Cockatrice formatted) and application-ready json files (mtgjson formatted) with information about spoiled cards from upcoming sets.

## Output [![Build Status](https://github.com/Cockatrice/Magic-Spoiler/workflows/Deploy/badge.svg?branch=master&event=schedule)](https://github.com/Cockatrice/Magic-Spoiler/actions?query=workflow%3ADeploy+event%3Aschedule) ##
Just looking for XML or JSON files?  [They are in our `files` branch!](https://github.com/Cockatrice/Magic-Spoiler/tree/files) 

When run by Travis, the script automatically updates the files and uploads new versions there. ([History of changes](https://github.com/Cockatrice/Magic-Spoiler/commits/files))<br>
Travis CI is run daily on a cron job basis.

## Errors ##
Noticed an error in the card data?  Check out our [Contributing file](https://github.com/Cockatrice/Magic-Spoiler/blob/master/.github/CONTRIBUTING.md) for information on how to help!

## Running ##

### Requirements ###
 * Python 3.6
 * several Python Modules (see [requirements.txt](https://github.com/Cockatrice/Magic-Spoiler/blob/master/requirements.txt))

```
pip install -r requirements.txt
```

### Usage ###
 
```
$> python -m magic_spoiler
```

Outputs the following files to `out/` directory:<br>
`spoiler.xml`, `spoiler.json`<br>
`{SET_CODE}.xml`, `{SET_CODE}.json`
> **spoiler** → files contain all currently available spoilers from different sets<br>
> **{SETCODE}** → files contain just the spoiler available for this single set<br>

<br>

**Enable "Download Spoilers Automatically" in `Cockatrice → Settings → Card Sources → Spoilers` to get updates automatically pushed to your client!**<br>
You can also [add the desired <b>.xml</b> file(s) to your <i>customsets</i> folder manually](https://github.com/Cockatrice/Cockatrice/wiki/Custom-Cards-&-Sets#to-add-custom-sets-follow-these-steps) to make Cockatrice use it.
