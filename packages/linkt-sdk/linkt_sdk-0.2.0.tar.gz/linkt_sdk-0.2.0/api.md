# Icp

Types:

```python
from linkt.types import EntityTargetConfig, IcpResponse, IcpListResponse, IcpGetActiveRunsResponse
```

Methods:

- <code title="post /v1/icp">client.icp.<a href="./src/linkt/resources/icp.py">create</a>(\*\*<a href="src/linkt/types/icp_create_params.py">params</a>) -> <a href="./src/linkt/types/icp_response.py">IcpResponse</a></code>
- <code title="get /v1/icp/{icp_id}">client.icp.<a href="./src/linkt/resources/icp.py">retrieve</a>(icp_id) -> <a href="./src/linkt/types/icp_response.py">IcpResponse</a></code>
- <code title="put /v1/icp/{icp_id}">client.icp.<a href="./src/linkt/resources/icp.py">update</a>(icp_id, \*\*<a href="src/linkt/types/icp_update_params.py">params</a>) -> <a href="./src/linkt/types/icp_response.py">IcpResponse</a></code>
- <code title="get /v1/icp">client.icp.<a href="./src/linkt/resources/icp.py">list</a>(\*\*<a href="src/linkt/types/icp_list_params.py">params</a>) -> <a href="./src/linkt/types/icp_list_response.py">IcpListResponse</a></code>
- <code title="delete /v1/icp/{icp_id}">client.icp.<a href="./src/linkt/resources/icp.py">delete</a>(icp_id) -> None</code>
- <code title="get /v1/icp/{icp_id}/active_runs">client.icp.<a href="./src/linkt/resources/icp.py">get_active_runs</a>(icp_id) -> <a href="./src/linkt/types/icp_get_active_runs_response.py">IcpGetActiveRunsResponse</a></code>

# Sheet

Types:

```python
from linkt.types import EntityType, Sheet, SheetListResponse, SheetGetEntitiesResponse
```

Methods:

- <code title="post /v1/sheet">client.sheet.<a href="./src/linkt/resources/sheet/sheet.py">create</a>(\*\*<a href="src/linkt/types/sheet_create_params.py">params</a>) -> <a href="./src/linkt/types/sheet/sheet.py">Sheet</a></code>
- <code title="get /v1/sheet/{sheet_id}">client.sheet.<a href="./src/linkt/resources/sheet/sheet.py">retrieve</a>(sheet_id) -> <a href="./src/linkt/types/sheet/sheet.py">Sheet</a></code>
- <code title="put /v1/sheet/{sheet_id}">client.sheet.<a href="./src/linkt/resources/sheet/sheet.py">update</a>(sheet_id, \*\*<a href="src/linkt/types/sheet_update_params.py">params</a>) -> None</code>
- <code title="get /v1/sheet">client.sheet.<a href="./src/linkt/resources/sheet/sheet.py">list</a>(\*\*<a href="src/linkt/types/sheet_list_params.py">params</a>) -> <a href="./src/linkt/types/sheet_list_response.py">SheetListResponse</a></code>
- <code title="delete /v1/sheet/{sheet_id}">client.sheet.<a href="./src/linkt/resources/sheet/sheet.py">delete</a>(sheet_id) -> None</code>
- <code title="get /v1/sheet/{sheet_id}/export-csv">client.sheet.<a href="./src/linkt/resources/sheet/sheet.py">export_csv</a>(sheet_id, \*\*<a href="src/linkt/types/sheet_export_csv_params.py">params</a>) -> object</code>
- <code title="get /v1/sheet/{sheet_id}/entities">client.sheet.<a href="./src/linkt/resources/sheet/sheet.py">get_entities</a>(sheet_id, \*\*<a href="src/linkt/types/sheet_get_entities_params.py">params</a>) -> <a href="./src/linkt/types/sheet_get_entities_response.py">SheetGetEntitiesResponse</a></code>

