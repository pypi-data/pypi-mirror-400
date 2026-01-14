from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal.StructBase import StructBase
from .......Internal.ArgStruct import ArgStruct
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MinimumCls:
	"""Minimum commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("minimum", core, parent)

	# noinspection PyTypeChecker
	class FetchStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Reliability: int: decimal 'Reliability indicator'
			- 2 Seg_Reliability: int: decimal Reliability indicator for the segment
			- 3 Statist_Expired: int: decimal Reached statistical length in subframes
			- 4 Out_Of_Tolerance: int: decimal Percentage of measured subframes with failed limit check Unit: %
			- 5 Tx_Power_Min: float: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_int('Reliability', 'Reliability'),
			ArgStruct.scalar_int('Seg_Reliability'),
			ArgStruct.scalar_int('Statist_Expired'),
			ArgStruct.scalar_int('Out_Of_Tolerance'),
			ArgStruct.scalar_float('Tx_Power_Min')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Reliability: int = None
			self.Seg_Reliability: int = None
			self.Statist_Expired: int = None
			self.Out_Of_Tolerance: int = None
			self.Tx_Power_Min: float = None

	def fetch(self, segment=repcap.Segment.Default, carrierComponent=repcap.CarrierComponent.Default) -> FetchStruct:
		"""FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent<nr>:POWer:CC<no>:MINimum \n
		Snippet: value: FetchStruct = driver.multiEval.listPy.segment.power.cc.minimum.fetch(segment = repcap.Segment.Default, carrierComponent = repcap.CarrierComponent.Default) \n
		Return TX power results for component carrier CC<no> and a single segment in list mode. \n
			:param segment: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Segment')
			:param carrierComponent: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cc')
			:return: structure: for return value, see the help for FetchStruct structure arguments."""
		segment_cmd_val = self._cmd_group.get_repcap_cmd_value(segment, repcap.Segment)
		carrierComponent_cmd_val = self._cmd_group.get_repcap_cmd_value(carrierComponent, repcap.CarrierComponent)
		return self._core.io.query_struct(f'FETCh:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent{segment_cmd_val}:POWer:CC{carrierComponent_cmd_val}:MINimum?', self.__class__.FetchStruct())

	# noinspection PyTypeChecker
	class CalculateStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Reliability: int: No parameter help available
			- 2 Seg_Reliability: int: No parameter help available
			- 3 Statist_Expired: int: No parameter help available
			- 4 Out_Of_Tolerance: int: No parameter help available
			- 5 Tx_Power_Min: float | bool: No parameter help available"""
		__meta_args_list = [
			ArgStruct.scalar_int('Reliability', 'Reliability'),
			ArgStruct.scalar_int('Seg_Reliability'),
			ArgStruct.scalar_int('Statist_Expired'),
			ArgStruct.scalar_int('Out_Of_Tolerance'),
			ArgStruct.scalar_float_ext('Tx_Power_Min')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Reliability: int = None
			self.Seg_Reliability: int = None
			self.Statist_Expired: int = None
			self.Out_Of_Tolerance: int = None
			self.Tx_Power_Min: float | bool = None

	def calculate(self, segment=repcap.Segment.Default, carrierComponent=repcap.CarrierComponent.Default) -> CalculateStruct:
		"""CALCulate:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent<nr>:POWer:CC<no>:MINimum \n
		Snippet: value: CalculateStruct = driver.multiEval.listPy.segment.power.cc.minimum.calculate(segment = repcap.Segment.Default, carrierComponent = repcap.CarrierComponent.Default) \n
		No command help available \n
			:param segment: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Segment')
			:param carrierComponent: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cc')
			:return: structure: for return value, see the help for CalculateStruct structure arguments."""
		segment_cmd_val = self._cmd_group.get_repcap_cmd_value(segment, repcap.Segment)
		carrierComponent_cmd_val = self._cmd_group.get_repcap_cmd_value(carrierComponent, repcap.CarrierComponent)
		return self._core.io.query_struct(f'CALCulate:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent{segment_cmd_val}:POWer:CC{carrierComponent_cmd_val}:MINimum?', self.__class__.CalculateStruct())
