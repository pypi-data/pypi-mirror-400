from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.ArgSingleSuppressed import ArgSingleSuppressed
from ...Internal.Types import DataType


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class VfThroughputCls:
	"""VfThroughput commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("vfThroughput", core, parent)

	def fetch(self) -> float:
		"""FETCh:LTE:MEASurement<Instance>:MEValuation:VFTHroughput \n
		Snippet: value: float = driver.multiEval.vfThroughput.fetch() \n
		Queries the 'View Filter Throughput'. \n
		Use RsCmwLteMeas.reliability.last_value to read the updated reliability indicator. \n
			:return: vf_throughput: float Unit: %"""
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_str_suppressed(f'FETCh:LTE:MEASurement<Instance>:MEValuation:VFTHroughput?', suppressed)
		return Conversions.str_to_float(response)
