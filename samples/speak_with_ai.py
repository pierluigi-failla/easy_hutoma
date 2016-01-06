# -*- coding: utf-8 -*-
import logging

import datetime
from hutoma import EasyHutoma
from hutoma.audio import RecordAudio, PlayAudio

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

USER_KEY = '???'  # use a valid user key

# Limitation apply based on your Hutoma Pricing plan


def generate_filename(tag):
    format = '%Y%m%d_%H%M%S'
    date = datetime.datetime.now().strftime(format)
    return '{0}_{1}'.format(date, tag)


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
