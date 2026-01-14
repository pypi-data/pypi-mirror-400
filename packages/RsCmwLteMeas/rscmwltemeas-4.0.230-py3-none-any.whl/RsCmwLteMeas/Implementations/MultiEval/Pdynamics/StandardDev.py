from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.StructBase import StructBase
from ....Internal.ArgStruct import ArgStruct


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StandardDevCls:
	"""StandardDev commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("standardDev", core, parent)

	# noinspection PyTypeChecker
	class ResultData(StructBase):
		"""Response structure. Fields: \n
			- 1 Reliability: int: decimal 'Reliability indicator'
			- 2 Out_Of_Tolerance: int: decimal Out of tolerance result, i.e. the percentage of measurement intervals of the statistic count for power measurements exceeding the specified power limits. Unit: %
			- 3 Off_Power_Before: float: No parameter help available
			- 4 On_Power_Rms: float: No parameter help available
			- 5 On_Power_Peak: float: No parameter help available
			- 6 Off_Power_After: float: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_int('Reliability', 'Reliability'),
			ArgStruct.scalar_int('Out_Of_Tolerance'),
			ArgStruct.scalar_float('Off_Power_Before'),
			ArgStruct.scalar_float('On_Power_Rms'),
			ArgStruct.scalar_float('On_Power_Peak'),
			ArgStruct.scalar_float('Off_Power_After')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Reliability: int = None
			self.Out_Of_Tolerance: int = None
			self.Off_Power_Before: float = None
			self.On_Power_Rms: float = None
			self.On_Power_Peak: float = None
			self.Off_Power_After: float = None

	def read(self) -> ResultData:
		"""READ:LTE:MEASurement<Instance>:MEValuation:PDYNamics:SDEViation \n
		Snippet: value: ResultData = driver.multiEval.pdynamics.standardDev.read() \n
		Return the current, average, minimum, maximum and standard deviation single-value results of the power dynamics
		measurement. A single result table row is returned, from left to right. The meaning of the values depends on the selected
		time mask, as follows:
			Table Header: Time mask / <Power1> / <Power2> / <Power3> / <Power4> \n
			- General on / off / OFF power (before) / ON power RMS / ON power peak / OFF power (after)
			- PUCCH / PUSCH / SRS / SRS ON / ON power RMS / ON power peak / ON power (after)
			- SRS blanking / SRS OFF / ON power RMS / ON power peak / ON power (after)
		The values described below are returned by FETCh and READ commands. CALCulate commands return limit check results instead,
		one value for each result listed below. \n
			:return: structure: for return value, see the help for ResultData structure arguments."""
		return self._core.io.query_struct(f'READ:LTE:MEASurement<Instance>:MEValuation:PDYNamics:SDEViation?', self.__class__.ResultData())

	def fetch(self) -> ResultData:
		"""FETCh:LTE:MEASurement<Instance>:MEValuation:PDYNamics:SDEViation \n
		Snippet: value: ResultData = driver.multiEval.pdynamics.standardDev.fetch() \n
		Return the current, average, minimum, maximum and standard deviation single-value results of the power dynamics
		measurement. A single result table row is returned, from left to right. The meaning of the values depends on the selected
		time mask, as follows:
			Table Header: Time mask / <Power1> / <Power2> / <Power3> / <Power4> \n
			- General on / off / OFF power (before) / ON power RMS / ON power peak / OFF power (after)
			- PUCCH / PUSCH / SRS / SRS ON / ON power RMS / ON power peak / ON power (after)
			- SRS blanking / SRS OFF / ON power RMS / ON power peak / ON power (after)
		The values described below are returned by FETCh and READ commands. CALCulate commands return limit check results instead,
		one value for each result listed below. \n
			:return: structure: for return value, see the help for ResultData structure arguments."""
		return self._core.io.query_struct(f'FETCh:LTE:MEASurement<Instance>:MEValuation:PDYNamics:SDEViation?', self.__class__.ResultData())
