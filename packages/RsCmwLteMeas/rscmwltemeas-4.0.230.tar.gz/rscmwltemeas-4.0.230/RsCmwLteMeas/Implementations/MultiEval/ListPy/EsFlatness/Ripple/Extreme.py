from typing import List

from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ......Internal.ArgSingleSuppressed import ArgSingleSuppressed
from ......Internal.Types import DataType
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ExtremeCls:
	"""Extreme commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("extreme", core, parent)

	def fetch(self, ripple=repcap.Ripple.Default) -> List[float]:
		"""FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:ESFLatness:RIPPle<nr>:EXTReme \n
		Snippet: value: List[float] = driver.multiEval.listPy.esFlatness.ripple.extreme.fetch(ripple = repcap.Ripple.Default) \n
		Return equalizer spectrum flatness single value results (ripple 1 or ripple 2) for all measured list mode segments. The
		values described below are returned by FETCh commands. CALCulate commands return limit check results instead, one value
		for each result listed below. \n
		Use RsCmwLteMeas.reliability.last_value to read the updated reliability indicator. \n
			:param ripple: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Ripple')
			:return: ripple: float Comma-separated list of values, one per measured segment Unit: dB"""
		ripple_cmd_val = self._cmd_group.get_repcap_cmd_value(ripple, repcap.Ripple)
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_bin_or_ascii_float_list_suppressed(f'FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:ESFLatness:RIPPle{ripple_cmd_val}:EXTReme?', suppressed)
		return response

	def calculate(self, ripple=repcap.Ripple.Default) -> List[float | bool]:
		"""CALCulate:LTE:MEASurement<Instance>:MEValuation:LIST:ESFLatness:RIPPle<nr>:EXTReme \n
		Snippet: value: List[float | bool] = driver.multiEval.listPy.esFlatness.ripple.extreme.calculate(ripple = repcap.Ripple.Default) \n
		Return equalizer spectrum flatness single value results (ripple 1 or ripple 2) for all measured list mode segments. The
		values described below are returned by FETCh commands. CALCulate commands return limit check results instead, one value
		for each result listed below. \n
		Use RsCmwLteMeas.reliability.last_value to read the updated reliability indicator. \n
			:param ripple: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Ripple')
			:return: ripple: (float or boolean items) float Comma-separated list of values, one per measured segment Unit: dB"""
		ripple_cmd_val = self._cmd_group.get_repcap_cmd_value(ripple, repcap.Ripple)
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_str_suppressed(f'CALCulate:LTE:MEASurement<Instance>:MEValuation:LIST:ESFLatness:RIPPle{ripple_cmd_val}:EXTReme?', suppressed)
		return Conversions.str_to_float_or_bool_list(response)
