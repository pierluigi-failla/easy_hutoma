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
    parser.add_argument('--source_file',
                        default='../data/source.txt',
                        help='the source training file (default=%(default)r)')
    parser.add_argument('--target_file',
                        default='../data/target.txt',
                        help='the target training file (default=%(default)r)')
    parser.add_argument('--sleep',
                        default=60,
                        help='seconds to wait in check status loop (default=%(default)r)')
    args = parser.parse_args()
    return args


def main():
    args = add_args()

    hutoma = EasyHutoma(args.user_key)

    input = raw_input('Attention! this will delete all existing AIs (type "quit" to exit): ')
    if 'quit' in input:
        return

    # get the list of available AIs
    ais = hutoma.list_ai()
    print 'AIs list: {0}'.format(ais)
    for ai in ais:
        print 'deleting {0}...'.format(ai)
        hutoma.delete_ai(ai)

    ais = hutoma.create_ai()
    print 'New AI created: {0}'.format(ais)

    aiid = ais[0]
    print 'AI id: {0}'.format(aiid)

    print 'Upload data files...'
    hutoma.training_upload_files(aiid, args.source_file, args.target_file)

    print 'Training monitor (check every {0} secs):'.format(args.sleep)

    print 'Start training...'
    start_time = time.time()
    response, _ = hutoma.training_start(aiid)
    print '\tStatus: {trainingStatusDetails:s}\n\tRuntime status: {runtimeStatusDetails:s}'.format(**response)
    print '\tScore: {score:s}'.format(**response)
    print '\tAIid: {0}'.format(aiid)

    while response.get('trainingStatus ', -1) < 3:
        time.sleep(args.sleep)
        response, _ = hutoma.current_status(aiid)
        print
        print '\n\tStatus: {trainingStatusDetails:s}\n\tRuntime status: {runtimeStatusDetails:s}'.format(**response)
        print '\tScore: {score:s}'.format(**response)
        print '\tAIid: {0}'.format(aiid)
    print '{0} secs to train'.format(int(time.time() - start_time))

    print 'API calls: {0}'.format(hutoma.api_calls_count())

if __name__ == "__main__":
    main()
