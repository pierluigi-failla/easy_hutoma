# -*- coding: utf-8 -*-
import argparse
import datetime
import logging

from hutoma import EasyHutoma
from hutoma.audio import RecordAudio, PlayAudio

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

# Limitation apply based on your Hutoma Pricing plan


def add_args():
    parser = argparse.ArgumentParser(description='Create and train AI')
    parser.add_argument('--user_key',
                        help='provide your Hutoma API user key')
    parser.add_argument('--aiid',
                        default=None,
                        help='the AI id to be used, if None the first one will be used (default=%(default)r)')
    args = parser.parse_args()
    return args


def generate_filename(tag):
    return '{0}_{1}'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), tag)


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

    record = RecordAudio()
    play = PlayAudio()

    while True:
        path = '../data/{0}.wav'.format(generate_filename('human'))
        print 'Human: recording in progress... ',
        record.record_to_file(path)
        print 'Done'

        print 'AI thinking... '
        response = hutoma.speak(aiid, 12345, path)
        print 'AI: {0}'.format(response['output'])
        path = '../data/{0}.wav'.format(generate_filename('human'))
        with open(path, 'wb') as fin:
            fin.write(response['tts'])
        fin.close()
        print 'AI: speaking...',
        play.play_wav_file(path)
        print 'Done'

if __name__ == "__main__":
    main()
