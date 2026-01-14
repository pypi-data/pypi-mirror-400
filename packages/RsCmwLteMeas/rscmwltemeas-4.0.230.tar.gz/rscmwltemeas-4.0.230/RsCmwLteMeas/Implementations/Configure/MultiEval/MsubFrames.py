from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.Types import DataType
from ....Internal.StructBase import StructBase
from ....Internal.ArgStruct import ArgStruct
from ....Internal.ArgSingleList import ArgSingleList
from ....Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MsubFramesCls:
	"""MsubFrames commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("msubFrames", core, parent)

	def set(self, sub_frame_offset: int, sub_frame_count: int, meas_subframe: int) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:MSUBframes \n
		Snippet: driver.configure.multiEval.msubFrames.set(sub_frame_offset = 1, sub_frame_count = 1, meas_subframe = 1) \n
		Configures the scope of the measurement, i.e. which subframes are measured. \n
			:param sub_frame_offset: decimal Start of the measured subframe range relative to the trigger event. Range: 0 to 9
			:param sub_frame_count: decimal Length of the measured subframe range. Range: 1 to 320
			:param meas_subframe: decimal Subframe containing the measured slots for modulation and spectrum results. Range: 0 to SubframeCount-1
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('sub_frame_offset', sub_frame_offset, DataType.Integer), ArgSingle('sub_frame_count', sub_frame_count, DataType.Integer), ArgSingle('meas_subframe', meas_subframe, DataType.Integer))
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:MSUBframes {param}'.rstrip())

	# noinspection PyTypeChecker
	class MsubFramesStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Sub_Frame_Offset: int: decimal Start of the measured subframe range relative to the trigger event. Range: 0 to 9
			- 2 Sub_Frame_Count: int: decimal Length of the measured subframe range. Range: 1 to 320
			- 3 Meas_Subframe: int: decimal Subframe containing the measured slots for modulation and spectrum results. Range: 0 to SubframeCount-1"""
		__meta_args_list = [
			ArgStruct.scalar_int('Sub_Frame_Offset'),
			ArgStruct.scalar_int('Sub_Frame_Count'),
			ArgStruct.scalar_int('Meas_Subframe')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Sub_Frame_Offset: int = None
			self.Sub_Frame_Count: int = None
			self.Meas_Subframe: int = None

	def get(self) -> MsubFramesStruct:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:MSUBframes \n
		Snippet: value: MsubFramesStruct = driver.configure.multiEval.msubFrames.get() \n
		Configures the scope of the measurement, i.e. which subframes are measured. \n
			:return: structure: for return value, see the help for MsubFramesStruct structure arguments."""
		return self._core.io.query_struct(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:MSUBframes?', self.__class__.MsubFramesStruct())
