"""This module is used to test the VendBuilder class."""

from unittest import mock, TestCase

from eightam_onb_helper.tests.common.cosmos_client_mock import CosmosClientMock
from eightam_onb_helper.src.eam_onb_helper.vend import VendBuilder
from eightam_db_helper.src.eam_db_helper.db import DatabaseHelper


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

# pylint: disable=unused-argument


class TestVendBuilder(TestCase):
    """This class is used to test the VendBuilder class."""
    @mock.patch('uuid.uuid4', return_value='test_id')
    def test_format(self, mock_uuid4):
        """This method is used to test the format method."""
        vend_builder = VendBuilder(DATA_BASE, ['test_company_name'])
        item = {
            'itemType': 'company'
        }
        formatted_item = vend_builder.format(item)
        self.assertEqual(formatted_item, {'id': 'test_id', 'type': 'company'})

    @mock.patch('uuid.uuid4', return_value='test_company_id')
    @mock.patch(
        'eightam_onb_helper.src.eam_onb_helper.common.helpers.generate_sign_up_code',
        return_value='test_sign_up_code'
    )
    @mock.patch('time.time', return_value=123456)
    def test_build_company(self, mock_uuid4, mock_signup_code, mock_time):
        """This method is used to test the build_company method."""
        DATA_BASE.client.results = [
            {'dates': {'added': 123456}, 'itemType': 'company'}]
        vend_builder = VendBuilder(
            DATA_BASE,
            [
                'test_company_name',
                'test_demo',
                'test_subscription_type',
                'test_website',
                'test_street',
                'test_city',
                'test_province',
                'test_postal_code',
                'test_country',
                'test_office',
                'test_phone',
                '',
                '',
                '',
                'test_email'
            ]
        )
        company = vend_builder.build_company()

        self.assertEqual(company, {
            'id': 'test_company_id',
            'name': 'test_company_name',
            'email': 'test_email',
            'isDemo': 'test_demo',
            'signUpCode': 'test_sign_up_code',
            'subscriptionType': 'test_subscription_type',
            'website': 'test_website',
            'address': {
                'street': 'test_street',
                'city': 'test_city',
                'province': 'test_province',
                'postalCode': 'test_postal_code',
                'country': 'test_country',
                'office': 'test_office'
            },
            'phone': 'test_phone',
            'dates': {'added': 123456},
            'type': 'company'
        })

    @mock.patch('uuid.uuid4', return_value='test_company_id')
    def test_build_profile_state(self, mock_uuid4):
        """Test the build_profile_state method."""
        DATA_BASE.client.results = [{
            "itemType": "vendorPreQualProfileState"
        }]

        vend_builder = VendBuilder(DATA_BASE, ['test_company_name'])
        profile_state = vend_builder.build_profile_state()
        self.assertEqual(profile_state, {
            "id": "test_company_id",
            "type": "vendorPreQualProfileState",
            "vendorId": "test_company_id",
            "vendorName": "test_company_name",
        })

    @mock.patch('uuid.uuid4', return_value='test_company_id')
    def build_payment_state(self, mock_uuid4):
        """Test the build_payment_state method."""
        DATA_BASE.client.results = [{
            "itemType": "vendorPreQualPaymentState"
        }]

        vend_builder = VendBuilder(DATA_BASE, ['test_company_name'])
        payment_state = vend_builder.build_payment_state()
        self.assertEqual(payment_state, {
            "id": "test_company_id",
            "type": "vendorPreQualPaymentState",
            "vendorId": "test_company_id",
            "vendorName": "test_company_name",
        })

    @mock.patch('uuid.uuid4', return_value='test_company_id')
    def test_build_documents_state(self, mock_uuid4):
        """Test the build_documents_state method."""
        DATA_BASE.client.results = [{
            "itemType": "vendorPreQualDocumentsState"
        }]

        vend_builder = VendBuilder(DATA_BASE, ['test_company_name'])
        documents_state = vend_builder.build_documents_state()
        self.assertEqual(documents_state, {
            "id": "test_company_id",
            "type": "vendorPreQualDocumentsState",
            "vendorId": "test_company_id",
            "vendorName": "test_company_name",
        })

    @mock.patch('uuid.uuid4', return_value='test_company_id')
    def test_build_requirements_state(self, mock_uuid4):
        """Test the build_requirements_state method."""
        DATA_BASE.client.results = [{
            "itemType": "vendorPreQualRequirementsState"
        }]

        vend_builder = VendBuilder(DATA_BASE, ['test_company_name'])
        requirements_state = vend_builder.build_requirements_state()
        self.assertEqual(requirements_state, {
            "id": "test_company_id",
            "type": "vendorPreQualRequirementsState",
            "vendorId": "test_company_id",
            "vendorName": "test_company_name",
        })

    @mock.patch('uuid.uuid4', return_value='test_company_id')
    def test_build_stepper_state(self, mock_uuid4):
        """Test the build_stepper_state method."""
        DATA_BASE.client.results = [{
            "itemType": "vendorStepperState"
        }]

        vend_builder = VendBuilder(DATA_BASE, ['test_company_name'])
        stepper_state = vend_builder.build_stepper_state()
        self.assertEqual(stepper_state, {
            "id": "test_company_id",
            "type": "vendorStepperState",
            "vendorId": "test_company_id",
            "vendorName": "test_company_name",
        })

    @mock.patch('uuid.uuid4', return_value='test_id')
    def test_build_additional_req(self, mock_uuid4):
        """Test the build_additional_requirements method."""
        DATA_BASE.client.results = [{'text': 'test_text'}]
        vend_builder = VendBuilder(DATA_BASE, ['test_company_name'])
        additional_requirements = vend_builder.build_additional_requirements()
        self.assertEqual(additional_requirements, [{
            "id": "test_id",
            "type": "vendorAdditionalRequirement",
            "text": "test_text",
            "defaultDocumentIdList": ["4270e05d-8339-4d13-b2ec-2f7a6848a063"],
            "additionalRequirementId": "test_id",
            "vendorId": "test_id",
            "isActive": False
        }])

    @mock.patch('uuid.uuid4', return_value='test_id')
    def test_build_safety_stats(self, mock_uuid4):
        """Test the build_safety_stats method."""
        DATA_BASE.client.results = [{
            "itemType": "vendorSafetyStats",
            "vendorName": "test_company_name"
        }]
        vend_builder = VendBuilder(DATA_BASE, ['test_company_name'])
        safety_stats = vend_builder.build_safety_stats()
        self.assertEqual(safety_stats, {
            "id": "test_id",
            "type": "vendorSafetyStats",
            "vendorId": "test_id"
        })
