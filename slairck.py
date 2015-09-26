#!/usr/bin/env python

import sys
sys.dont_write_bytecode = True

import glob
import yaml
import json
import os
import sys
import time
import logging
from argparse import ArgumentParser

from util import load_config
from slackbot import SlackBot
from ircbot import IrcBot

def main_loop(bots, config):
    if "LOGFILE" in config:
        logging.basicConfig(filename=config[
                            "LOGFILE"], level=logging.INFO, format='%(asctime)s %(message)s')
    try:
        for bot in bots:
            bot.init()
        while True:
            for bot in bots:
                #print 'processing', bot
                bot.process()
                relay_ins = bot.collect_relay()
                for xbot in bots:
                    if type(bot) == type(xbot):
                        continue
                    xbot.relay(bot, relay_ins)

            time.sleep(.2)
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        logging.exception('OOPS')


if __name__ == "__main__":
    config = load_config('config')
    slackbot = SlackBot(config['slack']['token'], config)
    ircbot = IrcBot(config['irc']['host'], int(config['irc'].get('port', '6667')), config)

    if config.has_key("DAEMON"):
        if config["DAEMON"]:
            import daemon
            with daemon.DaemonContext():
                main_loop((slackbot, ircbot), config)
    main_loop((slackbot, ircbot), config)
