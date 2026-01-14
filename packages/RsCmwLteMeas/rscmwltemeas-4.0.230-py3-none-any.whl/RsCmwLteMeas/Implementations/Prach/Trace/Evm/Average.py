from typing import List

from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.ArgSingleSuppressed import ArgSingleSuppressed
from .....Internal.Types import DataType


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AverageCls:
	"""Average commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("average", core, parent)

	def read(self) -> List[float]:
		"""READ:LTE:MEASurement<Instance>:PRACh:TRACe:EVM:AVERage \n
		Snippet: value: List[float] = driver.prach.trace.evm.average.read() \n
		Return the values of the EVM vs subcarrier traces. Each value is averaged over the samples in one preamble subcarrier.
		The results of the current, average and maximum traces can be retrieved. See also 'View EVM, Magnitude Error, Phase
		Error'. \n
		Use RsCmwLteMeas.reliability.last_value to read the updated reliability indicator. \n
			:return: results: float The number of results depends on the preamble format. Format 0 to 3: 839 EVM values, format 4: 139 EVM values Unit: %"""
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_bin_or_ascii_float_list_suppressed(f'READ:LTE:MEASurement<Instance>:PRACh:TRACe:EVM:AVERage?', suppressed)
		return response

	def fetch(self) -> List[float]:
		"""FETCh:LTE:MEASurement<Instance>:PRACh:TRACe:EVM:AVERage \n
		Snippet: value: List[float] = driver.prach.trace.evm.average.fetch() \n
		Return the values of the EVM vs subcarrier traces. Each value is averaged over the samples in one preamble subcarrier.
		The results of the current, average and maximum traces can be retrieved. See also 'View EVM, Magnitude Error, Phase
		Error'. \n
		Use RsCmwLteMeas.reliability.last_value to read the updated reliability indicator. \n
			:return: results: float The number of results depends on the preamble format. Format 0 to 3: 839 EVM values, format 4: 139 EVM values Unit: %"""
		suppressed = ArgSingleSuppressed(0, DataType.Integer, False, 1, 'Reliability')
		response = self._core.io.query_bin_or_ascii_float_list_suppressed(f'FETCh:LTE:MEASurement<Instance>:PRACh:TRACe:EVM:AVERage?', suppressed)
		return response
