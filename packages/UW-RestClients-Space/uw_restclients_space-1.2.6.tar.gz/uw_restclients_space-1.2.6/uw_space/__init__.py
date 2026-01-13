# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from urllib.parse import quote_plus
from restclients_core.exceptions import DataFailureException
from uw_space.dao import SPACE_DAO
from uw_space.models import Facility

logger = logging.getLogger(__name__)


class Facilities(object):

    def __init__(self):
        self.dao = SPACE_DAO()
        self._read_headers = {
            'Accept': 'application/json',
            'Connection': 'keep-alive'}

    def search_by_code(self, facility_code):
        url = f"/space/v2/facility.json?facility_code={facility_code}"
        response = self.dao.getURL(url, self._read_headers)
        logger.debug(
            {'url': url, 'status': response.status, 'data': response.data})
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)
        return self.__process_json(json.loads(response.data))

    def search_by_name(self, facility_name):
        name = quote_plus(facility_name)
        url = f"/space/v2/facility.json?long_name={name}"
        response = self.dao.getURL(url, self._read_headers)
        logger.debug(
            {"url": url, "status": response.status, "data": response.data})
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)
        return self.__process_json(json.loads(response.data))

    def search_by_street(self, street_address):
        street = quote_plus(street_address)
        url = f"/space/v2/facility.json?street={street}"
        response = self.dao.getURL(url, self._read_headers)
        logger.debug(
            {"url": url, "status": response.status, "data": response.data})
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)
        return self.__process_json(json.loads(response.data))

    def search_by_number(self, facility_number):
        url = f"/space/v2/facility/{facility_number}.json"
        response = self.dao.getURL(url, self._read_headers)
        logger.debug(
            {'url': url, 'status': response.status, 'data': response.data})
        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)
        return Facility.from_json(json.loads(response.data))

    def __process_json(self, json_data):
        objs = []
        total_count = json_data.get("TotalCount", 0)
        if total_count == 0:
            return objs
        facilities = json_data.get("Facilities")
        for facility in facilities:
            status = facility.get("Status")
            if status == "A":
                # Active
                fnumber = facility.get("FacilityNumber")
                if fnumber and len(fnumber):
                    fac = self.search_by_number(fnumber)
                    if fac:
                        fac.status = status
                        objs.append(fac)
        return objs