## Entity

Types:

```python
from linkt.types.sheet import EntityRetrieveResponse
```

Methods:

- <code title="get /v1/sheet/{sheet_id}/entity/{entity_id}">client.sheet.entity.<a href="./src/linkt/resources/sheet/entity.py">retrieve</a>(entity_id, \*, sheet_id) -> <a href="./src/linkt/types/sheet/entity_retrieve_response.py">EntityRetrieveResponse</a></code>
- <code title="put /v1/sheet/{sheet_id}/entity/{entity_id}/comments">client.sheet.entity.<a href="./src/linkt/resources/sheet/entity.py">update_comments</a>(entity_id, \*, sheet_id, \*\*<a href="src/linkt/types/sheet/entity_update_comments_params.py">params</a>) -> None</code>
- <code title="put /v1/sheet/{sheet_id}/entity/{entity_id}/status">client.sheet.entity.<a href="./src/linkt/resources/sheet/entity.py">update_status</a>(entity_id, \*, sheet_id, \*\*<a href="src/linkt/types/sheet/entity_update_status_params.py">params</a>) -> None</code>

## Schema

Types:

```python
from linkt.types.sheet import (
    SchemaGetResponse,
    SchemaGetDefaultResponse,
    SchemaGetFieldDefinitionsResponse,
)
```

Methods:

- <code title="put /v1/sheet/schema/{sheet_id}">client.sheet.schema.<a href="./src/linkt/resources/sheet/schema.py">add_fields</a>(sheet_id, \*\*<a href="src/linkt/types/sheet/schema_add_fields_params.py">params</a>) -> None</code>
- <code title="delete /v1/sheet/schema/{sheet_id}">client.sheet.schema.<a href="./src/linkt/resources/sheet/schema.py">delete_fields</a>(sheet_id, \*\*<a href="src/linkt/types/sheet/schema_delete_fields_params.py">params</a>) -> None</code>
- <code title="get /v1/sheet/schema/{sheet_id}">client.sheet.schema.<a href="./src/linkt/resources/sheet/schema.py">get</a>(sheet_id) -> <a href="./src/linkt/types/sheet/schema_get_response.py">SchemaGetResponse</a></code>
- <code title="get /v1/sheet/schema/default">client.sheet.schema.<a href="./src/linkt/resources/sheet/schema.py">get_default</a>() -> <a href="./src/linkt/types/sheet/schema_get_default_response.py">SchemaGetDefaultResponse</a></code>
- <code title="get /v1/sheet/schema/field">client.sheet.schema.<a href="./src/linkt/resources/sheet/schema.py">get_field_definitions</a>() -> <a href="./src/linkt/types/sheet/schema_get_field_definitions_response.py">SchemaGetFieldDefinitionsResponse</a></code>

# Task

Types:

```python
from linkt.types import (
    IngestTaskConfig,
    SearchV2Config,
    SearchV3Config,
    SignalCsvConfigInput,
    SignalSheetConfigInput,
    SignalTopicConfigInput,
    SignalTypeConfig,
    StandardPromptConfig,
    TaskCreateResponse,
    TaskRetrieveResponse,
    TaskListResponse,
    TaskExecuteResponse,
)
```

Methods:

