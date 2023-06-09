# luncho_python
Use luncho.ts and luncho.py rather than LunchoAPI.ts and others.

This Python package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: 0.0.1
- Package version: 1.0.0
- Build package: org.openapitools.codegen.languages.PythonClientCodegen

## Requirements.

Python >= 3.6

## Installation & Usage
### pip install

If the python package is hosted on a repository, you can install directly using:

```sh
pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git`)

Then import the package:
```python
import luncho_python
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import luncho_python
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import time
import luncho_python
from pprint import pprint
from luncho_python.api import luncho_api
from luncho_python.model.http_validation_error import HTTPValidationError
from luncho_python.model.luncho_data import LunchoData
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = luncho_python.Configuration(
    host = "http://localhost"
)



# Enter a context with an instance of the API client
with luncho_python.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = luncho_api.LunchoApi(api_client)
    
    try:
        # All Luncho Data
        api_response = api_instance.all_luncho_data()
        pprint(api_response)
    except luncho_python.ApiException as e:
        print("Exception when calling LunchoApi->all_luncho_data: %s\n" % e)
```

## Documentation for API Endpoints

All URIs are relative to *http://localhost*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*LunchoApi* | [**all_luncho_data**](docs/LunchoApi.md#all_luncho_data) | **GET** /v1/all-luncho-data | All Luncho Data
*LunchoApi* | [**countries**](docs/LunchoApi.md#countries) | **GET** /v1/countries | Countries
*LunchoApi* | [**country_code**](docs/LunchoApi.md#country_code) | **GET** /v1/country-code | Country Code
*LunchoApi* | [**health**](docs/LunchoApi.md#health) | **GET** /v1/health | Health
*LunchoApi* | [**luncho_data**](docs/LunchoApi.md#luncho_data) | **GET** /v1/luncho-data | Luncho Data


## Documentation For Models

 - [HTTPValidationError](docs/HTTPValidationError.md)
 - [LunchoData](docs/LunchoData.md)
 - [ValidationError](docs/ValidationError.md)


## Documentation For Authorization

 All endpoints do not require authorization.

## Author




## Notes for Large OpenAPI documents
If the OpenAPI document is large, imports in luncho_python.apis and luncho_python.models may fail with a
RecursionError indicating the maximum recursion limit has been exceeded. In that case, there are a couple of solutions:

Solution 1:
Use specific imports for apis and models like:
- `from luncho_python.api.default_api import DefaultApi`
- `from luncho_python.model.pet import Pet`

Solution 2:
Before importing the package, adjust the maximum recursion limit as shown below:
```
import sys
sys.setrecursionlimit(1500)
import luncho_python
from luncho_python.apis import *
from luncho_python.models import *
```

