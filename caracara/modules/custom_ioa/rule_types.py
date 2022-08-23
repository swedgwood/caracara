from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class RuleType:
    id_: str
    name: str
    long_desc: str
    platform: str
    disposition_map: Dict[int, str]
    fields: List[RuleTypeField]

    def __repr__(self) -> str:
        return (
            f"<RuleType(id_={repr(self.id_)}, name={repr(self.name)}, "
            f"platform={repr(self.platform)}, ...)>"
        )

    @staticmethod
    def from_data_dict(data_dict: dict) -> RuleType:
        disposition_map = {}
        for mapping in data_dict["disposition_map"]:
            disposition_map[mapping["id"]] = mapping["label"]

        fields = []
        for raw_field in data_dict["fields"]:
            fields.append(RuleTypeField.from_data_dict(raw_field))

        rule_type = RuleType(
            id_=data_dict["id"],
            name=data_dict["name"],
            long_desc=data_dict["long_desc"],
            platform=data_dict["platform"],
            disposition_map=disposition_map,
            fields=fields
        )

        return rule_type

    def get_field(
        self, field_name_or_label: str, field_type: Optional[str] = None
    ) -> Optional[RuleTypeField]:
        for field in self.fields:
            if (field_name_or_label in [field.name, field.label]
                    and (field_type is None or field.type == field_type)):
                return field
        return None

    def dump(self, released: bool, channel: int) -> dict:  # TODO consider storing released/channel
        """Dump a dictionary representing this rule conforming to the api.RuleTypeV1 model in the
        CrowdStrike API Swagger doc."""
        dumped = {
            "id": self.id_,
            "name": self.name,
            "long_desc": self.long_desc,
            "platform": self.platform,
            "disposition_map": [
                {"id": k, "label": v} for k, v in self.disposition_map.items()
            ],
            "fields": [field.dump() for field in self.fields],
            "released": released,
            "channel": channel,
        }

        return dumped


@dataclass
class RuleTypeField:
    label: str
    name: str
    type: str
    options: List[RuleTypeFieldOption]

    @staticmethod
    def from_data_dict(data_dict: dict) -> RuleTypeField:
        options = []
        for raw_option in data_dict["options"]:
            options.append(RuleTypeFieldOption.from_data_dict(raw_option))

        field = RuleTypeField(
            label=data_dict["label"],
            name=data_dict["name"],
            type=data_dict["type"],
            options=options,
        )

        return field

    def dump(self):
        """Dump this rule type field, conforming to the real structure of the 'fields' key in
        `api.RuleTypeV1` from the Crowdstrike API Swagger doc (`domain.Field`, but also including a
        `type` and `options`)
        """
        return {
            "label": self.label,
            "name": self.name,
            "type": self.type,
            "options": [option.dump() for option in self.options]
        }

    def to_concrete_field(self):
        field = {
            "label": self.label,
            "name": self.name,
            "type": self.type,
        }

        if self.type == "excludable":
            field["values"] = [{"label": "include", "value": ".*"}]
        elif self.type == "set":
            field["values"] = [option.dump() for option in self.options]
        else:
            raise Exception(f"Unknown rule field type {repr(self.type)}")

        return field


@dataclass
class RuleTypeFieldOption:
    label: str
    value: str

    @staticmethod
    def from_data_dict(data_dict: dict) -> RuleTypeFieldOption:
        return RuleTypeFieldOption(
            label=data_dict["label"],
            value=data_dict["value"],
        )

    def dump(self):
        return {"label": self.label, "value": self.value}
