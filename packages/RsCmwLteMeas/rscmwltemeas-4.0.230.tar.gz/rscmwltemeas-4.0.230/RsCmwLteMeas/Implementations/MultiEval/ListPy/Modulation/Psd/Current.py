from typing import List

from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ......Internal.ArgSingleSuppressed import ArgSingleSuppressed
from ......Internal.Types import DataType


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CurrentCls:
	"""Current commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("current", core, parent)

	def fetch(self) -> List[float]:
		"""FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:MODulation:PSD:CURRent \n
		Snippet: value: List[float] = driver.multiEval.listPy.modulation.psd.current.fetch() \n
		Return RB power values for all measured list mode segments. The values described below are returned by FETCh commands.
		CALCulate commands return limit check results instead, one value for each result listed below. \n
		Use RsCmwLteMeas.reliability.last_value to read the updated reliability indicator. \n
			:return: psd: float Comma-separated list of values, one per measured segment Unit: dBm"""
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_bin_or_ascii_float_list_suppressed(f'FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:MODulation:PSD:CURRent?', suppressed)
		return response

	def calculate(self) -> List[float | bool]:
		"""CALCulate:LTE:MEASurement<Instance>:MEValuation:LIST:MODulation:PSD:CURRent \n
		Snippet: value: List[float | bool] = driver.multiEval.listPy.modulation.psd.current.calculate() \n
		Return RB power values for all measured list mode segments. The values described below are returned by FETCh commands.
		CALCulate commands return limit check results instead, one value for each result listed below. \n
		Use RsCmwLteMeas.reliability.last_value to read the updated reliability indicator. \n
			:return: psd: (float or boolean items) float Comma-separated list of values, one per measured segment Unit: dBm"""
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_str_suppressed(f'CALCulate:LTE:MEASurement<Instance>:MEValuation:LIST:MODulation:PSD:CURRent?', suppressed)
		return Conversions.str_to_float_or_bool_list(response)
