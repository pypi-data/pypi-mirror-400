from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SrsCls:
	"""Srs commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("srs", core, parent)

	def get_enable(self) -> bool:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:SRS:ENABle \n
		Snippet: value: bool = driver.configure.multiEval.srs.get_enable() \n
		Specifies whether a sounding reference signal is allowed (ON) or not (OFF) . For the combined signal path scenario, use
		CONFigure:LTE:SIGN<i>:CELL[:PCC]:SRS:ENABle. \n
			:return: enable: OFF | ON OFF: No SRS signal is allowed. ON: An SRS signal is allowed in the last SC-FDMA symbol of each subframe.
		"""
		response = self._core.io.query_str('CONFigure:LTE:MEASurement<Instance>:MEValuation:SRS:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:SRS:ENABle \n
		Snippet: driver.configure.multiEval.srs.set_enable(enable = False) \n
		Specifies whether a sounding reference signal is allowed (ON) or not (OFF) . For the combined signal path scenario, use
		CONFigure:LTE:SIGN<i>:CELL[:PCC]:SRS:ENABle. \n
			:param enable: OFF | ON OFF: No SRS signal is allowed. ON: An SRS signal is allowed in the last SC-FDMA symbol of each subframe.
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:SRS:ENABle {param}')
