from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NetworkCls:
	"""Network commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("network", core, parent)

	# noinspection PyTypeChecker
	def get_rfp_sharing(self) -> enums.Sharing:
		"""CONFigure:LTE:MEASurement<Instance>:NETWork:RFPSharing \n
		Snippet: value: enums.Sharing = driver.configure.network.get_rfp_sharing() \n
		No command help available \n
			:return: sharing: No help available
		"""
		response = self._core.io.query_str('CONFigure:LTE:MEASurement<Instance>:NETWork:RFPSharing?')
		return Conversions.str_to_scalar_enum(response, enums.Sharing)

	def set_rfp_sharing(self, sharing: enums.Sharing) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:NETWork:RFPSharing \n
		Snippet: driver.configure.network.set_rfp_sharing(sharing = enums.Sharing.FSHared) \n
		No command help available \n
			:param sharing: No help available
		"""
		param = Conversions.enum_scalar_to_str(sharing, enums.Sharing)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:NETWork:RFPSharing {param}')

	# noinspection PyTypeChecker
	def get_dmode(self) -> enums.DuplexMode:
		"""CONFigure:LTE:MEASurement<Instance>:NETWork:DMODe \n
		Snippet: value: enums.DuplexMode = driver.configure.network.get_dmode() \n
		No command help available \n
			:return: mode: No help available
		"""
		response = self._core.io.query_str_with_opc('CONFigure:LTE:MEASurement<Instance>:NETWork:DMODe?')
		return Conversions.str_to_scalar_enum(response, enums.DuplexMode)

	def set_dmode(self, mode: enums.DuplexMode) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:NETWork:DMODe \n
		Snippet: driver.configure.network.set_dmode(mode = enums.DuplexMode.FDD) \n
		No command help available \n
			:param mode: No help available
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.DuplexMode)
		self._core.io.write_with_opc(f'CONFigure:LTE:MEASurement<Instance>:NETWork:DMODe {param}')
