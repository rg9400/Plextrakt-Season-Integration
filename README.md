# Plextrakt-Season-Integration
Script to pull season data such as titles and summaries from Trakt into Plex. The goal was to be extremely flexible, so there are numerous flags available when calling the script. This should give granularity so that users can get the script to behave how they want. 

Python3+ only (developed with Python 3.8)

**Requires latest plexapi and requests. Run `python -m pip install --upgrade git+https://github.com/pkkid/python-plexapi requests` with python replaced with whatever your python3 binary is to make sure you have the latest one.**

The script has to make two calls to Trakt per show, so the number of requests can add up. Please be respectful of their API servers, and configure the script to not constantly rescrape your entire Plex library continously.

Note that the data is only as good as what is available in Trakt. If Trakt has poor summaries, those will get added still.

See examples of this data in Plex below:

 ### Screenshots
<details><summary>Expand</summary>
<p>
<img src="/screenshots/season%20titles.png?raw=true"></img>
<img src="/screenshots/season%20summary.png?raw=true"></img>
</p>
</details>

## File Config

**PLEX_URL** - Set this to the local URL for your Plex Server

**PLEX_TOKEN** - Find your token by following the instructions here https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

**TRAKT_CLIENT_ID** - You can create a Trakt account, then click *Your API Apps* under Settings, create a new app, give it a name. You can leave image, javascript, and the check-in/scrobble permissions blank, but you need to select a redirect uri. You can use the device authentication option listed in the help text or set something like google.com

## Command Line Interface

The script is constructed by calling `python trakt_seasons.py [general parameters] reset|pull [command-specific parameters]`

### General Parameters

**`--debug`**: Prints debug info to the log file

### Command
One of `reset` or `pull` is required. `reset` will reset the specified season data in Plex. `pull` will pull the specified season data from Trakt into Plex.

### Command Specific Parameters
One of the below two parameters is required to determine which data to process.

**`--libraries`**: A list of libraries to process. Do not use if you want to select specific shows instead. Please note that you need to use the exact name of the library as it appears in Plex, place it in quotes, and separate multiple libraries with a space after using this flag.\
Example: `--libraries "TV Shows" "Anime`

**`--shows`**: A list of specific shows to process. Do not use if you want to select entire libraries instead. Please note that you need to use the exact name of the show as it appears in Plex, place it in quotes, and separate multiple libraries with a comma. Can work in addition to the list of libraries, e.g. if you want your entire anime library but only "American Horror Story" from your TV Show library.\
Example: `--shows "Avatar: The Last Airbender" "The Legend of Korra"`

**`--data|-d`**: Specify whether to pull `title` or `summary` data. Default is both.
Example: `--data title`

**`--unlock|-u`**: 
* (*reset*) Specify whether to unlock `title` or `summary` data after resetting so it can be rescraped in subsequent pulls. Default is none so that all processed items are locked after the reset. To unlock both, add both values after the flag.
Example: `--unlock title summary`
* (*pull*) Specify whether to unlock `successful_title`, `failed_title`, `successful_summary`, or `failed_summary` after the pull so that those items can be rescraped in subsequent pulls. Default is none so that all processed items are locked after the pull. To unlock multiple items, add those values after the flag.
Example: `--unlock failed_title failed_summary`

**`--force|-f`**: (*pull only*) Set this flag to force rescrape all existing locked season title/summary data in Plex. Default is False so that the script ignores and filters out these items.

### Full Example
`python trakt_seasons.py --debug pull --libraries "TV Shows" --anime "Dragon Ball Z" -f -d titles -u failed_summary`