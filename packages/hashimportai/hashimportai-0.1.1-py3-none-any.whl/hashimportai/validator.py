from .errors import ValidationError


class WorkflowValidator:
    def __init__(self, actions: dict, manifest: dict):
        self.actions = actions["data"]["data"]["nodes"]
        self.manifest = manifest["data"]["data"]["actions"]

        self.executors = []
        for action in self.manifest.values():
            if "executor" in action:
                self.executors.append(action['executor'])
        
    def get_node_inputs_from_manifest(self, node_type: str):
        for action in self.manifest.values():
            if action.get("executor") == node_type:
                return action.get("inputs")
    
    def validate_and_get_workflow_actions_data_structure(self):
        are_all_executors_present = True
        for node in self.actions:
            if node.get("type") not in set(self.executors):                
                are_all_executors_present = False
                break
            
        if not are_all_executors_present:
            raise ValidationError(
                f"Missing required executors: {', '.join(self.executors)}"
            )
            
        return self._get_workflow_actions_data_structure()

    def map_form_data_to_workflow_actions_data_structure_for_repeating_actions(self, form_data: dict, workflow_actions_data_structure: dict):
        exclude_values = {"is_link"}
        
        form_data_keys = form_data.keys()
        workflow_actions_data_structure_keys = workflow_actions_data_structure.keys()
        
        # print(f"form_data: {form_data}")
        
        keys_to_remove_from_workflow_actions_data_structure = set(workflow_actions_data_structure_keys) - set(form_data_keys)
        # print(f"keys_to_remove_from_workflow_actions_data_structure: {keys_to_remove_from_workflow_actions_data_structure}")

        workflow_actions_data_structure_refined = workflow_actions_data_structure.copy()
        for key in keys_to_remove_from_workflow_actions_data_structure:
            workflow_actions_data_structure_refined.pop(key)
            
        for k, v in form_data.items():
            if isinstance(v, list):
                template = workflow_actions_data_structure_refined[k]
                workflow_actions_data_structure_refined[k] = [template.copy() for _ in range(len(v))]
                
        # print(f"workflow_actions_data_structure_refined: {workflow_actions_data_structure_refined}")

        for k, v in workflow_actions_data_structure_refined.items():
            if isinstance(v, list):
                for i in range(len(v)):
                    # print("index: ", i)
                   
                    v[i]["key"] = form_data[k][i]["key"]
                    if form_data[k][i]["value"] not in exclude_values:
                        v[i]["value"] = form_data[k][i]["value"]
                    
                    # print("form data: ", form_data[k][i])
                    # print("workflow data: ", v[i])
            else:
                for key, value in v.items():
                    if value not in exclude_values:
                        v[key] = form_data[k][key]
                
        # print(f"workflow_actions_data_structure_refined (2): {workflow_actions_data_structure_refined}")

        return workflow_actions_data_structure_refined
    
    def map_form_data_to_workflow_actions_data_structure(self, form_data: dict, workflow_actions_data_structure: dict):
        exclude_values = {"is_link"}

        for k, v in workflow_actions_data_structure.items():
            for key, value in v.items():
                if value not in exclude_values:
                    # print(f"key: {k}, key2: {key}")
                    workflow_actions_data_structure[k][key] = form_data[k][key]        
        return workflow_actions_data_structure
       
    def _get_workflow_actions_data_structure(self):
        workflow_actions_data_structure = {}
        try:
            # Lets now get the inputs needed for each action, default all to None and value for linkers only
            
            # This code below will pick the linker id from the database
            # node_inputs = {}
            # for node in self.actions:
            #     required_inputs = self.get_node_inputs_from_manifest(node.get("type"))
            #     def get_value(key, node, value):
            #         # print(f"manifest_node: {value}")
            #         # TODO please move this assumption to a config file
            #         if key == "hashlet_id":
            #             return node.get('data').get(key).get('_id')
            #         elif value.get('is_link'):
            #             return "is_link"
            #         else:
            #             return None
            #     required_inputs_values = {key: get_value(key, node, value) for key, value in required_inputs.items()}
            #     node_inputs[node.get('type')] = required_inputs_values
            # print(f"node_inputs: {node_inputs}")
            
           
            for k, x in self.manifest.items():
                # print(f"x: {x}")
                def get_value(value):
                    if value.get('is_link'):
                        return "is_link"
                    else:
                        return None
                required_inputs_values = {key: get_value(value) for key, value in x.get('inputs').items()}
                workflow_actions_data_structure[k] = required_inputs_values
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(
                f"Error: {e}"
            )
        finally:
            return workflow_actions_data_structure
