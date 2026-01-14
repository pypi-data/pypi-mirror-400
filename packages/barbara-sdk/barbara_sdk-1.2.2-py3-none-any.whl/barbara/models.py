import os
import mimetypes
import json
from enum import Enum
import pandas as pd
from packaging.version import Version
from ._utils import calculate_next_version, calculate_sha, get_file_size, encode_to_base64, zip_folder

# Define constants
_UPLOADED_FROM_BARBARA_CLIENT = 'Model uploaded using Barbara Python SDK'

class MODEL_TYPE(Enum):
    TENSORFLOW_SAVED_MODEL = 0
    ONNX = 1
    PYTORCH_TORCHSCRIPT = 2
    SCIKIT_LEARN = 3
    XGBOOST = 4
    

class ENGINE_TYPE(Enum):
    TENSORFLOW_TFX = 0
    NVIDIA_TRITON = 1
    MLFLOW = 2


model_type_map = {
    0: 'TensorFlow Saved Model',
    1: 'ONNX',
    2: 'PyTorch TorchScript',
    3: 'Scikit-learn',
    4: 'XGBoost'
}

engine_type_map = {
    0: 'TensorFlow TFX',
    1: 'NVIDIA Triton',
    2: 'MLflow'    
}

class Models:
    def __init__(self, api_client):
        """
        ### Description
        Initialize the Models class.
        
        ### Parameters
        * **api_client** (ApiClient): Instance of ApiClient used for making API requests.
        """
        self.api_client = api_client
        """
        Instance of ApiClient used for making API requests.
        """
    
    def _get_latest_version(self, model_id):
        """
        Get the latest version of a model by its ID.
        
        Parameters:
        model_id (str): The ID of the model.
        
        Returns:
        str: The name of the latest version or None if no versions are found.
        """
        # Retrieve all versions of the model
        versions = self._get_versions(model_id)
        
        # If versions are found, get the name of the latest version
        if versions and len(versions) != 0:
            version_name = versions[-1]['name']
        else:
            version_name = None
            self.api_client.log.warning(f"No versions found for model {model_id}.")

        return version_name
    
    def _create(self, model_name, model_type=MODEL_TYPE.TENSORFLOW_SAVED_MODEL, engine=ENGINE_TYPE.TENSORFLOW_TFX):
        """
        Create a new model.
        
        Parameters:
        model_name (str): The name of the model to create.
        model_type (MODEL_TYPE): The type of the model. Default is MODEL_TYPE.TENSORFLOW_SAVED_MODEL.
        engine (ENGINE_TYPE): The engine type. Default is ENGINE_TYPE.TENSORFLOW_TFX.
        
        Returns:
        str: The ID of the created model or None if creation fails.
        """
        # Prepare the endpoint
        endpoint = f"api/v1/models/"
        data = {
            'name': model_name,
            'longDescription': model_name,
            'developer': self.api_client._username,
            'modelType': model_type.value,
            'engine': engine.value
        }
        
        # Make a POST request to create the model
        result = self.api_client._make_request('POST', endpoint, data=data)
        
        # Extract and return the model ID if creation is successful
        if result:
            model_id = result['application']['_id']
        else:
            model_id = None
            self.api_client.log.error(f"Failed to create new model {model_name}.")
        return model_id
    
    def _get(self):
        """
        Retrieve a list of all models.
        
        Returns:
        list: A list of models or None if retrieval fails.
        """
        # Make a GET request to retrieve models
        endpoint = f"api/v1/models/"
        ret = self.api_client._make_request('GET', endpoint)
        if 'modelApplicationList' in ret:
            return ret['modelApplicationList']
        else:
            return None
    
    def _get_id(self, model_name):
        """
        Get the ID of a model by its name.
        
        Parameters:
        model_name (str): The name of the model.
        
        Returns:
        str: The ID of the model or None if not found.
        """
        # Get all the models
        model_list = self._get()
        model_id = None        
        
        # Iterate through the models to find the one with the specified name 
        if model_list:
            for model in model_list:
                if model['name'] == model_name:
                    model_id = model['_id']
        else:
            self.api_client.log.warning(f"No models found.")

        return model_id
    
    def _get_model(self, model_name):
        """
        Get the ID of a model by its name.
        
        Parameters:
        model_name (str): The name of the model.
        
        Returns:
        str: The ID of the model or None if not found.
        """
        # Get all the models
        model_list = self._get()
        modelFound = None        
        
        # Iterate through the models to find the one with the specified name 
        if model_list:
            for model in model_list:
                if model['name'] == model_name:
                    modelFound = model
        else:
            self.api_client.log.warning(f"No models found.")

        return modelFound

    def _get_versions(self, model_id):
        """
        Get all versions of a model by its ID.
        
        Parameters:
        model_id (str): The ID of the model.
        
        Returns:
        list: A list of model versions or None if retrieval fails.
        """
        # Make a GET request to retrieve versions
        endpoint = f"api/v1/models/{model_id}/modelversions"
        ret = self.api_client._make_request('GET', endpoint)
        return ret

    def _get_version_id(self, model_name, version_name):
        """
        Get the ID of a model version by the model name and version name.
        
        Parameters:
        model_name (str): The name of the model.
        version_name (str): The name of the version.
        
        Returns:
        str: The ID of the version or None if not found.
        """
        # Get the ID of the model with the given name
        model_id = self._get_id(model_name)
        version_id = None
        if model_id:
            # If the model ID is found, retrieve all versions of this model
            versions = self._get_versions(model_id)
            
            # Iterate through the versions to find the one with the specified name
            if versions:
                for version in versions:
                    if version['name'] == version_name:
                        version_id = version['_id']
                        break 
            else:
                self.api_client.log.error(f"Failed to retrieve versions of model {model_name}.")
        else:
            self.api_client.log.error(f"Model {model_name} not found.")
        
        # Return the ID of the found version, or None if no matching version was found
        return version_id
    
    def list(self):
        """
        ### Description
        List all models and return them as a DataFrame.
        
        ### Parameters
        No parameters.
        
        ### Returns
        * **df** (pd.DataFrame): Pandas Dataframe containing model details.
        """
        if not self.api_client.check_api_version():
            return None
        
        # Log the command
        self.api_client.log.info(f"Models.list() command executed by the user")
        
        # Get all the models
        models = self._get()
        if models:
            # Create a DataFrame from the list of models            
            df = pd.DataFrame(models)                                                   

            if not df.empty:
                # Replace numeric values with strings
                df['modelType'] = df['modelType'].replace(model_type_map)
                df['engine'] = df['engine'].replace(engine_type_map)

            # Select and rename columns for better readability
            df = df[['_id', 'name', 'developer', 'created', 'modelType', 'engine']]                                    
            
            df = df.rename(columns={'_id': 'Model id', 'name': 'Model name', 'developer': 'Author', 'created': 'Created', 'modelType': 'Model type', 'engine': 'Engine'})

            # Log the number of models retrieved
            self.api_client.log.info(f"List of models retrieved: {len(df.index)} models in total.")
        else:
            # Return an empty DataFrame if no models are found
            df = pd.DataFrame(columns=['Model id', 'Model name', 'Author', 'Created', 'Model type', 'Engine'])
            self.api_client.log.warning(f"No models found.")
        
        # Return the DataFrame containing the list of models
        return df
    
    def list_versions(self, model_name):
        """
        ### Description
        List all versions of a specified model and return them as a DataFrame.
        
        ### Parameters
        * **model_name** (str): The name of the model.
        
        ### Returns
        * **df** (pd.DataFrame): Pandas Dataframe containing versions details.
        """
        if not self.api_client.check_api_version():
            return None

        # Log the command
        self.api_client.log.info(f"Models.list_versions() command executed by the user")
        
        # Get model ID
        model_id = self._get_id(model_name)
        if model_id:
            versions = self._get_versions(model_id)
            if versions:
                # Create a DataFrame from the list of versions
                df = pd.DataFrame(versions)
                
                # Select and rename columns for better readability
                df = df[['_id', 'name', 'size', 'created']]
                df = df.rename(columns={'_id': 'Version id', 'name': 'Version name', 'size': 'Size', 'created': 'Created'})
                self.api_client.log.info(f"List of versions for model {model_name} retrieved: {len(df.index)} versions in total.") 
            else:
                # Return an empty DataFrame if no versions are found
                df = pd.DataFrame(columns=['Version id', 'Version name', 'Size', 'Created'])
                self.api_client.log.warning(f"No versions found for model {model_name}.")
        else:
            # Return an empty DataFrame if the model is not found
            df = pd.DataFrame(columns=['Version id', 'Version name', 'Size', 'Created'])
            self.api_client.log.error(f"Model {model_name} not found.")
            
        # Return the DataFrame containing the list of versions
        return df

    def upload(self, file_path, model_name, version_name=None, model_type=MODEL_TYPE.TENSORFLOW_SAVED_MODEL, engine=ENGINE_TYPE.TENSORFLOW_TFX, release_notes=None):
        """
        ### Description
        Upload a new version of a model.
        
        ### Parameters
        * **file_path** (str): The path to the file to be uploaded.
        * **model_name** (str): The name of the model.
        * **version_name** (str, optional): The name of the version. If not provided, the next version will be calculated.
        * **model_type** (MODEL_TYPE): The type of the model. Default is MODEL_TYPE.TENSORFLOW_SAVED_MODEL.
        * **engine** (ENGINE_TYPE): The engine type. Default is ENGINE_TYPE.TENSORFLOW_TFX.
        
        ### Returns
        * **version_id** (str): The ID of the uploaded version or None if upload fails.
        """
        if not self.api_client.check_api_version():
            return None        
        if engine.value > ENGINE_TYPE.MLFLOW.value:
            self.api_client.log.error(f"Engine type {engine} is not supported in this version.")
            return None
        if model_type.value > MODEL_TYPE.XGBOOST.value:
            self.api_client.log.error(f"Model type {model_type} is not supported in this version.")
            return None


        # Log the command
        self.api_client.log.info(f"Models.upload() command executed by the user")
        model_id = None
        version_id = None
        model = None

        # Get the ID of the model, create it if it does not exist
        model = self._get_model(model_name)
        if model:
            model_id = model['_id']
            if model['modelType'] != model_type.value:
                self.api_client.log.error(f"Model type {model_type} does not match the existing model type.")
                return None
            if model['engine'] != engine.value:
                self.api_client.log.error(f"Engine type {engine} does not match the existing engine type.")
                return None
            
        
        
        if not model_id:
            model_id = self._create(model_name, model_type, engine)        
        
        if model_id:
            # Calculate the next version name if not provided
            if version_name == None:
                current_version_name = self._get_latest_version(model_id)
                version_name = calculate_next_version(current_version_name)
            endpoint = f"api/v1/models/{model_id}/modelversions"

            # Zip the folder if the file is not already a zip file
            if not file_path.endswith('.zip'):
                file_path = zip_folder(file_path)
            file_name = os.path.basename(file_path)
            sha256 = calculate_sha(file_path)
            size = get_file_size(file_path)

            # Create release notes array
            #release_notes_array = list((_UPLOADED_FROM_BARBARA_CLIENT))
            if release_notes:
                release_notes_array = release_notes.strip().splitlines()
            else:                
                release_notes_array = _UPLOADED_FROM_BARBARA_CLIENT.strip().splitlines()                        
            
            data = [
                ('name',    version_name),
                ('sha256',  sha256),
                ('size',    str(size)),     
            ]
            for line in release_notes_array:
                data.append(('releaseNotes[]', line))

            files = {'url': (file_name, open(file_path, 'rb'), mimetypes.guess_type(file_path)[0])}

            # Make a POST request to upload the new version
            result = self.api_client._make_request('POST', endpoint, data=data, files=files)
            if result:
                version_id = result['_id']
                self.api_client.log.info(f"Model {model_name} v{version_name} uploaded successfully.") 
            else:
                version_id = None
                self.api_client.log.error(f"Failed to upload model {model_name}:{version_name}.")
        else:
            self.api_client.log.error(f"Failed to create new model {model_name}.")
        return version_id

    def delete(self, model_name):        
        """
        ### Description
        Delete a model by its name.
        
        ### Parameters
        * **model_name** (str): The name of the model to delete.
        
        ### Returns
        * **model_id** (str): The ID of the deleted model or None if deletion fails.
        """
        if not self.api_client.check_api_version():
            return None

        # Log the command
        self.api_client.log.info(f"Models.delete() command executed by the user")
        
        # Get model ID
        model_id = self._get_id(model_name)
        if model_id:
            # Make a DELETE request to remove the model
            endpoint = f"api/v1/models/{model_id}"
            result = self.api_client._make_request('DELETE', endpoint)
            if result and result == 'Done.':
                self.api_client.log.info(f"Model {model_name} deleted successfully.")
            else:
                model_id = None
                self.api_client.log.error(f"Failed to delete {model_name}.")
        else:
            self.api_client.log.error(f"Model {model_name} not found.")
        
        # Return the model ID
        return model_id

    def _deploy_new_workload(self, node_id, model_id, version_id, engine, grpc_port=9083, rest_port=9084, monitoring_port=9085, autoRun=True, gpu=False):
        """
        ### Description
        Deploy a new model workload on a node.
        
        ### Parameters
        * **node_id** (str): The ID of the node.
        * **model_id** (str): The ID of the model.
        * **version_id** (str): The ID of the model version.
        * **engine** (ENGINE_TYPE): The engine type.
        * **grpc_port** (int): The gRPC port number.
        * **rest_port** (int): The REST API port number.
        * **monitoring_port** (int): The monitoring port number.
        * **autoRun** (bool): Whether to automatically run the model. Default is True.
        * **gpu** (bool): Whether to use GPU. Default is False.
        
        ### Returns
        * **workload_id** (str): The ID of the deployed workload or None if deployment fails.
        """
        # Endpoint for new deployment of the model on the node
        endpoint = f"api/v1/devices/{node_id}/model/workloads"
        
        # Data to be sent in the request
        json_data = {
            'appVersionId': version_id,
            'applicationId': model_id,
            'runDocker': autoRun,
            'forcePull': False,
            'gpu': gpu,
            'appConfig': encode_to_base64('{}'),
            'enableLogs': True,
            'services': [
                {
                    'name': encode_to_base64('modelservice'),
                    'ports': [
                        {
                            'name': encode_to_base64('PORT_NUMBER'),
                            'value': encode_to_base64(str(grpc_port))
                        },
                        {
                            'name': encode_to_base64('REST_API_PORT_NUMBER'),
                            'value': encode_to_base64(str(rest_port))
                        }
                    ],
                    'env': [],
                    'volumes': []
                }    
            ]            
        }

        if engine != ENGINE_TYPE.TENSORFLOW_TFX.value:
            json_data['services'][0]['ports'].append(
                {
                    'name': encode_to_base64('MONITORING_PORT_NUMBER'),
                    'value': encode_to_base64(str(monitoring_port))
                }
            )

        # Make a POST request to deploy the model
        result = self.api_client._make_request('POST', endpoint, json=json.dumps(json_data))

        # Get workload Id
        if result:
            workload_id = result['space']['_id']
        else:
            workload_id = None
        
        # Return the workload id
        return workload_id
        
    def _deploy_update_workload(self, workload_id, node_id, model_id, version_id, engine, grpc_port=9083, rest_port=9084, monitoring_port=9085, autoRun=True, gpu=False):
        """
        Update an existing model workload on a node.
        
        Parameters:
        workload_id (str): The ID of the existing workload.
        node_id (str): The ID of the node.
        model_id (str): The ID of the model.
        version_id (str): The ID of the model version.
        engine (ENGINE_TYPE): The engine type.
        grpc_port (int): The gRPC port number.
        rest_port (int): The REST API port number.
        monitoring_port (int): The monitoring port number.
        autoRun (bool): Whether to automatically run the model. Default is True.
        gpu (bool): Whether to use GPU. Default is False.
        
        Returns:
        str: The ID of the updated workload or None if update fails.
        """
        # Endpoint for updating of the model on the node
        endpoint = f"api/v1/devices/{node_id}/model/workloads/{workload_id}"
        
        # Data to be sent in the request
        json_data = {
            'appVersionId': version_id,
            'applicationId': model_id,
            'runDocker': autoRun,
            'forcePull': False,
            'gpu': gpu,
            'appConfig': encode_to_base64('{}'),
            'enableLogs': True,
            'services': [
                {
                    'name': encode_to_base64('modelservice'),
                    'ports': [
                        {
                            'name': encode_to_base64('PORT_NUMBER'),
                            'value': encode_to_base64(str(grpc_port))
                        },
                        {
                            'name': encode_to_base64('REST_API_PORT_NUMBER'),
                            'value': encode_to_base64(str(rest_port))
                        }
                    ],
                    'env': [],
                    'volumes': []
                } 
            ]            
        }

        if engine != ENGINE_TYPE.TENSORFLOW_TFX.value:
            json_data['services'][0]['ports'].append(
                {
                    'name': encode_to_base64('MONITORING_PORT_NUMBER'),
                    'value': encode_to_base64(str(monitoring_port))
                }
            )
        
        # Make a POST request to deploy the model
        result = self.api_client._make_request('PUT', endpoint, json=json.dumps(json_data))
        
        # Get workload Id
        if result:
            workload_id = result['space']['_id']
        else:
            workload_id = None
        
        # Return the workload ID
        return workload_id

    def deploy(self, node_name, model_name, version_name=None, grpc_port=9083, rest_port=9084, monitoring_port=9085, timeout=300, gpu=False, autoRun=True):
        """
        ### Description
        Deploy a model on a specified node.

        ### Parameters
        * **node_name** (str): Name of the node where the model will be deployed.
        * **model_name** (str): Name of the model to be deployed.
        * **version_name** (str, optional): Name of the version to be deployed. If not provided, the latest version will be deployed.
        * **grpc_port** (int, optional): The gRPC port number. Default is 9083.
        * **rest_port** (int, optional): The REST API port number. Default is 9084.
        * **monitoring_port** (int, optional): The monitoring port number. Not used in Tensorflow over TFX (monitoring is performed through rest_port).  Default is 9085.
        * **timeout** (int, optional): Time to wait for the model to be installed. Default is 300 seconds.
        * **gpu** (bool, optional): Whether to use GPU. Default is False.
        * **autoRun** (bool, optional): Whether to automatically run the model. Default is True.

        ### Returns
        * **workload_id** (str): Workload ID of the deployed model or None if deployment fails.
        """

        if not self.api_client.check_api_version():
            print("Deploying model 2")
            return None

        # Log the command
        self.api_client.log.info(f"Models.deploy() command executed by the user")
        

        # Get the ID of the model
        model = self._get_model(model_name)                

        # Check if the model ID is found
        if model:
            model_id = model['_id']
            engine = model['engine']
            model_type = model['modelType']

            self.api_client.log.debug(f"Model {model_name} Engine: {engine} Model Type: {model_type}")

            # If version_name is not provided, get the latest version
            if not version_name:
                version_name = self._get_latest_version(model_id)
            
            # Get the ID of the specified version
            if version_name:
                version_id = self._get_version_id(model_name, version_name)
                if version_id:
                    # Get the ID of the specified node
                    node_id = self.api_client.nodes._get_id(node_name)
                    
                    # Check if the node ID is found
                    if node_id:
                        # Check if there is already a workload running the model
                        workload_id = self.api_client.workloads._get_id(node_name, model_name)
                        
                        # If the workload exists then update it, otherwise install new workload
                        if workload_id:
                            workload_id = self._deploy_update_workload(workload_id, node_id, model_id, version_id, engine, grpc_port, rest_port, monitoring_port, autoRun, gpu)
                        else:
                            workload_id = self._deploy_new_workload(node_id, model_id, version_id, engine, grpc_port, rest_port, monitoring_port, autoRun, gpu)
                        
                        # Wait for the model to be installed
                        if workload_id:
                            workload_id = self.api_client.workloads._wait_for_workload("install", workload_id, version_id=version_id, timeout=timeout)
                        else:
                            self.api_client.log.error(f"Failed to deploy or update the model {model_name}:{version_name} in node {node_name}.")                        

                        if workload_id:
                            if autoRun:
                                # Ensure the model is running
                                workload_id = self.api_client.workloads._wait_for_workload('start', workload_id, version_id=version_id, timeout=timeout)
                            else:
                                workload_id = self.api_client.workloads._wait_for_workload('stop', workload_id, version_id=version_id, timeout=timeout)
                        else:
                            self.api_client.log.error(f"Timeout exceeded when attempting to deploy or update {model_name}:{version_name} in node {node_name}.")                            
                        
                        if workload_id:
                            self.api_client.log.info(f"Model {model_name}:{version_name} deployed successfully to node {node_name}.")                        
                        else:
                            self.api_client.log.error(f"Timeout exceeded when attempting to start serving {model_name}:{version_name} in node {node_name}.")
                    else:
                        self.api_client.log.error(f"Node {node_name} not found.")
                        workload_id = None
                else:
                    self.api_client.log.error(f"Version {model_name}:{version_name} not found.")
                    workload_id = None
            else:            
                self.api_client.log.error(f"No versions found for model {model_name}.")
                workload_id = None
        else:
            self.api_client.log.error(f"Model {model_name} not found.")
            workload_id = None
        
        # Return the workload ID
        return workload_id

    def get_model_type_name(self, modelType):
        """
        ### Description
        Get the name of the model type from the model type enum.
        
        ### Parameters
        * **modelType** (MODEL_TYPE): The model type enum.
        
        ### Returns
        * **str**: The name of the model type.
        """
        return model_type_map[modelType]
    
    def get_engine_type_name(self, engineType):
        """
        ### Description
        Get the name of the engine type from the engine type enum.
        
        ### Parameters
        * **engineType** (ENGINE_TYPE): The engine type enum.
        
        ### Returns
        * **str**: The name of the engine type.
        """
        return engine_type_map[engineType]