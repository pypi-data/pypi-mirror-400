# Caller Attribution Examples

Comprehensive examples demonstrating arlogi's caller attribution feature using the `caller_depth` parameter.

## Modern Setup

Before using caller attribution, ensure arlogi is configured using the `LoggingConfig` pattern:

```python
from arlogi import LoggingConfig, LoggerFactory, get_logger

# Configure arlogi
config = LoggingConfig(level="INFO")
LoggerFactory._apply_configuration(config)

# Get logger
logger = get_logger("example")
```

---

## Basic Caller Attribution

### Using `caller_depth=0` (Current Function)

Shows the function where the log call is made:

```python
from arlogi import get_logger

logger = get_logger("example")

def process_data(data):
    # Shows [process_data()] - the current function
    logger.info("Processing data started", caller_depth=0)

    result = data * 2

    # Shows [process_data()] - still the current function
    logger.info("Processing completed", caller_depth=0, result=result)

    return result

process_data(42)
```

**Output:**

```text
INFO    [process_data()]                          Processing data started
INFO    [process_data()]                          Processing completed, result=84
```

### Using `caller_depth=1` (Immediate Caller)

Shows the function that called the current function:

```python
from arlogi import get_logger

logger = get_logger("example")

def helper_function():
    # Shows [from main_function()] - the function that called helper_function
    logger.info("Helper operation completed", caller_depth=1)
    logger.info("Helper operation details", caller_depth=1, operation_type="compute")

def main_function():
    logger.info("Main started", caller_depth=0)

    # This call will show main_function as the caller
    helper_function()

    logger.info("Main completed", caller_depth=0)

main_function()
```

**Output:**

```text
INFO    [main_function()]                        Main started
INFO    [from main_function()]                   Helper operation completed
INFO    [from main_function()]                   Helper operation details, operation_type=compute
INFO    [main_function()]                        Main completed
```

### Using `caller_depth=2` (Caller's Caller)

Shows the function that called the caller:

```python
from arlogi import get_logger

logger = get_logger("example")

def deep_function():
    # Shows [from top_function()] - two levels up the call stack
    logger.info("Deep operation", caller_depth=2)
    logger.info("Deep details", caller_depth=2, depth="deep")

def middle_function():
    logger.info("Middle function", caller_depth=0)
    deep_function()

def top_function():
    logger.info("Top function", caller_depth=0)
    middle_function()

top_function()
```

**Output:**

```text
INFO    [top_function()]                        Top function
INFO    [middle_function()]                      Middle function
INFO    [from top_function()]                   Deep operation
INFO    [from top_function()]                   Deep details, depth=deep
```

## Cross-Module Attribution

### Same Module Attribution

```python
# file: app.py
from arlogi import get_logger

logger = get_logger("app")

def helper_function():
    # Shows [from main_function()] - same module, relative path
    logger.info("Helper completed", caller_depth=1)

def main_function():
    logger.info("Main started", caller_depth=0)
    helper_function()
    logger.info("Main completed", caller_depth=0)

main_function()
```

**Output:**

```text
INFO    [main_function()]                        Main started
INFO    [from main_function()]                   Helper completed
INFO    [main_function()]                        Main completed
```

### Cross-Module Attribution

```python
# file: utils/helpers.py
from arlogi import get_logger

logger = get_logger("utils.helpers")

def process_data(data):
    # Shows [from app.main_function()] - different module, full path
    logger.info("Processing data", caller_depth=1, data_id=data.get("id"))
    return {"status": "processed"}

# file: app/main.py
from utils.helpers import process_data
from arlogi import get_logger

logger = get_logger("app.main")

def main_function():
    logger.info("Starting main", caller_depth=0)
    result = process_data({"id": 123, "content": "test"})
    logger.info("Main completed", caller_depth=0, result=result)

main_function()
```

**Output:**

```text
INFO    [app.main_function()]                    Starting main
INFO    [from app.main_function()]               Processing data, data_id=123
INFO    [app.main_function()]                    Main completed, result={'status': 'processed'}
```

## Real-World Application Examples

### Web API Handler

```python
from arlogi import get_logger

logger = get_logger("api.handlers")

def handle_request(request):
    request_id = generate_request_id()

    logger.info(
        "Request received",
        caller_depth=1,  # Shows the API endpoint that called this handler
        request_id=request_id,
        method=request.method,
        path=request.path
    )

    try:
        result = process_business_logic(request)

        logger.info(
            "Request processed successfully",
            caller_depth=1,  # Still shows the API endpoint
            request_id=request_id,
            status_code=200
        )

        return result

    except Exception as e:
        logger.exception(
            "Request processing failed",
            caller_depth=1,  # Shows the API endpoint
            request_id=request_id,
            error_type=type(e).__name__
        )
        raise

def user_endpoint(request):
    # The handler call above will show [from user_endpoint()]
    return handle_request(request)

def product_endpoint(request):
    # The handler call above will show [from product_endpoint()]
    return handle_request(request)
```

