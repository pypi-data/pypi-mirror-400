from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CatalogCls:
	"""Catalog commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("catalog", core, parent)

	def get_source(self) -> List[str]:
		"""TRIGger:LTE:MEASurement<Instance>:MEValuation:CATalog:SOURce \n
		Snippet: value: List[str] = driver.trigger.multiEval.catalog.get_source() \n
		Lists all trigger source values that can be set using method RsCmwLteMeas.trigger.multiEval.source. \n
			:return: source_list: string Comma-separated list of all supported values. Each value is represented as a string.
		"""
		response = self._core.io.query_str('TRIGger:LTE:MEASurement<Instance>:MEValuation:CATalog:SOURce?')
		return Conversions.str_to_str_list(response)
