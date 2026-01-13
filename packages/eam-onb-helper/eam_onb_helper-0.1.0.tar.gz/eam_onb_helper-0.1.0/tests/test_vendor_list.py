"""This module is used to test the CommonBuilder class."""

from unittest import TestCase

from eightam_onb_helper.tests.common.cosmos_client_mock import CosmosClientMock
from eightam_db_helper.src.eam_db_helper.db import DatabaseHelper
from eightam_onb_helper.src.eam_onb_helper.vendor_list import CommonBuilder


DATA_BASE = DatabaseHelper(
    {
        'account_uri': 'test_uri',
        'key': 'test_key',
        'db_name': 'test_database',
        'container_name': 'test_container',
        'env_id': 'test_env'
    },
    CosmosClientMock
)


COMMON_BUILDER = CommonBuilder(
    DATA_BASE,
    {
        'vendor_id': 'test_vendor_id',
        'vendor_name': 'test_vendor_name',
        'vendor_address': 'test_vendor_address',
        'vendor_phone': 'test_vendor_phone',
        'vendor_icon': 'test_vendor_icon',
        'vendor_admin': 'test_vendor_admin',
        'vendor_overall_rating': 'test_vendor_overall_rating',
        'vendor_subscription_type': 'test_vendor_subscription_type',
        'vendor_dates': 'test_vendor_dates',
        'employer_id': 'test_employer_id',
        'employer_name': 'test_employer_name',
        'employer_address': 'test_employer_address',
        'employer_phone': 'test_employer_phone',
        'employer_icon': 'test_employer_icon',
        'employer_admin': 'test_employer_admin'
    }
)


# pylint: disable=unused-argument
class TestCommonBuilder(TestCase):
    """This class is used to test the CommonBuilder class."""

    def test_build_vendor_list(self):
        """Test the build_vendor_list method."""
        DATA_BASE.client.results = [{'id': '1', 'itemType': 'template'}]
        vendor_list = COMMON_BUILDER.build_vendor_list()
        self.assertEqual(vendor_list, {
            'id': COMMON_BUILDER.item_id,
            'vendorId': 'test_vendor_id',
            'vendorName': 'test_vendor_name',
            'vendorAddress': 'test_vendor_address',
            'vendorPhone': 'test_vendor_phone',
            'vendorIcon': 'test_vendor_icon',
            'vendorAccountAdmin': 'test_vendor_admin',
            'vendorOverallRating': 'test_vendor_overall_rating',
            'vendorSubscriptionType': 'test_vendor_subscription_type',
            'vendorDates': 'test_vendor_dates',
            'employerId': 'test_employer_id',
            'employerName': 'test_employer_name',
            'employerAddress': 'test_employer_address',
            'employerPhone': 'test_employer_phone',
            'employerIcon': 'test_employer_icon',
            'employerAccountAdmin': 'test_employer_admin',
            'type': 'vendorList'
        })
