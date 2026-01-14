from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal.StructBase import StructBase
from ......Internal.ArgStruct import ArgStruct
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ExtremeCls:
	"""Extreme commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("extreme", core, parent)

	# noinspection PyTypeChecker
	class FetchStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Reliability: int: decimal 'Reliability indicator'
			- 2 Seg_Reliability: int: decimal Reliability indicator for the segment
			- 3 Statist_Expired: int: decimal Reached statistical length in slots
			- 4 Out_Of_Tolerance: int: decimal Percentage of measured subframes with failed limit check Unit: %
			- 5 Ripple_1: float: float Max (range 1) - min (range 1) Unit: dB
			- 6 Ripple_2: float: float Max (range 2) - min (range 2) Unit: dB
			- 7 Max_R_1_Min_R_2: float: float Max (range 1) - min (range 2) Unit: dB
			- 8 Max_R_2_Min_R_1: float: float Max (range 2) - min (range 1) Unit: dB
			- 9 Min_R_1: float: float Min (range 1) Unit: dB
			- 10 Max_R_1: float: float Max (range 1) Unit: dB
			- 11 Min_R_2: float: float Min (range 2) Unit: dB
			- 12 Max_R_2: float: float Max (range 2) Unit: dB"""
		__meta_args_list = [
			ArgStruct.scalar_int('Reliability', 'Reliability'),
			ArgStruct.scalar_int('Seg_Reliability'),
			ArgStruct.scalar_int('Statist_Expired'),
			ArgStruct.scalar_int('Out_Of_Tolerance'),
			ArgStruct.scalar_float('Ripple_1'),
			ArgStruct.scalar_float('Ripple_2'),
			ArgStruct.scalar_float('Max_R_1_Min_R_2'),
			ArgStruct.scalar_float('Max_R_2_Min_R_1'),
			ArgStruct.scalar_float('Min_R_1'),
			ArgStruct.scalar_float('Max_R_1'),
			ArgStruct.scalar_float('Min_R_2'),
			ArgStruct.scalar_float('Max_R_2')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Reliability: int = None
			self.Seg_Reliability: int = None
			self.Statist_Expired: int = None
			self.Out_Of_Tolerance: int = None
			self.Ripple_1: float = None
			self.Ripple_2: float = None
			self.Max_R_1_Min_R_2: float = None
			self.Max_R_2_Min_R_1: float = None
			self.Min_R_1: float = None
			self.Max_R_1: float = None
			self.Min_R_2: float = None
			self.Max_R_2: float = None

	def fetch(self, segment=repcap.Segment.Default) -> FetchStruct:
		"""FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent<nr>:ESFLatness:EXTReme \n
		Snippet: value: FetchStruct = driver.multiEval.listPy.segment.esFlatness.extreme.fetch(segment = repcap.Segment.Default) \n
		Return equalizer spectrum flatness single value results for segment <no> in list mode. \n
			:param segment: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Segment')
			:return: structure: for return value, see the help for FetchStruct structure arguments."""
		segment_cmd_val = self._cmd_group.get_repcap_cmd_value(segment, repcap.Segment)
		return self._core.io.query_struct(f'FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent{segment_cmd_val}:ESFLatness:EXTReme?', self.__class__.FetchStruct())

	# noinspection PyTypeChecker
	class CalculateStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Reliability: int: decimal 'Reliability indicator'
			- 2 Seg_Reliability: int: decimal Reliability indicator for the segment
			- 3 Statist_Expired: int: decimal Reached statistical length in slots
			- 4 Out_Of_Tolerance: int: decimal Percentage of measured subframes with failed limit check Unit: %
			- 5 Ripple_1: float | bool: Limit check result for max (range 1) - min (range 1) .
			- 6 Ripple_2: float | bool: Limit check result for max (range 2) - min (range 2) .
			- 7 Max_R_1_Min_R_2: float | bool: Limit check result for max (range 1) - min (range 2) . Unit: dB
			- 8 Max_R_2_Min_R_1: float | bool: Limit check result for max (range 2) - min (range 1) . Unit: dB"""
		__meta_args_list = [
			ArgStruct.scalar_int('Reliability', 'Reliability'),
			ArgStruct.scalar_int('Seg_Reliability'),
			ArgStruct.scalar_int('Statist_Expired'),
			ArgStruct.scalar_int('Out_Of_Tolerance'),
			ArgStruct.scalar_float_ext('Ripple_1'),
			ArgStruct.scalar_float_ext('Ripple_2'),
			ArgStruct.scalar_float_ext('Max_R_1_Min_R_2'),
			ArgStruct.scalar_float_ext('Max_R_2_Min_R_1')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Reliability: int = None
			self.Seg_Reliability: int = None
			self.Statist_Expired: int = None
			self.Out_Of_Tolerance: int = None
			self.Ripple_1: float | bool = None
			self.Ripple_2: float | bool = None
			self.Max_R_1_Min_R_2: float | bool = None
			self.Max_R_2_Min_R_1: float | bool = None

	def calculate(self, segment=repcap.Segment.Default) -> CalculateStruct:
		"""CALCulate:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent<nr>:ESFLatness:EXTReme \n
		Snippet: value: CalculateStruct = driver.multiEval.listPy.segment.esFlatness.extreme.calculate(segment = repcap.Segment.Default) \n
		Return equalizer spectrum flatness single value results for segment <no> in list mode. \n
			:param segment: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Segment')
			:return: structure: for return value, see the help for CalculateStruct structure arguments."""
		segment_cmd_val = self._cmd_group.get_repcap_cmd_value(segment, repcap.Segment)
		return self._core.io.query_struct(f'CALCulate:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent{segment_cmd_val}:ESFLatness:EXTReme?', self.__class__.CalculateStruct())
