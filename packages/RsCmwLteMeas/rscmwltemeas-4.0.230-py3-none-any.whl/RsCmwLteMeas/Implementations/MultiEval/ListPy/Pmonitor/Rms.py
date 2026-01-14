from typing import List

from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.ArgSingleSuppressed import ArgSingleSuppressed
from .....Internal.Types import DataType


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RmsCls:
	"""Rms commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rms", core, parent)

	def fetch(self) -> List[float]:
		"""FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:PMONitor:RMS \n
		Snippet: value: List[float] = driver.multiEval.listPy.pmonitor.rms.fetch() \n
		Return the power monitor results for all measured segments in list mode. The commands return one power result per
		subframe for the measured carrier. The power values are RMS averaged over the subframe or represent the peak value within
		the subframe.
			INTRO_CMD_HELP: Commands for querying the result list structure: \n
			- method RsCmwLteMeas.multiEval.listPy.segment.pmonitor.array.start.fetch
			- method RsCmwLteMeas.multiEval.listPy.segment.pmonitor.array.length.fetch \n
		Use RsCmwLteMeas.reliability.last_value to read the updated reliability indicator. \n
			:return: step_rms_power: float Comma-separated list of power values, one value per subframe, from first subframe of first measured segment to last subframe of last measured segment For an inactive segment only one INV is returned, independent of the number of configured subframes. Unit: dBm"""
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_bin_or_ascii_float_list_suppressed(f'FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:PMONitor:RMS?', suppressed)
		return response
