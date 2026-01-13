"""This module is used to generate a sign up code."""

import random
import geonamescache


def generate_sign_up_code() -> str:
    """This method is used to generate a sign up code."""
    geo_name = geonamescache.GeonamesCache()
    counties = geo_name.get_us_counties()
    random_county = random.choice(counties)["name"].split(" ")[0]
    random_number = str(random.randint(0, 9999))

    return random_county + random_number
