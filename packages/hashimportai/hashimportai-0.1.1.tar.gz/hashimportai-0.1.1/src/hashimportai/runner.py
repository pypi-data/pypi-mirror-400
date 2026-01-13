from .client import HashImportClient
from .validator import WorkflowValidator
from .executor import WorkflowExecutor
from typing import Dict, Callable, Optional, Any

class WorkflowRunner:
    def __init__(
        self, 
        workflow_id: str, 
        multi_part_actions: list, 
        subscribers: Optional[Dict[str, Callable[[str, Any], None]]] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize WorkflowRunner
        
        Args:
            workflow_id: ID of the workflow to execute
            multi_part_actions: List of action names that require multipart uploads
            subscribers: Optional dict mapping action names to callback functions
            api_key: Optional API key (passed to HashImportClient)
            base_url: Optional base URL (passed to HashImportClient)
        """
        self.workflow_id = workflow_id
        self.client = HashImportClient(api_key=api_key, base_url=base_url)
        self.multi_part_actions = multi_part_actions
        self.subscribers = subscribers or {}

    async def run(self, hash_value: str, form_data: dict):
        try:
            manifest_data = await self.client.fetch_manifest(hash_value)
            workflow_data = await self.client.fetch_workflow(self.workflow_id)
            
            validator = WorkflowValidator(workflow_data, manifest_data)
            # this is from manifest
            workflow_actions_data_structure = validator.validate_and_get_workflow_actions_data_structure()            
            # print(f"workflow_actions_data_structure: {workflow_actions_data_structure}")
            
            form_data_contains_list = any(isinstance(value, list) for value in form_data.values())
            if form_data_contains_list:
                # print(f"form_data_contains_list: {form_data_contains_list}")
                workflow_actions_data_structure_refined = validator.map_form_data_to_workflow_actions_data_structure_for_repeating_actions(form_data, workflow_actions_data_structure)
            else:
                workflow_actions_data_structure_refined = validator.map_form_data_to_workflow_actions_data_structure(form_data, workflow_actions_data_structure)
                       
            executor = WorkflowExecutor(
                self.multi_part_actions, 
                self.client, 
                workflow_actions_data_structure_refined, 
                hash_value,
                subscribers=self.subscribers
            )
            await executor.execute()
        except Exception as e:
            print(f"Error running workflow: {e}")
            raise e
