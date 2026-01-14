from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MaProtocolCls:
	"""MaProtocol commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("maProtocol", core, parent)

	def set(self, controler: str=None) -> None:
		"""ROUTe:LTE:MEASurement<Instance>:SCENario:MAPRotocol \n
		Snippet: driver.route.scenario.maProtocol.set(controler = 'abc') \n
		Activates the 'Measure@ProtocolTest' scenario and optionally selects the controlling protocol test application.
		The signal routing and analyzer settings are ignored by the measurement application. Configure the corresponding settings
		within the protocol test application used in parallel. \n
			:param controler: string Protocol test application Example: 'Protocol Test1'
		"""
		param = ''
		if controler:
			param = Conversions.value_to_quoted_str(controler)
		self._core.io.write(f'ROUTe:LTE:MEASurement<Instance>:SCENario:MAPRotocol {param}'.strip())
