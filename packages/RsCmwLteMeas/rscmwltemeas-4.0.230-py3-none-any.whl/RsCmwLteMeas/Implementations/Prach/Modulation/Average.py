from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.StructBase import StructBase
from ....Internal.ArgStruct import ArgStruct


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AverageCls:
	"""Average commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("average", core, parent)

	# noinspection PyTypeChecker
	class ResultData(StructBase):
		"""Response structure. Fields: \n
			- 1 Reliability: int: decimal 'Reliability indicator'
			- 2 Out_Of_Tolerance: int: decimal Out of tolerance result, i.e. the percentage of measurement intervals of the statistic count for modulation measurements exceeding the specified modulation limits. Unit: %
			- 3 Evm_Rms_Low: float: float EVM RMS value, low EVM window position. Unit: %
			- 4 Evm_Rms_High: float: float EVM RMS value, high EVM window position. Unit: %
			- 5 Evm_Peak_Low: float: float EVM peak value, low EVM window position. Unit: %
			- 6 Evm_Peak_High: float: float EVM peak value, high EVM window position. Unit: %
			- 7 Mag_Error_Rms_Low: float: float Magnitude error RMS value, low EVM window position. Unit: %
			- 8 Mag_Error_Rms_High: float: float Magnitude error RMS value, low EVM window position. Unit: %
			- 9 Mag_Error_Peak_Low: float: float Magnitude error peak value, low EVM window position. Unit: %
			- 10 Mag_Err_Peak_High: float: float Magnitude error peak value, high EVM window position. Unit: %
			- 11 Ph_Error_Rms_Low: float: float Phase error RMS value, low EVM window position. Unit: deg
			- 12 Ph_Error_Rms_High: float: float Phase error RMS value, high EVM window position. Unit: deg
			- 13 Ph_Error_Peak_Low: float: float Phase error peak value, low EVM window position. Unit: deg
			- 14 Ph_Error_Peak_High: float: float Phase error peak value, high EVM window position. Unit: deg
			- 15 Frequency_Error: float: float Carrier frequency error. Unit: Hz
			- 16 Timing_Error: float: float Transmit time error. Unit: Ts (basic LTE time unit)
			- 17 Tx_Power: float: float UE RMS power. Unit: dBm
			- 18 Peak_Power: float: float UE peak power. Unit: dBm"""
		__meta_args_list = [
			ArgStruct.scalar_int('Reliability', 'Reliability'),
			ArgStruct.scalar_int('Out_Of_Tolerance'),
			ArgStruct.scalar_float('Evm_Rms_Low'),
			ArgStruct.scalar_float('Evm_Rms_High'),
			ArgStruct.scalar_float('Evm_Peak_Low'),
			ArgStruct.scalar_float('Evm_Peak_High'),
			ArgStruct.scalar_float('Mag_Error_Rms_Low'),
			ArgStruct.scalar_float('Mag_Error_Rms_High'),
			ArgStruct.scalar_float('Mag_Error_Peak_Low'),
			ArgStruct.scalar_float('Mag_Err_Peak_High'),
			ArgStruct.scalar_float('Ph_Error_Rms_Low'),
			ArgStruct.scalar_float('Ph_Error_Rms_High'),
			ArgStruct.scalar_float('Ph_Error_Peak_Low'),
			ArgStruct.scalar_float('Ph_Error_Peak_High'),
			ArgStruct.scalar_float('Frequency_Error'),
			ArgStruct.scalar_float('Timing_Error'),
			ArgStruct.scalar_float('Tx_Power'),
			ArgStruct.scalar_float('Peak_Power')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Reliability: int = None
			self.Out_Of_Tolerance: int = None
			self.Evm_Rms_Low: float = None
			self.Evm_Rms_High: float = None
			self.Evm_Peak_Low: float = None
			self.Evm_Peak_High: float = None
			self.Mag_Error_Rms_Low: float = None
			self.Mag_Error_Rms_High: float = None
			self.Mag_Error_Peak_Low: float = None
			self.Mag_Err_Peak_High: float = None
			self.Ph_Error_Rms_Low: float = None
			self.Ph_Error_Rms_High: float = None
			self.Ph_Error_Peak_Low: float = None
			self.Ph_Error_Peak_High: float = None
			self.Frequency_Error: float = None
			self.Timing_Error: float = None
			self.Tx_Power: float = None
			self.Peak_Power: float = None

	def read(self) -> ResultData:
		"""READ:LTE:MEASurement<Instance>:PRACh:MODulation:AVERage \n
		Snippet: value: ResultData = driver.prach.modulation.average.read() \n
		Return the current, average and standard deviation single-value results. The values described below are returned by FETCh
		and READ commands. CALCulate commands return limit check results instead, one value for each result listed below. \n
			:return: structure: for return value, see the help for ResultData structure arguments."""
		return self._core.io.query_struct(f'READ:LTE:MEASurement<Instance>:PRACh:MODulation:AVERage?', self.__class__.ResultData())

	def fetch(self) -> ResultData:
		"""FETCh:LTE:MEASurement<Instance>:PRACh:MODulation:AVERage \n
		Snippet: value: ResultData = driver.prach.modulation.average.fetch() \n
		Return the current, average and standard deviation single-value results. The values described below are returned by FETCh
		and READ commands. CALCulate commands return limit check results instead, one value for each result listed below. \n
			:return: structure: for return value, see the help for ResultData structure arguments."""
		return self._core.io.query_struct(f'FETCh:LTE:MEASurement<Instance>:PRACh:MODulation:AVERage?', self.__class__.ResultData())

	# noinspection PyTypeChecker
	class CalculateStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Reliability: int: decimal 'Reliability indicator'
			- 2 Out_Of_Tolerance: int: decimal Out of tolerance result, i.e. the percentage of measurement intervals of the statistic count for modulation measurements exceeding the specified modulation limits. Unit: %
			- 3 Evm_Rms_Low: float | bool: float EVM RMS value, low EVM window position. Unit: %
			- 4 Evm_Rms_High: float | bool: float EVM RMS value, high EVM window position. Unit: %
			- 5 Evm_Peak_Low: float | bool: float EVM peak value, low EVM window position. Unit: %
			- 6 Evm_Peak_High: float | bool: float EVM peak value, high EVM window position. Unit: %
			- 7 Mag_Error_Rms_Low: float | bool: float Magnitude error RMS value, low EVM window position. Unit: %
			- 8 Mag_Error_Rms_High: float | bool: float Magnitude error RMS value, low EVM window position. Unit: %
			- 9 Mag_Error_Peak_Low: float | bool: float Magnitude error peak value, low EVM window position. Unit: %
			- 10 Mag_Err_Peak_High: float | bool: float Magnitude error peak value, high EVM window position. Unit: %
			- 11 Ph_Error_Rms_Low: float | bool: float Phase error RMS value, low EVM window position. Unit: deg
			- 12 Ph_Error_Rms_High: float | bool: float Phase error RMS value, high EVM window position. Unit: deg
			- 13 Ph_Error_Peak_Low: float | bool: float Phase error peak value, low EVM window position. Unit: deg
			- 14 Ph_Error_Peak_High: float | bool: float Phase error peak value, high EVM window position. Unit: deg
			- 15 Frequency_Error: float | bool: float Carrier frequency error. Unit: Hz
			- 16 Timing_Error: float | bool: float Transmit time error. Unit: Ts (basic LTE time unit)
			- 17 Tx_Power: float | bool: float UE RMS power. Unit: dBm
			- 18 Peak_Power: float | bool: float UE peak power. Unit: dBm"""
		__meta_args_list = [
			ArgStruct.scalar_int('Reliability', 'Reliability'),
			ArgStruct.scalar_int('Out_Of_Tolerance'),
			ArgStruct.scalar_float_ext('Evm_Rms_Low'),
			ArgStruct.scalar_float_ext('Evm_Rms_High'),
			ArgStruct.scalar_float_ext('Evm_Peak_Low'),
			ArgStruct.scalar_float_ext('Evm_Peak_High'),
			ArgStruct.scalar_float_ext('Mag_Error_Rms_Low'),
			ArgStruct.scalar_float_ext('Mag_Error_Rms_High'),
			ArgStruct.scalar_float_ext('Mag_Error_Peak_Low'),
			ArgStruct.scalar_float_ext('Mag_Err_Peak_High'),
			ArgStruct.scalar_float_ext('Ph_Error_Rms_Low'),
			ArgStruct.scalar_float_ext('Ph_Error_Rms_High'),
			ArgStruct.scalar_float_ext('Ph_Error_Peak_Low'),
			ArgStruct.scalar_float_ext('Ph_Error_Peak_High'),
			ArgStruct.scalar_float_ext('Frequency_Error'),
			ArgStruct.scalar_float_ext('Timing_Error'),
			ArgStruct.scalar_float_ext('Tx_Power'),
			ArgStruct.scalar_float_ext('Peak_Power')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Reliability: int = None
			self.Out_Of_Tolerance: int = None
			self.Evm_Rms_Low: float | bool = None
			self.Evm_Rms_High: float | bool = None
			self.Evm_Peak_Low: float | bool = None
			self.Evm_Peak_High: float | bool = None
			self.Mag_Error_Rms_Low: float | bool = None
			self.Mag_Error_Rms_High: float | bool = None
			self.Mag_Error_Peak_Low: float | bool = None
			self.Mag_Err_Peak_High: float | bool = None
			self.Ph_Error_Rms_Low: float | bool = None
			self.Ph_Error_Rms_High: float | bool = None
			self.Ph_Error_Peak_Low: float | bool = None
			self.Ph_Error_Peak_High: float | bool = None
			self.Frequency_Error: float | bool = None
			self.Timing_Error: float | bool = None
			self.Tx_Power: float | bool = None
			self.Peak_Power: float | bool = None

	def calculate(self) -> CalculateStruct:
		"""CALCulate:LTE:MEASurement<Instance>:PRACh:MODulation:AVERage \n
		Snippet: value: CalculateStruct = driver.prach.modulation.average.calculate() \n
		Return the current, average and standard deviation single-value results. The values described below are returned by FETCh
		and READ commands. CALCulate commands return limit check results instead, one value for each result listed below. \n
			:return: structure: for return value, see the help for CalculateStruct structure arguments."""
		return self._core.io.query_struct(f'CALCulate:LTE:MEASurement<Instance>:PRACh:MODulation:AVERage?', self.__class__.CalculateStruct())
