from .errors import WorkflowExecutionError
from .client import HashImportClient
from pathlib import Path
from typing import Dict, Callable, Optional, Any
import asyncio

LINKER_OUTPUT_FIELD_NAME = "linked_output"

class WorkflowExecutor:
    def __init__(
        self, 
        multi_part_actions, 
        client: HashImportClient, 
        workflow_metadata, 
        hash_value: str,
        subscribers: Optional[Dict[str, Callable[[str, Any], None]]] = None
    ):
        self.multi_part_actions = multi_part_actions
        self.client = client
        self.workflow_metadata = workflow_metadata
        self.hash_value = hash_value
        self.subscribers = subscribers or {}

    async def execute(self):
        is_linked_field_value = None        
        for action_name, payload in self.workflow_metadata.items():
            
            async def handle_response(response):
                    if response:
                        response_data = response.get("data", {})
                        result = response_data.get("result", {})
                        if isinstance(result, dict) and LINKER_OUTPUT_FIELD_NAME in result:
                            linked_output = result.get(LINKER_OUTPUT_FIELD_NAME)
                            if linked_output:
                                is_linked_field_value = Path(linked_output).name
                    
                    # Call subscriber callback if registered for this action
                    if action_name in self.subscribers:
                        callback = self.subscribers[action_name]
                        if callable(callback):
                            try:
                                # Support both sync and async callbacks
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(action_name, response)
                                else:
                                    callback(action_name, response)
                            except Exception as e:
                                print(f"Error in subscriber callback for {action_name}: {e}")
                    else:
                        print(f"error: {response}")
                        # Call subscriber even on error if registered
                        if action_name in self.subscribers:
                            callback = self.subscribers[action_name]
                            if callable(callback):
                                try:
                                    if asyncio.iscoroutinefunction(callback):
                                        await callback(action_name, response)
                                    else:
                                        callback(action_name, response)
                                except Exception as e:
                                    print(f"Error in subscriber callback for {action_name}: {e}")
            
            if type(payload) == list:
                for item in payload:
                    if is_linked_field_value:
                        for key, value in item.items():
                            if value == "is_link":
                                item[key] = is_linked_field_value                   
                    response = await self._execute_action_async(action_name, item)
                    await handle_response(response)
            else:
                if is_linked_field_value:
                    for key, value in payload.items():
                        if value == "is_link":
                            payload[key] = is_linked_field_value
                # TODO : This is a patch untill we fix the api to use either or of key / value, as of now expects both but manifest has declared only one (key)
                if action_name == "get":
                    if payload.get("key") is not None:
                        print("calling action: ", action_name)
                        payload["value"] = payload["key"]    
                        print("payload: ", payload)      
                response = await self._execute_action_async(action_name, payload)     
                await handle_response(response)
            
            # TODO: Move this to a func - remove later once stable
            # if response:
            #     # Extract linked_output from response to fill in the is_link field for subsequent actions
            #     response_data = response.get("data", {})
            #     result = response_data.get("result", {})
            #     if isinstance(result, dict) and LINKER_OUTPUT_FIELD_NAME in result:
            #         linked_output = result.get(LINKER_OUTPUT_FIELD_NAME)
            #         if linked_output:
            #             is_linked_field_value = Path(linked_output).name
                
            #     # Call subscriber callback if registered for this action
            #     if action_name in self.subscribers:
            #         callback = self.subscribers[action_name]
            #         if callable(callback):
            #             try:
            #                 # Support both sync and async callbacks
            #                 if asyncio.iscoroutinefunction(callback):
            #                     await callback(action_name, response)
            #                 else:
            #                     callback(action_name, response)
            #             except Exception as e:
            #                 print(f"Error in subscriber callback for {action_name}: {e}")
            # else:
            #     print(f"error: {response}")
            #     # Call subscriber even on error if registered
            #     if action_name in self.subscribers:
            #         callback = self.subscribers[action_name]
            #         if callable(callback):
            #             try:
            #                 if asyncio.iscoroutinefunction(callback):
            #                     await callback(action_name, response)
            #                 else:
            #                     callback(action_name, response)
            #             except Exception as e:
            #                 print(f"Error in subscriber callback for {action_name}: {e}")

    async def _execute_action_async(self, action_name, payload):
        if action_name in self.multi_part_actions:
            response = await self.client.execute_action_multipart(self.hash_value, action_name, payload)
        else:
            response = await self.client.execute_action_json(self.hash_value, action_name, payload)
        return response
