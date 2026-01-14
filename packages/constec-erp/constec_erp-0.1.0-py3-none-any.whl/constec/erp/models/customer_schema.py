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






T = TypeVar("T", bound="CustomerSchema")



@_attrs_define
class CustomerSchema:
    """ Customer response schema.

        Attributes:
            cli_cod (str):
            cli_raz_soc (None | str | Unset):
            cli_nom_fantasia (None | str | Unset):
            cli_direc (None | str | Unset):
            cli_loc (None | str | Unset):
            cli_cod_pos (None | str | Unset):
            cli_tel (None | str | Unset):
            cli_e_mail (None | str | Unset):
            cli_cuit (None | str | Unset):
            cli_habilitado (bool | None | Unset):
            cli_contacto (None | str | Unset):
            cli_fec_mod (datetime.datetime | None | Unset):
     """

    cli_cod: str
    cli_raz_soc: None | str | Unset = UNSET
    cli_nom_fantasia: None | str | Unset = UNSET
    cli_direc: None | str | Unset = UNSET
    cli_loc: None | str | Unset = UNSET
    cli_cod_pos: None | str | Unset = UNSET
    cli_tel: None | str | Unset = UNSET
    cli_e_mail: None | str | Unset = UNSET
    cli_cuit: None | str | Unset = UNSET
    cli_habilitado: bool | None | Unset = UNSET
    cli_contacto: None | str | Unset = UNSET
    cli_fec_mod: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        cli_cod = self.cli_cod

        cli_raz_soc: None | str | Unset
        if isinstance(self.cli_raz_soc, Unset):
            cli_raz_soc = UNSET
        else:
            cli_raz_soc = self.cli_raz_soc

        cli_nom_fantasia: None | str | Unset
        if isinstance(self.cli_nom_fantasia, Unset):
            cli_nom_fantasia = UNSET
        else:
            cli_nom_fantasia = self.cli_nom_fantasia

        cli_direc: None | str | Unset
        if isinstance(self.cli_direc, Unset):
            cli_direc = UNSET
        else:
            cli_direc = self.cli_direc

        cli_loc: None | str | Unset
        if isinstance(self.cli_loc, Unset):
            cli_loc = UNSET
        else:
            cli_loc = self.cli_loc

        cli_cod_pos: None | str | Unset
        if isinstance(self.cli_cod_pos, Unset):
            cli_cod_pos = UNSET
        else:
            cli_cod_pos = self.cli_cod_pos

        cli_tel: None | str | Unset
        if isinstance(self.cli_tel, Unset):
            cli_tel = UNSET
        else:
            cli_tel = self.cli_tel

        cli_e_mail: None | str | Unset
        if isinstance(self.cli_e_mail, Unset):
            cli_e_mail = UNSET
        else:
            cli_e_mail = self.cli_e_mail

        cli_cuit: None | str | Unset
        if isinstance(self.cli_cuit, Unset):
            cli_cuit = UNSET
        else:
            cli_cuit = self.cli_cuit

        cli_habilitado: bool | None | Unset
        if isinstance(self.cli_habilitado, Unset):
            cli_habilitado = UNSET
        else:
            cli_habilitado = self.cli_habilitado

        cli_contacto: None | str | Unset
        if isinstance(self.cli_contacto, Unset):
            cli_contacto = UNSET
        else:
            cli_contacto = self.cli_contacto

        cli_fec_mod: None | str | Unset
        if isinstance(self.cli_fec_mod, Unset):
            cli_fec_mod = UNSET
        elif isinstance(self.cli_fec_mod, datetime.datetime):
            cli_fec_mod = self.cli_fec_mod.isoformat()
        else:
            cli_fec_mod = self.cli_fec_mod


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "cli_Cod": cli_cod,
        })
        if cli_raz_soc is not UNSET:
            field_dict["cli_RazSoc"] = cli_raz_soc
        if cli_nom_fantasia is not UNSET:
            field_dict["cli_NomFantasia"] = cli_nom_fantasia
        if cli_direc is not UNSET:
            field_dict["cli_Direc"] = cli_direc
        if cli_loc is not UNSET:
            field_dict["cli_Loc"] = cli_loc
        if cli_cod_pos is not UNSET:
            field_dict["cli_CodPos"] = cli_cod_pos
        if cli_tel is not UNSET:
            field_dict["cli_Tel"] = cli_tel
        if cli_e_mail is not UNSET:
            field_dict["cli_EMail"] = cli_e_mail
        if cli_cuit is not UNSET:
            field_dict["cli_CUIT"] = cli_cuit
        if cli_habilitado is not UNSET:
            field_dict["cli_Habilitado"] = cli_habilitado
        if cli_contacto is not UNSET:
            field_dict["cli_Contacto"] = cli_contacto
        if cli_fec_mod is not UNSET:
            field_dict["cli_FecMod"] = cli_fec_mod

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cli_cod = d.pop("cli_Cod")

        def _parse_cli_raz_soc(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cli_raz_soc = _parse_cli_raz_soc(d.pop("cli_RazSoc", UNSET))


        def _parse_cli_nom_fantasia(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cli_nom_fantasia = _parse_cli_nom_fantasia(d.pop("cli_NomFantasia", UNSET))


        def _parse_cli_direc(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cli_direc = _parse_cli_direc(d.pop("cli_Direc", UNSET))


        def _parse_cli_loc(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cli_loc = _parse_cli_loc(d.pop("cli_Loc", UNSET))


        def _parse_cli_cod_pos(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cli_cod_pos = _parse_cli_cod_pos(d.pop("cli_CodPos", UNSET))


        def _parse_cli_tel(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cli_tel = _parse_cli_tel(d.pop("cli_Tel", UNSET))


        def _parse_cli_e_mail(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cli_e_mail = _parse_cli_e_mail(d.pop("cli_EMail", UNSET))


        def _parse_cli_cuit(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cli_cuit = _parse_cli_cuit(d.pop("cli_CUIT", UNSET))


        def _parse_cli_habilitado(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        cli_habilitado = _parse_cli_habilitado(d.pop("cli_Habilitado", UNSET))


        def _parse_cli_contacto(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cli_contacto = _parse_cli_contacto(d.pop("cli_Contacto", UNSET))


        def _parse_cli_fec_mod(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                cli_fec_mod_type_0 = isoparse(data)



                return cli_fec_mod_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        cli_fec_mod = _parse_cli_fec_mod(d.pop("cli_FecMod", UNSET))


        customer_schema = cls(
            cli_cod=cli_cod,
            cli_raz_soc=cli_raz_soc,
            cli_nom_fantasia=cli_nom_fantasia,
            cli_direc=cli_direc,
            cli_loc=cli_loc,
            cli_cod_pos=cli_cod_pos,
            cli_tel=cli_tel,
            cli_e_mail=cli_e_mail,
            cli_cuit=cli_cuit,
            cli_habilitado=cli_habilitado,
            cli_contacto=cli_contacto,
            cli_fec_mod=cli_fec_mod,
        )


        customer_schema.additional_properties = d
        return customer_schema

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
