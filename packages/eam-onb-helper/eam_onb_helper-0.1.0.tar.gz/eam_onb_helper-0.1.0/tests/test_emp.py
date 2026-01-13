"""This class is used to test the EmpBuilder class."""

from unittest import mock, TestCase

from eightam_onb_helper.tests.common.cosmos_client_mock import CosmosClientMock
from eightam_onb_helper.src.eam_onb_helper.emp import EmpBuilder
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
class TestEmpBuilder(TestCase):
    """This class is used to test the EmpBuilder class."""
    @mock.patch('uuid.uuid4', return_value='test_id')
    def test_format(self, mock_uuid4):
        """This method is used to test the format method."""
        emp_builder = EmpBuilder(DATA_BASE, ['test_company_name'])
        item = {
            'itemType': 'company'
        }
        formatted_item = emp_builder.format(item)
        self.assertEqual(formatted_item, {'id': 'test_id', 'type': 'company'})

    @mock.patch('uuid.uuid4', return_value='test_company_id')
    @mock.patch(
        'eightam_onb_helper.src.eam_onb_helper.common.helpers.generate_sign_up_code',
        return_value='test_sign_up_code'
    )
    @mock.patch('time.time', return_value=1234)
    def test_build_company(self, mock_uuid4, mock_sign_up_cdoe, mock_time):
        """This method is used to test the build_company method."""
        DATA_BASE.client.results = [
            {'itemType': 'test_item_type', 'dates': {'added': 1234}}]
        emp_builder = EmpBuilder(
            DATA_BASE,
            [
                'test_company_name',
                'test_is_demo',
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

        company = emp_builder.build_company()

        self.assertEqual(company, {
            'id': 'test_company_id',
            'type': 'company',
            'name': 'test_company_name',
            'accountType': 'employer',
            'email': 'test_email',
            'isDemo': 'test_is_demo',
            'signUpCode': 'test_sign_up_code',
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
            'dates': {'added': 1234}
        })

    @mock.patch('uuid.uuid4', return_value='test_company_id')
    @mock.patch(
        'eightam_onb_helper.src.eam_onb_helper.emp.EmpBuilder.format',
        return_value={'type': 'test_item_type'}
    )
    def test_build_tags(self, mock_uuid, mock_format):
        """This method is used to test the build_tags method."""
        DATA_BASE.client.results = [{'type': 'test_item_type'}]
        emp_builder = EmpBuilder(DATA_BASE, ['test_company_name'])
        tags = emp_builder.build_tags()
        self.assertEqual(
            tags, {'companyId': 'test_company_id', 'type': 'test_item_type'})

    @mock.patch('uuid.uuid4', return_value='test_company_id')
    @mock.patch(
        'eightam_onb_helper.src.eam_onb_helper.emp.EmpBuilder.format',
        return_value={'type': 'test_item_type'}
    )
    def test_build_employer_doc_config(self, mock_uuid, mock_format):
        """This method is used to test the build_employer_doc_config method."""
        DATA_BASE.client.results = [{'type': 'test_item_type'}]
        emp_builder = EmpBuilder(DATA_BASE, ['test_company_name'])
        employer_doc_config = emp_builder.build_employer_doc_config()
        self.assertEqual(
            employer_doc_config,
            {
                'type': 'test_item_type',
                'employerId': 'test_company_id',
                'employerName': 'test_company_name'
            }
        )
