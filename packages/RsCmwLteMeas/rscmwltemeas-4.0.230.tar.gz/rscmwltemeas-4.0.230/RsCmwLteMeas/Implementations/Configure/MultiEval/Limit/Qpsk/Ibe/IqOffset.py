from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal.Types import DataType
from .......Internal.StructBase import StructBase
from .......Internal.ArgStruct import ArgStruct
from .......Internal.ArgSingleList import ArgSingleList
from .......Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IqOffsetCls:
	"""IqOffset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("iqOffset", core, parent)

	def set(self, offset_1: float, offset_2: float, offset_3: float) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:QPSK:IBE:IQOFfset \n
		Snippet: driver.configure.multiEval.limit.qpsk.ibe.iqOffset.set(offset_1 = 1.0, offset_2 = 1.0, offset_3 = 1.0) \n
		Defines I/Q origin offset values used for calculation of an upper limit for the in-band emission (QPSK modulation) .
		Three different values can be set for three TX power ranges, see 'In-band emissions limits'. \n
			:param offset_1: numeric Offset for high TX power range Range: -256 dBc to 256 dBc, Unit: dB
			:param offset_2: numeric Offset for intermediate TX power range Range: -256 dBc to 256 dBc, Unit: dB
			:param offset_3: numeric Offset for low TX power range Range: -256 dBc to 256 dBc, Unit: dB
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('offset_1', offset_1, DataType.Float), ArgSingle('offset_2', offset_2, DataType.Float), ArgSingle('offset_3', offset_3, DataType.Float))
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:QPSK:IBE:IQOFfset {param}'.rstrip())

	# noinspection PyTypeChecker
	class IqOffsetStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Offset_1: float: numeric Offset for high TX power range Range: -256 dBc to 256 dBc, Unit: dB
			- 2 Offset_2: float: numeric Offset for intermediate TX power range Range: -256 dBc to 256 dBc, Unit: dB
			- 3 Offset_3: float: numeric Offset for low TX power range Range: -256 dBc to 256 dBc, Unit: dB"""
		__meta_args_list = [
			ArgStruct.scalar_float('Offset_1'),
			ArgStruct.scalar_float('Offset_2'),
			ArgStruct.scalar_float('Offset_3')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Offset_1: float = None
			self.Offset_2: float = None
			self.Offset_3: float = None

	def get(self) -> IqOffsetStruct:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:QPSK:IBE:IQOFfset \n
		Snippet: value: IqOffsetStruct = driver.configure.multiEval.limit.qpsk.ibe.iqOffset.get() \n
		Defines I/Q origin offset values used for calculation of an upper limit for the in-band emission (QPSK modulation) .
		Three different values can be set for three TX power ranges, see 'In-band emissions limits'. \n
			:return: structure: for return value, see the help for IqOffsetStruct structure arguments."""
		return self._core.io.query_struct(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:QPSK:IBE:IQOFfset?', self.__class__.IqOffsetStruct())
