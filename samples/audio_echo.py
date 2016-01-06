# -*- coding: utf-8 -*-
import logging

from hutoma.audio import RecordAudio, PlayAudio

logger = logging.getLogger()
logger.setLevel(logging.WARN)

# This is much more a test for recording and playing sounds


def main():
    record = RecordAudio()
    print 'Speak at the microphone...'
    record.record_to_file('../data/test.wav')
    print 'Audio has been recorded to ../data/test.wav'
    play = PlayAudio()
    print 'Playing ../data/test.wav'
    play.play_wav_file('../data/test.wav')
    print 'Done'

if __name__ == "__main__":
    main()
