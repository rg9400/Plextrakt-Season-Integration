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
import argparse

################################ CONFIG BELOW ################################
PLEX_URL = "http://localhost:32400"
PLEX_TOKEN = ""
TRAKT_CLIENT_ID = ""
###############################################################################

## CODE BELOW ##

#Set up the argparse for all the script arguments
parser = argparse.ArgumentParser(description="Plextrakt Season Integration", epilog='Run \'trakt_seasons.py COMMAND --help\' for more info on a command')
parser._positionals.title = 'required arguments'
parser.add_argument(
                  '--debug', 
                  action='store_true', 
                  default=False,
                  help='Print debug info to the log file. Default is False'
                  )
parent_parser = argparse.ArgumentParser(add_help=False)
items = parent_parser.add_argument_group("(required) items to process")
items.add_argument(
                  '--libraries',
                  nargs='+',
                  default=[],
                  help='Space separated list of libraries in quotes to process with names matching Plex exactly.'
                  )
items.add_argument(
                  '--shows',
                  nargs='+',
                  default=[],
                  help='Space separated list of shows in quotes to process with names matching Plex exactly.'
                  )
parent_parser.add_argument(
                  '--data', '-d',
                  choices=['title', 'summary'],
                  nargs='+',
                  default=['title', 'summary'],
                  help='Process title or summary data. Default is both'
                  )
subparsers = parser.add_subparsers(dest='command', help='COMMAND')
reset = subparsers.add_parser(
                  'reset',
                  help='Reset season data in Plex',
                  parents=[parent_parser])
reset.add_argument(
                  '--unlock', '-u',
                  choices=['title', 'summary'],
                  nargs='+',
                  default=[],
                  help='Space separated list of fields to unlock after reset so they can be rescraped. Default is none'
                  )
pull = subparsers.add_parser(
                  'pull',
                  help='Pull season data from Trakt into Plex',
                  parents=[parent_parser]
                  ) 
pull.add_argument(
                  '--force', '-f',
                  action='store_true',
                  default=False,
                  help="Rescrape existing locked data"
                  )
pull.add_argument(
                  '--unlock', '-u',
                  choices=['failed_title', 'failed_summary', 'successful_title', 'successful summary'],
                  nargs='+',
                  default=[],
                  help='Unlock failed_title, successful_title, failed_summary, or successful_summary after reset so they can be rescraped. Default is none'
                  )

args = parser.parse_args()
if not (args.shows or args.libraries):
    parser.error('Nothing to process, add at least one item via either --shows or --libraries')

# Set up the rotating log files
size = 10*1024*1024  # 5MB
max_files = 5  # Keep up to 5 logs
log_filename = os.path.join(os.path.dirname(sys.argv[0]), 'trakt_seasons.log')
file_logger = RotatingFileHandler(log_filename, maxBytes=size, backupCount=max_files)
console = StreamHandler()
logger_formatter = Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s')
console_formatter = Formatter('%(message)s')
console.setFormatter(console_formatter)
file_logger.setFormatter(logger_formatter)
log = getLogger('Trakt Seasons')
console.setLevel(INFO)
if args.debug:
    file_logger.setLevel(DEBUG)
    log.setLevel(DEBUG)
else:
    file_logger.setLevel(INFO)
    log.setLevel(INFO)
log.addHandler(console)
log.addHandler(file_logger)

