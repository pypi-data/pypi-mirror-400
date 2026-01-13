# Compressed FHIR

A Python library for storing FHIR JSON resources in a compressed form in memory, optimizing memory usage while maintaining fast access to FHIR data.

## Overview

Compressed FHIR is a specialized library that provides efficient memory storage for FHIR (Fast Healthcare Interoperability Resources) JSON resources. It uses zlib or msgpack for compression while ensuring quick access to the stored healthcare data.

## Features

- Efficient memory storage of FHIR resources
- Fast access to compressed FHIR data
- Compatible with standard FHIR JSON formats
- Minimal memory footprint
- Python 3.10+ support

## Installation

You can install the package using pip:

```bash
pip install compressedfhir
```

Or using pipenv:

```bash
pipenv install compressedfhir
```

## Requirements

- Python 3.10 or higher
- msgpack >= 1.0.0
- orjson >= 3.10.16

## Usage

```python
from typing import Any
from collections import OrderedDict

from compressedfhir.fhir.fhir_resource import FhirResource
from compressedfhir.utilities.compressed_dict.v1.compressed_dict_storage_mode import CompressedDictStorageMode


resource1 = FhirResource(
    initial_dict={"resourceType": "Observation", "id": "456"},
    storage_mode=CompressedDictStorageMode.default(),
)

my_dict: OrderedDict[str,Any] = resource1.dict()
my_plain_dict: dict[str, Any] = resource1.to_plain_dict()
my_json: str = resource1.json()

with resource1.transaction():
   assert "email" not in resource1
   assert resource1.get("name") == "Custom Mode User"
   assert resource1.get("active") is True
```

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/icanbwell/compressed-fhir.git
   cd compressed-fhir
   ```

2. Install dependencies using pipenv:
   ```bash
   pipenv install --dev
   ```

3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Docker Support

The project includes Docker support for development and deployment:

```bash
# Build the Docker image
docker build -t compressed-fhir .

# Run using docker-compose
docker-compose up
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Authors

- Imran Qureshi (imran.qureshi@icanbwell.com)

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Project Status

Current status: Beta

The project is under active development. Please check the GitHub repository for the latest updates and changes.
