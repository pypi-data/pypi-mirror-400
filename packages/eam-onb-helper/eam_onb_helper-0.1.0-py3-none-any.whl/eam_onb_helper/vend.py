"""This module is used to build the vendor object and associated items for the EAM ONB Helper."""

import uuid
import time

from .common import helpers


class VendBuilder:
    """This class is used to build the Vendor object and associated items for the EAM ONB Helper."""

    def __init__(self, data_base, company_data: list) -> None:
        self.company_id = str(uuid.uuid4())
        self.company_name = company_data[0]
        self.data_base = data_base
        self.company_data = company_data

    def format(self, item) -> dict:
        """This method is used to format the item."""
        item['id'] = str(uuid.uuid4())
        item['type'] = item['itemType']

        if item['type'] != 'company':
            item['vendorId'] = self.company_id
            item['vendorName'] = self.company_name

        del item['itemType']

        return item

    def build_company(self) -> dict:
        """This method is used to build the company."""
        company = self.data_base.get_result(
            query="SELECT * FROM c WHERE c.type = 'template' AND c.itemType = 'company'")

        company['name'] = self.company_name
        company['email'] = self.company_data[14]
        company['isDemo'] = self.company_data[1]
        company['signUpCode'] = helpers.generate_sign_up_code()
        company['subscriptionType'] = self.company_data[2]
        company['website'] = self.company_data[3]
        company['address'] = {
            'street': self.company_data[4],
            'city': self.company_data[5],
            'province': self.company_data[6],
            'postalCode': self.company_data[7],
            'country': self.company_data[8],
            'office': self.company_data[9]
        }
        company['phone'] = self.company_data[10]
        company['dates']['added'] = int(time.time())

        company = self.format(company)

        company['id'] = self.company_id
        return company

    def build_profile_state(self) -> dict:
        """This method is used to build the profile state."""
        return self.format(
            self.data_base.get_result(
                query="SELECT * FROM c WHERE c.type = 'template'"
                "AND c.itemType = 'vendorPreQualProfileState'"
            )
        )

    def build_payment_state(self) -> dict:
        """This method is used to build the payment state."""
        return self.format(
            self.data_base.get_result(
                query="SELECT * FROM c WHERE c.type = 'template'"
                "AND c.itemType = 'vendorPreQualPaymentState'"
            )
        )

    def build_documents_state(self) -> dict:
        """This method is used to build the documents state."""
        return self.format(
            self.data_base.get_result(
                query="SELECT * FROM c WHERE c.type = 'template'"
                "AND c.itemType = 'vendorPreQualDocumentsState'"
            )
        )

    def build_requirements_state(self) -> dict:
        """This method is used to build the requirements state."""
        return self.format(
            self.data_base.get_result(
                query="SELECT * FROM c WHERE c.type = 'template'"
                "AND c.itemType = 'vendorPreQualRequirementsState'"
            )
        )

    def build_stepper_state(self) -> dict:
        """This method is used to build the stepper state."""
        return self.format(
            self.data_base.get_result(
                query="SELECT * FROM c WHERE c.type = 'template'"
                "AND c.itemType = 'vendorStepperState'"
            )
        )

    def build_additional_requirements(self) -> list:
        """This method is used to build the additional requirements."""
        additional_requirements = self.data_base.get_results(
            query="SELECT * FROM c WHERE c.type = 'additionalRequirement'")
        for item in additional_requirements:
            item["id"] = str(uuid.uuid4())
            item["type"] = "vendorAdditionalRequirement"
            item["text"] = item['text']
            item["defaultDocumentIdList"] = [
                "4270e05d-8339-4d13-b2ec-2f7a6848a063"]
            item["additionalRequirementId"] = item['id']
            item["vendorId"] = self.company_id
            item["isActive"] = False

        return additional_requirements

    def build_safety_stats(self) -> dict:
        """This method is used to build the safety stats."""
        safety_stats = self.format(self.data_base.get_result(
            query="SELECT * FROM c WHERE c.type = 'template' AND c.itemType = 'vendorSafetyStats'"))
        del safety_stats['vendorName']

        return safety_stats
