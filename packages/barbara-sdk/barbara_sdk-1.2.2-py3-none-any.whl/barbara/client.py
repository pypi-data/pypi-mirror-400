import requests
import logging
import time
from .nodes import Nodes
from .models import Models
from .workloads import Workloads
from packaging.version import Version
from dotenv import load_dotenv
import os

# Define constants
_API_KEY_EXPIRY_IN_SECS_DEFAULT = 240
_VERSION = "1.2.2"

class ApiClient:
    def __init__(self, client_id, client_secret, username, password):
        """
        ### Description
        Initialize the ApiClient with the necessary credentials and setup logging.
        
        ### Parameters
        
        * **client_id** (str): The client ID for authentication.
        * **client_secret** (str): The client secret for authentication.
        * **username** (str): The username for authentication.
        * **password** (str): The password for authentication.
        """
        # Set the base URL and token URL for API requests
        # Set the base URL and token URL for API requests                
        # Set up logging for the class
        self.log = logging.getLogger(__name__)
        """
        ApiClient logger instance
        """
        self.log.info(f"Barbara Python SDK. Version {_VERSION}.")

        load_dotenv()

        self._base_url = os.getenv("BBR_BASE_URL", 'https://prod.bap.barbara.tech')
        self._token_url = os.getenv("BBR_TOKEN_URL", 'https://prod.auth.barbara.tech/realms/bbr_prod/protocol/openid-connect/token')                

        self._fix_base_url()

        # Store the provided credentials
        self._client_id = client_id
        self._client_secret = client_secret
        self._username = username
        self._password = password
        
        
        # Initialize the API key timestamp
        self._api_key_timestamp = 0
        self._api_key_expiry_in_secs = _API_KEY_EXPIRY_IN_SECS_DEFAULT 
        # Refresh the API key upon initialization
        self._refresh_api_key()

        # Initialize the API version
        self._api_version = "2.7.0"        
        self._min_library_version = ""
        # Get the API version from the server
        self._get_api_version()
        
        # Initialize instances of Nodes, Models, and Workloads
        self.nodes = Nodes(self)
        """
        Nodes instance
        """
        self.models = Models(self)
        """
        Models instance
        """
        self.workloads = Workloads(self)
        """
        Workloads instance
        """
        return
    
    def check_api_version(self):
        """
        ### Description
        Check if the SDK version is compatible with the API version.
        
        ### Parameters
        None.
        
        ### Returns
        * **is_compatible** (bool): True if the SDK version is compatible with the API version, False otherwise.
        """
        # Log the check_version command
        self.log.debug(f"ApiClient.check_version() command executed by the user")
        
        self.log.debug(f"SDK version: {_VERSION}. API version: {self._api_version}. Minimum Python SDK version: {self._min_library_version}.")
        # Check if the SDK version is compatible with the API version
        is_compatible = self._min_library_version != '' and Version(_VERSION) >= Version(self._min_library_version)
        # Log the compatibility result
        if is_compatible:
            self.log.debug(f"SDK version {_VERSION} is compatible with API version {self._api_version}. Please upgrade to the latest version.")
        else:
            self.log.error(f"SDK version {_VERSION} is not compatible with API version {self._api_version}. Please upgrade to the latest version.")
        
        # Return the compatibility result
        return is_compatible

    def _refresh_api_key(self):
        """
        Refresh the API key by making a request to the token URL.
        
        No parameters.
        
        Returns:
        None
        """
        # Prepare the payload for the request
        params = None
        headers = None
        data = {
            'client_id': self._client_id,
            'grant_type': 'password',
            'client_secret': self._client_secret,
            'username': self._username,
            'password': self._password
            }
        
        # Make a POST request to the token URL and capture any exception
        try:
            response = requests.request('POST', self._token_url, params=params, data=data, headers=headers)
            response.raise_for_status() # Raise an exception for unsuccessful HTTP status codes
            response_json = response.json()
            self.api_key = response_json['access_token']
            if 'expires_in' in response_json:
                self._api_key_expiry_in_secs =  int(response_json['expires_in'] * 0.8)
            self._api_key_timestamp = time.time()
        except KeyError: # Handles the 'response' key error case
            self.log.error(f"Error finding access token field in JSON.")
        except requests.exceptions.JSONDecodeError: # Handles all .json error cases
            self.log.error(f"Error decoding response JSON.")
        except requests.exceptions.HTTPError as errh: # Handles all HTTP error cases, raised by response.raise_for_status()
            self.log.error(f"HTTP error: {errh}.")            
        except requests.exceptions.RequestException as errr: # Handles the rest of .requests error cases
            self.log.error(f"Request exception: {errr}.")
        else:
            self.log.info(f"API Key refreshed.")

        return

    def _make_request(self, method, endpoint, params=None, json=None, data=None, headers=None, files=None):
        """
        Make an HTTP request to the specified endpoint.
        
        Parameters:
        method (str): The HTTP method to use for the request (e.g., 'GET', 'POST').
        endpoint (str): The API endpoint to call.
        params (dict, optional): The query parameters to include in the request.
        json (dict, optional): The JSON data to include in the request body.
        data (dict, optional): The form data to include in the request body.
        headers (dict, optional): The headers to include in the request.
        files (dict, optional): The files to include in the request.
        
        Returns:
        dict: The JSON response from the API call, or None if an error occurs.
        """
        # Get the current time
        current_time = time.time()
        
        # Refresh the API key if it has expired
        if (current_time - self._api_key_timestamp) > self._api_key_expiry_in_secs:
            self._refresh_api_key()
            
        # Construct the full URL for the request
        url = f"{self._base_url}/{endpoint}"
        
        # Add the Authorization header
        headers = headers or {}
        headers['Authorization'] = f"Bearer {self.api_key}"
        
        # If JSON data is provided, use it as the request body and set the Content-Type header
        if json:
            data = json
            headers['Content-Type'] = 'application/json'            

        result = None

        # Make the HTTP request with the specified method and parameters and capture any exception
        try:
            response = requests.request(method, url, params=params, data=data, headers=headers, files=files)
            response.raise_for_status() # Raise an exception for unsuccessful HTTP status codes
            response_json = response.json()
            result = response_json['response']
        except KeyError: # Handles the 'response' key error case
            self.log.error(f"Error finding response field in JSON.")
        except requests.exceptions.JSONDecodeError: # Handles all .json error cases
            self.log.error(f"Error decoding response JSON.")
        except requests.exceptions.HTTPError as errh: # Handles all HTTP error cases, raised by response.raise_for_status()
            self.log.error(f"HTTP error: {errh}.")
            if response.status_code in [400, 499]:
                self.log.debug(f"HTTP error: {response.text}.")
        except requests.exceptions.RequestException as errr: # Handles the rest of .requests error cases
            self.log.error(f"Request exception: {errr}.")
        else:
            self.log.debug(f"HTTP response - Method: {method} - Endpoint: {endpoint} - Result: {result}.")

        # Return the result of the request
        return result

    def get_version(self):
        """
        ### Description
        Log and return the version of the SDK.
        
        ### Parameters
        None.
        
        ### Returns
        * **version** (str): The version of the SDK.
        """
        # Log the SDK version
        self.log.info(f"ApiClient.get_version() command executed by the user")
        self.log.info(f"Barbara Python SDK. Version {_VERSION}.")
        
        # Return the SDK version
        return _VERSION    
    
    def _get_api_version(self):
        """
        ### Description
        Get the API version from the server.
        
        ### Parameters
        None.
        
        ### Returns
        None.
        """        
        # Prepare the payload for the request
        params = None
        headers = None
        data = None

        # Construct the full URL for the request
        url = f"{self._base_url}/api/v1/apiversion"

        # Add the Authorization header
        headers = headers or {}
        headers['Authorization'] = f"Bearer {self.api_key}"                

        response = None
        
        # Make a POST request to the token URL and capture any exception
        try:
            response = requests.request('GET', url, params=params, data=data, headers=headers)
            if response.status_code == 200:                                
                response_json = response.json()['response']
                self._api_version = response_json['version']
                self._min_library_version = response_json['pythonSDKMinVersion']
            else:
                self.log.debug(f"API version not found.")
            response.raise_for_status() # Raise an exception for unsuccessful HTTP status codes
        except KeyError: # Handles the 'response' key error case
            self.log.error(f"Error finding version fieldd in JSON.")
        except requests.exceptions.JSONDecodeError: # Handles all .json error cases
            self.log.error(f"Error decoding response JSON.")
        except requests.exceptions.HTTPError as errh: # Handles all HTTP error cases, raised by response.raise_for_status()                            
            self.log.error(f"HTTP error: {errh}.")            
        except requests.exceptions.RequestException as errr: # Handles the rest of .requests error cases
            self.log.error(f"Request exception: {errr}.")
        else:
            self.log.info(f"API version updated to {self._api_version}. Minimum Python SDK version: {self._min_library_version}.")


        return
    
    def _fix_base_url(self):
        """
        ### Description
        Fix the base URL for the API requests.
        
        ### Parameters
        None.
        
        ### Returns
        None.
        """        
        index = self._base_url.find('barbaraiot.com')
        if self._base_url.find('barbaraiot.com') != -1:
            ping = self._ping(self._base_url)
            if not ping:
                self._base_url = self._base_url.replace('barbaraiot.com', 'barbara.tech')
                self._token_url = self._token_url.replace('barbaraiot.com', 'barbara.tech')
    
    def _ping(self, base_url):
        """
        ### Description
        Ping the server to check if it is reachable.
        
        ### Parameters
        * **base_url** (str): The base URL of the server.
        
        ### Returns
        * **is_reachable** (bool): True if the server is reachable, False otherwise.
        """        
        # Prepare the payload for the request
        params = None
        headers = None
        data = None

        # Construct the full URL for the request
        url = f"{base_url}/api/v1/ping"

        response = None
        ret = False
        
        # Make a POST request to the token URL and capture any exception
        try:
            response = requests.request('GET', url, params=params, data=data, headers=headers, allow_redirects=False)
            if response.status_code == 200:
                ret = True
        except:            
            ret = False                
        
        return ret
        
