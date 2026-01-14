from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="SellerSchema")



@_attrs_define
class SellerSchema:
    """ Seller response schema.

        Attributes:
            ven_cod (str):
            ven_desc (None | str | Unset):
            ven_direc (None | str | Unset):
            ven_loc (None | str | Unset):
            ven_tel (None | str | Unset):
            ven_email (None | str | Unset):
            ven_activo (bool | None | Unset):
            ven_fec_mod (datetime.datetime | None | Unset):
     """

    ven_cod: str
    ven_desc: None | str | Unset = UNSET
    ven_direc: None | str | Unset = UNSET
    ven_loc: None | str | Unset = UNSET
    ven_tel: None | str | Unset = UNSET
    ven_email: None | str | Unset = UNSET
    ven_activo: bool | None | Unset = UNSET
    ven_fec_mod: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        ven_cod = self.ven_cod

        ven_desc: None | str | Unset
        if isinstance(self.ven_desc, Unset):
            ven_desc = UNSET
        else:
            ven_desc = self.ven_desc

        ven_direc: None | str | Unset
        if isinstance(self.ven_direc, Unset):
            ven_direc = UNSET
        else:
            ven_direc = self.ven_direc

        ven_loc: None | str | Unset
        if isinstance(self.ven_loc, Unset):
            ven_loc = UNSET
        else:
            ven_loc = self.ven_loc

        ven_tel: None | str | Unset
        if isinstance(self.ven_tel, Unset):
            ven_tel = UNSET
        else:
            ven_tel = self.ven_tel

        ven_email: None | str | Unset
        if isinstance(self.ven_email, Unset):
            ven_email = UNSET
        else:
            ven_email = self.ven_email

        ven_activo: bool | None | Unset
        if isinstance(self.ven_activo, Unset):
            ven_activo = UNSET
        else:
            ven_activo = self.ven_activo

        ven_fec_mod: None | str | Unset
        if isinstance(self.ven_fec_mod, Unset):
            ven_fec_mod = UNSET
        elif isinstance(self.ven_fec_mod, datetime.datetime):
            ven_fec_mod = self.ven_fec_mod.isoformat()
        else:
            ven_fec_mod = self.ven_fec_mod


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "ven_Cod": ven_cod,
        })
        if ven_desc is not UNSET:
            field_dict["ven_Desc"] = ven_desc
        if ven_direc is not UNSET:
            field_dict["ven_Direc"] = ven_direc
        if ven_loc is not UNSET:
            field_dict["ven_Loc"] = ven_loc
        if ven_tel is not UNSET:
            field_dict["ven_Tel"] = ven_tel
        if ven_email is not UNSET:
            field_dict["ven_email"] = ven_email
        if ven_activo is not UNSET:
            field_dict["ven_Activo"] = ven_activo
        if ven_fec_mod is not UNSET:
            field_dict["ven_FecMod"] = ven_fec_mod

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ven_cod = d.pop("ven_Cod")

        def _parse_ven_desc(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ven_desc = _parse_ven_desc(d.pop("ven_Desc", UNSET))


        def _parse_ven_direc(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ven_direc = _parse_ven_direc(d.pop("ven_Direc", UNSET))


        def _parse_ven_loc(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ven_loc = _parse_ven_loc(d.pop("ven_Loc", UNSET))


        def _parse_ven_tel(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ven_tel = _parse_ven_tel(d.pop("ven_Tel", UNSET))


        def _parse_ven_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ven_email = _parse_ven_email(d.pop("ven_email", UNSET))


        def _parse_ven_activo(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        ven_activo = _parse_ven_activo(d.pop("ven_Activo", UNSET))


        def _parse_ven_fec_mod(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                ven_fec_mod_type_0 = isoparse(data)



                return ven_fec_mod_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        ven_fec_mod = _parse_ven_fec_mod(d.pop("ven_FecMod", UNSET))


        seller_schema = cls(
            ven_cod=ven_cod,
            ven_desc=ven_desc,
            ven_direc=ven_direc,
            ven_loc=ven_loc,
            ven_tel=ven_tel,
            ven_email=ven_email,
            ven_activo=ven_activo,
            ven_fec_mod=ven_fec_mod,
        )


        seller_schema.additional_properties = d
        return seller_schema

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
