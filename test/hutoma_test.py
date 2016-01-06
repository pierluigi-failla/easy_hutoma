# -*- coding: utf-8 -*-

import logging
import unittest

from hutoma import EasyHutoma, HutomaException

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

USER_KEY = ''  # use a valid user key


class EasyHutomaTest(unittest.TestCase):
    def test(self):
        hutoma = EasyHutoma(USER_KEY)

        try:
            # get the list of AIs
            ais = hutoma.list_ai()
            self.assertTrue(isinstance(ais, list))

            # if no AIs create one
            if len(ais) == 0:
                ais = hutoma.create_ai()
            self.assertTrue(len(ais) > 0)

            # test deletion
            old_len = len(ais)
            ais = hutoma.delete_ai(ais[0])
            self.assertEqual(len(ais), old_len - 1)

            # ensure at least 1 AI
            if len(ais) == 0:
                ais = hutoma.create_ai()

        except HutomaException as e:
            logging.warn(e.message)

            # TODO(pierluigi) enrich with additional tests


if __name__ == '__main__':
    unittest.main()
