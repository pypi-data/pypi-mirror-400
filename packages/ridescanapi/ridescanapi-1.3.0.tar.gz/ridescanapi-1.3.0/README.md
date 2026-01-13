# RideScan Python SDK

The official Python client for the **RideScan Safety Layer API**. This SDK allows developers to programmatically manage robots, missions, and file uploads, and retrieve risk scores directly from their Python applications.

## Installation

```bash
pip install ridescanapi

```

## Getting Started

### 1. Obtain your API Key

To use this SDK, you must have a valid API Key.

1. Go to the **RideScan Developer Console**.
2. **Create an account** or Log in.
3. Navigate to the **API Keys** section in your dashboard.
4. Click **Generate New Key**.
5. Copy the key (it starts with `rsk_...`).

### 2. Initialize the Client

You can use the client as a context manager (recommended) to automatically handle session closing, or as a standard object.

**Using Context Manager (Recommended):**

```python
from ridescanapi import RideScanClient

API_KEY = "rsk_your_api_key_here"

with RideScanClient(api_key=API_KEY) as client:
    # Your code here
    robots = client.get_robots()
    print(robots)

```

**Using Standard Initialization:**

```python
client = RideScanClient(api_key=API_KEY)
try:
    robots = client.get_robots()
finally:
    client.session.close() # Always close the session manually

```

---

## API Reference

### Robot Resources

#### `create_robot(name, robot_type)`

Registers a new robot in the system.

* **Arguments:**
* `name` (str): A friendly name for the robot (e.g., "Warehouse-Spot-01").
* `robot_type` (str or int): The type identifier (e.g., `"SPOT"`, `"UR6"`).


* **Sample Usage:**

```python
response = client.create_robot(
    name="Warehouse-Spot-01",
    robot_type="SPOT"
)
print(response)

```

* **Returns:** `dict`

```json
{
  "robot_id": "123e4567-e89b-12d3-a456-426614174000",
  "robot_name": "Warehouse-Spot-01",
  "message": "Robot created"
}

```

#### `get_robots(robot_id=None, name=None, robot_type=None)`

Search for robots matching specific criteria. If no arguments are provided, returns all robots.
*(Note: This uses a POST request internally to support secure filtering).*

* **Arguments:**
* `robot_id` (str, optional): Search by specific UUID.
* `name` (str, optional): Filter by name.
* `robot_type` (str, optional): Filter by type.


* **Sample Usage:**

```python
# Get all robots
all_robots = client.get_robots()

# Filter by type
spot_robots = client.get_robots(robot_type="SPOT")

# Get specific robot by ID
specific_robot = client.get_robots(robot_id="123e4567-e89b-12d3-a456-426614174000")

```

* **Returns:** `List[dict]`

#### `edit_robot(robot_id, new_name=None, new_type=None)`

Updates a robot's details.

* **Arguments:**
* `robot_id` (str): The UUID of the robot to update.
* `new_name` (str, optional): New name.
* `new_type` (str or int, optional): New type.


* **Sample Usage:**

```python
updated_robot = client.edit_robot(
    robot_id="123e4567-e89b-12d3-a456-426614174000",
    new_name="Warehouse-Spot-02-Renamed"
)

```

* **Returns:** `dict` (Updated robot object).

#### `delete_robot(robot_id)`

Permanently deletes a robot and **all** associated missions and files.

* **Arguments:** `robot_id` (str).
* **Sample Usage:**

```python
client.delete_robot(robot_id="123e4567-e89b-12d3-a456-426614174000")

```

* **Returns:** `dict` (`{"message": "Robot deleted"}`).

---

### Mission Resources

#### `create_mission(robot_id, mission_name)`

Creates a new mission scope under a specific robot.

* **Arguments:**
* `robot_id` (str): The UUID of the parent robot.
* `mission_name` (str): Descriptive name (e.g., "Calibration-Run-Jan").


* **Sample Usage:**

