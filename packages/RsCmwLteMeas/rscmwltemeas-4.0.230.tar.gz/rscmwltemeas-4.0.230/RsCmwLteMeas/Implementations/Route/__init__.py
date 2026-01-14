from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.StructBase import StructBase
from ...Internal.ArgStruct import ArgStruct
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RouteCls:
	"""Route commands group definition. 5 total commands, 1 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("route", core, parent)

	@property
	def scenario(self):
		"""scenario commands group. 3 Sub-classes, 1 commands."""
		if not hasattr(self, '_scenario'):
			from .Scenario import ScenarioCls
			self._scenario = ScenarioCls(self._core, self._cmd_group)
		return self._scenario

	# noinspection PyTypeChecker
	class ValueStruct(StructBase):  # From ReadStructDefinition CmdPropertyTemplate.xml
		"""Structure for reading output parameters. Fields: \n
			- Scenario: enums.Scenario: SALone | CSPath | MAPRotocol SALone: Standalone (nonsignaling) CSPath: Combined signal path MAPRotocol: Measure at protocol test
			- Controller: str: string Controlling application for scenario CSPath or MAPRotocol
			- Rx_Connector: enums.RxConnector: RF connector for the input path
			- Rf_Converter: enums.RxConverter: RX module for the input path"""
		__meta_args_list = [
			ArgStruct.scalar_enum('Scenario', enums.Scenario),
			ArgStruct.scalar_str('Controller'),
			ArgStruct.scalar_enum('Rx_Connector', enums.RxConnector),
			ArgStruct.scalar_enum('Rf_Converter', enums.RxConverter)]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Scenario: enums.Scenario=None
			self.Controller: str=None
			self.Rx_Connector: enums.RxConnector=None
			self.Rf_Converter: enums.RxConverter=None

	def get_value(self) -> ValueStruct:
		"""ROUTe:LTE:MEASurement<Instance> \n
		Snippet: value: ValueStruct = driver.route.get_value() \n
		Returns the configured routing settings. For possible connector and converter values, see 'Values for RF path selection'. \n
			:return: structure: for return value, see the help for ValueStruct structure arguments.
		"""
		return self._core.io.query_struct('ROUTe:LTE:MEASurement<Instance>?', self.__class__.ValueStruct())

	def clone(self) -> 'RouteCls':
		"""Clones the group by creating new object from it and its whole existing subgroups.
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group."""
		new_group = RouteCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
