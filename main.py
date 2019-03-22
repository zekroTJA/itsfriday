import sys
import argparse
import logging
import twitter

import config
import twrapper
import fmgr
import timer


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default='config.json', type=str,
        help='The location of the config. if not existent, a new config file will be created there.')
    parser.add_argument('--cron', action='store_const', const=True, default=False, 
        help='If this is passed, no timer loop will be created. A send will be performed and then, '+
             'the script will exit.')
    return parser.parse_args()


def init() -> int:
    args = parse_args()

    cfg = config.init(args.config)
    if cfg == None:
        logging.critical("Config file was not found. A default config file has been generated. "+
            "Open this config at '%s' and enter your values." % args.config) 
        return 1

    # try:
    #     twc = twrapper.Twitter(cfg.get("twitter"))
    # except twitter.TwitterError as e:
    #     logging.critical("Failed creating twitter session: %s" % e.message)

    # twc.update("Hey, das ist nur ein API test ;) Bitte ignorieren ^^", "http://ih1.redbubble.net/image.151611002.9466/flat,800x800,075,f.jpg")
    # mgr = fmgr.FileManager(cfg.get("image_files").val())
    # print(mgr.get_rnd_file())

    def handler():
        print("TEST")

    t = timer.Timer(4, cfg.get("time").val(), handler)
    t.start_blocking()

    return 0


if __name__ == '__main__':
    sys.exit(init())