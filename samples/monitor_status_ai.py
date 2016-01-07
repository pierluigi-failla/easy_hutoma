# -*- coding: utf-8 -*-
import argparse
import logging
import time

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
    parser.add_argument('--sleep',
                        default=60,
                        help='seconds to wait in check status loop (default=%(default)r)')
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

    print 'Training monitor (check every {0} secs):'.format(args.sleep)
    while True:
        response, _ = hutoma.current_status(aiid)
        print '\tStatus: {trainingStatusDetails:s}\n\tRuntime status: {runtimeStatusDetails:s}'.format(**response)
        print '\tScore: {score:s}'.format(**response)
        print '\tAIid: {0}'.format(aiid)
        if response.get('trainingStatus ', -1) < 3:
            print 'Training ended...'
            break
        time.sleep(SLEEEP_SECS)

    print 'API calls: {0}'.format(hutoma.api_calls_count())

if __name__ == "__main__":
    main()
