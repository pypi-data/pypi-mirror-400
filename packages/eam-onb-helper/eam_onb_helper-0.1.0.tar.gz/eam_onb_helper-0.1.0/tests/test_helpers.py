"""This module is used to test the functions in the helpers module."""

from unittest import mock

# from eightam_onb_helper.common.helpers import generate_sign_up_code
from eightam_onb_helper.src.eam_onb_helper.common.helpers import generate_sign_up_code


@mock.patch(
    'eightam_onb_helper.src.eam_onb_helper.common.helpers.'\
        'geonamescache.GeonamesCache.get_us_counties',
    return_value=[{'name': 'test_county'}, {'name': 'test_county'}]
)
@mock.patch('random.randint', return_value=1234)
#pylint: disable=unused-argument
def test_generate_sign_up_code(mock_choice, mock_randint):
    """This method is used to test the generate_sign_up_code method."""
    assert generate_sign_up_code() == 'test_county1234'
