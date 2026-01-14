from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ScenarioCls:
	"""Scenario commands group definition. 4 total commands, 3 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("scenario", core, parent)

	@property
	def salone(self):
		"""salone commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_salone'):
			from .Salone import SaloneCls
			self._salone = SaloneCls(self._core, self._cmd_group)
		return self._salone

	@property
	def combinedSignalPath(self):
		"""combinedSignalPath commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_combinedSignalPath'):
			from .CombinedSignalPath import CombinedSignalPathCls
			self._combinedSignalPath = CombinedSignalPathCls(self._core, self._cmd_group)
		return self._combinedSignalPath

	@property
	def maProtocol(self):
		"""maProtocol commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_maProtocol'):
			from .MaProtocol import MaProtocolCls
			self._maProtocol = MaProtocolCls(self._core, self._cmd_group)
		return self._maProtocol

	# noinspection PyTypeChecker
	def get_value(self) -> enums.Scenario:
		"""ROUTe:LTE:MEASurement<Instance>:SCENario \n
		Snippet: value: enums.Scenario = driver.route.scenario.get_value() \n
		Returns the active scenario. \n
			:return: scenario: SALone | CSPath | MAPRotocol SALone: Standalone (nonsignaling) CSPath: Combined signal path MAPRotocol: Measure at protocol test
		"""
		response = self._core.io.query_str('ROUTe:LTE:MEASurement<Instance>:SCENario?')
		return Conversions.str_to_scalar_enum(response, enums.Scenario)

	def clone(self) -> 'ScenarioCls':
		"""Clones the group by creating new object from it and its whole existing subgroups.
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group."""
		new_group = ScenarioCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
