from typing import List

from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.ArgSingleSuppressed import ArgSingleSuppressed
from .....Internal.Types import DataType


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PhaseCls:
	"""Phase commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("phase", core, parent)

	def read(self) -> List[float]:
		"""READ:LTE:MEASurement<Instance>:MEValuation:TRACe:ESFLatness:PHASe \n
		Snippet: value: List[float] = driver.multiEval.trace.esFlatness.phase.read() \n
		Returns the phase values of the equalizer spectrum flatness trace. The GUI shows only the magnitude values. \n
		Use RsCmwLteMeas.reliability.last_value to read the updated reliability indicator. \n
			:return: phase: float Comma-separated list of phase values, one value per subcarrier For not allocated subcarriers, NCAP is returned. Unit: deg"""
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_bin_or_ascii_float_list_suppressed(f'READ:LTE:MEASurement<Instance>:MEValuation:TRACe:ESFLatness:PHASe?', suppressed)
		return response

	def fetch(self) -> List[float]:
		"""FETCh:LTE:MEASurement<Instance>:MEValuation:TRACe:ESFLatness:PHASe \n
		Snippet: value: List[float] = driver.multiEval.trace.esFlatness.phase.fetch() \n
		Returns the phase values of the equalizer spectrum flatness trace. The GUI shows only the magnitude values. \n
		Use RsCmwLteMeas.reliability.last_value to read the updated reliability indicator. \n
			:return: phase: float Comma-separated list of phase values, one value per subcarrier For not allocated subcarriers, NCAP is returned. Unit: deg"""
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_bin_or_ascii_float_list_suppressed(f'FETCh:LTE:MEASurement<Instance>:MEValuation:TRACe:ESFLatness:PHASe?', suppressed)
		return response