```python
mission = client.create_mission(
    robot_id="123e4567-e89b-12d3-a456-426614174000",
    mission_name="Site-Inspection-Alpha"
)
print(f"New Mission ID: {mission['mission_id']}")

```

* **Returns:** `dict` containing `mission_id`.

#### `get_missions(robot_id=None, mission_id=None, mission_name=None, ...)`

Search for missions.
*(Note: This uses a POST request internally to support advanced filtering).*

* **Arguments:**
* `robot_id` (str, optional): Filter by robot.
* `mission_id` (str, optional): Filter by mission UUID.
* `mission_name` (str, optional): Filter by name.
* `start_time` / `end_time` (str, optional): Filter by date range (ISO format).


* **Sample Usage:**

```python
# Get all missions for a specific robot
robot_missions = client.get_missions(
    robot_id="123e4567-e89b-12d3-a456-426614174000"
)

# Search by mission name
specific_mission = client.get_missions(
    mission_name="Calibration-Run-Jan"
)

```

* **Returns:** `List[dict]`.

#### `edit_mission(robot_id, mission_id, new_name)`

Renames an existing mission.

* **Arguments:** `robot_id`, `mission_id`, `new_name`.
* **Sample Usage:**

```python
client.edit_mission(
    robot_id="123e4567-e89b-12d3-a456-426614174000",
    mission_id="987fcdeb-51a2-12d3-a456-426614174000",
    new_name="Site-Inspection-Beta"
)

```

* **Returns:** `dict` (Updated mission object).

#### `delete_mission(robot_id, mission_id)`

Permanently deletes a mission.

* **Arguments:** `robot_id`, `mission_id`.
* **Sample Usage:**

```python
client.delete_mission(
    robot_id="123e4567-e89b-12d3-a456-426614174000",
    mission_id="987fcdeb-51a2-12d3-a456-426614174000"
)

```

* **Returns:** `dict`.

---

### File Resources

#### `upload_files(robot_id, mission_id, file_paths, file_type='calib_file')`

Bulk uploads files (.bag, .csv, .zip) to the server. This handles large file streaming automatically.

* **Arguments:**
* `robot_id` (str): Robot UUID.
* `mission_id` (str): Mission UUID.
* `file_paths` (List[str]): List of **absolute local paths** to the files.
* `file_type` (str):
* `'calib_file'` (Default) - Use for model training/calibration.
* `'process_file'` - Use for inference/risk analysis.




* **Sample Usage:**

```python
# Upload calibration data
result = client.upload_files(
    robot_id="123e4567-e89b-12d3-a456-426614174000",
    mission_id="987fcdeb-51a2-12d3-a456-426614174000",
    file_paths=["/path/to/data/run1.bag", "/path/to/data/run2.csv"],
    file_type="calib_file"
)
print(f"Uploaded: {result['uploaded_files']}")

```

* **Returns:** `dict`

```json
{
  "success": true,
  "uploaded_files": ["uuid_day1.bag", "uuid_day2.bag"],
  "failed_files": []
}

```

#### `list_files(robot_id, mission_id)`

Lists all files uploaded for a specific mission.

* **Arguments:** `robot_id`, `mission_id`.
* **Sample Usage:**

```python
files = client.list_files(
    robot_id="123e4567-e89b-12d3-a456-426614174000",
    mission_id="987fcdeb-51a2-12d3-a456-426614174000"
)
for file in files:
    print(f"File: {file['original_filename']} (ID: {file['unique_filename']})")

```

* **Returns:** `List[dict]` containing `unique_filename`, `original_filename`, `file_size`, etc.

#### `delete_file(robot_id, mission_id, unique_filename)`

Deletes a specific file from storage and database.

* **Arguments:**
* `robot_id` (str): Robot UUID.
* `mission_id` (str): Mission UUID.
* `unique_filename` (str): The unique ID returned by `list_files` (e.g., `abc123_data.csv`).


* **Sample Usage:**

```python
client.delete_file(
    robot_id="123e4567-e89b-12d3-a456-426614174000",
    mission_id="987fcdeb-51a2-12d3-a456-426614174000",
    unique_filename="550e8400-e29b-41d4-a716-446655440000_data.bag"
)

```