def main():
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    trakt_headers = {"content-type": "application/json", "trakt-api-version": "2", "trakt-api-key": TRAKT_CLIENT_ID, 'User-agent': 'Season Renamer v0.1'}

    process_list = []
    if len(args.libraries) > 0:
        for library in args.libraries:
            try:
                process_list.extend(plex.library.section(library).all())
                log.info("Processing all shows found in library {}".format(library))
            except:
                log.error("Could not find library {} in Plex".format(library))
    else:
        log.debug('No libraries identified to be processed')
    if len(args.shows) > 0:
        for show in args.shows:
            try:
                process_list.append(plex.search(show)[0])
                log.info("Proccessing show {}".format(show))
            except:
                log.error("Could not find show {} in Plex".format(show))
    else:
        log.debug('No specific shows identified to be processed')
    deduped_list = set(process_list)      

    if args.command == 'reset':
        reset_show_counter = 0
        reset_season_counter = 0
        log.info('Begining reset process')
        reset_title_locking_indicator = int('title' not in args.unlock)
        reset_summary_locking_indicator = int('summary' not in args.unlock)
        for show in deduped_list:
            reset_show_counter += 1
            for season in show.seasons():
                reset_season_counter += 1
                old_season_title = season.title
                old_season_summary = season.summary
                edit = {}
                if 'title' in args.data:
                    edit['title.value'] = ''
                    edit['title.locked'] = reset_title_locking_indicator
                if 'summary' in args.data:
                    edit['summary.value'] = ''
                    edit['summary.locked'] = reset_summary_locking_indicator
                season.edit(**edit)
                if 'title' in args.data:
                    log.debug("""
                    Show: {}
                    Season: {}
                    Old Title: {}
                    New Title: {}
                    Locked: {}
                    """
                    .format(show.title, season.seasonNumber, old_season_title, season.reload().title, bool(reset_title_locking_indicator)))
                if 'summaries' in args.data:
                    log.debug("""
                    Show: {}
                    Season: {}
                    Old Summary: {}
                    New Summary: {}
                    Locked: {}
                    """
                    .format(show.title, season.seasonNumber, old_season_summary, season.reload().summary, bool(reset_summary_locking_indicator)))
        log.info("Reset process finished")
        log.info("Reset {} seasons across {} shows".format(reset_season_counter, reset_show_counter))

    if args.command == 'pull':
        log.info('Starting pull process')
        show_counter = 0
        season_counter = 0
        new_title_counter = 0
        new_summary_counter = 0
        pull_successful_title_locking_indicator = int('successful_title' not in args.unlock)
        pull_failed_title_locking_indicator = int('failed_title' not in args.unlock)
        pull_succesful_summary_locking_indicator = int('successful_summary' not in args.unlock)
        pull_failed_summary_locking_indicator = int('failed_summary' not in args.unlock)
        if args.force:
            log.info("Force Refresh enabled. Rescraping all items in the list")
        else:
            log.info("Force refresh disabled. Will filter out locked items")
        for show in deduped_list:
            season_list = list(filter(lambda x: (x.seasonNumber != 0), show.seasons()))
            if not args.force:
                if 'title' in args.data:
                    all_titles_locked = all("title" in (field.name for field in season.fields) for season in season_list)
                else:
                    all_titles_locked = True
                if 'summary' in args.data:
                    all_summaries_locked = all("summary" in (field.name for field in season.fields) for season in season_list)
                else:
                    all_summaries_locked = True
                if all_titles_locked and all_summaries_locked:
                    log.debug('Skipping show {} because force refresh is disabled and all requested items are locked'.format(show.title))
                    continue
            if "thetvdb" in show.guid:
                id = int(re.search(r'thetvdb:\/\/(.*)\?', show.guid).group(1))
                trakt_search_api = 'https://api.trakt.tv/search/tvdb/{}?type=show'.format(id)
            elif "themoviedb" in show.guid:
                id = int(re.search(r'themoviedb:\/\/(.*)\?', show.guid).group(1))
                trakt_search_api = 'https://api.trakt.tv/search/tmdb/{}?type=show'.format(id)
            else: 
                log.warning('Could not find a TVDB or TMDB ID for show {}'.format(show.title))
                continue
                
            try:
                trakt_search = requests.get(trakt_search_api, headers=trakt_headers).json()
                slug = trakt_search[0]['show']['ids']['slug']
            except:
                log.warning('Could not find Trakt slug for show {} and guid {}'.format(show.title, show.guid))
                continue

            trakt_season_api = 'https://api.trakt.tv/shows/{}/seasons?extended=full'.format(slug)
            try:
              trakt_seasons = requests.get(trakt_season_api, headers=trakt_headers).json()
            except:
              log.warning("Trakt season page inaccessible, skipping show {}".format(show.title))
              continue
            show_counter += 1
            for season in trakt_seasons:
                season_number = season['number']
                if season_number != 0:
                    season_title = season['title']
                    if season_title == 'Season {}'.format(season_number):
                        season_title = None
                    season_summary = season['overview']
                    try:
                        plex_season = show.season(season_number)
                        if not args.force:
                            locked_title = "title" in (field.name for field in plex_season.fields)
                            locked_summary = "summary" in (field.name for field in plex_season.fields)
                        else:
                            locked_title = False
                            locked_summary = False
                        if not (locked_title and locked_summary):
                            season_counter += 1
                        old_season_title = plex_season.title
                        old_season_summary = plex_season.summary
                        edit = {}
                        if 'title' in args.data and not locked_title:
                            if season_title:
                                edit['title.value'] = season_title
                                edit['title.locked'] = pull_successful_title_locking_indicator
                                log.debug("""
                                Show: {}
                                Season: {}
                                Old Title: {}
                                New Title: {}
                                Locked: {}
                                """
                                .format(show.title, plex_season.seasonNumber, old_season_title, season_title, bool(pull_successful_title_locking_indicator)))
                                new_title_counter += 1
                            else:
                                edit['title.value'] = old_season_title
                                edit['title.locked'] = pull_failed_title_locking_indicator
                                log.debug("{} Season {} - No title found on Trakt. Locked on Plex: {}". format(show.title, plex_season.seasonNumber, bool(pull_failed_title_locking_indicator)))
                        if 'summary' in args.data and not locked_summary:
                            if season_summary:
                                edit['summary.value'] = season_summary
                                edit['summary.locked'] = pull_succesful_summary_locking_indicator
                                log.debug("""
                                Show: {}
                                Season: {}
                                Old Summary: {}
                                New Summary: {}
                                Locked: {}
                                """
                                .format(show.title, plex_season.seasonNumber, old_season_summary, season_summary, bool(pull_succesful_summary_locking_indicator)))
                                new_summary_counter += 1
                            else:
                                edit['summary.value'] = old_season_summary
                                edit['summary.locked'] = pull_failed_summary_locking_indicator
                                log.debug("{} Season {} - No summary found on Trakt. Locked on Plex: {}".format(show.title, plex_season.seasonNumber, bool(pull_failed_summary_locking_indicator)))
                        plex_season.edit(**edit)
                    except:
                        log.warning("{} Season {} exists on Trakt but not in Plex".format(show.title, season_number))
            time.sleep(5)
        log.info("Pull process finished")
        log.info("Processed {} shows across {} seasons. Found {} new titles and {} new summaries".format(show_counter, season_counter, new_title_counter, new_summary_counter))

if __name__ == "__main__":
    main()
    print("Done.")
