from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal.StructBase import StructBase
from ......Internal.ArgStruct import ArgStruct
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StandardDevCls:
	"""StandardDev commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("standardDev", core, parent)

	# noinspection PyTypeChecker
	class FetchStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Reliability: int: decimal 'Reliability indicator'
			- 2 Seg_Reliability: int: decimal Reliability indicator for the segment
			- 3 Statist_Expired: int: decimal Reached statistical length in slots
			- 4 Out_Of_Tolerance: int: decimal Percentage of measured subframes with failed limit check Unit: %
			- 5 Evm_Rms_Low: float: float EVM RMS value, low EVM window position Unit: %
			- 6 Evm_Rms_High: float: float EVM RMS value, high EVM window position Unit: %
			- 7 Evm_Peak_Low: float: float EVM peak value, low EVM window position Unit: %
			- 8 Evm_Peak_High: float: float EVM peak value, high EVM window position Unit: %
			- 9 Mag_Error_Rms_Low: float: float Magnitude error RMS value, low EVM window position Unit: %
			- 10 Mag_Error_Rms_High: float: float Magnitude error RMS value, low EVM window position Unit: %
			- 11 Mag_Error_Peak_Low: float: float Magnitude error peak value, low EVM window position Unit: %
			- 12 Mag_Err_Peak_High: float: float Magnitude error peak value, high EVM window position Unit: %
			- 13 Ph_Error_Rms_Low: float: float Phase error RMS value, low EVM window position Unit: deg
			- 14 Ph_Error_Rms_High: float: float Phase error RMS value, high EVM window position Unit: deg
			- 15 Ph_Error_Peak_Low: float: float Phase error peak value, low EVM window position Unit: deg
			- 16 Ph_Error_Peak_High: float: float Phase error peak value, high EVM window position Unit: deg
			- 17 Iq_Offset: float: float I/Q origin offset Unit: dBc
			- 18 Frequency_Error: float: float Carrier frequency error Unit: Hz
			- 19 Timing_Error: float: float Time error Unit: Ts (basic LTE time unit)
			- 20 Tx_Power: float: float User equipment power Unit: dBm
			- 21 Peak_Power: float: float User equipment peak power Unit: dBm
			- 22 Psd: float: No parameter help available
			- 23 Evm_Dmrs_Low: float: float EVM DMRS value, low EVM window position Unit: %
			- 24 Evm_Dmrs_High: float: float EVM DMRS value, high EVM window position Unit: %
			- 25 Mag_Err_Dmrs_Low: float: float Magnitude error DMRS value, low EVM window position Unit: %
			- 26 Mag_Err_Dmrs_High: float: float Magnitude error DMRS value, high EVM window position Unit: %
			- 27 Ph_Error_Dmrs_Low: float: float Phase error DMRS value, low EVM window position Unit: deg
			- 28 Ph_Error_Dmrs_High: float: float Phase error DMRS value, high EVM window position Unit: deg"""
		__meta_args_list = [
			ArgStruct.scalar_int('Reliability', 'Reliability'),
			ArgStruct.scalar_int('Seg_Reliability'),
			ArgStruct.scalar_int('Statist_Expired'),
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
			ArgStruct.scalar_float('Iq_Offset'),
			ArgStruct.scalar_float('Frequency_Error'),
			ArgStruct.scalar_float('Timing_Error'),
			ArgStruct.scalar_float('Tx_Power'),
			ArgStruct.scalar_float('Peak_Power'),
			ArgStruct.scalar_float('Psd'),
			ArgStruct.scalar_float('Evm_Dmrs_Low'),
			ArgStruct.scalar_float('Evm_Dmrs_High'),
			ArgStruct.scalar_float('Mag_Err_Dmrs_Low'),
			ArgStruct.scalar_float('Mag_Err_Dmrs_High'),
			ArgStruct.scalar_float('Ph_Error_Dmrs_Low'),
			ArgStruct.scalar_float('Ph_Error_Dmrs_High')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Reliability: int = None
			self.Seg_Reliability: int = None
			self.Statist_Expired: int = None
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
			self.Iq_Offset: float = None
			self.Frequency_Error: float = None
			self.Timing_Error: float = None
			self.Tx_Power: float = None
			self.Peak_Power: float = None
			self.Psd: float = None
			self.Evm_Dmrs_Low: float = None
			self.Evm_Dmrs_High: float = None
			self.Mag_Err_Dmrs_Low: float = None
			self.Mag_Err_Dmrs_High: float = None
			self.Ph_Error_Dmrs_Low: float = None
			self.Ph_Error_Dmrs_High: float = None

	def fetch(self, segment=repcap.Segment.Default) -> FetchStruct:
		"""FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent<nr>:MODulation:SDEViation \n
		Snippet: value: FetchStruct = driver.multiEval.listPy.segment.modulation.standardDev.fetch(segment = repcap.Segment.Default) \n
		Returns modulation single-value results for segment <no> in list mode. The values described below are returned by FETCh
		commands. The first four values (reliability to out of tolerance result) are also returned by CALCulate commands.
		The remaining values returned by CALCulate commands are limit check results, one value for each result listed below. \n
			:param segment: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Segment')
			:return: structure: for return value, see the help for FetchStruct structure arguments."""
		segment_cmd_val = self._cmd_group.get_repcap_cmd_value(segment, repcap.Segment)
		return self._core.io.query_struct(f'FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent{segment_cmd_val}:MODulation:SDEViation?', self.__class__.FetchStruct())
