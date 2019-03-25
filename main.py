#!/usr/bin/python3

import sys
import argparse
import logging
import twitter

import config
import twrapper
import fmgr
import timer


VERSION = '1.0'


def parse_args():
    """
    Initializes command line arguments and
    parses them on startup returning the parsed
    args namespace.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default='config.json', type=str,
        help='The location of the config. if not existent, a new config file will be created there. (default "./config.json")')
    parser.add_argument('--once', action='store_const', const=True, default=False, 
        help='If this is passed, no timer loop will be created. A send will be performed and then, '+
             'the script will exit.')
    parser.add_argument('--log-level', '-l', default=2, type=int, 
        help='Set log level of the default logger. (default 1)')
    parser.add_argument('--version', '-v', action='version', 
        version=('It\'s Friday! v.%s - © 2019 Ringo Hoffmann (zekro Development)' % VERSION))
    return parser.parse_args()


def init() -> int:
    # Parsing command line arguments
    args = parse_args()

    # Setting log level
    logging.basicConfig(level=(args.log_level * 10))

    # Parsing config or creating a new one if not existent
    cfg = config.init(args.config)
    if cfg == None:
        logging.critical('Config file was not found. A default config file has been generated. '+
            'Open this config at "%s" and enter your values.' % args.config) 
        return 1

    # Creating twitter wrapper instance and testing
    # credentials
    try:
        twc = twrapper.Twitter(cfg.get('twitter'))
    except twitter.TwitterError as e:
        logging.critical('Failed creating twitter session: %s' % e.message)
        return 1

    # Creating file manager instance
    mgr = fmgr.FileManager(cfg.get('image_files').val())

    def handler() -> int:
        """
        Handler which picks a random image from the pool
        and posts it to the Twitter timeline.
        """
        try:
            file = mgr.get_rnd_file()
            twc.update(cfg.get('message').val(), file)
            return 0
        except Exception as e:
            logging.error('tweeting failed: ' + str(e))
            return 1

    # If flag '--once' was passed, execute the handler once
    # and then exit with the handlers return value
    if args.once:
        return(handler())
    
    # Starting the loop waiting for the trigger
    # time.
    logging.info('Starting timer...')
    t = timer.Timer(4, cfg.get('time').val(), handler)
    t.start_blocking()

    return 1


if __name__ == '__main__':
    sys.exit(init())