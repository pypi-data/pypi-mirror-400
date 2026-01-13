#!/usr/bin/env python3
"""Integration test: Parser + Models v1.3.0"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from blueprint.parser import _parse_task
from blueprint.models import TaskStatus, FailureAction

# Full v1.3.0 task
TASK_DATA = {
    "task_id": "T1.2",
    "name": "Implement JWT token validation",
    "status": "not_started",
    "dependencies": ["T1.1"],
    "interface": {
        "input": "JWT token string and secret key",
        "input_type": "json",
        "input_schema": {
            "type": "object",
            "properties": {"token": {"type": "string"}},
            "required": ["token"]
        },
        "output": "Validated claims",
        "output_type": "json",
        "output_schema": {"type": "object"},
        "example_input": '{"token": "eyJ..."}',
        "example_output": '{"valid": true}'
    },
    "execution_context": {
        "working_directory": "/project",
        "environment_variables": {"PYTHONPATH": "/project/src"},
        "required_tools": ["python3", "pytest"],
        "timeout_seconds": 300,
        "setup_command": "pip install pyjwt"
    },
    "acceptance_criteria": ["Validates signature", "Rejects expired"],
    "test_command": "pytest tests/test_jwt.py -v",
    "on_failure": {
        "max_retries": 2,
        "retry_delay_seconds": 10,
        "action": "block"
    },
    "rollback": "git checkout HEAD~1 -- src/auth/jwt.py",
    "files_to_create": ["src/auth/jwt.py"]
}

def test_parser_v13():
    print("Testing Parser v1.3.0 Integration")
    print("=" * 50)
    
    task = _parse_task(TASK_DATA)
    
    # Core
    assert task.task_id == "T1.2"
    assert task.status == TaskStatus.NOT_STARTED
    print("✅ Core fields parsed")
    
    # Interface with schema
    assert task.interface.input_type == "json"
    assert task.interface.input_schema["type"] == "object"
    assert task.interface.example_input == '{"token": "eyJ..."}'
    print("✅ Typed interface parsed")
    
    # Execution context
    assert task.execution_context.working_directory == "/project"
    assert "python3" in task.execution_context.required_tools
    assert task.execution_context.timeout_seconds == 300
    assert task.execution_context.setup_command == "pip install pyjwt"
    print("✅ Execution context parsed")
    
    # Error policy
    assert task.on_failure.max_retries == 2
    assert task.on_failure.action == FailureAction.BLOCK
    print("✅ Error policy parsed")
    
    print()
    print("=" * 50)
    print("PARSER INTEGRATION TEST PASSED ✅")
    return True

if __name__ == "__main__":
    test_parser_v13()
