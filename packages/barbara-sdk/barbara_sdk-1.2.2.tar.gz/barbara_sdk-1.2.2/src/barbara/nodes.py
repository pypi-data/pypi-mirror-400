import pandas as pd

class Nodes:
    def __init__(self, api_client):
        """
        ### Description
        Initialize the Nodes class.

        ### Parameters:
        * **api_client** (ApiClient): Instance of ApiClient used for making API requests.
        """
        self.api_client = api_client
        """
        Instance of ApiClient used for making API requests.
        """
    
    def _get(self):
        """
        Retrieve the list of nodes.

        Returns:
        list: A list of nodes retrieved.
        """
        # Make a GET request to retrieve nodes
        endpoint = f"api/v1/devices/"
        response = self.api_client._make_request('GET', endpoint)
        nodes = response['deviceList'] if response and 'deviceList' in response else []
        return nodes
    
    def _get_id(self, node_name):
        """
        Get the ID of a node by its name.

        Parameters:
        node_name (str): The name of the node.

        Returns:
        str: The ID of the node or None if not found.
        """
        # Get the nodes
        nodes = self._get()
        node_id = None
        if nodes:
            # Iterate through the nodes to find the one with the specified name
            for node in nodes:
                if node['name'] == node_name:
                    node_id = node['_id']
                    break
        else:
            self.api_client.log.warning(f"No nodes found.")
        
        # Return the ID of the found node, or None if no matching node was found
        return node_id
    
    def list(self):
        """
        ### Description
        Retrieve and list all nodes, returning them as a pandas DataFrame.

        ### Parameters
        None.

        ### Returns
        * **df** (pd.DataFrame): A Pandas DataFrame containing the list of nodes with columns 'Node id', 'Node name', and 'Created'.
        """
        if not self.api_client.check_api_version():
            return None

        # Log the command
        self.api_client.log.info(f"Nodes.list() command executed by the user")
        
        # Retrieve the list of nodes
        nodes = self._get()
        if nodes:
            # Convert the list of nodes to a DataFrame
            df = pd.DataFrame(nodes)
            
            # Select specific columns for the DataFrame
            df = df[['_id', 'name', 'created']]
            
            # Rename the columns for better readability
            df = df.rename(columns={'_id': 'Node id', 'name': 'Node name', 'created': 'Created'})
            self.api_client.log.info(f"List of nodes retrieved: {len(df.index)} nodes in total.") 
        else:
            # Create an empty DataFrame with the specified columns if no nodes are found
            df = pd.DataFrame(columns=['Node id', 'Node name', 'Created'])
            self.api_client.log.warning(f"No nodes found.")

        # Return the DataFrame containing the list of nodes
        return df
