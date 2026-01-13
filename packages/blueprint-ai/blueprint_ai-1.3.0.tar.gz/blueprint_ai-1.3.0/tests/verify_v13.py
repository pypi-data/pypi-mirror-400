#!/usr/bin/env python3
"""Verification script for Blueprint v1.3.0 models.

Tests that the v1.3.0 models correctly parse the 'Future Output' example
from BLUEPRINT_SPEC.md with full execution context, typed interfaces,
and error policies.

Run: python tests/verify_v13.py
"""
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from blueprint.models import (
    Task,
    TaskStatus,
    Interface,
    ExecutionContext,
    ErrorPolicy,
    FailureAction,
)


# The "Future Output" example from BLUEPRINT_SPEC v1.3.0
FUTURE_OUTPUT_EXAMPLE = {
    "task_id": "T1.2",
    "name": "Implement JWT token validation",
    "status": "not_started",
    "assignee": None,
    "estimated_sessions": 2,
    "dependencies": ["T1.1"],
    
    "interface": {
        "input": "JWT token string and secret key",
        "input_type": "json",
        "input_schema": {
            "type": "object",
            "properties": {
                "token": {"type": "string", "pattern": "^eyJ"},
                "secret": {"type": "string", "minLength": 32}
            },
            "required": ["token", "secret"]
        },
        "example_input": '{"token": "eyJhbGciOiJIUzI1NiIs...", "secret": "my-32-char-secret-key-here-now"}',
        
        "output": "Validated claims or error",
        "output_type": "json",
        "output_schema": {
            "type": "object",
            "properties": {
                "valid": {"type": "boolean"},
                "claims": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "exp": {"type": "integer"}
                    }
                },
                "error": {"type": "string"}
            },
            "required": ["valid"]
        },
        "example_output": '{"valid": true, "claims": {"user_id": "u123", "exp": 1704326400}}'
    },
    
    "execution_context": {
        "working_directory": "/project",
        "environment_variables": {
            "PYTHONPATH": "/project/src",
            "JWT_SECRET": "${secrets.JWT_SECRET}"
        },
        "required_tools": ["python3", "pytest"],
        "timeout_seconds": 300,
        "setup_command": "pip install pyjwt pytest"
    },
    
    "files_to_create": [
        "src/auth/jwt.py",
        "tests/test_jwt.py"
    ],
    
    "acceptance_criteria": [
        "Validates JWT signature using HS256 algorithm",
        "Rejects tokens where exp < current timestamp",
        "Returns claims dict on valid token",
        "Returns error message on invalid token"
    ],
    
    "test_command": "cd /project && python -m pytest tests/test_jwt.py -v --tb=short",
    
    "on_failure": {
        "max_retries": 2,
        "retry_delay_seconds": 10,
        "action": "block"
    },
    
    "rollback": "git checkout HEAD~1 -- src/auth/jwt.py tests/test_jwt.py",
    
    "notes": "Use PyJWT library. HS256 algorithm. Claims must include user_id and exp."
}


def test_full_v13_task():
    """Test parsing a complete v1.3.0 task with all new fields."""
    print("=" * 60)
    print("Testing v1.3.0 Task Model Parsing")
    print("=" * 60)
    
    # Parse the task
    task = Task(**FUTURE_OUTPUT_EXAMPLE)
    
    # Core fields
    assert task.task_id == "T1.2", f"task_id mismatch: {task.task_id}"
    assert task.name == "Implement JWT token validation"
    assert task.status == TaskStatus.NOT_STARTED
    assert task.dependencies == ["T1.1"]
    assert len(task.acceptance_criteria) == 4
    print("✅ Core fields parsed correctly")
    
    # Interface with typed schema
    assert task.interface is not None
    assert task.interface.input_type == "json"
    assert task.interface.output_type == "json"
    assert task.interface.input_schema is not None
    assert task.interface.input_schema["type"] == "object"
    assert "token" in task.interface.input_schema["properties"]
    assert task.interface.output_schema is not None
    assert task.interface.has_schema() == True
    assert task.interface.has_examples() == True
    print("✅ Typed interface parsed correctly")
    
    # Execution context
    assert task.execution_context is not None
    assert task.execution_context.working_directory == "/project"
    assert task.execution_context.environment_variables["PYTHONPATH"] == "/project/src"
    assert task.execution_context.environment_variables["JWT_SECRET"] == "${secrets.JWT_SECRET}"
    assert "python3" in task.execution_context.required_tools
    assert "pytest" in task.execution_context.required_tools
    assert task.execution_context.timeout_seconds == 300
    assert task.execution_context.setup_command == "pip install pyjwt pytest"
    print("✅ Execution context parsed correctly")
    
    # Error policy
    assert task.on_failure is not None
    assert task.on_failure.max_retries == 2
    assert task.on_failure.retry_delay_seconds == 10
    assert task.on_failure.action == FailureAction.BLOCK
    print("✅ Error policy parsed correctly")
    
    # Helper methods
    assert task.has_execution_context() == True
    assert task.has_error_policy() == True
    assert task.has_typed_interface() == True
    assert task.get_effective_timeout() == 300
    assert task.get_effective_retries() == 2
    print("✅ Helper methods work correctly")
    
    # Serialization round-trip
    task_dict = task.model_dump()
    task_restored = Task(**task_dict)
    assert task_restored.task_id == task.task_id
    assert task_restored.execution_context.working_directory == task.execution_context.working_directory
    print("✅ Serialization round-trip successful")
    
    print()
    print("=" * 60)
    print("ALL v1.3.0 TESTS PASSED ✅")
    print("=" * 60)
    
    return True


