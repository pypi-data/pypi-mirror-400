from typing import List

from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ......Internal.ArgSingleSuppressed import ArgSingleSuppressed
from ......Internal.Types import DataType


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MaximumCls:
	"""Maximum commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("maximum", core, parent)

	def fetch(self) -> List[float]:
		"""FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:POWer:TXPower:MAXimum \n
		Snippet: value: List[float] = driver.multiEval.listPy.power.txPower.maximum.fetch() \n
		Return the total TX power of all component carriers, for all measured list mode segments. \n
		Use RsCmwLteMeas.reliability.last_value to read the updated reliability indicator. \n
			:return: tx_power: float Comma-separated list of values, one per measured segment Unit: dBm"""
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_bin_or_ascii_float_list_suppressed(f'FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:POWer:TXPower:MAXimum?', suppressed)
		return response

	def calculate(self) -> List[float | bool]:
		"""CALCulate:LTE:MEASurement<Instance>:MEValuation:LIST:POWer:TXPower:MAXimum \n
		Snippet: value: List[float | bool] = driver.multiEval.listPy.power.txPower.maximum.calculate() \n
		No command help available \n
		Use RsCmwLteMeas.reliability.last_value to read the updated reliability indicator. \n
			:return: tx_power: (float or boolean items) No help available"""
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_str_suppressed(f'CALCulate:LTE:MEASurement<Instance>:MEValuation:LIST:POWer:TXPower:MAXimum?', suppressed)
		return Conversions.str_to_float_or_bool_list(response)
