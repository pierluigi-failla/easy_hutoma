# -*- coding: utf-8 -*-

import logging
import time

from config import USER_KEY
from hutoma import EasyHutoma

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

SOURCE_FILE = '../data/source.txt'
TARGET_FILE = '../data/target.txt'

SLEEEP_SECS = 1*60


def main():
    hutoma = EasyHutoma(USER_KEY)

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
    hutoma.training_upload_files(aiid, SOURCE_FILE, TARGET_FILE)

    print 'Training monitor (check every {0} secs):'.format(SLEEEP_SECS)

    print 'Start training...'
    start_time = time.time()
    response, _ = hutoma.training_start(aiid)
    print '\n\tStatus: {trainingStatusDetails:s}\n\tRuntime status: {runtimeStatusDetails:s}\n\tScore: {score:s}'.format(**response)

    while response.get('trainingStatus ', -1) < 3:
        time.sleep(SLEEEP_SECS)
        response, _ = hutoma.current_status(aiid)
        print '\n\tStatus: {trainingStatusDetails:s}\n\tRuntime status: {runtimeStatusDetails:s}\n\tScore: {score:s}'.format(**response)
    print '{0} secs to train'.format(int(time.time() - start_time))

    print 'API calls: {0}'.format(hutoma.api_calls_count())

if __name__ == "__main__":
    main()
