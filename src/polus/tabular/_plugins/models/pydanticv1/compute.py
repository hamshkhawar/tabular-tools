"""Extending automatically generated compute model.

This file modifies and extend certain fields and
functions of PolusComputeSchema.py which is automatically
generated by datamodel-codegen from JSON schema.
"""

from polus.tabular._plugins.io import IOBase
from polus.tabular._plugins.io import Version
from polus.tabular._plugins.models.pydanticv1.PolusComputeSchema import PluginInput
from polus.tabular._plugins.models.pydanticv1.PolusComputeSchema import PluginOutput
from polus.tabular._plugins.models.pydanticv1.PolusComputeSchema import PluginSchema


class PluginInput(PluginInput, IOBase):  # type: ignore
    """Base Class for Input Args."""


class PluginOutput(PluginOutput, IOBase):  # type: ignore
    """Base Class for Output Args."""


class PluginSchema(PluginSchema):  # type: ignore
    """Extended Compute Plugin Schema with extended IO defs."""

    inputs: list[PluginInput]
    outputs: list[PluginOutput]
    version: Version
