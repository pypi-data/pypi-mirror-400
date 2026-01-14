from ........Internal.Core import Core
from ........Internal.CommandsGroup import CommandsGroup
from ........Internal.Types import DataType
from ........Internal.StructBase import StructBase
from ........Internal.ArgStruct import ArgStruct
from ........Internal.ArgSingleList import ArgSingleList
from ........Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OcombinationCls:
	"""Ocombination commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ocombination", core, parent)

	def set(self, relative_level: float | bool, absolute_level: float | bool) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:ACLR:EUTRa:CAGGregation:OCOMbination \n
		Snippet: driver.configure.multiEval.limit.aclr.eutra.carrierAggregation.ocombination.set(relative_level = 1.0, absolute_level = 1.0) \n
		Defines relative and absolute limits for the ACLR measured in an adjacent E-UTRA channel. The settings apply to all
		'other' channel bandwidth combinations, not covered by other commands in this chapter. \n
			:param relative_level: (float or boolean) numeric | ON | OFF Range: -256 dB to 256 dB, Unit: dB ON | OFF enables or disables the limit check.
			:param absolute_level: (float or boolean) numeric | ON | OFF Range: -256 dBm to 256 dBm, Unit: dBm ON | OFF enables or disables the limit check.
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('relative_level', relative_level, DataType.FloatExt), ArgSingle('absolute_level', absolute_level, DataType.FloatExt))
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:ACLR:EUTRa:CAGGregation:OCOMbination {param}'.rstrip())

	# noinspection PyTypeChecker
	class OcombinationStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Relative_Level: float | bool: numeric | ON | OFF Range: -256 dB to 256 dB, Unit: dB ON | OFF enables or disables the limit check.
			- 2 Absolute_Level: float | bool: numeric | ON | OFF Range: -256 dBm to 256 dBm, Unit: dBm ON | OFF enables or disables the limit check."""
		__meta_args_list = [
			ArgStruct.scalar_float_ext('Relative_Level'),
			ArgStruct.scalar_float_ext('Absolute_Level')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Relative_Level: float | bool = None
			self.Absolute_Level: float | bool = None

	def get(self) -> OcombinationStruct:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:ACLR:EUTRa:CAGGregation:OCOMbination \n
		Snippet: value: OcombinationStruct = driver.configure.multiEval.limit.aclr.eutra.carrierAggregation.ocombination.get() \n
		Defines relative and absolute limits for the ACLR measured in an adjacent E-UTRA channel. The settings apply to all
		'other' channel bandwidth combinations, not covered by other commands in this chapter. \n
			:return: structure: for return value, see the help for OcombinationStruct structure arguments."""
		return self._core.io.query_struct(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:ACLR:EUTRa:CAGGregation:OCOMbination?', self.__class__.OcombinationStruct())
