from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SindexCls:
	"""Sindex commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sindex", core, parent)

	def get_auto(self) -> bool:
		"""CONFigure:LTE:MEASurement<Instance>:PRACh:MODulation:SINDex:AUTO \n
		Snippet: value: bool = driver.configure.prach.modulation.sindex.get_auto() \n
		Enables or disables automatic detection of the sequence index. To configure the index manually for disabled automatic
		detection, see method RsCmwLteMeas.configure.prach.modulation.sindex.value. \n
			:return: seq_index_auto: OFF | ON
		"""
		response = self._core.io.query_str('CONFigure:LTE:MEASurement<Instance>:PRACh:MODulation:SINDex:AUTO?')
		return Conversions.str_to_bool(response)

	def set_auto(self, seq_index_auto: bool) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:PRACh:MODulation:SINDex:AUTO \n
		Snippet: driver.configure.prach.modulation.sindex.set_auto(seq_index_auto = False) \n
		Enables or disables automatic detection of the sequence index. To configure the index manually for disabled automatic
		detection, see method RsCmwLteMeas.configure.prach.modulation.sindex.value. \n
			:param seq_index_auto: OFF | ON
		"""
		param = Conversions.bool_to_str(seq_index_auto)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:PRACh:MODulation:SINDex:AUTO {param}')

	def get_value(self) -> int:
		"""CONFigure:LTE:MEASurement<Instance>:PRACh:MODulation:SINDex \n
		Snippet: value: int = driver.configure.prach.modulation.sindex.get_value() \n
		Specifies the sequence index, i.e. which of the 64 preamble sequences of the cell is used by the UE. This setting is only
		relevant if automatic detection is disabled, see method RsCmwLteMeas.configure.prach.modulation.sindex.auto. \n
			:return: sequence_index: numeric Range: 0 to 63
		"""
		response = self._core.io.query_str('CONFigure:LTE:MEASurement<Instance>:PRACh:MODulation:SINDex?')
		return Conversions.str_to_int(response)

	def set_value(self, sequence_index: int) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:PRACh:MODulation:SINDex \n
		Snippet: driver.configure.prach.modulation.sindex.set_value(sequence_index = 1) \n
		Specifies the sequence index, i.e. which of the 64 preamble sequences of the cell is used by the UE. This setting is only
		relevant if automatic detection is disabled, see method RsCmwLteMeas.configure.prach.modulation.sindex.auto. \n
			:param sequence_index: numeric Range: 0 to 63
		"""
		param = Conversions.decimal_value_to_str(sequence_index)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:PRACh:MODulation:SINDex {param}')
