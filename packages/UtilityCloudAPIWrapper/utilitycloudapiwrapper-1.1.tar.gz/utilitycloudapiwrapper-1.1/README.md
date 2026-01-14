# UtilityCloudAPIWrapper

**UtilityCloudAPIWrapper** is a robust Python-based library designed to facilitate seamless interactions with the Utility Cloud API. Its modular design simplifies API requests while integrating advanced configuration management to handle authentication, request validation, and error handling with ease.

---

## Table of Contents
- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## About

This project leverages Python's capabilities to simplify the process of making authenticated requests and managing configurations for the Utility Cloud API. It includes the following key modules:

1. **UtilityCloudAPIWrapper.py**: Contains core classes (`UtilityCloudAPIWrapper`, `EasyReq`, `_UtilityCloudAuth`) to handle API communication, authentication, and error processing.
2. **UCWrapBetterConfig.py**: Extends the `BetterConfig` class to provide default configurations and customizable settings for authentication and API endpoints.

---

## Features

- **Flexible Authentication**: Use `_UtilityCloudAuth` to manage API authentication, key storage, and revalidation workflows.
- **Enhanced Configuration Management**: Easily load and customize API settings using `UCWrapBetterConfig`.
- **Core API Methods**:
  - Retrieve asset and work order details (`GetWorkOrderDetails`).
  - Query work orders (`QueryWorkOrders`).
- **Request Validation**: Simplifies API request validation through `EasyReq`.
- **Error Handling & Logging**: Built-in error extraction, logging, and detailed response handling.

---

## Installation

To begin using `UtilityCloudAPIWrapper`, ensure Python 3.8.9 is installed. Then follow these steps:

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/UtilityCloudAPIWrapper.git
   ```

2. Navigate to the project directory:
   ```bash
   cd UtilityCloudAPIWrapper
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Basic Example
1. Set up the configuration:
   ```python
   from UCWrapBetterConfig.uc_wrap_better_config import UCWrapBetterConfig

   config_manager = UCWrapBetterConfig(config_filename="config.json", config_dir="./config/")
   config_manager.load("config.json")
   ```

2. Initialize the API wrapper:
   ```python
   from UtilityCloudAPIWrapper.utility_cloud_api_wrapper import UtilityCloudAPIWrapper

   api_wrapper = UtilityCloudAPIWrapper(config=config_manager)
   ```

3. Example of querying work orders:
   ```python
   response = api_wrapper.QueryWorkOrders(parameters={"filters": {"status": "open"}})
   print(response)
   ```

---

## Project Structure

Below is a general project structure:


---

## Core Classes and Methods Overview

### UtilityCloudAPIWrapper
The `UtilityCloudAPIWrapper` class provides the main interface for interacting with the Utility Cloud API. Key features include:
- **Methods**:
  - `init_config`: Initialize and validate configuration.
  - `QueryWorkOrders`: Query for work orders with filters.
  - `GetWorkOrderDetails`: Fetch detailed information about work orders.

### _UtilityCloudAuth
Handles authentication and authorization for the Utility Cloud API. Key features include:
- Auto authentication handling (`RunAuth`, `ReadAuth`, `ReqNewAuth`).
- Configuration-based key management.
- Authentication purging (`PurgeAuthKey`, `PurgeAll`).

### EasyReq
Provides a simplified way to make API requests. Key features include:
- Validation of HTTP methods (`_validate_request_method`).
- Custom error processing (`_process_error_response` and `_extract_error_message`).

### UCWrapBetterConfig
An enhanced configuration class that:
- Provides default Utility Cloud API settings (e.g., `base_url` and `auth_runtype_default`).
- Allows override with custom configuration options.

---

## Contributing

Contributions are welcome!
- Fork the repository.
- Create a new branch (`feature/your-feature-name`).
- Commit changes and push to your branch.
- Submit a pull request explaining your changes.

---

## License

The `UtilityCloudAPIWrapper` is licensed under the [MIT License](LICENSE). See `LICENSE` for details.

---

Happy coding! 🚀