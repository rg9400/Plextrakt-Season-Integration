# Plextrakt-Season-Integration
Script to pull season data such as titles and summaries from Trakt into Plex. The goal was to be extremely flexible, so the configuration is a bit more involved. However, it should give granularity so that users can get the script to behave how they want.

The script has to make two calls to Trakt per show, so the number of requests can add up. Please be respectful of their API servers, and configure the script to not constantly rescrape your entire Plex library continously.

Note that the data is only as good as what is available in Trakt. If Trakt has poor summaries, those will get added still.

See examples of this data in Plex below:

 ### Screenshots
<details><summary>Expand</summary>
<p>
<img src="/screenshots/season%titles.png"></img>
<img src="/screenshots/season%summary.png"></img>
</p>
</details>

## General

**PLEX_URL** - Set this to the local URL for your Plex Server

**PLEX_TOKEN** - Find your token by following the instructions here https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

**TRAKT_CLIENT_ID** - You can create a Trakt account, then click *Your API Apps* under Settings, create a new app, give it a name. You can leave image, javascript, and the check-in/scrobble permissions blank, but you need to select a redirect uri. You can use the device authentication option listed in the help text or set something like google.com

**DEBUG** - Set to True for the log file to contain detailed logs rather than what is seen on console

## Reset

**RESET** - Set to True to reset all custom titles/summaries in the specified libraries. Please note that resets will happen before any Trakt pull if enabled.

**RESET_LIBRARIES** - A list of libraries to reset. Leave empty if you want to select specific shows instead. Will only work if Reset is enabled. Please note that you need to use the exact name of the library as it appears in Plex, place it in quotes, and separate multiple libraries with a comma. Follow the format given by the default option.

**RESET_SHOWS** - A list of specific shows to reset. Leave empty if you want to select entire libraries instead. Will only work if Reset is enabled. Please note that you need to use the exact name of the show as it appears in Plex, place it in quotes, and separate multiple libraries with a comma. Follow the format given by the default option. Can work in addition to the list of libraries, e.g. if you want your entire anime library but only "American Horror Story" from your TV Show library.

**RESET_TITLES** - Set to True if you want to reset the season's titles

**RESET_SUMMARIES** - Set to True if you want to reset the season's summaries

**LOCK_TITLE_ON_RESET** - Set to True if you want to lock the title after resetting it. This can prevent it from being changed by future runs of the script.

**LOCK_SUMMARY_ON_RESET** - Set to True if you want to lock the summary after resetting it. This can prevent it from being changed by future runs of the script.

## Trakt Data Pull

**TRAKT_PULL** - Set to True to pull season data from Trakt

**TV_SHOW_LIBRARIES** - A list of libraries for which to pull data. Leave empty if you want to select specific shows instead. Will only work if Trakt Pull is enabled. Please note that you need to use the exact name of the library as it appears in Plex, place it in quotes, and separate multiple libraries with a comma. Follow the format given by the default option.

**TV_SHOW_NAMES** - A list of specific shows for which to pull data. Leave empty if you want to select entire libraries instead. Will only work if Trakt Pull is enabled. Please note that you need to use the exact name of the show as it appears in Plex, place it in quotes, and separate multiple libraries with a comma. Follow the format given by the default option. Can work in addition to the list of libraries, e.g. if you want your entire anime library but only "American Horror Story" from your TV Show library.

**FORCE_REFRESH** - Set to True to grab data for already locked season titles/shows, otherwise, it will ignore and filter those out.

**PULL_SEASON_TITLES** - Set to True to turn on grabbing season titles from Trakt

**PULL_SEASON_SUMMARIES** - Set to True to turn on grabbing season summaries from Trakt

**LOCK_TITLE_ON_SUCCESSFUL_PULL** - Set to True to lock season titles found on Trakt so they won't get rescraped in subsequent pulls

**LOCK_TITLE_ON_FAILED_PULL** - Set to True to lock season titles *NOT* found on Trakt so they won't get rescraped in subsequent pulls

**LOCK_SUMMARY_ON_SUCCESSFUL_PULL** - Set to True to lock season summaries found on Trakt so they won't get rescraped in subsequent pulls

**LOCK_SUMMARY_ON_FAILED_PULL** - Set to True to lock summaries *NOT* found on Trakt so they won't get rescraped in subsequent pulls


