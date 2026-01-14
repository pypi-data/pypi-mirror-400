from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PfOffsetCls:
	"""PfOffset commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pfOffset", core, parent)

	def get_auto(self) -> bool:
		"""CONFigure:LTE:MEASurement<Instance>:PRACh:PFOFfset:AUTO \n
		Snippet: value: bool = driver.configure.prach.pfOffset.get_auto() \n
		Enables or disables automatic detection of the PRACH frequency offset. To configure the offset manually for disabled
		automatic detection, see method RsCmwLteMeas.configure.prach.pfOffset.value. \n
			:return: prach_freq_auto: OFF | ON
		"""
		response = self._core.io.query_str('CONFigure:LTE:MEASurement<Instance>:PRACh:PFOFfset:AUTO?')
		return Conversions.str_to_bool(response)

	def set_auto(self, prach_freq_auto: bool) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:PRACh:PFOFfset:AUTO \n
		Snippet: driver.configure.prach.pfOffset.set_auto(prach_freq_auto = False) \n
		Enables or disables automatic detection of the PRACH frequency offset. To configure the offset manually for disabled
		automatic detection, see method RsCmwLteMeas.configure.prach.pfOffset.value. \n
			:param prach_freq_auto: OFF | ON
		"""
		param = Conversions.bool_to_str(prach_freq_auto)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:PRACh:PFOFfset:AUTO {param}')

	def get_value(self) -> int:
		"""CONFigure:LTE:MEASurement<Instance>:PRACh:PFOFfset \n
		Snippet: value: int = driver.configure.prach.pfOffset.get_value() \n
		Specifies the PRACH frequency offset. This setting is only relevant if automatic detection is disabled, see method
		RsCmwLteMeas.configure.prach.pfOffset.auto.
		For the combined signal path scenario, use CONFigure:LTE:SIGN<i>:CELL:PRACh:PFOFfset. \n
			:return: prach_freq_offset: numeric Range: 0 to Total RB - 6 depending on channel bandwidth, see table below
		"""
		response = self._core.io.query_str('CONFigure:LTE:MEASurement<Instance>:PRACh:PFOFfset?')
		return Conversions.str_to_int(response)

	def set_value(self, prach_freq_offset: int) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:PRACh:PFOFfset \n
		Snippet: driver.configure.prach.pfOffset.set_value(prach_freq_offset = 1) \n
		Specifies the PRACH frequency offset. This setting is only relevant if automatic detection is disabled, see method
		RsCmwLteMeas.configure.prach.pfOffset.auto.
		For the combined signal path scenario, use CONFigure:LTE:SIGN<i>:CELL:PRACh:PFOFfset. \n
			:param prach_freq_offset: numeric Range: 0 to Total RB - 6 depending on channel bandwidth, see table below
		"""
		param = Conversions.decimal_value_to_str(prach_freq_offset)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:PRACh:PFOFfset {param}')
