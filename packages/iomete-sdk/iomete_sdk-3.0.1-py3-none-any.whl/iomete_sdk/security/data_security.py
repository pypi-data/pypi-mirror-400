import logging
from dataclasses import dataclass
from typing import List

from iomete_sdk.api_utils import ClientError, APIUtils
from iomete_sdk.security.policy_models import AccessPolicyView, RowFilterPolicyView, DataMaskPolicyView


@dataclass
class DataSecurityApiClient:
    logger = logging.getLogger('DataSecurityApiClient')

    host: str
    api_key: str
    domain: str

    data_security_endpoint: str = None
    api_utils: APIUtils = None

    def __post_init__(self):
        self.api_utils = APIUtils(self.api_key)

        self.logger.debug(f"Host: {self.host}")
        self.data_security_endpoint = f"{self.host}/api/v1/domains/{self.domain}/data-security"

    def create_access_policy(self, policy: AccessPolicyView) -> AccessPolicyView:
        data = self.api_utils.call(method="POST",
                                   url=f"{self.data_security_endpoint}/access/policy",
                                   payload=policy.to_dict())

        return AccessPolicyView.from_dict(data)

    def get_access_policies(self) -> List[AccessPolicyView]:
        data = self.api_utils.call(method="GET",
                                   url=f"{self.data_security_endpoint}/access/policy")

        return [AccessPolicyView.from_dict(policy) for policy in data]

    def get_access_policy_by_id(self, policy_id: int) -> AccessPolicyView:
        data = self.api_utils.call(method="GET",
                                   url=f"{self.data_security_endpoint}/access/policy/{policy_id}")

        return AccessPolicyView.from_dict(data)

    def update_access_policy_by_id(self, policy_id: int, policy: AccessPolicyView) -> AccessPolicyView:
        data = self.api_utils.call(method="PUT",
                                   url=f"{self.data_security_endpoint}/access/policy/{policy_id}",
                                   payload=policy.to_dict())

        return AccessPolicyView.from_dict(data)

    def delete_access_policy_by_id(self, policy_id: int):
        self.api_utils.call(method="DELETE",
                            url=f"{self.data_security_endpoint}/access/policy/{policy_id}")

    def create_filter_policy(self, policy: RowFilterPolicyView) -> RowFilterPolicyView:
        data = self.api_utils.call(method="POST",
                                   url=f"{self.data_security_endpoint}/filter/policy",
                                   payload=policy.to_dict())

        return RowFilterPolicyView.from_dict(data)

    def get_filter_policies(self) -> List[RowFilterPolicyView]:
        data = self.api_utils.call(method="GET",
                                   url=f"{self.data_security_endpoint}/filter/policy")

        return [RowFilterPolicyView.from_dict(policy) for policy in data]

    def get_filter_policy_by_id(self, policy_id: int) -> RowFilterPolicyView:
        data = self.api_utils.call(method="GET",
                                   url=f"{self.data_security_endpoint}/filter/policy/{policy_id}")

        return RowFilterPolicyView.from_dict(data)

    def update_filter_policy_by_id(self, policy_id: int, policy: RowFilterPolicyView) -> RowFilterPolicyView:
        data = self.api_utils.call(method="PUT",
                                   url=f"{self.data_security_endpoint}/filter/policy/{policy_id}",
                                   payload=policy.to_dict())

        return RowFilterPolicyView.from_dict(data)

    def delete_filter_policy_by_id(self, policy_id: int):
        self.api_utils.call(method="DELETE",
                            url=f"{self.data_security_endpoint}/filter/policy/{policy_id}")

    def create_masking_policy(self, policy: DataMaskPolicyView) -> DataMaskPolicyView:
        data = self.api_utils.call(method="POST",
                                   url=f"{self.data_security_endpoint}/mask/policy",
                                   payload=policy.to_dict())

        return DataMaskPolicyView.from_dict(data)

    def get_masking_policies(self) -> List[DataMaskPolicyView]:
        data = self.api_utils.call(method="GET",
                                   url=f"{self.data_security_endpoint}/mask/policy")

        return [DataMaskPolicyView.from_dict(policy) for policy in data]

    def get_masking_policy_by_id(self, policy_id: int) -> DataMaskPolicyView:
        data = self.api_utils.call(method="GET",
                                   url=f"{self.data_security_endpoint}/mask/policy/{policy_id}")

        return DataMaskPolicyView.from_dict(data)

    def update_masking_policy_by_id(self, policy_id: int, policy: DataMaskPolicyView) -> DataMaskPolicyView:
        data = self.api_utils.call(method="PUT",
                                   url=f"{self.data_security_endpoint}/mask/policy/{policy_id}",
                                   payload=policy.to_dict())

        return DataMaskPolicyView.from_dict(data)

    def delete_masking_policy_by_id(self, policy_id: int):
        self.api_utils.call(method="DELETE",
                            url=f"{self.data_security_endpoint}/mask/policy/{policy_id}")
