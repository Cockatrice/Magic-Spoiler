# Contributing to SpoilerSeason #
Thank you for your interest in contributing to SpoilerSeason!
This project is an attempt to create a central source for new Magic: the Gathering spoilers and provide data files for miscellaneous projects including our friends over at [Cockatrice](https://github.com/Cockatrice/Cockatrice)

## How can I help? ##
SpoilerSeason grabs its data from many sources, but those sources often contain errors.  If you just want to improve the card data and fix errors, you can start in the [errors.json](https://github.com/Cockatrice/Magic-Spoiler/blob/files/errors.json) file in the [files branch](https://github.com/Cockatrice/Magic-Spoiler/tree/files) or our [issue tracker.](https://github.com/Cockatrice/Magic-Spoiler/issues)
Once you've found an error, whether it be in the errors.json file or from using the data files, make sure that error hasn't already been fixed in the appropriate file on the [files branch.](https://github.com/Cockatrice/Magic-Spoiler/tree/files) If it's still present, let's get it fixed! 
- If the error is with one of the fields in a card, check our [cards_corrections.json](https://github.com/Cockatrice/Magic-Spoiler/blob/master/cards_corrections.json) file. The syntax for this file is `"cardname": { "field to correct": "new value" }` If you're fixing the card name, you'd put the bad card name as `cardname`
- If the card shouldn't exist at all, check the [cards_delete.json](https://github.com/Cockatrice/Magic-Spoiler/blob/master/cards_delete.json) file. This file is just an array of cards to delete. Card name is case sensitive!
- If the card is a legitimate spoiler and it isn't showing up yet, you can manually add it. The file you want is [cards_manual.json](https://github.com/Cockatrice/Magic-Spoiler/blob/master/cards_manual.json) Make sure you link the spoil source in your Push Request.

All Push requests for card fixes should have the name of the card being fixed and the type of fix (fix/correction, delete, or manual). In the details of the PR, you **MUST INCLUDE A VALID LINK** to the page the spoiler is located at. For minor fixes, a link to the card image is OK. And of course link the issue you're fixing if there is one!

## Anything else? ##
If you notice errors, please file an [issue](https://github.com/Cockatrice/Magic-Spoiler/issues)

Code improvement PRs are always welcome!
