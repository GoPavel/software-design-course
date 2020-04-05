import enum
from typing import Type

import schematics
from schematics.exceptions import ValidationError


class StrEnumType(schematics.types.BaseType):
    def __init__(self, enum_cls: Type[enum.Enum], *args, **kwargs):
        if not issubclass(enum_cls, enum.Enum):
            raise TypeError("Expected enum class")
        if not issubclass(enum_cls, str):
            raise TypeError("Expected string enum class")

        super().__init__(*args, **kwargs)
        self.enum_cls = enum_cls

    def to_primitive(self, value, context=None):
        return value.value

    def to_native(self, value, context=None):
        if isinstance(value, bytes):
            value = value.decode()
        return self.enum_cls(value)


class ConstStringType(schematics.types.StringType):
    def __init__(self, const_str: str, *args, **kwargs):
        super().__init__(*args, **kwargs, default=const_str)
        self.const = const_str

    def validate_const(self, value):
        if value != self.const:
            raise ValidationError(f"value must be equal \"{self.const}\"")
