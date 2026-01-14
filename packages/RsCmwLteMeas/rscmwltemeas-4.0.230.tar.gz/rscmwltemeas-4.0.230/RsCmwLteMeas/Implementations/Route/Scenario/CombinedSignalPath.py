from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.Types import DataType
from ....Internal.StructBase import StructBase
from ....Internal.ArgStruct import ArgStruct
from ....Internal.ArgSingleList import ArgSingleList
from ....Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CombinedSignalPathCls:
	"""CombinedSignalPath commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("combinedSignalPath", core, parent)

	def set(self, master: str, carrier: str=None) -> None:
		"""ROUTe:LTE:MEASurement<Instance>:SCENario:CSPath \n
		Snippet: driver.route.scenario.combinedSignalPath.set(master = 'abc', carrier = 'abc') \n
		Activates the combined signal path scenario and selects the controlling application and primary carrier. The selected
		application controls most signal routing settings, analyzer settings and some measurement control settings while the
		combined signal path scenario is active. The command usage depends on the carrier aggregation mode of the measured
		signal: no UL carrier aggregation, non-contiguous UL carrier aggregation or intraband contiguous UL carrier aggregation.
		The following table provides an overview.
			Table Header: CA type / Setting command / Query returns \n
			- No UL CA / ROUT:LTE:MEAS:SCEN:CSP <Controller> <Carrier> can be skipped and equals 'PCC'. / <Controller>, 'PCC'
			- Non-contiguous UL CA / ROUT:LTE:MEAS:SCEN:CSP <Controller>, <Carrier> <Carrier>: measured carrier ('PCC', 'SCC2', ...) / <Controller>, <Carrier>
			- Intraband contiguous UL CA / ROUT:LTE:MEAS:SCEN:CSP <Controller>, <Carrier> <Carrier>: set of carriers ('Set A', 'Set B', ...) / <Controller>, <Carrier>, <Set> <Carrier>: carrier selecting RF path ('PCC', 'SCC2', ...) <Set>: measured set of carriers ('Set A', 'Set B', ...) \n
			:param master: No help available
			:param carrier: string Uplink carrier or set of uplink carriers configured in the controlling application Examples: 'PCC', 'SCC2', 'Set A', 'Set B' If a set is selected, a query returns the carrier of the set that is used by the measurement to select the RF path.
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('master', master, DataType.String), ArgSingle('carrier', carrier, DataType.String, None, is_optional=True))
		self._core.io.write(f'ROUTe:LTE:MEASurement<Instance>:SCENario:CSPath {param}'.rstrip())

	# noinspection PyTypeChecker
	class GetStruct(StructBase):
		"""Response structure. Fields: \n
			- 1 Master: str: string Controlling application Example: 'LTE Sig1' or 'LTE Sig2'
			- 2 Carrier: str: string Uplink carrier or set of uplink carriers configured in the controlling application Examples: 'PCC', 'SCC2', 'Set A', 'Set B' If a set is selected, a query returns the carrier of the set that is used by the measurement to select the RF path.
			- 3 Set_Py: str: string Measured set of uplink carriers Example: 'Set A', 'Set B' Only returned for intraband contiguous UL CA."""
		__meta_args_list = [
			ArgStruct.scalar_str('Master'),
			ArgStruct.scalar_str('Carrier'),
			ArgStruct.scalar_str('Set_Py')]

		def __init__(self):
			StructBase.__init__(self, self)
			self.Master: str = None
			self.Carrier: str = None
			self.Set_Py: str = None

	def get(self) -> GetStruct:
		"""ROUTe:LTE:MEASurement<Instance>:SCENario:CSPath \n
		Snippet: value: GetStruct = driver.route.scenario.combinedSignalPath.get() \n
		Activates the combined signal path scenario and selects the controlling application and primary carrier. The selected
		application controls most signal routing settings, analyzer settings and some measurement control settings while the
		combined signal path scenario is active. The command usage depends on the carrier aggregation mode of the measured
		signal: no UL carrier aggregation, non-contiguous UL carrier aggregation or intraband contiguous UL carrier aggregation.
		The following table provides an overview.
			Table Header: CA type / Setting command / Query returns \n
			- No UL CA / ROUT:LTE:MEAS:SCEN:CSP <Controller> <Carrier> can be skipped and equals 'PCC'. / <Controller>, 'PCC'
			- Non-contiguous UL CA / ROUT:LTE:MEAS:SCEN:CSP <Controller>, <Carrier> <Carrier>: measured carrier ('PCC', 'SCC2', ...) / <Controller>, <Carrier>
			- Intraband contiguous UL CA / ROUT:LTE:MEAS:SCEN:CSP <Controller>, <Carrier> <Carrier>: set of carriers ('Set A', 'Set B', ...) / <Controller>, <Carrier>, <Set> <Carrier>: carrier selecting RF path ('PCC', 'SCC2', ...) <Set>: measured set of carriers ('Set A', 'Set B', ...) \n
			:return: structure: for return value, see the help for GetStruct structure arguments."""
		return self._core.io.query_struct(f'ROUTe:LTE:MEASurement<Instance>:SCENario:CSPath?', self.__class__.GetStruct())
