# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from unittest import TestCase
from restclients_core.exceptions import DataFailureException
from uw_space import Facilities
from uw_space.models import Facility
from uw_space.utils import fdao_space_override

data = {
    'city': 'Seattle',
    'street': '3900 East Stevens Way NE',
    'state': 'WA',
    'post_code': '98195',
    'code': 'MEB',
    'last_updated': '2022-09-22 19:41:34-07:53',
    'latitude': 47.6536929997,
    'longitude': -122.304747,
    'name': 'Mechanical Engineering Building',
    'number': '1347',
    'site': 'Seattle Main Campus',
    'status': 'A',
    'type': 'Building'
    }


@fdao_space_override
class TestSpace(TestCase):

    def test_model(self):
        self.maxDiff = None
        fac_json = {
            "FacilityCode": "MEB",
            "FacilityNumber": "1347",
            "ModifiedDate": None,
            "LongName": "Mechanical Engineering Building",
            "Addresses": [
                {
                    "StreetAddress": "3900 East Stevens Way NE",
                    "City": "Seattle",
                    "State": "WA",
                    "PostalCode": "98195"
                }
            ],
            "CenterPoint": {
                "Latitude": 47.6536929997,
                "Longitude": -122.304747
            },
            "Site": {
                "Description": "Seattle Main Campus"
            },
            "FacilityType": {
                "Description": "Building"
            },
            "Status": "A"
        }
        fac = Facility.from_json(fac_json)
        self.assertEqual(fac.json_data(), {
             'city': 'Seattle',
             'code': 'MEB',
             'last_updated': None,
             'latitude': 47.6536929997,
             'longitude': -122.304747,
             'name': 'Mechanical Engineering Building',
             'number': '1347',
             'post_code': '98195',
             'site': 'Seattle Main Campus',
             'state': 'WA',
             'status': 'A',
             'street': '3900 East Stevens Way NE',
             'type': 'Building'
        })
        self.assertIsNotNone(str(fac))
        fac = Facility.from_json(
            {
                "FacilityCode": "MEB",
                "FacilityNumber": "1347",
                "ModifiedDate": "6/4/2025 9:35:03 AM",
                "LongName": "Mechanical Engineering Building"
            }
        )
        self.assertEqual(fac.json_data(), {
            'city': '',
            'street': '',
            'state': '',
            'post_code': '',
            'code': 'MEB',
            'last_updated': "2025-06-04 09:35:03-07:53",
            'latitude': '',
            'longitude': '',
            'name': 'Mechanical Engineering Building',
            'number': '1347',
            'site': '',
            'status': None,
            'type': ''
        })

        fac = Facilities().search_by_code("MDR")
        self.assertEqual(len(fac), 1)
        self.assertEqual(fac[0].json_data(), {
            'city': 'Seattle',
            'street': '4320 Little Canoe Channel NE',
            'state': 'WA',
            'post_code': '98195',
            'code': 'MDR',
            'last_updated': "2022-09-22 12:49:38-07:53",
            'latitude': 47.6601320001,
            'longitude': -122.305391,
            'name': 'Madrona Hall',
            'number': '6471',
            'site': 'Seattle Main Campus',
            'status': 'A',
            'type': 'Building'
            })

    def test_search_by_number(self):
        fac = Facilities().search_by_number("1347")
        self.assertEqual(fac.json_data(), data)

        self.assertRaises(
            DataFailureException,
            Facilities().search_by_number, "0"
        )

    def test_search_by_name(self):
        fac = Facilities().search_by_name("Allen Library")
        self.assertEqual(len(fac), 1)
        self.assertEqual(
            fac[0].json_data(),
            {
                'city': 'Seattle',
                'street': '1900 NE Grant Ln',
                'state': 'WA',
                'post_code': '98195',
                'code': 'ALB',
                'last_updated': '2025-06-04 09:35:13-07:53',
                'latitude': 47.6555730001,
                'longitude': -122.30705,
                'name': 'Allen Library',
                'number': '1107',
                'site': 'Seattle Main Campus',
                'status': 'A',
                'type': 'Building'
            })
        fac = Facilities().search_by_name("None")
        self.assertEqual(len(fac), 0)

    def test_search_by_street(self):
        fac = Facilities().search_by_street("668 NE Northlake Way")
        self.assertEqual(len(fac), 1)
        self.assertEqual(
            fac[0].json_data(),
            {
                'city': 'Seattle',
                'street': '668 NE Northlake Way',
                'state': 'WA',
                'post_code': '98105-6428',
                'code': 'EHD',
                'last_updated': '2025-06-04 09:35:03-07:53',
                'latitude': 47.654766,
                'longitude': -122.321073,
                'name': '668 NE Northlake Way (Environmental Hlth Dept)',
                'number': '1072',
                'site': 'Seattle U-District',
                'status': 'A',
                'type': 'Building'
            })
