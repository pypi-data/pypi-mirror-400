from typing import List

from codemie_tools.base.base_toolkit import DiscoverableToolkit
from codemie_tools.base.models import ToolKit, Tool, ToolSet
from codemie_tools.qa.zephyr.tools import ZephyrGenericTool
from codemie_tools.qa.zephyr.tools_vars import ZEPHYR_TOOL
from codemie_tools.qa.zephyr_squad.tools import ZephyrSquadGenericTool
from codemie_tools.qa.zephyr_squad.tools_vars import ZEPHYR_SQUAD_TOOL
from codemie_tools.qa.xray.tools import XrayGetTestsTool, XrayCreateTestTool, XrayExecuteGraphQLTool
from codemie_tools.qa.xray.tools_vars import (
    XRAY_GET_TESTS_TOOL,
    XRAY_CREATE_TEST_TOOL,
    XRAY_EXECUTE_GRAPHQL_TOOL
)


class QualityAssuranceToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.QUALITY_ASSURANCE
    tools: List[Tool] = [
        Tool.from_metadata(ZEPHYR_TOOL, tool_class=ZephyrGenericTool),
        Tool.from_metadata(ZEPHYR_SQUAD_TOOL, tool_class=ZephyrSquadGenericTool),
        Tool.from_metadata(XRAY_GET_TESTS_TOOL, tool_class=XrayGetTestsTool),
        Tool.from_metadata(XRAY_CREATE_TEST_TOOL, tool_class=XrayCreateTestTool),
        Tool.from_metadata(XRAY_EXECUTE_GRAPHQL_TOOL, tool_class=XrayExecuteGraphQLTool),
    ]
    label: str = ToolSet.QUALITY_ASSURANCE.value


class QualityAssuranceToolkit(DiscoverableToolkit):
    @classmethod
    def get_definition(cls):
        return QualityAssuranceToolkitUI()
