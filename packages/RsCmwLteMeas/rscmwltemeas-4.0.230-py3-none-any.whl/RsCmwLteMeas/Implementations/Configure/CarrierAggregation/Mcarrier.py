from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class McarrierCls:
	"""Mcarrier commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mcarrier", core, parent)

	# noinspection PyTypeChecker
	def get_enhanced(self) -> enums.MeasCarrierEnhanced:
		"""CONFigure:LTE:MEASurement<Instance>:CAGGregation:MCARrier:ENHanced \n
		Snippet: value: enums.MeasCarrierEnhanced = driver.configure.carrierAggregation.mcarrier.get_enhanced() \n
		Selects a component carrier for single carrier measurements. \n
			:return: meas_carrier: CC1 | CC2 | CC3 | CC4
		"""
		response = self._core.io.query_str('CONFigure:LTE:MEASurement<Instance>:CAGGregation:MCARrier:ENHanced?')
		return Conversions.str_to_scalar_enum(response, enums.MeasCarrierEnhanced)

	def set_enhanced(self, meas_carrier: enums.MeasCarrierEnhanced) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:CAGGregation:MCARrier:ENHanced \n
		Snippet: driver.configure.carrierAggregation.mcarrier.set_enhanced(meas_carrier = enums.MeasCarrierEnhanced.CC1) \n
		Selects a component carrier for single carrier measurements. \n
			:param meas_carrier: CC1 | CC2 | CC3 | CC4
		"""
		param = Conversions.enum_scalar_to_str(meas_carrier, enums.MeasCarrierEnhanced)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:CAGGregation:MCARrier:ENHanced {param}')
