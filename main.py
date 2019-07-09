#!/usr/bin/python3

import sys
import argparse
import logging
import pytter

import config
import fmgr
import timer
import fqueue


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
    logging.basicConfig(
        level=(args.log_level * 10), 
        format='%(asctime)s | %(levelname)s | %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S')

    # Parsing config or creating a new one if not existent
    cfg = config.init(args.config)
    if cfg == None:
        logging.critical('Config file was not found. A default config file has been generated. '+
            'Open this config at "%s" and enter your values.' % args.config) 
        return 1

    queue = fqueue.Queue(cfg.get('queue_file').val())

    # Creating twitter wrapper instance and testing
    # credentials
    _creds = cfg.get('twitter')
    creds = pytter.Credentials(
        consumer_key=_creds.get('consumer_key').val(),
        consumer_secret=_creds.get('consumer_secret').val(),
        access_token_key=_creds.get('access_token_key').val(),
        access_token_secret=_creds.get('access_token_secret').val())

    try:
        twc = pytter.Client(creds)
        me = twc.me()
        logging.info('Logged in as {} ({})'.format(me.username, me.id_str))
    except Exception as e:
        logging.critical('Failed creating twitter session: {0}'.format(e))
        return 1

    # Creating file manager instance
    mgr = fmgr.FileManager(cfg.get('image_files').val())

    def handler():
        """
        Handler which picks a random image from the pool
        and posts it to the Twitter timeline.
        """
        try:
            qv = queue.next()
            if qv:
                media = qv[0] if len(qv) > 0 else None
                text  = qv[1] if len(qv) > 1 else None
                logging.info('picked tweet info from queue')
            else:
                media = mgr.get_rnd_file()
                text  = cfg.get('message').val()
            return twc.status_update(text=text, media=media)
        except Exception as e:
            logging.error('Tweeting failed: ' + str(e))
            return None

    # If flag '--once' was passed, execute the handler once
    # and then exit with the handlers return value
    if args.once:
        t = handler()
        if t:
            logging.info('Sent tweet ID: {}'.format(t.id_str))
            return 0
        return 1
    
    # Starting the loop waiting for the trigger
    # time.
    logging.info('Starting timer...')
    t = timer.Timer(4, cfg.get('time').val(), handler)
    t.start_blocking()

    return 1


if __name__ == '__main__':
    sys.exit(init())