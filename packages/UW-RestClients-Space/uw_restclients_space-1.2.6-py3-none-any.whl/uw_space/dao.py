# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from restclients_core.dao import DAO
from os.path import abspath, dirname
import os


class SPACE_DAO(DAO):
    def __init__(self):
        return super(SPACE_DAO, self).__init__()

    def service_name(self):
        return "space"

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]
