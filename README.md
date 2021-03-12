# Plextrakt-Season-Integration
Script to pull season data such as titles and summaries from Trakt into Plex. The goal was to be extremely flexible, so there are numerous flags available when calling the script. This should give granularity so that users can get the script to behave how they want. 

Python3+ only (developed with Python 3.8)

**Requires plexapi 4.4.1 or higher and requests. Run `python -m pip install --upgrade plexapi requests` with python replaced with whatever your python3 binary is to make sure you have the latest one.**

The script has to make two calls to Trakt per show, so the number of requests can add up. Please be respectful of their API servers, and configure the script to not constantly rescrape your entire Plex library continously.

Note that the data is only as good as what is available in Trakt. If Trakt has poor summaries, those will get added still.

Now supports libraries using the TMDB agent as well, but I cannot vouch for the data as it is entirely feasible that the seasons TMDB and Trakt are using vary widely.

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

**`--help|-h`**: Show a help message for general parameters and commands and exit

**`--debug`**: Prints debug info to the log file. Default is false

### Command
One of `reset` or `pull` is required. 
* **`reset`**: reset the specified season data in Plex. 
* **`pull`**: pull the specified season data from Trakt into Plex.

### Command Specific Parameters

**`--help|-h`**: Show a help message for command-specific parameters and exit

One of the below two parameters is required to determine which data to process. Both can work together, e.g. if you want your entire anime library but only "American Horror Story" from your TV Show library.

* **`--libraries`**: A list of libraries to process. Do not use if you want to select specific shows instead. Please note that you need to use the exact name of the library as it appears in Plex, place it in quotes, and separate multiple libraries with a space after using this flag.\
Example: `--libraries "TV Shows" "Anime"`
* **`--shows`**: A list of specific shows to process. Do not use if you want to select entire libraries instead. Please note that you need to use the exact name of the show as it appears in Plex, place it in quotes, and separate multiple libraries with a comma.\
Example: `--shows "Avatar: The Last Airbender" "The Legend of Korra"`

**`--data|-d`**: Specify whether to proccess `title` or `summary` data. Default is both.\
Example: `--data title`

**`--exclude|-e`**: Specify a label (in lowercase) that you want to exclude. Shows with this label will not be processed.\
Example: `--exclude overriden`

**`--unlock|-u`**: 
* (*reset*) Specify whether to unlock `title` or `summary` data after resetting so it can be rescraped in subsequent pulls. Default is none so that all processed items are locked after the reset. To unlock both, add both values after the flag.\
Example: `--unlock title summary`
* (*pull*) Specify whether to unlock `successful_title`, `failed_title`, `successful_summary`, or `failed_summary` after the pull so that those items can be rescraped in subsequent pulls. Default is none so that all processed items are locked after the pull. To unlock multiple items, add those values after the flag.\
Example: `--unlock failed_title failed_summary`

**`--force|-f`**: (*pull only*) Set this flag to force rescrape all existing locked season title/summary data in Plex. Default is False so that the script ignores and filters out these items.

### Full Example
`python trakt_seasons.py --debug pull --libraries "TV Shows" --shows "Dragon Ball Z" -f -d summary -u failed_summary`

You can also run this on two separate schedules. One will scrape only new items, and another will force scrape all items, excluding labels you can use to signal that certain things have been overriden manually

`python trakt_seasons.py --debug pull --libraries "TV Shows" "Anime"` running weekly
`python trakt_seasons.py --debug pull --force --exclude plextrakt --libraries "TV Shows" "Anime"` running every month or two
