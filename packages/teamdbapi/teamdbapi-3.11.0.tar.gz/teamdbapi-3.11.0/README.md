# teamdbapi
This module enables you to easily access the TeamDB Web API.

- Package version: 3.11.0
- TeamDB Web API version: 2.0

## Requirements.

- Python 3.4+
- TeamDB 3.11.0

## Installation and usage
### pip install

Install via  [pip](https://pypi.org/project/pip/).

```sh
pip install teamdbapi
```

Then import the package:
```python
import teamdbapi 
```

## Getting Started

Please follow the installation procedure above and then, depending your TeamDB WebApi configuration, try the following :

### Using the HTTP protocole

```python
import teamdbapi
from teamdbapi.rest import ApiException

# Create a Configuration object
configuration = teamdbapi.Configuration()
configuration.host = "http://localhost:9001" # Replace with your TeamDB API address if different

# Create an instance of the Client API
client_api = teamdbapi.ApiClient(configuration)

# Create an instance of the Assembly API using the client_api
assembly_api = teamdbapi.AssemblyApi(client_api)

# Try to execute the request
try:

    #  Retrieve and print the current assembly before modification
    result = assembly_api.get_current_assembly()
    print(result)

    # Set the desired current assembly, and print the response details
    result = assembly_api.select_current_assembly_with_http_info(assembly_id = "6189993b-ad4d-4c41-8268-8419a63e5554") # Replace with your own valid Assembly id.
    print(result)

    # Retrieve and print the current assembly after modification
    result = assembly_api.get_current_assembly()
    print(result)

except ApiException as e:
    print("Exception when selecting the current assembly : %s\n" % e)
```

### Using the HTTPS protocole

```python
import teamdbapi
from teamdbapi.rest import ApiException

# Create a Configuration object
configuration = teamdbapi.Configuration()
configuration.host = "https://localhost:9001" # Replace with your TeamDB API address if different
configuration.api_key['TDB_API_Key'] = 'user_token' # Replace {user_token} by a valid TeamDB WebApi user token.

# Create an instance of the Client API
client_api = teamdbapi.ApiClient(configuration)

# Create an instance of the Assembly API using the client_api
assembly_api = teamdbapi.AssemblyApi(client_api)

# Try to execute the request
try:

    #  Retrieve and print the current assembly before modification
    result = assembly_api.get_current_assembly()
    print(result)

    # Set the desired current assembly, and print the response details
    result = assembly_api.select_current_assembly_with_http_info(assembly_id = "6189993b-ad4d-4c41-8268-8419a63e5554") # Replace with your own valid Assembly id.
    print(result)

    # Retrieve and print the current assembly after modification
    result = assembly_api.get_current_assembly()
    print(result)

except ApiException as e:
    print("Exception when selecting the current assembly : %s\n" % e)
```

**_NOTE:_** Each method has a detailed version (for example: select_current_assembly => select_current_assembly_with_http_info). This can be useful, for example, if you want to retrieve a detailed response: content, HTTP status code, HTTP header.

## Documentation for API Endpoints

With a TeamDB Client, check the documentation at *http://localhost:9001* (Default value for the TeamDB Web API URL)

## Documentation For Authorization

Endpoints are subject to the same authorization as in TeamDB.

## Author

Trackside Software
support@trackside.fr

