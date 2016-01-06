# -*- coding: utf-8 -*-

import logging
import time

from config import USER_KEY
from hutoma import EasyHutoma

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

SLEEEP_SECS = 1*60


def main():
    hutoma = EasyHutoma(USER_KEY)

    # get the list of available AIs
    ais = hutoma.list_ai()
    aiid = ais[0]
    print 'AI id: {0}'.format(aiid)

    print 'Training monitor (check every {0} secs):'.format(SLEEEP_SECS)
    while True:
        response, _ = hutoma.current_status(aiid)
        print '\tStatus: {trainingStatusDetails:s}\n\tRuntime status: {runtimeStatusDetails:s}\n\tScore: {score:s}'.format(**response)
        if response.get('trainingStatus ', -1) < 3:
            print 'Training ended...'
            break
        time.sleep(SLEEEP_SECS)

    print 'API calls: {0}'.format(hutoma.api_calls_count())

if __name__ == "__main__":
    main()
