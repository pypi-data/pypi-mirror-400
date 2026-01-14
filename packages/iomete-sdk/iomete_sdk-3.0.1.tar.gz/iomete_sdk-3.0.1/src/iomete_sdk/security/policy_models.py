from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from dataclasses_json import dataclass_json, LetterCase


class ResourceInclusionType(str, Enum):
    INCLUDE = "INCLUDE"
    EXCLUDE = "EXCLUDE"


class PolicyPriority(str, Enum):
    NORMAL = "NORMAL"
    OVERRIDE = "OVERRIDE"


class AccessType(str, Enum):
    ALL = "ALL"
    SELECT = "SELECT"
    UPDATE = "UPDATE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    READ = "READ"
    WRITE = "WRITE"
    REFRESH = "REFRESH"


class DataMaskType(str, Enum):
    MASK = "MASK"
    MASK_SHOW_LAST_4 = "MASK_SHOW_LAST_4"
    MASK_SHOW_FIRST_4 = "MASK_SHOW_FIRST_4"
    MASK_HASH = "MASK_HASH"
    MASK_NULL = "MASK_NULL"
    MASK_NONE = "MASK_NONE"
    MASK_DATE_SHOW_YEAR = "MASK_DATE_SHOW_YEAR"
    CUSTOM = "CUSTOM"


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ValidityPeriod:
    # format: yyyy/MM/dd HH:mm:ss
    start_time: str = None
    # format: yyyy/MM/dd HH:mm:ss
    end_time: str = None
    # example values: "US/Arizona", "Europe/Berlin", "Asia/Tokyo"
    time_zone: str = "Universal"


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AccessPolicyResource:
    databases: List[str] = None
    databases_inclusion_type: ResourceInclusionType = ResourceInclusionType.INCLUDE
    tables: List[str] = None
    tables_inclusion_type: ResourceInclusionType = ResourceInclusionType.INCLUDE
    columns: List[str] = None
    columns_inclusion_type: ResourceInclusionType = ResourceInclusionType.INCLUDE


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AccessPolicyItem:
    users: Optional[List[str]] = None
    groups: Optional[List[str]] = None
    roles: Optional[List[str]] = None
    accesses: List[AccessType] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AccessPolicyView:
    id: Optional[int] = None
    is_enabled: bool = True

    name: str = ""
    description: Optional[str] = None
    validity_period: Optional[ValidityPeriod] = None
    priority: PolicyPriority = PolicyPriority.NORMAL

    resources: List[AccessPolicyResource] = None
    allow_policy_items: Optional[List[AccessPolicyItem]] = None
    allow_exceptions: Optional[List[AccessPolicyItem]] = None
    deny_policy_items: Optional[List[AccessPolicyItem]] = None
    deny_exceptions: Optional[List[AccessPolicyItem]] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataMaskPolicyResource:
    database: str = None
    table: str = None
    column: str = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataMaskPolicyItem:
    data_mask_type: str = None,
    data_mask_custom_expr: Optional[str] = None
    users: Optional[List[str]] = None
    groups: Optional[List[str]] = None
    roles: Optional[List[str]] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataMaskPolicyView:
    id: Optional[int] = None
    is_enabled: bool = True

    name: str = ""
    description: Optional[str] = None
    validity_period: Optional[ValidityPeriod] = None
    priority: PolicyPriority = PolicyPriority.NORMAL

    resources: List[DataMaskPolicyResource] = None
    data_mask_policy_items: List[DataMaskPolicyItem] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RowFilterPolicyItem:
    filter_expr: str = None
    users: Optional[List[str]] = None
    groups: Optional[List[str]] = None
    roles: Optional[List[str]] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RowFilterPolicyResource:
    database: str = None
    table: str = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RowFilterPolicyView:
    id: Optional[int] = None
    is_enabled: bool = True

    name: str = ""
    description: Optional[str] = None
    validity_period: Optional[ValidityPeriod] = None
    priority: PolicyPriority = PolicyPriority.NORMAL

    resources: List[RowFilterPolicyResource] = None
    row_filter_policy_items: List[RowFilterPolicyItem] = None
