from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal.Types import DataType
from .......Internal.StructBase import StructBase
from .......Internal.ArgStruct import ArgStruct
from .......Internal.ArgSingleList import ArgSingleList
from .......Internal.ArgSingle import ArgSingle
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class IbeCls:
	"""Ibe commands group definition. 2 total commands, 1 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ibe", core, parent)

	@property
	def iqOffset(self):
		"""iqOffset commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_iqOffset'):
			from .IqOffset import IqOffsetCls
			self._iqOffset = IqOffsetCls(self._core, self._cmd_group)
		return self._iqOffset

	def set(self, enable: bool, minimum: float, evm: float, rb_power: float, iq_image: float, qAMmodOrder=repcap.QAMmodOrder.Default) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:QAM<ModOrder>:IBE \n
		Snippet: driver.configure.multiEval.limit.qam.ibe.set(enable = False, minimum = 1.0, evm = 1.0, rb_power = 1.0, iq_image = 1.0, qAMmodOrder = repcap.QAMmodOrder.Default) \n
		Defines parameters used for calculation of an upper limit for the in-band emission, for QAM modulations, see 'In-band
		emissions limits'. \n
			:param enable: OFF | ON OFF: disables the limit check ON: enables the limit check
			:param minimum: numeric Range: -256 dB to 256 dB, Unit: dB
			:param evm: numeric Range: 0 % to 100 %, Unit: %
			:param rb_power: numeric Range: -256 dBm to 256 dBm, Unit: dBm
			:param iq_image: numeric Range: -256 dB to 256 dB, Unit: dB
			:param qAMmodOrder: optional repeated capability selector. Default value: Qam16 (settable in the interface 'Qam')
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('enable', enable, DataType.Boolean), ArgSingle('minimum', minimum, DataType.Float), ArgSingle('evm', evm, DataType.Float), ArgSingle('rb_power', rb_power, DataType.Float), ArgSingle('iq_image', iq_image, DataType.Float))
		qAMmodOrder_cmd_val = self._cmd_group.get_repcap_cmd_value(qAMmodOrder, repcap.QAMmodOrder)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:QAM{qAMmodOrder_cmd_val}:IBE {param}'.rstrip())

	# noinspection PyTypeChecker
	class IbeStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Enable: bool: OFF | ON OFF: disables the limit check ON: enables the limit check
			- 2 Minimum: float: numeric Range: -256 dB to 256 dB, Unit: dB
			- 3 Evm: float: numeric Range: 0 % to 100 %, Unit: %
			- 4 Rb_Power: float: numeric Range: -256 dBm to 256 dBm, Unit: dBm
			- 5 Iq_Image: float: numeric Range: -256 dB to 256 dB, Unit: dB"""
		__meta_args_list = [
			ArgStruct.scalar_bool('Enable'),
			ArgStruct.scalar_float('Minimum'),
			ArgStruct.scalar_float('Evm'),
			ArgStruct.scalar_float('Rb_Power'),
			ArgStruct.scalar_float('Iq_Image')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Enable: bool = None
			self.Minimum: float = None
			self.Evm: float = None
			self.Rb_Power: float = None
			self.Iq_Image: float = None

	def get(self, qAMmodOrder=repcap.QAMmodOrder.Default) -> IbeStruct:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:QAM<ModOrder>:IBE \n
		Snippet: value: IbeStruct = driver.configure.multiEval.limit.qam.ibe.get(qAMmodOrder = repcap.QAMmodOrder.Default) \n
		Defines parameters used for calculation of an upper limit for the in-band emission, for QAM modulations, see 'In-band
		emissions limits'. \n
			:param qAMmodOrder: optional repeated capability selector. Default value: Qam16 (settable in the interface 'Qam')
			:return: structure: for return value, see the help for IbeStruct structure arguments."""
		qAMmodOrder_cmd_val = self._cmd_group.get_repcap_cmd_value(qAMmodOrder, repcap.QAMmodOrder)
		return self._core.io.query_struct(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:LIMit:QAM{qAMmodOrder_cmd_val}:IBE?', self.__class__.IbeStruct())

	def clone(self) -> 'IbeCls':
		"""Clones the group by creating new object from it and its whole existing subgroups.
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group."""
		new_group = IbeCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
