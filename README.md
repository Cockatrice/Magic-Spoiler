![](https://img.shields.io/badge/dynamic/xml?url=https%3A%2F%2Fraw.githubusercontent.com%2FCockatrice%2FMagic-Spoiler%2Ffiles%2Fspoiler.xml&query=%2F%2Finfo%2FcreatedAt&label=Last%20update)

[![](https://img.shields.io/badge/dynamic/xml.svg?label=Included%20sets&colorB=lightgrey&url=https%3A%2F%2Fraw.githubusercontent.com%2FCockatrice%2FMagic-Spoiler%2Ffiles%2Fspoiler.xml&query=count(%2F%2Flongname))](https://github.com/Cockatrice/Magic-Spoiler/tree/files) [![](https://img.shields.io/badge/dynamic/xml.svg?label=&colorB=lightgrey&url=https%3A%2F%2Fraw.githubusercontent.com%2FCockatrice%2FMagic-Spoiler%2Ffiles%2Fspoiler.xml&query=%2F%2Flongname)](https://github.com/Cockatrice/Magic-Spoiler/blob/files/spoiler.xml)<br>
[![](https://img.shields.io/badge/dynamic/xml.svg?label=Release%20dates&colorB=lightgrey&url=https%3A%2F%2Fraw.githubusercontent.com%2FCockatrice%2FMagic-Spoiler%2Ffiles%2Fspoiler.xml&query=%2F%2Freleasedate)](https://github.com/Cockatrice/Magic-Spoiler/blob/files/spoiler.xml)<br>
[![](https://img.shields.io/badge/dynamic/xml.svg?label=Included%20cards&colorB=lightgrey&url=https%3A%2F%2Fraw.githubusercontent.com%2FCockatrice%2FMagic-Spoiler%2Ffiles%2Fspoiler.xml&query=count(%2F%2Fcard))](https://github.com/Cockatrice/Magic-Spoiler/blob/files/spoiler.xml)

<br>

# Magic-Spoiler [![Discord](https://img.shields.io/discord/314987288398659595?label=Discord&logo=discord&logoColor=white)](https://discord.gg/3Z9yzmA) #

Magic-Spoiler is a Python script to query the [Scryfall](https://scryfall.com) API to compile XML files (Cockatrice formatted) with information about spoiled cards from upcoming sets.

## Output [![Build Status](https://github.com/Cockatrice/Magic-Spoiler/actions/workflows/deploy.yml/badge.svg?branch=master)](https://github.com/Cockatrice/Magic-Spoiler/actions/workflows/deploy.yml?query=branch%3Amaster) ##

>[!TIP]
>**Enable "Download Spoilers Automatically" in `Cockatrice → Settings → Card Sources → Spoilers` to get updates automatically pushed to your client!**<br>
You can also [add the desired <b>.xml</b> file(s) to your <i>customsets</i> folder manually](https://github.com/Cockatrice/Cockatrice/wiki/Custom-Cards-&-Sets#to-add-custom-sets-follow-these-steps) to make Cockatrice use them.

Just looking for XML files?  [They are in our `files` branch!](https://github.com/Cockatrice/Magic-Spoiler/tree/files) 

When run by our CI, the script automatically updates the files and uploads new versions to this branch. ([History of changes](https://github.com/Cockatrice/Magic-Spoiler/commits/files))<br>
GitHub Actions are scheduled to autoamtically run on a daily basis.

## Contributing ##
Noticed an error in the card data? Check out our [Contributing file](https://github.com/Cockatrice/Magic-Spoiler/blob/master/.github/CONTRIBUTING.md) for information on how to help fixing it!

We do happily accept PR's that improve our script as well!

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

### Output ###

All spoiler files are written to the `out/` directory:

| File Name | Content |
|:--|:--|
| `spoiler.xml` | file contains **all** currently available spoilers from different **sets** |
| `{SET_CODE}.xml` | files contain just the spoiler available for this **single set** |
