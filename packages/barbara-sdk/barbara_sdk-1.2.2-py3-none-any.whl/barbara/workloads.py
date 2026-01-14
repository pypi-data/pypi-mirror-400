import math
import time
import pandas as pd

class Workloads:
    def __init__(self, api_client):
        """
        ### Description
        Initialize the Workloads class.

        ### Parameters
        * **api_client** (ApiClient): Instance of ApiClient used for making API requests.
        """
        self.api_client = api_client
        """
        Instance of ApiClient used for making API requests.
        """
    
    def _get(self, filter=None, search=None):
        """
        Retrieve the list of running workloads.

        Parameters:
        filter (str, optional): The filter to apply to the workloads.
        search (str, optional): The search query to apply to the workloads.

        Returns:
        list: A list of running workloads retrieved, or None if not found.
        """
        # Prepare endpoint and make GET request
        endpoint = "api/v1/devices/applications/running" #?filter={filter}&search={search}"
        if filter or search:
            endpoint += "?"
            if filter:
                endpoint += f"filter={filter}"
                if search:
                    endpoint += "&"
            if search:
                endpoint += f"search={search}"                
        result = self.api_client._make_request('GET', endpoint)
        workloads = None                
        if result:
            workloads = result['appsRunning']
            
        # Return list of workloads
        return workloads
    
    def _get_id(self, node_name, model_name, version_name=None):
        """
        Get the ID of a workload by node name, model name, and optionally version name.

        Parameters:
        node_name (str): The name of the node.
        model_name (str): The name of the model.
        version_name (str, optional): The name of the version.

        Returns:
        str: The ID of the workload or None if not found.
        """
        # Get workloads
        workloads = self._get()
        workload_id = None
        if workloads:
            # Iterate through the workloads to find the one with the specified names
            for workload in workloads:
                if node_name == workload['deviceName'] and model_name == workload['applicationName']:
                    workload_id = workload['spaceId']
                    if version_name and version_name == workload["appVersionName"]:
                        workload_id = workload['spaceId']
                        break
        else:
            self.api_client.log.warning(f"No workloads found.")
        
        # Return the workload ID or None if not found
        return workload_id
    
    def _get_node_id(self, workload_id):
        """
        Get the ID of a node by workload ID.

        Parameters:
        workload_id (str): The ID of the workload.

        Returns:
        str: The ID of the node or None if not found.
        """
        # Get workloads
        workloads = self._get()
        node_id = None
        if workloads:
            # Iterate through the workloads to find the one with the specified workload ID
            for workload in workloads:
                if workload_id == workload['spaceId']:
                    node_id = workload['deviceId']
                    break
        else:
            self.api_client.log.warning(f"No workloads found.")
            
        # Return the node ID or None if not found
        return node_id
    
    def _get_readable_status(self, workload):
        """
        Get the readable status message of a workload.

        Parameters:
        workload (dict): The workload dictionary.

        Returns:
        str: The readable status message.
        """
        return workload['spaceStatus']['status'][-1]['msg']
    
    def _wait_for_workload(self, action, workload_id, version_id=None, timeout=400):
        """
        Wait for a workload to reach a desired state based on the action.

        Parameters:
        action (str): The action to wait for ('install', 'start', 'stop', 'remove').
        workload_id (str): The ID of the workload.
        version_id (str, optional): The ID of the version.
        timeout (int, optional): The maximum time to wait in seconds.

        Returns:
        str: The workload ID if the action was successful, or None if timed out.
        """
        # Set waiting and retry parameters
        waiting_criteria_satisfied = False
        retries_step_size = 5  # Seconds
        retries_max = math.ceil(timeout / retries_step_size)
        
        # Loop until the waiting criteria is satisfied or timeout
        for retry in range(retries_max):
            workloads = self._get()                        
            
            if action == 'install':
                if workloads:
                    for workload in workloads:
                        if workload['_id'] == workload_id and version_id and workload['appVersionId'] == version_id:
                            waiting_criteria_satisfied = True
            elif action == 'start':
                if workloads:
                    for workload in workloads:
                        workload_status = self._get_readable_status(workload)
                        if workload['_id'] == workload_id and workload_status == 'Started':
                            waiting_criteria_satisfied = True
            elif action == 'stop':
                if workloads:
                    for workload in workloads:
                        workload_status = self._get_readable_status(workload)
                        if workload['_id'] == workload_id and workload_status == 'Stopped':
                            waiting_criteria_satisfied = True
            elif action == 'remove':
                if workloads:
                    workload_deleted = True
                    for workload in workloads:
                        if workload['_id'] == workload_id:
                            workload_deleted = False
                    if workload_deleted:
                        waiting_criteria_satisfied = True
                else:
                    waiting_criteria_satisfied = True

            if waiting_criteria_satisfied:
                break
            
            # Wait before the next retry
            self.api_client.log.debug(f"Waiting for {action} command. Retry number {retry + 1} of {retries_max}.")
            time.sleep(retries_step_size)
        
        # Return the workload ID if the action was successful, or None if timed out
        if not waiting_criteria_satisfied:
            workload_id = None
        return workload_id

    def list(self):
        """
        ### Description
        Retrieve and list all workloads, returning them as a pandas DataFrame.

        ### Parameters
        None.

        ### Returns
        * **df** (pd.DataFrame): A Pandas DataFrame containing the list of workloads with columns:
            * 'Workload id'
            * 'Type'
            * 'Name'
            * 'Version name'
            * 'Status'
            * 'Node name'.
            * 'Model type'
            * 'Engine'
        """
        if not self.api_client.check_api_version():
            return None

        # Log the command
        self.api_client.log.info(f"Workloads.list() command executed by the user")
        
        # Get workloads
        workloads = self._get()
        if workloads:
            # Iterate through each workload to get status and type            
            for workload in workloads:
                workload['status'] = self._get_readable_status(workload)
                if workload['type'] == 0:
                    workload['typeText'] = "Docker app"
                    workload['modelType'] = "N/A"
                    workload['engine'] = "N/A"
                elif workload['type'] == 1:
                    workload['typeText'] = "Marketplace app"
                    workload['modelType'] = "N/A"
                    workload['engine'] = "N/A"
                elif workload['type'] == 2:
                    workload['typeText'] = "Model"
                    workload['modelType'] = self.api_client.models.get_model_type_name(workload['modelType'])
                    workload['engine'] = self.api_client.models.get_engine_type_name(workload['engine'])
                
                
            
            # Convert the list of workloads to a DataFrame
            df = pd.DataFrame(workloads)
            
            # Select specific columns for the DataFrame
            df = df[['_id', 'typeText', 'applicationName', 'appVersionName', 'status', 'deviceName', 'modelType', 'engine', 'gpu']]
            
            # Rename the columns for better readability
            df = df.rename(columns={'_id': 'Workload id', 'typeText': 'Type', 'applicationName': 'Name', 'appVersionName': 'Version name', 'status': 'Status', 'deviceName': 'Node name', 'modelType': 'Model type', 'engine': 'Engine', 'gpu': 'GPU'})
            self.api_client.log.info(f"List of workloads retrieved: {len(df.index)} workloads in total.")
        else:
            # Create an empty DataFrame with the specified columns if no nodes are found
            df = pd.DataFrame(columns=['Workload id', 'Type', 'Name', 'Version name', 'Status', 'Node name', 'Model type', 'Engine', 'GPU'])
            self.api_client.log.warning(f"No workloads found.")
        
        return df

    def start(self, workload_id, timeout=120):
        """
        ### Description
        Start a workload by its ID and wait for it to reach the 'Started' state.

        ### Parameters
        * **workload_id** (str): The ID of the workload to start.
        * **timeout** (int, optional): The maximum time to wait for the workload to start in seconds.

        ### Returns
        * **workload_id** (str): The workload ID if started successfully, or None if failed or timed out.
        """
        if not self.api_client.check_api_version():
            return None

        # Log the command
        self.api_client.log.info(f"Workloads.start() command executed by the user")
        
        # Get the node ID
        node_id = self._get_node_id(workload_id)
        if node_id:
            # Send the start request
            endpoint = f"api/v1/devices/{node_id}/workloads/{workload_id}/start"
            result = self.api_client._make_request('POST', endpoint)
            if result and result == 'Done.':
                # Wait for the workload to start
                return_workload_id = self._wait_for_workload("start", workload_id, timeout=timeout)
                if return_workload_id:
                    self.api_client.log.info(f"Workload {workload_id} started successfully.")
                else:
                    self.api_client.log.error(f"Timeout exceeded when attempting to start workload {workload_id}.")
            else:
                return_workload_id = None
                self.api_client.log.error(f"Failed to start workload {workload_id}.")
        else:
            return_workload_id = None
            self.api_client.log.error(f"Workload {workload_id} not found.")
        
        # Return the workload ID if started successfully, or None if failed or timed out
        return return_workload_id
    
    def stop(self, workload_id, timeout=120):
        """
        ### Description
        Stop a workload by its ID and wait for it to reach the 'Stopped' state.

        ### Parameters
        * **workload_id** (str): The ID of the workload to stop.
        * **timeout** (int, optional): The maximum time to wait for the workload to stop in seconds.

        ### Returns
        * **workload_id** (str): The workload ID if stopped successfully, or None if failed or timed out.
        """
        if not self.api_client.check_api_version():
            return None

        # Log the command
        self.api_client.log.info(f"Workloads.stop() command executed by the user")

        # Get the node ID
        node_id = self._get_node_id(workload_id)
        if node_id:
            # Send the stop request
            endpoint = f"api/v1/devices/{node_id}/workloads/{workload_id}/stop"
            result = self.api_client._make_request('POST', endpoint)
            if result and result == 'Done.':
                # Wait for the workload to stop
                return_workload_id = self._wait_for_workload("stop", workload_id, timeout=timeout)
                if return_workload_id:
                    self.api_client.log.info(f"Workload {workload_id} stopped successfully.")
                else:
                    self.api_client.log.error(f"Timeout exceeded when attempting to stop workload {workload_id}.")
            else:
                return_workload_id = None
                self.api_client.log.error(f"Failed to stop workload {workload_id}.")
        else:
            return_workload_id = None
            self.api_client.log.error(f"Workload {workload_id} not found.")

        # Return the workload ID if stopped successfully, or None if failed or timed out
        return return_workload_id
    
    def remove(self, workload_id, timeout=120):
        """
        ### Description
        Remove a workload by its ID and wait for it to be completely removed.

        ### Parameters
        * **workload_id** (str): The ID of the workload to remove.
        * **timeout** (int, optional): The maximum time to wait for the workload to be removed in seconds.

        ### Returns
        * **workload_id** (str): The workload ID if removed successfully, or None if failed or timed out.
        """
        if not self.api_client.check_api_version():
            return None

        # Log the command
        self.api_client.log.info(f"Workloads.remove() command executed by the user")

        # Get the node ID
        node_id = self._get_node_id(workload_id)
        if node_id:
            # Send the remove request
            endpoint = f"api/v1/devices/{node_id}/workloads/{workload_id}"
            result = self.api_client._make_request('DELETE', endpoint)
            if result and result == 'Done.':
                # Wait for the workload to be removed
                return_workload_id = self._wait_for_workload("remove", workload_id, timeout=timeout)
                if return_workload_id:
                    self.api_client.log.info(f"Workload {workload_id} removed successfully.")
                else:
                    self.api_client.log.error(f"Timeout exceeded when attempting to remove workload {workload_id}.")
            else:
                return_workload_id = None
                self.api_client.log.error(f"Failed to remove workload {workload_id}.")
        else:
            return_workload_id = None
            self.api_client.log.error(f"Workload {workload_id} not found.")

        # Return the workload ID if removed successfully, or None if failed or timed out
        return return_workload_id
    
    def prune_volumes(self, node_name):
        """
        ### Description
        Prune unused volumes on a node.

        ### Parameters
        * **node_name** (str): The name of the node to prune volumes on.                
        """
        if not self.api_client.check_api_version():
            return None

        # Log the command
        self.api_client.log.info(f"Workloads.prune_volumes() command executed by the user")

        # Get the node ID
        node_id = self.api_client.nodes._get_id(node_name)
        if node_id:
            # Send the remove request
            endpoint = f"api/v1/devices/{node_id}/docker/actions/prunevolumes"
            self.api_client._make_request('POST', endpoint)            
        else:
            self.api_client.log.error(f"Node {node_name} not found.")

        return
