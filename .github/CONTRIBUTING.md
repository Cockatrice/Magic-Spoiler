# Contributing to Magic-Spoiler #
Thank you for your interest in contributing to Magic-Spoiler!<br>
This project is an attempt to create a central source for new Magic: the Gathering spoilers and provide data files for miscellaneous projects like [Cockatrice](https://github.com/Cockatrice/Cockatrice).


## How can I help? ##
Magic-Spoiler grabs its data from [Scryfall](https://scryfall.com/), but there can be errors of course.
If you want to improve the card data and fix errors for all users, you simply have to report them directly to Scryfall.
Once you've found a mistake in our data files, make sure that error hasn't already been fixed at the Scryfall webpage in betweeen. If it's still present there, let's get it fixed!
- If the error is with one of the fields in a card (e.g. a spelling error or missing cmc) search for that card on the Scryfall webpage. Below the card art on the left, there are some links. Choose the botton one (`Report card issue`) and provide the information in the form. Once their team check & fixes the errors, it'll show up in our spoiler files, too.<br>
It only takes a few days - be patient.
- If the card is a legitimate spoiler and it isn't showing up yet, you can request it by [contacting the Scryfall support](https://scryfall.com/contact) and let them know. Make sure to link the official spoiler source in your report.
- If the card shouldn't exist at all, let the Scryfall team know as well, please.

What you should **NOT** do however, is to submit PR's to our files branch and fix the xml files there directly.<br>
You have to provide updates to Scryfall as all other changes would get overridden again.


## Code Style Guidelines ##


#### Naming ####

Use `UpperCamelCase` for classes, structs, enums, etc. and `lowerCamelCase` for
function and variable names.

Don't use [Hungarian Notation](
https://en.wikipedia.org/wiki/Hungarian_notation).

Member variables aren't decorated in any way. Don't prefix or suffix them with
underscores, etc.

Use a separate line for each declaration, don't use a single line like this
`int one = 1, two = 2` and instead split them into two lines.


#### Braces ####


#### Indentation and Spacing ####

Always indent using 4 spaces, do not use tabs. Opening and closing braces
should be on the same indentation layer, member access specifiers in classes or
structs should not be indented.

All operators and braces should be separated by spaces, do not add a space next
to the inside of a brace.

If multiple lines of code that follow eachother have single line comments
behind them, place all of them on the same indentation level. This indentation
level should be equal to the longest line of code for each of these comments,
without added spacing.

#### Lines ####

Do not leave trailing whitespace on any line. Most IDEs check for this
nowadays and clean it up for you.

Lines should be 120 characters or less. Please break up lines that are too long
into smaller parts, for example at spaces or after opening a brace.


## Anything else? ##
If you notice any other errors or have suggestions to the code, please [file an issue](https://github.com/Cockatrice/Magic-Spoiler/issues) in our repository.

<br>

**Code improvement PRs are always welcome!**
