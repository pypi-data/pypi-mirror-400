"""This module contains the common builder class for the EAM ONB Helper."""

import uuid
import dataclasses
import time
from eam_db_helper.db import DatabaseHelper


@dataclasses.dataclass
class CommonBuilder:
    """This class is used to build common objects for the EAM ONB Helper."""

    def __init__(self, database: DatabaseHelper, vendor_list_data: dict) -> None:
        self.database = database
        self.vendor_list_data = vendor_list_data

    def build_vendor_list(self) -> dict:
        """This method is used to build a vendor list."""
        vendor_list = self.database.get_result(
            query="SELECT * FROM c WHERE c.type = 'template' AND c.itemType  = 'vendorList'"
        )

        vendor_list['id'] = str(uuid.uuid4())
        vendor_list['vendorId'] = self.vendor_list_data['vendor_id']
        vendor_list['vendorName'] = self.vendor_list_data['vendor_name']
        vendor_list['vendorAddress'] = self.vendor_list_data['vendor_address']
        vendor_list['vendorPhone'] = self.vendor_list_data['vendor_phone']
        vendor_list['vendorIcon'] = self.vendor_list_data['vendor_icon']
        vendor_list['vendorAccountAdmin'] = self.vendor_list_data['vendor_admin']
        vendor_list['vendorOverallRating'] = self.vendor_list_data['vendor_overall_rating']
        vendor_list['vendorSubscriptionType'] = self.vendor_list_data['vendor_subscription_type']
        vendor_list['vendorDates'] = self.vendor_list_data['vendor_dates']

        vendor_list['employerId'] = self.vendor_list_data['employer_id']
        vendor_list['employerName'] = self.vendor_list_data['employer_name']
        vendor_list['employerAddress'] = self.vendor_list_data['employer_address']
        vendor_list['employerPhone'] = self.vendor_list_data['employer_phone']
        vendor_list['employerIcon'] = self.vendor_list_data['employer_icon']
        vendor_list['employerAccountAdmin'] = self.vendor_list_data['employer_admin']

        vendor_list['type'] = 'vendorList'

        del vendor_list['itemType']

        return vendor_list

    def build_vendor_rating_archive(self) -> dict:
        """This method is used to build a vendor rating archive."""
        vendor_rating_archive = self.database.get_result(
            query="SELECT * FROM c WHERE c.type = 'template' AND c.itemType  = 'vendorRatingArchive'"
        )

        vendor_rating_archive['id'] = str(uuid.uuid4())
        vendor_rating_archive['type'] = 'vendorRatingArchive'
        vendor_rating_archive['vendorName'] = self.vendor_list_data['vendor_name']
        vendor_rating_archive['vendorId'] = self.vendor_list_data['vendor_id']
        vendor_rating_archive['employerName'] = self.vendor_list_data['employer_name']
        vendor_rating_archive['employerId'] = self.vendor_list_data['employer_id']

        del vendor_rating_archive['itemType']

        return vendor_rating_archive
