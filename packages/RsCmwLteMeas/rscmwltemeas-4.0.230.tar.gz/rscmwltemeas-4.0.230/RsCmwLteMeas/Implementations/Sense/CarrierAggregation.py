from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CarrierAggregationCls:
	"""CarrierAggregation commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("carrierAggregation", core, parent)

	def get_fshware(self) -> bool:
		"""SENSe:LTE:MEASurement<Instance>:CAGGregation:FSHWare \n
		Snippet: value: bool = driver.sense.carrierAggregation.get_fshware() \n
		This command is only relevant for combined signal path measurements in multi-CMW setups. It queries whether the
		measurement instance and the carrier to be measured are in the same CMW. If they are in different CMWs, the measurement
		fails. To correct the problem, use another measurement instance or select another carrier, so that both are in the same
		CMW. \n
			:return: value: OFF | ON OFF: Different CMWs - error ON: Same CMW - ok
		"""
		response = self._core.io.query_str('SENSe:LTE:MEASurement<Instance>:CAGGregation:FSHWare?')
		return Conversions.str_to_bool(response)