* **Returns:** `dict`.

---

### Model & Inference Resources

#### `calibrate_model(robot_id, mission_id, epochs=100, robot_type="SPOT", retrain=False, ...)`

Triggers an asynchronous Kubernetes job to train a model using uploaded **calibration files**.

* **Arguments:**
* `robot_id` (str): Robot UUID.
* `mission_id` (str): Mission UUID.
* `epochs` (int): Training duration (Default: 100).
* `robot_type` (str or int): Robot type identifier (Default: `"SPOT"`).
* `retrain` (bool): Force re-training if a model already exists (Default: `False`).
* `file_names` (List[str], optional): specific subset of unique filenames to use. If `None`, uses all uploaded calibration files.


* **Sample Usage:**

```python
training_response = client.calibrate_model(
    robot_id="123e4567-e89b-12d3-a456-426614174000",
    mission_id="987fcdeb-51a2-12d3-a456-426614174000",
    epochs=200,
    robot_type="SPOT",
    retrain=True
)
print(f"Task Queued: {training_response['message']}")

```

* **Returns:** `dict` indicating the task was queued.

```json
{
  "message": "Training task queued",
  "details": {"task_id": "..."}
}

```

#### `run_inference(robot_id, mission_id, file_names=None, device='cpu')`

Runs risk analysis on uploaded **inference files** using the trained model.

* **Arguments:**
* `robot_id` (str): Robot UUID.
* `mission_id` (str): Mission UUID.
* `device` (str): Compute device (`'cpu'` or `'cuda'`).
* `file_names` (List[str], optional): specific subset of unique filenames to analyze. If `None`, uses all available files.


* **Sample Usage:**

```python
# Run inference on GPU
inference_results = client.run_inference(
    robot_id="123e4567-e89b-12d3-a456-426614174000",
    mission_id="987fcdeb-51a2-12d3-a456-426614174000",
    device="cuda"
)

```

* **Returns:** `dict` (Inference results).

#### `get_model_status(mission_id)`

Checks the status of calibration or inference tasks.

* **Arguments:** `mission_id`.
* **Sample Usage:**

```python
status = client.get_model_status(mission_id="987fcdeb-51a2-12d3-a456-426614174000")
print(f"Training Status: {status.get('calibration_status')}")

```

* **Returns:** `dict`

```json
{
  "calibration_status": "Training_Completed",
  "inference_status": "processing_completed",
  "epochs": 100,
  "upload_time": "..."
}

```

---

## Error Handling

The SDK raises specific exceptions from `ridescanapi.exceptions` to help you handle errors gracefully.

| Exception Class | HTTP Code | Description |
| --- | --- | --- |
| `AuthenticationError` | 401 | Invalid API Key. Check your dashboard. |
| `ValidationError` | 400 | Missing arguments, invalid file types, or malformed requests. |
| `ResourceNotFoundError` | 404 | Robot, Mission, or File ID does not exist. |
| `ConflictError` | 409 | Resource already exists (e.g., creating a robot with a duplicate ID). |
| `ServerError` | 500+ | Internal backend issue. |
| `RideScanError` | - | Generic base exception for other errors. |

**Example Usage:**

```python
from ridescanapi.exceptions import ResourceNotFoundError, ValidationError

try:
    client.delete_robot("invalid-id")
except ResourceNotFoundError:
    print("Robot not found!")
except ValidationError as e:
    print(f"Invalid input: {e}")

```

---

## Enums & Values

### `robot_type`

Used in `create_robot` and `calibrate_model`.

* `"SPOT"` (Boston Dynamics Spot)
* `"UR6"`

### `file_type`

Used in `upload_files`.

* `"calib_file"`: Files used to train/calibrate the model.
* `"process_file"`: Files used for inference/risk assessment.

### `device`

Used in `run_inference`.

* `"cpu"` (Default)
* `"cuda"` (GPU - Requires backend support)

```

```