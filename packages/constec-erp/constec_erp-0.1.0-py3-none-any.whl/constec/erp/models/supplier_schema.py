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






T = TypeVar("T", bound="SupplierSchema")



@_attrs_define
class SupplierSchema:
    """ Supplier response schema.

        Attributes:
            pro_cod (str):
            pro_raz_soc (None | str | Unset):
            pro_contacto (None | str | Unset):
            pro_direc (None | str | Unset):
            pro_loc (None | str | Unset):
            pro_cod_pos (None | str | Unset):
            pro_tel (None | str | Unset):
            pro_e_mail (None | str | Unset):
            pro_cuit (None | str | Unset):
            pro_habilitado (bool | None | Unset):
            pro_fec_mod (datetime.datetime | None | Unset):
     """

    pro_cod: str
    pro_raz_soc: None | str | Unset = UNSET
    pro_contacto: None | str | Unset = UNSET
    pro_direc: None | str | Unset = UNSET
    pro_loc: None | str | Unset = UNSET
    pro_cod_pos: None | str | Unset = UNSET
    pro_tel: None | str | Unset = UNSET
    pro_e_mail: None | str | Unset = UNSET
    pro_cuit: None | str | Unset = UNSET
    pro_habilitado: bool | None | Unset = UNSET
    pro_fec_mod: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        pro_cod = self.pro_cod

        pro_raz_soc: None | str | Unset
        if isinstance(self.pro_raz_soc, Unset):
            pro_raz_soc = UNSET
        else:
            pro_raz_soc = self.pro_raz_soc

        pro_contacto: None | str | Unset
        if isinstance(self.pro_contacto, Unset):
            pro_contacto = UNSET
        else:
            pro_contacto = self.pro_contacto

        pro_direc: None | str | Unset
        if isinstance(self.pro_direc, Unset):
            pro_direc = UNSET
        else:
            pro_direc = self.pro_direc

        pro_loc: None | str | Unset
        if isinstance(self.pro_loc, Unset):
            pro_loc = UNSET
        else:
            pro_loc = self.pro_loc

        pro_cod_pos: None | str | Unset
        if isinstance(self.pro_cod_pos, Unset):
            pro_cod_pos = UNSET
        else:
            pro_cod_pos = self.pro_cod_pos

        pro_tel: None | str | Unset
        if isinstance(self.pro_tel, Unset):
            pro_tel = UNSET
        else:
            pro_tel = self.pro_tel

        pro_e_mail: None | str | Unset
        if isinstance(self.pro_e_mail, Unset):
            pro_e_mail = UNSET
        else:
            pro_e_mail = self.pro_e_mail

        pro_cuit: None | str | Unset
        if isinstance(self.pro_cuit, Unset):
            pro_cuit = UNSET
        else:
            pro_cuit = self.pro_cuit

        pro_habilitado: bool | None | Unset
        if isinstance(self.pro_habilitado, Unset):
            pro_habilitado = UNSET
        else:
            pro_habilitado = self.pro_habilitado

        pro_fec_mod: None | str | Unset
        if isinstance(self.pro_fec_mod, Unset):
            pro_fec_mod = UNSET
        elif isinstance(self.pro_fec_mod, datetime.datetime):
            pro_fec_mod = self.pro_fec_mod.isoformat()
        else:
            pro_fec_mod = self.pro_fec_mod


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "pro_Cod": pro_cod,
        })
        if pro_raz_soc is not UNSET:
            field_dict["pro_RazSoc"] = pro_raz_soc
        if pro_contacto is not UNSET:
            field_dict["pro_Contacto"] = pro_contacto
        if pro_direc is not UNSET:
            field_dict["pro_Direc"] = pro_direc
        if pro_loc is not UNSET:
            field_dict["pro_Loc"] = pro_loc
        if pro_cod_pos is not UNSET:
            field_dict["pro_CodPos"] = pro_cod_pos
        if pro_tel is not UNSET:
            field_dict["pro_Tel"] = pro_tel
        if pro_e_mail is not UNSET:
            field_dict["pro_EMail"] = pro_e_mail
        if pro_cuit is not UNSET:
            field_dict["pro_CUIT"] = pro_cuit
        if pro_habilitado is not UNSET:
            field_dict["pro_Habilitado"] = pro_habilitado
        if pro_fec_mod is not UNSET:
            field_dict["pro_FecMod"] = pro_fec_mod

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pro_cod = d.pop("pro_Cod")

        def _parse_pro_raz_soc(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pro_raz_soc = _parse_pro_raz_soc(d.pop("pro_RazSoc", UNSET))


        def _parse_pro_contacto(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pro_contacto = _parse_pro_contacto(d.pop("pro_Contacto", UNSET))


        def _parse_pro_direc(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pro_direc = _parse_pro_direc(d.pop("pro_Direc", UNSET))


        def _parse_pro_loc(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pro_loc = _parse_pro_loc(d.pop("pro_Loc", UNSET))


        def _parse_pro_cod_pos(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pro_cod_pos = _parse_pro_cod_pos(d.pop("pro_CodPos", UNSET))


        def _parse_pro_tel(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pro_tel = _parse_pro_tel(d.pop("pro_Tel", UNSET))


        def _parse_pro_e_mail(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pro_e_mail = _parse_pro_e_mail(d.pop("pro_EMail", UNSET))


        def _parse_pro_cuit(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pro_cuit = _parse_pro_cuit(d.pop("pro_CUIT", UNSET))


        def _parse_pro_habilitado(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        pro_habilitado = _parse_pro_habilitado(d.pop("pro_Habilitado", UNSET))


        def _parse_pro_fec_mod(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                pro_fec_mod_type_0 = isoparse(data)



                return pro_fec_mod_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        pro_fec_mod = _parse_pro_fec_mod(d.pop("pro_FecMod", UNSET))


        supplier_schema = cls(
            pro_cod=pro_cod,
            pro_raz_soc=pro_raz_soc,
            pro_contacto=pro_contacto,
            pro_direc=pro_direc,
            pro_loc=pro_loc,
            pro_cod_pos=pro_cod_pos,
            pro_tel=pro_tel,
            pro_e_mail=pro_e_mail,
            pro_cuit=pro_cuit,
            pro_habilitado=pro_habilitado,
            pro_fec_mod=pro_fec_mod,
        )


        supplier_schema.additional_properties = d
        return supplier_schema

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