### Database Operations

```python
from arlogi import get_logger

logger = get_logger("database.operations")

def execute_query(query, params=None):
    start_time = time.time()

    # Show the business function that initiated the query
    logger.trace(
        "Executing query",
        caller_depth=1,
        query=query,
        params=params
    )

    try:
        cursor = db.cursor()
        cursor.execute(query, params or [])
        result = cursor.fetchall()
        duration = (time.time() - start_time) * 1000

        # Show the business function for the result
        logger.debug(
            "Query completed",
            caller_depth=1,
            query=query,
            duration_ms=round(duration, 2),
            rows_affected=len(result)
        )

        return result

    except Exception as e:
        duration = (time.time() - start_time) * 1000

        # Show the business function for the error
        logger.error(
            "Query failed",
            caller_depth=1,
            query=query,
            duration_ms=round(duration, 2),
            error=str(e)
        )
        raise

def get_user_profile(user_id):
    logger.info("Fetching user profile", caller_depth=1, user_id=user_id)

    query = "SELECT * FROM users WHERE id = %s"
    params = (user_id,)

    # execute_query will log this as [from get_user_profile()]
    return execute_query(query, params)

def authenticate_user(username, password):
    logger.info("Authenticating user", caller_depth=1, username=username)

    query = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
    params = (username, hash_password(password))

    # execute_query will log this as [from authenticate_user()]
    return execute_query(query, params)
```

### Background Job Processing

```python
from arlogi import get_logger

logger = get_logger("jobs.processor")

def process_job(job_data):
    job_id = job_data.get("id")
    job_type = job_data.get("type")

    # Show the job queue that dispatched this job
    logger.info(
        "Job processing started",
        caller_depth=1,
        job_id=job_id,
        job_type=job_type
    )

    try:
        if job_type == "email":
            result = send_email_job(job_data)
        elif job_type == "report":
            result = generate_report_job(job_data)
        elif job_type == "cleanup":
            result = cleanup_job(job_data)
        else:
            raise ValueError(f"Unknown job type: {job_type}")

        # Show the job queue for completion
        logger.info(
            "Job processing completed",
            caller_depth=1,
            job_id=job_id,
            result_status=result.get("status")
        )

        return result

    except Exception as e:
        # Show the job queue for failure
        logger.exception(
            "Job processing failed",
            caller_depth=1,
            job_id=job_id,
            error_type=type(e).__name__
        )
        raise

def email_job_dispatcher():
    # process_job will show [from email_job_dispatcher()]
    process_job({
        "id": "job-123",
        "type": "email",
        "to": "user@example.com",
        "subject": "Welcome"
    })

def report_job_dispatcher():
    # process_job will show [from report_job_dispatcher()]
    process_job({
        "id": "job-456",
        "type": "report",
        "format": "pdf",
        "date_range": "2025-01-01:2025-12-31"
    })
```

### Class Method Attribution

```python
from arlogi import get_logger

logger = get_logger("services.user")

class UserService:
    def __init__(self):
        logger.info("UserService instance created", caller_depth=0)

    def create_user(self, user_data):
        logger.info("Creating user", caller_depth=1, email=user_data.get("email"))

        user_id = self._generate_user_id()
        self._save_user(user_id, user_data)
        self._send_welcome_email(user_data)

        logger.info("User created successfully", caller_depth=1, user_id=user_id)
        return user_id

    def _generate_user_id(self):
        # Shows [from create_user()] - parent method
        logger.trace("Generating user ID", caller_depth=1)
        return f"user_{uuid.uuid4().hex[:8]}"

    def _save_user(self, user_id, user_data):
        # Shows [from create_user()] - grandparent method
        logger.debug("Saving user to database", caller_depth=2, user_id=user_id)
        # Database save logic here

    def _send_welcome_email(self, user_data):
        # Shows [from create_user()] - grandparent method
        logger.info("Sending welcome email", caller_depth=2, email=user_data.get("email"))
        # Email sending logic here

# Usage
def application_logic():
    logger.info("Application started", caller_depth=0)

    service = UserService()

    # create_user will show [from application_logic()]
    user_id = service.create_user({
        "email": "newuser@example.com",
        "name": "New User"
    })

    logger.info("Application completed", caller_depth=0, user_id=user_id)
```

