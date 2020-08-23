#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Description: Rename season title for TV shows on Plex and populate season data such as titles and summaries.
# Make sure plexapi is up to date as this script utilizes features available in the latest version only
# Based on the script by SwiftPanda https://github.com/blacktwin/JBOPS/blob/master/utility/rename_seasons.py
# Author:       /u/RG9400
# Requires:     plexapi, requests

import re
import os
import sys
import time
import requests
from logging.handlers import RotatingFileHandler 
from logging import DEBUG, INFO, getLogger, Formatter, StreamHandler
from plexapi.server import PlexServer

################################ CONFIG BELOW ################################
PLEX_URL = "http://localhost:32400"
PLEX_TOKEN = ""
TRAKT_CLIENT_ID = ""
DEBUG = False #Set to True for the log file to contain detailed logs rather than what is seen on console

#Config for resetting Plex data. Note resets happen before the Trakt Pull
RESET = False #Set to True to reset all custom titles/summaries in the specified libraries.
RESET_LIBRARIES = ["Anime", "TV Shows"] #List of libraries to reset if enabled above. Leave empty to not reset data for an entire library.
RESET_SHOWS = ["Dragon Ball Z", "The Legend of Korra"] #List of shows to reset if enabled above. Leave empty to not reset data for specific shows
RESET_TITLES = True #Set to True if you want to reset the season's titles
RESET_SUMMARIES = True #Set to True if you want to reset the season's summaries
LOCK_TITLE_ON_RESET = True #Set to True if you want to lock the title after resetting it. This can prevent it from being changed by future runs of the script.
LOCK_SUMMARY_ON_RESET = True #Set to True if you want to lock the summary after resetting it. This can prevent it from being changed by future runs of the script.

#Config for pulling data from Trakt
TRAKT_PULL = True #Set to True to grab data from Trakt
TV_SHOW_LIBRARIES = ["TV Shows", "Anime"] #List of libraries for which to grab data if enabled above. Leave empty to not grab data for an entire library.
TV_SHOW_NAMES = ["Avatar: The Last Airbender", "American Horror Story"] #List of shows for which to grab data if enabled above. Leave empty to not grab data for specific shows.
FORCE_REFRESH = False #Set to True to grab data for already locked season titles/shows, otherwise, it will ignore and filter those out.
PULL_SEASON_TITLES = True #Set to True to turn on grabbing season titles from Trakt
PULL_SEASON_SUMMARIES = True #Set to True to turn on grabbing season summaries from Trakt
LOCK_TITLE_ON_SUCCESSFUL_PULL = True #Set to True to lock season titles found on Trakt so they won't get rescraped in subsequent pulls
LOCK_TITLE_ON_FAILED_PULL = True #Set to True to lock season titles *NOT* found on Trakt so they won't get rescraped in subsequent pulls
LOCK_SUMMARY_ON_SUCCESSFUL_PULL = True #Set to True to lock season summaries found on Trakt so they won't get rescraped in subsequent pulls
LOCK_SUMMARY_ON_FAILED_PULL = True #Set to True to lock summaries *NOT* found on Trakt so they won't get rescraped in subsequent pulls
###############################################################################

## CODE BELOW ##
# Set up the rotating log files
size = 10*1024*1024  # 5MB
max_files = 5  # Keep up to 7 logs
os.makedirs(os.path.join(os.path.dirname(sys.argv[0]), 'logs'), exist_ok=True)
log_filename = os.path.join(os.path.dirname(sys.argv[0]), 'logs/rename_seasons.log')
file_logger = RotatingFileHandler(log_filename, maxBytes=size, backupCount=max_files)
console = StreamHandler()
logger_formatter = Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s')
console_formatter = Formatter('%(message)s')
console.setFormatter(console_formatter)
file_logger.setFormatter(logger_formatter)
console.setLevel(INFO)
if DEBUG:
    file_logger.setLevel(DEBUG)
else:
    file_logger.setLevel(INFO)
log = getLogger('Rename Seasons')
log.addHandler(console)
log.addHandler(file_logger)
log.setLevel(DEBUG)