- <code title="post /v1/task">client.task.<a href="./src/linkt/resources/task.py">create</a>(\*\*<a href="src/linkt/types/task_create_params.py">params</a>) -> <a href="./src/linkt/types/task_create_response.py">TaskCreateResponse</a></code>
- <code title="get /v1/task/{task_id}">client.task.<a href="./src/linkt/resources/task.py">retrieve</a>(task_id) -> <a href="./src/linkt/types/task_retrieve_response.py">TaskRetrieveResponse</a></code>
- <code title="put /v1/task/{task_id}">client.task.<a href="./src/linkt/resources/task.py">update</a>(task_id, \*\*<a href="src/linkt/types/task_update_params.py">params</a>) -> None</code>
- <code title="get /v1/task">client.task.<a href="./src/linkt/resources/task.py">list</a>(\*\*<a href="src/linkt/types/task_list_params.py">params</a>) -> <a href="./src/linkt/types/task_list_response.py">TaskListResponse</a></code>
- <code title="delete /v1/task/{task_id}">client.task.<a href="./src/linkt/resources/task.py">delete</a>(task_id) -> None</code>
- <code title="post /v1/task/{task_id}/execute">client.task.<a href="./src/linkt/resources/task.py">execute</a>(task_id, \*\*<a href="src/linkt/types/task_execute_params.py">params</a>) -> <a href="./src/linkt/types/task_execute_response.py">TaskExecuteResponse</a></code>

# Signal

Types:

```python
from linkt.types import SignalResponse, SignalListResponse
```

Methods:

- <code title="get /v1/signal/{signal_id}">client.signal.<a href="./src/linkt/resources/signal.py">retrieve</a>(signal_id) -> <a href="./src/linkt/types/signal_response.py">SignalResponse</a></code>
- <code title="get /v1/signal">client.signal.<a href="./src/linkt/resources/signal.py">list</a>(\*\*<a href="src/linkt/types/signal_list_params.py">params</a>) -> <a href="./src/linkt/types/signal_list_response.py">SignalListResponse</a></code>

# Run

Types:

```python
from linkt.types import RunCreateResponse, RunRetrieveResponse, RunListResponse, RunGetQueueResponse
```

Methods:

- <code title="post /v1/run">client.run.<a href="./src/linkt/resources/run.py">create</a>(\*\*<a href="src/linkt/types/run_create_params.py">params</a>) -> <a href="./src/linkt/types/run_create_response.py">RunCreateResponse</a></code>
- <code title="get /v1/run/{run_id}">client.run.<a href="./src/linkt/resources/run.py">retrieve</a>(run_id) -> <a href="./src/linkt/types/run_retrieve_response.py">RunRetrieveResponse</a></code>
- <code title="get /v1/run">client.run.<a href="./src/linkt/resources/run.py">list</a>(\*\*<a href="src/linkt/types/run_list_params.py">params</a>) -> <a href="./src/linkt/types/run_list_response.py">RunListResponse</a></code>
- <code title="delete /v1/run/{run_id}">client.run.<a href="./src/linkt/resources/run.py">delete</a>(run_id) -> None</code>
- <code title="post /v1/run/{run_id}/cancel">client.run.<a href="./src/linkt/resources/run.py">cancel</a>(run_id) -> None</code>
- <code title="get /v1/run/{run_id}/queue">client.run.<a href="./src/linkt/resources/run.py">get_queue</a>(run_id, \*\*<a href="src/linkt/types/run_get_queue_params.py">params</a>) -> <a href="./src/linkt/types/run_get_queue_response.py">RunGetQueueResponse</a></code>

# Files

Types:

```python
from linkt.types import (
    CsvProcessingStatus,
    FileRetrieveResponse,
    FileListResponse,
    FileUploadResponse,
)
```

Methods:

- <code title="get /v1/files/{file_id}">client.files.<a href="./src/linkt/resources/files.py">retrieve</a>(file_id) -> <a href="./src/linkt/types/file_retrieve_response.py">FileRetrieveResponse</a></code>
- <code title="get /v1/files">client.files.<a href="./src/linkt/resources/files.py">list</a>(\*\*<a href="src/linkt/types/file_list_params.py">params</a>) -> <a href="./src/linkt/types/file_list_response.py">FileListResponse</a></code>
- <code title="post /v1/files/upload">client.files.<a href="./src/linkt/resources/files.py">upload</a>(\*\*<a href="src/linkt/types/file_upload_params.py">params</a>) -> <a href="./src/linkt/types/file_upload_response.py">FileUploadResponse</a></code>
