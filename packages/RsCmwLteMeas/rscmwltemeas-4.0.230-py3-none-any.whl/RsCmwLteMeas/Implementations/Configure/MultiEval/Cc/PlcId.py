from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PlcIdCls:
	"""PlcId commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("plcId", core, parent)

	def set(self, phs_layer_cell_id: int, carrierComponent=repcap.CarrierComponent.Default) -> None:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:CC<Nr>:PLCid \n
		Snippet: driver.configure.multiEval.cc.plcId.set(phs_layer_cell_id = 1, carrierComponent = repcap.CarrierComponent.Default) \n
		Specifies the physical layer cell ID of component carrier CC<no>. Without carrier aggregation, you can omit <no>.
			INTRO_CMD_HELP: For the combined signal path scenario, use: \n
			- CONFigure:LTE:SIGN<i>:CELL[:PCC]:PCID
			- CONFigure:LTE:SIGN<i>:CELL:SCC<c>:PCID \n
			:param phs_layer_cell_id: integer Range: 0 to 503
			:param carrierComponent: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cc')
		"""
		param = Conversions.decimal_value_to_str(phs_layer_cell_id)
		carrierComponent_cmd_val = self._cmd_group.get_repcap_cmd_value(carrierComponent, repcap.CarrierComponent)
		self._core.io.write(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:CC{carrierComponent_cmd_val}:PLCid {param}')

	def get(self, carrierComponent=repcap.CarrierComponent.Default) -> int:
		"""CONFigure:LTE:MEASurement<Instance>:MEValuation:CC<Nr>:PLCid \n
		Snippet: value: int = driver.configure.multiEval.cc.plcId.get(carrierComponent = repcap.CarrierComponent.Default) \n
		Specifies the physical layer cell ID of component carrier CC<no>. Without carrier aggregation, you can omit <no>.
			INTRO_CMD_HELP: For the combined signal path scenario, use: \n
			- CONFigure:LTE:SIGN<i>:CELL[:PCC]:PCID
			- CONFigure:LTE:SIGN<i>:CELL:SCC<c>:PCID \n
			:param carrierComponent: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Cc')
			:return: phs_layer_cell_id: integer Range: 0 to 503"""
		carrierComponent_cmd_val = self._cmd_group.get_repcap_cmd_value(carrierComponent, repcap.CarrierComponent)
		response = self._core.io.query_str(f'CONFigure:LTE:MEASurement<Instance>:MEValuation:CC{carrierComponent_cmd_val}:PLCid?')
		return Conversions.str_to_int(response)
