# -*- coding: utf-8 -*-
import logging
import string

from config import USER_KEY
from hutoma import EasyHutoma

logger = logging.getLogger()
logger.setLevel(logging.ERROR)


def main():
    hutoma = EasyHutoma(USER_KEY)

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
