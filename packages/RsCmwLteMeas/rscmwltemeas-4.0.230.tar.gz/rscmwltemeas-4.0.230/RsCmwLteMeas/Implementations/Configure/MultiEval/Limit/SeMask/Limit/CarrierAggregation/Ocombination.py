from ........Internal.Core import Core
from ........Internal.CommandsGroup import CommandsGroup
from ........Internal.Types import DataType
from ........Internal.StructBase import StructBase
from ........Internal.ArgStruct import ArgStruct
from ........Internal.ArgSingleList import ArgSingleList
from ........Internal.ArgSingle import ArgSingle
from ........ import enums
from ........ import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OcombinationCls:
	"""Ocombination commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ocombination", core, parent)

	def set(self, enable: bool, frequency_start: float, frequency_end: float, level: float, rbw: enums.Rbw, limit=repcap.Limit.Default) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:SEMask:LIMit<nr>:CAGGregation:OCOMbination \n
		Snippet: driver.configure.multiEval.limit.seMask.limit.carrierAggregation.ocombination.set(enable = False, frequency_start = 1.0, frequency_end = 1.0, level = 1.0, rbw = enums.Rbw.K030, limit = repcap.Limit.Default) \n
		Defines general requirements for the emission mask area <no>. The activation state, the area borders, an upper limit and
		the resolution bandwidth must be specified. The settings apply to all 'other' channel bandwidth combinations, not covered
		by other commands in this chapter. \n
			:param enable: OFF | ON OFF: Disables the check of these requirements. ON: Enables the check of these requirements.
			:param frequency_start: numeric Start frequency of the area, relative to the edges of the aggregated channel bandwidth. Range: 0 MHz to 65 MHz, Unit: Hz
			:param frequency_end: numeric Stop frequency of the area, relative to the edges of the aggregated channel bandwidth. Range: 0 MHz to 65 MHz, Unit: Hz
			:param level: numeric Upper limit for the area Range: -256 dBm to 256 dBm, Unit: dBm
			:param rbw: K030 | K100 | M1 Resolution bandwidth to be used for the area. K030: 30 kHz K100: 100 kHz M1: 1 MHz
			:param limit: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Limit')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('enable', enable, DataType.Boolean), ArgSingle('frequency_start', frequency_start, DataType.Float), ArgSingle('frequency_end', frequency_end, DataType.Float), ArgSingle('level', level, DataType.Float), ArgSingle('rbw', rbw, DataType.Enum, enums.Rbw))
		limit_cmd_val = self._cmd_group.get_repcap_cmd_value(limit, repcap.Limit)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:SEMask:LIMit{limit_cmd_val}:CAGGregation:OCOMbination {param}'.rstrip())

	# noinspection PyTypeChecker
	class OcombinationStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Enable: bool: OFF | ON OFF: Disables the check of these requirements. ON: Enables the check of these requirements.
			- 2 Frequency_Start: float: numeric Start frequency of the area, relative to the edges of the aggregated channel bandwidth. Range: 0 MHz to 65 MHz, Unit: Hz
			- 3 Frequency_End: float: numeric Stop frequency of the area, relative to the edges of the aggregated channel bandwidth. Range: 0 MHz to 65 MHz, Unit: Hz
			- 4 Level: float: numeric Upper limit for the area Range: -256 dBm to 256 dBm, Unit: dBm
			- 5 Rbw: enums.Rbw: K030 | K100 | M1 Resolution bandwidth to be used for the area. K030: 30 kHz K100: 100 kHz M1: 1 MHz"""
		__meta_args_list = [
			ArgStruct.scalar_bool('Enable'),
			ArgStruct.scalar_float('Frequency_Start'),
			ArgStruct.scalar_float('Frequency_End'),
			ArgStruct.scalar_float('Level'),
			ArgStruct.scalar_enum('Rbw', enums.Rbw)]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Enable: bool = None
			self.Frequency_Start: float = None
			self.Frequency_End: float = None
			self.Level: float = None
			self.Rbw: enums.Rbw = None

	def get(self, limit=repcap.Limit.Default) -> OcombinationStruct:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:SEMask:LIMit<nr>:CAGGregation:OCOMbination \n
		Snippet: value: OcombinationStruct = driver.configure.multiEval.limit.seMask.limit.carrierAggregation.ocombination.get(limit = repcap.Limit.Default) \n
		Defines general requirements for the emission mask area <no>. The activation state, the area borders, an upper limit and
		the resolution bandwidth must be specified. The settings apply to all 'other' channel bandwidth combinations, not covered
		by other commands in this chapter. \n
			:param limit: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Limit')
			:return: structure: for return value, see the help for OcombinationStruct structure arguments."""
		limit_cmd_val = self._cmd_group.get_repcap_cmd_value(limit, repcap.Limit)
		return self._core.io.query_struct(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:SEMask:LIMit{limit_cmd_val}:CAGGregation:OCOMbination?', self.__class__.OcombinationStruct())
