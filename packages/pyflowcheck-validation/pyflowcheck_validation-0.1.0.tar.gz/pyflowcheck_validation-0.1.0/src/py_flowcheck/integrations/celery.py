from py_flowcheck import check_input, Schema
from celery import Celery

# Initialize Celery app
celery_app = Celery("py_flowcheck")

# Define a schema for Celery task validation
task_schema = Schema({
    "task_name": str,
    "args": {"type": list, "nullable": True},
    "kwargs": {"type": dict, "nullable": True},
})

@check_input(schema=task_schema)
def validate_task(task):
    """
    Validates a Celery task against the defined schema.

    :param task: The task to validate (dict with 'task_name', 'args', 'kwargs').
    :raises ValidationError: If the task does not conform to the schema.
    """
    return task  # Return the validated task for further processing

# Example Celery task with validation
@celery_app.task(name="example_task")
def example_task(task):
    """
    Example Celery task that validates its input before execution.

    :param task: The task payload to validate.
    """
    validated_task = validate_task(task)
    print(f"Executing task: {validated_task['task_name']}")
    # Add your task logic here