def test_backward_compatibility():
    """Test that v0.1.0 style tasks still parse correctly."""
    print()
    print("=" * 60)
    print("Testing Backward Compatibility (v0.1.0 task)")
    print("=" * 60)
    
    # Minimal v0.1.0 task
    old_task_data = {
        "task_id": "T0.1",
        "name": "Simple task",
        "status": "not_started",
        "dependencies": [],
        "interface": {
            "input": "Some input",
            "output": "Some output"
        },
        "acceptance_criteria": ["It works"],
        "test_command": "echo done",
        "rollback": "git reset"
    }
    
    task = Task(**old_task_data)
    
    assert task.task_id == "T0.1"
    assert task.execution_context is None  # Not provided, should be None
    assert task.on_failure is None  # Not provided, should be None
    assert task.interface.input_schema is None  # Not provided
    assert task.has_execution_context() == False
    assert task.has_error_policy() == False
    assert task.has_typed_interface() == False
    assert task.get_effective_timeout() == 3600  # Default
    assert task.get_effective_retries() == 0  # Default
    
    print("✅ v0.1.0 task parsed correctly")
    print("✅ Optional v1.3.0 fields default to None")
    print("✅ Helper methods return correct defaults")
    print()
    print("=" * 60)
    print("BACKWARD COMPATIBILITY VERIFIED ✅")
    print("=" * 60)
    
    return True


def test_emoji_status_parsing():
    """Test that emoji status markers are parsed correctly."""
    print()
    print("=" * 60)
    print("Testing Emoji Status Parsing")
    print("=" * 60)
    
    statuses = [
        ("🔲 NOT_STARTED", TaskStatus.NOT_STARTED),
        ("🔄 IN_PROGRESS", TaskStatus.IN_PROGRESS),
        ("✅ COMPLETE", TaskStatus.COMPLETE),
        ("⛔ BLOCKED", TaskStatus.BLOCKED),
        ("⏭️ SKIPPED", TaskStatus.SKIPPED),
        ("not_started", TaskStatus.NOT_STARTED),
        ("complete", TaskStatus.COMPLETE),
    ]
    
    for status_str, expected in statuses:
        task = Task(
            task_id="T1",
            name="Test",
            status=status_str,
            dependencies=[],
            acceptance_criteria=[],
            test_command="true",
            rollback="true"
        )
        assert task.status == expected, f"Status '{status_str}' should parse to {expected}, got {task.status}"
        print(f"✅ '{status_str}' → {task.status.value}")
    
    print()
    print("=" * 60)
    print("EMOJI STATUS PARSING VERIFIED ✅")
    print("=" * 60)
    
    return True


def test_sub_models_isolation():
    """Test that sub-models can be created independently."""
    print()
    print("=" * 60)
    print("Testing Sub-Model Isolation")
    print("=" * 60)
    
    # ExecutionContext standalone
    ec = ExecutionContext(
        working_directory="/test",
        required_tools=["git"],
        timeout_seconds=60
    )
    assert ec.working_directory == "/test"
    assert ec.timeout_seconds == 60
    assert ec.setup_command is None
    print("✅ ExecutionContext creates independently")
    
    # ErrorPolicy standalone
    ep = ErrorPolicy(
        max_retries=3,
        action="abort"
    )
    assert ep.max_retries == 3
    assert ep.action == FailureAction.ABORT
    print("✅ ErrorPolicy creates independently")
    
    # Interface with schema standalone
    iface = Interface(
        input="Test input",
        output="Test output",
        input_type="json",
        input_schema={"type": "object"}
    )
    assert iface.has_schema() == True
    print("✅ Interface with schema creates independently")
    
    print()
    print("=" * 60)
    print("SUB-MODEL ISOLATION VERIFIED ✅")
    print("=" * 60)
    
    return True


def main():
    """Run all verification tests."""
    print()
    print("🚀 BLUEPRINT v1.3.0 MODEL VERIFICATION")
    print()
    
    results = []
    
    try:
        results.append(("Full v1.3.0 Task", test_full_v13_task()))
    except Exception as e:
        print(f"❌ Full v1.3.0 Task FAILED: {e}")
        results.append(("Full v1.3.0 Task", False))
    
    try:
        results.append(("Backward Compatibility", test_backward_compatibility()))
    except Exception as e:
        print(f"❌ Backward Compatibility FAILED: {e}")
        results.append(("Backward Compatibility", False))
    
    try:
        results.append(("Emoji Status Parsing", test_emoji_status_parsing()))
    except Exception as e:
        print(f"❌ Emoji Status Parsing FAILED: {e}")
        results.append(("Emoji Status Parsing", False))
    
    try:
        results.append(("Sub-Model Isolation", test_sub_models_isolation()))
    except Exception as e:
        print(f"❌ Sub-Model Isolation FAILED: {e}")
        results.append(("Sub-Model Isolation", False))
    
    print()
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        return 0
    else:
        print("💥 SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
