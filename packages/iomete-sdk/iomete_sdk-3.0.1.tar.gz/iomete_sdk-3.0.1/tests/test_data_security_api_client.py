import unittest
import uuid

from iomete_sdk.api_utils import ClientError
from iomete_sdk.security import DataSecurityApiClient
from iomete_sdk.security.policy_models import AccessPolicyView, DataMaskPolicyView, RowFilterPolicyView, \
    DataMaskPolicyItem, RowFilterPolicyItem, AccessPolicyResource, AccessType, AccessPolicyItem, DataMaskPolicyResource, \
    RowFilterPolicyResource, ValidityPeriod, ResourceInclusionType
from tests import TEST_TOKEN, TEST_HOST, TEST_DOMAIN


class TestDataSecurityApiClient(unittest.TestCase):
    def setUp(self):
        self.client = DataSecurityApiClient(
            host=TEST_HOST,
            api_key=TEST_TOKEN,
            domain=TEST_DOMAIN
        )
        self.policy_suffix = f"iomete-sdk-{uuid.uuid4().hex}-"

    def test_access_policies(self):
        # Create a policy
        policy_name = self.policy_suffix + "automated-access-policy"
        new_policy = AccessPolicyView(
            name=policy_name,
            description="iomete-sdk-automated-access-policy",
            resources=[
                AccessPolicyResource(
                    databases=["test_db"],
                    tables=["test_tbl"],
                    columns=["*"]
                )
            ],
            allow_policy_items=[
                AccessPolicyItem(
                    accesses=[AccessType.SELECT, AccessType.UPDATE],
                    users=['{USER}'])
            ]
        )
        created_policy = self.client.create_access_policy(new_policy)

        # Verify the created policy
        self.assertEqual(created_policy.name, policy_name)

        # Retrieve created policy
        existing_policy = self.client.get_access_policy_by_id(created_policy.id)

        # Update the policy
        updated_policy = existing_policy
        updated_policy.description = 'updated'
        updated_policy = self.client.update_access_policy_by_id(updated_policy.id, updated_policy)

        # Verify the updated policy
        self.assertEqual(updated_policy.description, 'updated')

        # Delete the policy
        self.client.delete_access_policy_by_id(updated_policy.id)

        # Verify the policy is deleted
        with self.assertRaises(ClientError):
            self.client.get_access_policy_by_id(updated_policy.id)

    def test_data_mask_policies(self):
        # Create a policy
        policy_name = self.policy_suffix + "automated-masking-policy"
        new_policy = DataMaskPolicyView(
            name=policy_name,
            description="iomete-sdk-automated-masking-policy",
            resources=[
                DataMaskPolicyResource(
                    database="test_db",
                    table="test_tbl",
                    column="test_col"
                )
            ],
            data_mask_policy_items=[
                DataMaskPolicyItem(
                    data_mask_type="MASK_SHOW_LAST_4",
                    users=["{USER}"]
                )]
        )
        created_policy = self.client.create_masking_policy(new_policy)

        # Verify the created policy
        self.assertEqual(created_policy.name, policy_name)

        # Retrieve created policy
        existing_policy = self.client.get_masking_policy_by_id(created_policy.id)

        # Update the policy
        updated_policy = existing_policy
        updated_policy.description = 'updated'
        updated_policy = self.client.update_masking_policy_by_id(updated_policy.id, updated_policy)

        # Verify the updated policy
        self.assertEqual(updated_policy.description, 'updated')

        # Delete the policy
        self.client.delete_masking_policy_by_id(updated_policy.id)

        # Verify the policy is deleted
        with self.assertRaises(ClientError):
            self.client.get_masking_policy_by_id(updated_policy.id)

    def test_row_filter_policies(self):
        # Create a policy
        policy_name = self.policy_suffix + "automated-row-filter-policy"
        new_policy = RowFilterPolicyView(
            name=policy_name,
            description="iomete-sdk-automated-masking-policy",
            resources=[
                RowFilterPolicyResource(
                    database="test_db",
                    table="test_tbl"
                )
            ],
            row_filter_policy_items=[
                RowFilterPolicyItem(
                    filter_expr="1 == 1",
                    users=["{USER}"],
                )]
        )
        created_policy = self.client.create_filter_policy(new_policy)

        # Verify the created policy
        self.assertEqual(created_policy.name, policy_name)

        # Retrieve created policy
        existing_policy = self.client.get_filter_policy_by_id(created_policy.id)

        # Update the policy
        updated_policy = existing_policy
        updated_policy.description = 'updated'
        updated_policy = self.client.update_filter_policy_by_id(updated_policy.id, updated_policy)

        # Verify the updated policy
        self.assertEqual(updated_policy.description, 'updated')

        # Delete the policy
        self.client.delete_filter_policy_by_id(updated_policy.id)

        # Verify the policy is deleted
        with self.assertRaises(ClientError):
            self.client.get_filter_policy_by_id(updated_policy.id)

    # def test_empty_access_policies(self):
    #     # Attempt to create a policy with no values
    #     policy_name = "empty-access-policy"
    #     new_policy = AccessPolicyView(
    #         name=policy_name,
    #         description="empty policy",
    #         resources=[],
    #         allow_policy_items=[]
    #     )
    #     with self.assertRaises(ClientError):
    #         self.client.create_access_policy(new_policy)

    def test_access_policies_multiple_users(self):
        # Create a policy with multiple users
        policy_name = self.policy_suffix + "multi-user-access-policy"
        new_policy = AccessPolicyView(
            name=policy_name,
            description="policy for multiple users",
            resources=[
                AccessPolicyResource(
                    databases=["test_db"],
                    tables=["test_tbl"],
                    columns=["test_col"],
                    columns_inclusion_type=ResourceInclusionType.EXCLUDE
                )
            ],
            allow_policy_items=[
                AccessPolicyItem(
                    accesses=[AccessType.SELECT, AccessType.UPDATE],
                    users=["{USER}", "{OWNER}"])
            ]
        )
        created_policy = self.client.create_access_policy(new_policy)

        # Verify the created policy
        self.assertEqual(created_policy.name, policy_name)

        # Retrieve created policy
        existing_policy = self.client.get_access_policy_by_id(created_policy.id)

        # Verify the policy has multiple users
        self.assertEqual(len(existing_policy.allow_policy_items[0].users), 2)
        self.assertEqual(existing_policy.resources[0].columns_inclusion_type, ResourceInclusionType.EXCLUDE)

        # Delete the policy
        self.client.delete_access_policy_by_id(existing_policy.id)

    def test_invalid_datamask_policies(self):
        # Attempt to create a policy with invalid mask type
        policy_name = self.policy_suffix + "invalid-datamask-policy"
        new_policy = DataMaskPolicyView(
            name=policy_name,
            description="invalid datamask policy",
            resources=[
                DataMaskPolicyResource(
                    database="test_db",
                    table="test_tbl",
                    column="test_col"
                )
            ],
            data_mask_policy_items=[
                DataMaskPolicyItem(
                    data_mask_type="INVALID_MASK_TYPE",
                    users=["{USER}"]
                )]
        )
        with self.assertRaises(ClientError):
            self.client.create_masking_policy(new_policy)

    def test_row_filter_policies_complex_expr(self):
        # Create a policy with complex filter expression
        policy_name = self.policy_suffix + "complex-row-filter-policy"
        new_policy = RowFilterPolicyView(
            name=policy_name,
            description="policy with complex filter expression",
            resources=[
                RowFilterPolicyResource(
                    database="test_db",
                    table="test_tbl"
                )
            ],
            row_filter_policy_items=[
                RowFilterPolicyItem(
                    filter_expr="(1 == 1) AND (2 > 1)",
                    users=["{USER}"],
                )]
        )
        created_policy = self.client.create_filter_policy(new_policy)

        # Verify the created policy
        self.assertEqual(created_policy.name, policy_name)

        # Retrieve created policy
        existing_policy = self.client.get_filter_policy_by_id(created_policy.id)

        # Verify the complex filter expression
        self.assertEqual(existing_policy.row_filter_policy_items[0].filter_expr, "(1 == 1) AND (2 > 1)")

        # Delete the policy
        self.client.delete_filter_policy_by_id(existing_policy.id)

    def test_access_policies_with_validity_period(self):
        # Create a policy with a validity period
        policy_name = self.policy_suffix +  "validity-period-access-policy"
        new_policy = AccessPolicyView(
            name=policy_name,
            description="policy with validity period",
            validity_period=ValidityPeriod(
                start_time="2023/07/01 00:00:00",
                end_time="2023/07/31 23:59:59",
                time_zone="US/Pacific"
            ),
            resources=[
                AccessPolicyResource(
                    databases=["test_db"],
                    tables=["test_tbl"],
                    columns=["*"]
                )
            ],
            allow_policy_items=[
                AccessPolicyItem(
                    accesses=[AccessType.SELECT, AccessType.UPDATE],
                    users=['{USER}'])
            ]
        )
        created_policy = self.client.create_access_policy(new_policy)

        # Verify the created policy
        self.assertEqual(created_policy.name, policy_name)

        # Retrieve created policy
        existing_policy = self.client.get_access_policy_by_id(created_policy.id)

        # Verify the validity period
        self.assertEqual(existing_policy.validity_period.start_time, "2023/07/01 00:00:00")
        self.assertEqual(existing_policy.validity_period.end_time, "2023/07/31 23:59:59")
        self.assertEqual(existing_policy.validity_period.time_zone, "US/Pacific")

        # Delete the policy
        self.client.delete_access_policy_by_id(existing_policy.id)

    # def test_invalid_validity_period(self):
    #     # Attempt to create a policy with an invalid validity period (start time is after end time)
    #     policy_name = self.policy_suffix + "invalid-validity-period-policy"
    #     new_policy = AccessPolicyView(
    #         name=policy_name,
    #         description="policy with invalid validity period",
    #         validity_period=ValidityPeriod(
    #             start_time="2023/07/31 23:59:59",
    #             end_time="2023/07/01 00:00:00",
    #             time_zone="US/Pacific"
    #         ),
    #         resources=[
    #             AccessPolicyResource(
    #                 databases=["test_db"],
    #                 tables=["test_tbl"],
    #                 columns=["*"]
    #             )
    #         ],
    #         allow_policy_items=[
    #             AccessPolicyItem(
    #                 accesses=[AccessType.SELECT, AccessType.UPDATE],
    #                 users=['{USER}'])
    #         ]
    #     )
    #     with self.assertRaises(ClientError):
    #         self.client.create_access_policy(new_policy)
