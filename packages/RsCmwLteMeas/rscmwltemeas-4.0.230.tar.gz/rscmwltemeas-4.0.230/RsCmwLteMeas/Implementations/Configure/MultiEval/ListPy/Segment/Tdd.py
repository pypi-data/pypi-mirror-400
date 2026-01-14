from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal.Types import DataType
from ......Internal.StructBase import StructBase
from ......Internal.ArgStruct import ArgStruct
from ......Internal.ArgSingleList import ArgSingleList
from ......Internal.ArgSingle import ArgSingle
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TddCls:
	"""Tdd commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("tdd", core, parent)

	def set(self, uplink_downlink: int, special_subframe: int, segment=repcap.Segment.Default) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent<nr>:TDD \n
		Snippet: driver.configure.multiEval.listPy.segment.tdd.set(uplink_downlink = 1, special_subframe = 1, segment = repcap.Segment.Default) \n
		Defines segment settings only relevant for uplink measurements with the duplex mode TDD.
		For general segment configuration, see method RsCmwLteMeas.configure.multiEval.listPy.segment.setup.set. \n
			:param uplink_downlink: integer UL-DL configuration, defining the combination of uplink, downlink and special subframes within a radio frame Range: 0 to 6
			:param special_subframe: integer Special subframe configuration, defining the inner structure of special subframes Range: 0 to 8
			:param segment: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Segment')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('uplink_downlink', uplink_downlink, DataType.Integer), ArgSingle('special_subframe', special_subframe, DataType.Integer))
		segment_cmd_val = self._cmd_group.get_repcap_cmd_value(segment, repcap.Segment)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent{segment_cmd_val}:TDD {param}'.rstrip())

	# noinspection PyTypeChecker
	class TddStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Uplink_Downlink: int: integer UL-DL configuration, defining the combination of uplink, downlink and special subframes within a radio frame Range: 0 to 6
			- 2 Special_Subframe: int: integer Special subframe configuration, defining the inner structure of special subframes Range: 0 to 8"""
		__meta_args_list = [
			ArgStruct.scalar_int('Uplink_Downlink'),
			ArgStruct.scalar_int('Special_Subframe')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Uplink_Downlink: int = None
			self.Special_Subframe: int = None

	def get(self, segment=repcap.Segment.Default) -> TddStruct:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent<nr>:TDD \n
		Snippet: value: TddStruct = driver.configure.multiEval.listPy.segment.tdd.get(segment = repcap.Segment.Default) \n
		Defines segment settings only relevant for uplink measurements with the duplex mode TDD.
		For general segment configuration, see method RsCmwLteMeas.configure.multiEval.listPy.segment.setup.set. \n
			:param segment: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Segment')
			:return: structure: for return value, see the help for TddStruct structure arguments."""
		segment_cmd_val = self._cmd_group.get_repcap_cmd_value(segment, repcap.Segment)
		return self._core.io.query_struct(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:LIST:SEGMent{segment_cmd_val}:TDD?', self.__class__.TddStruct())
