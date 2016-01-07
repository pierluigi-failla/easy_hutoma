# -*- coding: utf-8 -*-
import argparse
import logging
import string

from hutoma import EasyHutoma

logger = logging.getLogger()
logger.setLevel(logging.ERROR)


def add_args():
    parser = argparse.ArgumentParser(description='Create and train AI')
    parser.add_argument('--user_key',
                        help='provide your Hutoma API user key')
    parser.add_argument('--aiid',
                        default=None,
                        help='the AI id to be used, if None the first one will be used (default=%(default)r)')
    args = parser.parse_args()
    return args


def main():
    args = add_args()

    hutoma = EasyHutoma(args.user_key)

    aiid = args.aiid
    if not aiid:
        # get the list of available AIs
        ais = hutoma.list_ai()
        print 'AIs list: {0}'.format(ais)
        if len(ais) == 0:
            print 'No AIs is available...'
            return
        aiid = ais[0]
    print 'AI id: {0}'.format(aiid)

    print 'Hit Ctrl+C to quit...'

    while True:
        q = raw_input('Human: ')
        q = ''.join(ch for ch in q if ch not in set(string.punctuation)).strip()
        print '   AI: {0}'.format(hutoma.chat(aiid, 12345, q))

if __name__ == "__main__":
    main()