### Error Handling and Exception Tracking

```python
from arlogi import get_logger

logger = get_logger("error.tracking")

def risky_operation(data):
    logger.info("Starting risky operation", caller_depth=1, data_id=data.get("id"))

    try:
        result = process_data(data)
        logger.info("Operation successful", caller_depth=1, result=result)
        return result

    except ValueError as e:
        # Show the caller function for the error
        logger.warning(
            "Invalid data format",
            caller_depth=1,
            error=str(e),
            data_type=type(data).__name__
        )
        raise

    except ConnectionError as e:
        # Show the caller function for connection error
        logger.error(
            "Network connection failed",
            caller_depth=1,
            error=str(e),
            retry_possible=True
        )
        raise

    except Exception as e:
        # Show the caller function for unexpected errors
        logger.exception(
            "Unexpected error in operation",
            caller_depth=1,
            error_type=type(e).__name__
        )
        raise

def business_process():
    try:
        # risky_operation will show [from business_process()]
        risky_operation({"id": 123, "value": "test"})
    except Exception:
        # business_process will be shown as the caller
        logger.error("Business process failed", caller_depth=0)
        raise

def user_interface():
    try:
        # risky_operation will show [from user_interface()]
        risky_operation({"id": 456, "invalid": "data"})
    except Exception:
        # user_interface will be shown as the caller
        logger.error("UI operation failed", caller_depth=0)
        raise
```

## Performance Considerations

### Efficient Caller Attribution

```python
from arlogi import get_logger

logger = get_logger("performance.example")

def high_frequency_function():
    # Standard logging without caller attribution (fast)
    for i in range(1000):
        logger.debug("Processing item %d", i)

    # Caller attribution only when needed
    logger.info("Batch processing started", caller_depth=1, total=1000)

    for i in range(1000):
        # More expensive logging with caller attribution
        if i % 100 == 0:  # Log every 100th item
            logger.debug("Progress update", caller_depth=1, progress=i)

def optimized_error_tracking():
    try:
        # Standard logging for normal operations
        logger.info("Normal operation")

        # Caller attribution only for debugging
        if DEBUG_MODE:
            logger.debug("Detailed debug info", caller_depth=1, complex_data=data)

    except Exception as e:
        # Always use caller attribution for errors
        logger.exception("Error occurred", caller_depth=1, error_type=type(e).__name__)
```

## Testing with Caller Attribution

### Unit Test Examples

```python
import pytest
from arlogi import get_logger

def test_function_call_attribution(caplog):
    logger = get_logger("test_module")

    def test_function():
        logger.info("Test message", caller_depth=1)

    with caplog.at_level("INFO"):
        test_function()

        # Check that the log contains caller attribution
        assert "from test_function_call_attribution" in caplog.text

def test_deep_call_attribution(caplog):
    logger = get_logger("test_module")

    def deep_function():
        logger.info("Deep message", caller_depth=2)

    def middle_function():
        deep_function()

    def top_function():
        middle_function()

    with caplog.at_level("INFO"):
        top_function()

        # Check that the log shows top_function as caller
        assert "from test_deep_call_attribution" in caplog.text
```

## Best Practices

### Recommended Patterns

```python
from arlogi import get_logger

logger = get_logger("my_module")

# ✅ GOOD: Use caller_depth=0 for function entry/exit
def my_function():
    logger.info("Function started", caller_depth=0)
    # Function logic
    logger.info("Function completed", caller_depth=0)

# ✅ GOOD: Use caller_depth=1 to show business context
def helper_function():
    logger.info("Helper operation", caller_depth=1, operation_type="compute")

# ✅ GOOD: Use caller attribution for errors
def risky_operation():
    try:
        # Operation logic
        pass
    except Exception as e:
        logger.exception("Operation failed", caller_depth=1, error=str(e))
        raise

# ❌ AVOID: Overusing deep caller attribution
def deep_function():
    # caller_depth=3+ is rarely useful and adds overhead
    logger.info("Deep operation", caller_depth=3)
```

### Recommended Caller Attribution Depth

- `caller_depth=0`: Function boundaries and state changes
- `caller_depth=1`: Business operations and user actions
- `caller_depth=2`: Rare cases for debugging complex call chains
- `caller_depth=3+`: Generally avoid unless specific debugging needs

These examples demonstrate the power and flexibility of arlogi's caller attribution feature for creating maintainable, debuggable applications.
