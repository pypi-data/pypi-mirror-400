"""This module is used to Build the Employer object and associated items for the EAM ONB Helper."""

import uuid
import time

from .common import helpers


class EmpBuilder:
    """
    This class is used to build the Employer object and associated items for the EAM ONB Helper.
    """

    def __init__(self, database, company_data: list) -> None:
        self.company_id = str(uuid.uuid4())
        self.company_name = company_data[0]
        self.database = database
        self.company_data = company_data

    @staticmethod
    def format(item: dict) -> dict:
        """This method is used to format the item."""
        item['id'] = str(uuid.uuid4())
        item['type'] = item['itemType']
        del item['itemType']

        return item

    def build_company(self) -> dict:
        """This method is used to build the company."""
        company = self.database.get_result(
            query="SELECT * FROM c WHERE c.type = 'template' AND c.itemType = 'company'"
        )
        company['id'] = self.company_id
        company['name'] = self.company_data[0]
        company['type'] = 'company'
        del company['itemType']
        company['accountType'] = 'employer'
        company['email'] = self.company_data[13]
        company['isDemo'] = self.company_data[1]
        company['signUpCode'] = helpers.generate_sign_up_code()
        company['website'] = self.company_data[2]
        company['address'] = {
            'street': self.company_data[3],
            'city': self.company_data[4],
            'province': self.company_data[5],
            'postalCode': self.company_data[6],
            'country': self.company_data[7],
            'office': self.company_data[8]
        }
        company['phone'] = self.company_data[9]
        company['dates']['added'] = int(time.time())

        return company

    def build_tags(self) -> dict:
        """This method is used to build the tags."""
        tags = self.format(
            self.database.get_result(
                query="SELECT * FROM c WHERE c.type = 'template' AND c.itemType = 'tags'"
            )
        )
        tags['companyId'] = self.company_id
        return tags

    def build_employer_doc_config(self) -> dict:
        """This method is used to build the employer document configuration."""
        emp_doc_config = self.format(
            self.database.get_result(
                query="SELECT * FROM c WHERE c.type = 'template'"
                "AND c.itemType = 'employerDocConfig'"
            )
        )
        emp_doc_config['employerId'] = self.company_id
        emp_doc_config['employerName'] = self.company_name
        return emp_doc_config

    def build_updated_employer_doc_config(self) -> dict:
        """This method is used to build the updated employer document configuration."""
        emp_doc_config = self.format(
            self.database.get_result(
                query="SELECT * FROM c WHERE c.type = 'template'"
                "AND c.itemType = 'docConfig'"
            )
        )
        emp_doc_config['employerId'] = self.company_id
        emp_doc_config['employerName'] = self.company_name
        emp_doc_config['config']['type'] = "default"
        return emp_doc_config

    def build_employer_rating_archive(self) -> dict:
        """This method is used to build a vendor rating archive."""
        employer_rating_archive = self.database.get_result(
            query="SELECT * FROM c WHERE c.type = 'template' AND c.itemType  = 'employerRatingArchive'"
        )

        employer_rating_archive['id'] = str(uuid.uuid4())
        employer_rating_archive['type'] = 'employerRatingArchive'
        employer_rating_archive['employerName'] = self.company_name
        employer_rating_archive['employerId'] = self.company_id

        del employer_rating_archive['itemType']

        return employer_rating_archive
