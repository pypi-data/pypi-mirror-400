from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.test_suite import TestSuite





T = TypeVar("T", bound="ListTestSuiteRevisionsOutput")



@_attrs_define
class ListTestSuiteRevisionsOutput:
    """ 
        Attributes:
            test_suites (list[TestSuite] | Unset):
            next_page_token (str | Unset):
     """

    test_suites: list[TestSuite] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.test_suite import TestSuite
        test_suites: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.test_suites, Unset):
            test_suites = []
            for test_suites_item_data in self.test_suites:
                test_suites_item = test_suites_item_data.to_dict()
                test_suites.append(test_suites_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if test_suites is not UNSET:
            field_dict["testSuites"] = test_suites
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.test_suite import TestSuite
        d = dict(src_dict)
        test_suites = []
        _test_suites = d.pop("testSuites", UNSET)
        for test_suites_item_data in (_test_suites or []):
            test_suites_item = TestSuite.from_dict(test_suites_item_data)



            test_suites.append(test_suites_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_test_suite_revisions_output = cls(
            test_suites=test_suites,
            next_page_token=next_page_token,
        )


        list_test_suite_revisions_output.additional_properties = d
        return list_test_suite_revisions_output

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
