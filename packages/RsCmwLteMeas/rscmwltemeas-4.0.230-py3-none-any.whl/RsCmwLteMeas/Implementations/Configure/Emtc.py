from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EmtcCls:
	"""Emtc commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("emtc", core, parent)

	def get_enable(self) -> bool:
		"""CONFigure:LTE:MEASurement<Instance>:EMTC:ENABle \n
		Snippet: value: bool = driver.configure.emtc.get_enable() \n
		Enables or disables eMTC. For the combined signal path scenario, use CONFigure:LTE:SIGN<i>[:PCC]:EMTC:ENABle. \n
			:return: enable: OFF | ON
		"""
		response = self._core.io.query_str('CONFigure:LTE:MEASurement<Instance>:EMTC:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:EMTC:ENABle \n
		Snippet: driver.configure.emtc.set_enable(enable = False) \n
		Enables or disables eMTC. For the combined signal path scenario, use CONFigure:LTE:SIGN<i>[:PCC]:EMTC:ENABle. \n
			:param enable: OFF | ON
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:EMTC:ENABle {param}')

	def get_mb(self) -> bool:
		"""CONFigure:LTE:MEASurement<instance>:EMTC:MB<number> \n
		Snippet: value: bool = driver.configure.emtc.get_mb() \n
		Selects the maximum eMTC bandwidth.
		For the combined signal path scenario, use CONFigure:LTE:SIGN<i>[:PCC]:EMTC:MB<number>. \n
			:return: enable: OFF | ON OFF: Max bandwidth 1.4 MHz ON: Max bandwidth 5 MHz
		"""
		response = self._core.io.query_str('CONFigure:LTE:MEASurement<Instance>:EMTC:MB5?')
		return Conversions.str_to_bool(response)

	def set_mb(self, enable: bool) -> None:
		"""CONFigure:LTE:MEASurement<instance>:EMTC:MB<number> \n
		Snippet: driver.configure.emtc.set_mb(enable = False) \n
		Selects the maximum eMTC bandwidth.
		For the combined signal path scenario, use CONFigure:LTE:SIGN<i>[:PCC]:EMTC:MB<number>. \n
			:param enable: OFF | ON OFF: Max bandwidth 1.4 MHz ON: Max bandwidth 5 MHz
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:EMTC:MB5 {param}')

	def get_nband(self) -> int:
		"""CONFigure:LTE:MEASurement<Instance>:EMTC:NBANd \n
		Snippet: value: int = driver.configure.emtc.get_nband() \n
		Selects the narrowband used for eMTC. \n
			:return: number: numeric The maximum depends on the channel BW, see 'RB allocation, narrowbands and widebands for eMTC'. Range: 0 to 15
		"""
		response = self._core.io.query_str('CONFigure:LTE:MEASurement<Instance>:EMTC:NBANd?')
		return Conversions.str_to_int(response)

	def set_nband(self, number: int) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:EMTC:NBANd \n
		Snippet: driver.configure.emtc.set_nband(number = 1) \n
		Selects the narrowband used for eMTC. \n
			:param number: numeric The maximum depends on the channel BW, see 'RB allocation, narrowbands and widebands for eMTC'. Range: 0 to 15
		"""
		param = Conversions.decimal_value_to_str(number)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:EMTC:NBANd {param}')
