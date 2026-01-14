# Barbara-sdk: Python SDK for Barbara Edge Computing Platform

Deploy your machine learning models to the edge with the Barbara Python SDK. This intuitive library empowers you to streamline your workflow and accelerate edge AI development.

## Features

* **Seamless Uploads**: Upload your models directly from Python code or Jupyter Notebooks to your Barbara model library.
* **Simplified Deployment**: Deploy models directly to edge nodes with just a few lines of code.
* **Enhanced Efficiency**: Automate model training & deployment tasks and save valuable development time.
* **Streamlined Workflow**: Integrate edge AI development seamlessly into your existing Python environment.

## Prerequisites

* Python (version 3.8 or higher)

## Barbara API Credentials

To use this SDK you will need the following credentials:

* **Username**: Your Barbara *username*.
* **Password**: Your Barbara *password*.
* **Client Secret**: This credential is only available for users with an **Enterprise License**.
* **Client Id**: This credential is only available for users with an **Enterprise License**.

### Obtaining Enterprise Credentials

If you have an Enterprise License and require the Client Secret and Client ID, please contact Barbara support by sending an email to [support@barbara.tech](mailto:support@barbara.tech).

### Security Note

We **strongly recommend** storing your username and password securely and **avoiding embedding them directly in your code**. Consider using environment variables or a secure credential management solution.

## Installation with pip

```console
pip install barbara-sdk
```

## Usage

### Import the SDK:

```python
import barbara
```

### Create an instance of the SDK

```python
bbr = barbara.ApiClient('client_id', 'client_secret', 'username', 'password')
```

Replace 'client_id', 'client_secret', 'username' and 'password' with your actual API credentials.

### Uploading models to your Library

- Tensorflow over TFX

```python
bbr.models.upload('model_path', 'model_name')
```
or
```python
bbr.models.upload('model_path', 'model_name', model_type=barbara.MODEL_TYPE=TENSORFLOW_SAVED_MODEL, engine=barbara.ENGINE_TYPE.TENSORFLOW_TFX)
```

- Tensorflow over NVIDIA Triton

```python
bbr.models.upload('model_path', 'model_name', model_type=barbara.MODEL_TYPE.TENSORFLOW_SAVED_MODEL, engine=barbara.ENGINE_TYPE.NVIDIA_TRITON)
```

- Torchscript over NVIDIA Triton

```python
bbr.models.upload('model_path', 'model_name', model_type=barbara.MODEL_TYPE.PYTORCH_TORCHSCRIPT, engine=barbara.ENGINE_TYPE.NVIDIA_TRITON)
```

- Onnx over NVIDIA Triton

```python
bbr.models.upload('model_path', 'model_name', model_type=barbara.MODEL_TYPE.ONNX, engine=barbara.ENGINE_TYPE.NVIDIA_TRITON)
```

### Listing models in your Library

```python
bbr.models.list()
```

### Listing Edge Nodes

```python
bbr.nodes.list()
```

### Deploy a model to an Edge Node

```python
bbr.models.deploy('edge_node_name', 'model_name')
bbr.models.deploy('edge_node_name', 'model_over_tfx_name', grpc_port=9000, rest_port=9001)
bbr.models.deploy('edge_node_name', 'model_over_nvidia_triton_name', grpc_port=9000, rest_port=9001, monitoring_port=9002)
bbr.models.deploy('edge_node_name', 'model_over_mlflow_name', grpc_port=9000, rest_port=9001, monitoring_port=9002, release_notes='-Added new classes\n-Improved performance')
```

### Deploy a model to an Edge Node with GPU

```python
bbr.models.deploy('edge_node_name', 'model_name', gpu=True)
```

## Documentation

For detailed API reference and code examples, please refer to Barbara Academy



## License

See the [LICENSE](./_LICENSE) file for details.