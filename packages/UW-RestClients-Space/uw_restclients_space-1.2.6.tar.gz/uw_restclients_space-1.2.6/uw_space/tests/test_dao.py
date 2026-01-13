# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from unittest import TestCase
import mock
from commonconf import override_settings
from restclients_core.exceptions import DataFailureException
from uw_space.dao import SPACE_DAO
from uw_space.utils import fdao_space_override


@fdao_space_override
class TestSpaceDao(TestCase):

    def test_dao(self):
        dao = SPACE_DAO()
        self.assertEqual(dao.service_name(), "space")
        self.assertTrue(
            dao.service_mock_paths()[0].endswith("/uw_space/resources"))