def main():
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    trakt_headers = {"content-type": "application/json", "trakt-api-version": "2", "trakt-api-key": TRAKT_CLIENT_ID, 'User-agent': 'Season Renamer v0.1'}

    if RESET:
        resetting = True
        while resetting:
            log.info('Reset enabled, collecting items to reset')
            if not RESET_SUMMARIES and not RESET_TITLES:
                log.error('Reset enabled, but both summary and title resets are disabled, exiting the reset')
                break
            reset_list = []
            if len(RESET_LIBRARIES) > 0:
                for library in RESET_LIBRARIES:
                    try:
                        reset_list.extend(plex.library.section(library).all())
                        log.info("Resetting all shows found in library {}".format(library))
                    except:
                        log.error("Could not find library {} in Plex".format(library))
            else:
                log.debug('No libraries identified to be reset')
            if len(RESET_SHOWS) > 0:
                for show in RESET_SHOWS:
                    try:
                        reset_list.append(plex.search(show)[0])
                        log.info("Resetting show {}".format(show))
                    except:
                        log.error("Could not find show {} in Plex".format(show))
            else:
                log.debug('No specific shows identified to be reset')

            deduped_reset_list = set(reset_list)
            reset_title_locking_indicator = int(LOCK_TITLE_ON_RESET)
            reset_summary_locking_indicator = int(LOCK_SUMMARY_ON_RESET)
            for show in deduped_reset_list:
                for season in show.seasons():
                    old_season_title = season.title
                    old_season_summary = season.summary
                    edit = {}
                    if RESET_TITLES:
                        edit['title.value'] = ''
                        edit['title.locked'] = reset_title_locking_indicator
                    if RESET_SUMMARIES:
                        edit['summary.value'] = ''
                        edit['summary.locked'] = reset_summary_locking_indicator
                    season.edit(**edit)
                    if RESET_TITLES:
                        log.debug("""
                        Show: {}
                        Season: {}
                        Old Title: {}
                        New Title: {}
                        Locked: {}
                        """
                        .format(show.title, season.seasonNumber, old_season_title, season.reload().title, LOCK_TITLE_ON_RESET))
                    if RESET_SUMMARIES:
                        log.debug("""
                        Show: {}
                        Season: {}
                        Old Summary: {}
                        New Summary: {}
                        Locked: {}
                        """
                        .format(show.title, season.seasonNumber, old_season_summary, season.reload().summary, LOCK_SUMMARY_ON_RESET))
            log.info("Resetting finished")
            resetting = False

    if TRAKT_PULL:
        pulling = True
        while pulling:
            log.info('Trakt data pull is enabled, collecting items to pull')
            if not PULL_SEASON_SUMMARIES and not PULL_SEASON_TITLES:
                log.error('Trakt pull enabled, but both summary and title pulls are disabled, exiting the pull')
                break
            show_list = []
            if len(TV_SHOW_LIBRARIES) > 0:
                for library in TV_SHOW_LIBRARIES:
                    try:
                        show_list.extend(plex.library.section(library).all())
                        log.info("Appending all shows found in library {} to the rename list".format(library))
                    except:
                        log.error("Could not find library {} in Plex".format(library))
            else:
                log.debug('No libraries identified to be pulled')
            if len(TV_SHOW_NAMES) > 0:
                for show in TV_SHOW_NAMES:
                    try:
                        show_list.append(plex.search(show)[0])
                        log.info("Appending show {} to the rename list".format(show))
                    except:
                        log.error("Could not find show {} in Plex".format(show))
            else:
                log.debug('No specific shows identified to be pulled')

            deduped_pull_list = set(show_list)
            pull_successful_title_locking_indicator = int(LOCK_TITLE_ON_SUCCESSFUL_PULL)
            pull_failed_title_locking_indicator = int(LOCK_TITLE_ON_FAILED_PULL)
            pull_succesful_summary_locking_indicator = int(LOCK_SUMMARY_ON_SUCCESSFUL_PULL)
            pull_failed_summary_locking_indicator = int(LOCK_SUMMARY_ON_FAILED_PULL)
            if FORCE_REFRESH:
                log.info("Force Refresh enabled. Rescraping all items in the list")
            else:
                log.info("Force refresh disabled. Will filter out locked items")
            for show in deduped_pull_list:
                if not FORCE_REFRESH:
                    if PULL_SEASON_TITLES:
                        all_titles_locked = all("title" in (field.name for field in season.fields) for season in show.seasons() if season.seasonNumber != 0)
                    else:
                        all_titles_locked = True
                    if PULL_SEASON_SUMMARIES:
                        all_summaries_locked = all("summary" in (field.name for field in season.fields) for season in show.seasons() if season.seasonNumber != 0)
                    else:
                        all_summaries_locked = True
                    if all_titles_locked and all_summaries_locked:
                        log.info('Skipping show {} because force refresh is disabled and all requested items are locked'.format(show.title))
                        continue
                try:
                    tvdb_id = int(re.search(r'thetvdb:\/\/(.*)\?', show.guid).group(1))
                except:
                    log.warning('Error parsing TVDB ID for show {}'.format(show.title))
                    tvdb_id = None
                    slug = None

                if tvdb_id:
                    trakt_search_api = 'https://api.trakt.tv/search/tvdb/{}?type=show'.format(tvdb_id)
                    trakt_search = requests.get(trakt_search_api, headers=trakt_headers).json()
                    try:
                        slug = trakt_search[0]['show']['ids']['slug']
                    except:
                        log.warning('Could not find Trakt slug for show {} and TVDB ID {}'.format(show.title, tvdb_id))
                        slug = None
                else:
                    log.warning('No TVDB ID found for show {}, skipping'.format(show.title))

                if slug:
                    trakt_season_api = 'https://api.trakt.tv/shows/{}/seasons?extended=full'.format(slug)
                    trakt_seasons = requests.get(trakt_season_api, headers=trakt_headers).json()
                    for season in trakt_seasons:
                        season_number = season['number']
                        if season_number != 0:
                            season_title = season['title']
                            if season_title == 'Season {}'.format(season_number):
                                season_title = None
                            season_summary = season['overview']
                            try:
                                plex_season = show.season(season_number)
                                if not FORCE_REFRESH:
                                    locked_title = "title" in (field.name for field in plex_season.fields)
                                    locked_summary = "summary" in (field.name for field in plex_season.fields)
                                else:
                                    locked_title = False
                                    locked_summary = False
                                old_season_title = plex_season.title
                                old_season_summary = plex_season.summary
                                edit = {}
                                if PULL_SEASON_TITLES and not locked_title:
                                    if season_title:
                                        edit['title.value'] = season_title
                                        edit['title.locked'] = pull_successful_title_locking_indicator
                                        log.info("""
                                        Show: {}
                                        Season: {}
                                        Old Title: {}
                                        New Title: {}
                                        Locked: {}
                                        """
                                        .format(show.title, plex_season.seasonNumber, old_season_title, season_title, LOCK_TITLE_ON_SUCCESSFUL_PULL))
                                    else:
                                        edit['title.value'] = old_season_title
                                        edit['title.locked'] = pull_failed_title_locking_indicator
                                        log.debug("{} Season {} - No title found on Trakt. Locked on Plex: {}". format(show.title, plex_season.seasonNumber, LOCK_TITLE_ON_FAILED_PULL))
                                if PULL_SEASON_SUMMARIES and not locked_summary:
                                    if season_summary:
                                        edit['summary.value'] = season_summary
                                        edit['summary.locked'] = pull_succesful_summary_locking_indicator
                                        log.info("""
                                        Show: {}
                                        Season: {}
                                        Old Summary: {}
                                        New Summary: {}
                                        Locked: {}
                                        """
                                        .format(show.title, plex_season.seasonNumber, old_season_summary, season_summary, LOCK_SUMMARY_ON_SUCCESSFUL_PULL))
                                    else:
                                        edit['summary.value'] = old_season_summary
                                        edit['summary.locked'] = pull_failed_summary_locking_indicator
                                        log.debug("{} Season {} - No summary found on Trakt. Locked on Plex: {}".format(show.title, plex_season.seasonNumber, LOCK_SUMMARY_ON_FAILED_PULL))
                                plex_season.edit(**edit)
                            except:
                                log.warning("{} Season {} exists on Trakt but not in Plex".format(show.title, season_number))
                time.sleep(1)
            log.info("Pulling finished")
            pulling = False

if __name__ == "__main__":
    main()
    print("Done.")