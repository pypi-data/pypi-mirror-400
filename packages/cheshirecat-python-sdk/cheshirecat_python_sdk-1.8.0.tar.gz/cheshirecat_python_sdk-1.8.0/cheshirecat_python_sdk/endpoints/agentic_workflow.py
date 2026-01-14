from typing import Dict, Any

from cheshirecat_python_sdk.endpoints.base import AbstractEndpoint
from cheshirecat_python_sdk.models.api.factories import FactoryObjectSettingsOutput, FactoryObjectSettingOutput


class AgenticWorkflowEndpoint(AbstractEndpoint):
    def __init__(self, client: "CheshireCatClient"):
        super().__init__(client)
        self.prefix = "/agentic_workflow"

    def get_agentic_workflows_settings(self, agent_id: str) -> FactoryObjectSettingsOutput:
        """
        Get all agentic workflow settings for the agent with the given ID.
        :param agent_id: The ID of the agent.
        :return: FactoryObjectSettingsOutput, containing the settings for all agentic workflows.
        """
        return self.get(
            self.format_url("/settings"),
            agent_id,
            output_class=FactoryObjectSettingsOutput,
        )

    def get_agentic_workflow_settings(self, agentic_workflow: str, agent_id: str) -> FactoryObjectSettingOutput:
        """
        Get the settings for the agentic workflow with the given name.
        :param agentic_workflow: The name of the agentic workflow.
        :param agent_id: The ID of the agent.
        :return: FactoryObjectSettingOutput, containing the settings for the agentic workflow.
        """
        return self.get(
            self.format_url(f"/settings/{agentic_workflow}"),
            agent_id,
            output_class=FactoryObjectSettingOutput,
        )

    def put_agentic_workflow_settings(
        self, agentic_workflow: str, agent_id: str, values: Dict[str, Any]
    ) -> FactoryObjectSettingOutput:
        """
        Update the settings for the agentic workflow with the given name.
        :param agentic_workflow: The name of the agentic workflow.
        :param agent_id: The ID of the agent.
        :param values: The new settings for the agentic workflow.
        :return: FactoryObjectSettingOutput, containing the updated settings for the agentic workflow.
        """
        return self.put(
            self.format_url(f"/settings/{agentic_workflow}"),
            agent_id,
            output_class=FactoryObjectSettingOutput,
            payload=values,
        )
