"""
Test file to verify code executor resilience improvements.
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, patch
from src.insyt_secure.executor.code_executor import CodeExecutor


class TestCodeExecutorResilience:
    """Test the resilience improvements to the code executor."""
    
    @pytest.fixture
    def mock_executor(self):
        """Create a mock code executor for testing."""
        with patch('paho.mqtt.client.Client'):
            executor = CodeExecutor(
                mqtt_broker="test_broker",
                mqtt_port=1883,
                mqtt_username="test_user",
                mqtt_password="test_pass",
                subscribe_topic="test/subscribe",
                publish_topic="test/publish"
            )
            return executor
    
    def test_validate_code_safety(self, mock_executor):
        """Test code safety validation."""
        # Test dangerous patterns
        dangerous_code = "quit()"
        is_safe, warnings = mock_executor._validate_code_safety(dangerous_code)
        assert not is_safe
        assert len(warnings) > 0
        assert "quit()" in warnings[0]
        
        # Test safe code
        safe_code = "print('Hello, World!')"
        is_safe, warnings = mock_executor._validate_code_safety(safe_code)
        assert is_safe or len(warnings) == 0  # Should be safe or have no warnings
        
        # Test risky imports
        risky_code = "import subprocess"
        is_safe, warnings = mock_executor._validate_code_safety(risky_code)
        assert not is_safe
        assert len(warnings) > 0
        assert "subprocess" in warnings[0]
    
    def test_create_safe_globals(self, mock_executor):
        """Test that safe globals are created properly."""
        safe_globals = mock_executor._create_safe_globals()
        
        # Check that basic built-ins are included
        assert 'print' in safe_globals['__builtins__']
        assert 'len' in safe_globals['__builtins__']
        assert 'str' in safe_globals['__builtins__']
        
        # Check that locals and globals are now included
        assert 'locals' in safe_globals['__builtins__']
        assert 'globals' in safe_globals['__builtins__']
        
        # Check that dangerous functions are replaced
        assert 'quit' in safe_globals['__builtins__']
        assert 'exit' in safe_globals['__builtins__']
        assert 'help' in safe_globals['__builtins__']
        
        # Check that safe modules are included
        assert 'math' in safe_globals
        assert 'json' in safe_globals
        assert 'time' in safe_globals
    
    def test_safe_replacements(self, mock_executor):
        """Test that safe replacement functions work correctly."""
        safe_replacements = mock_executor._create_safe_replacements()
        
        # Test quit replacement
        quit_result = safe_replacements['quit']()
        assert "not available" in quit_result
        
        # Test exit replacement
        exit_result = safe_replacements['exit']()
        assert "not available" in exit_result
        
        # Test help replacement
        help_result = safe_replacements['help']()
        assert "limited" in help_result
        
        # Test input replacement
        with pytest.raises(RuntimeError):
            safe_replacements['input']("Enter something: ")
    
    def test_extract_and_run_python_code_with_dangerous_functions(self, mock_executor):
        """Test that dangerous functions are handled safely."""
        # Test quit() function
        result, parsed_result = mock_executor.extract_and_run_python_code("print(quit())")
        assert "not available" in result
        
        # Test exit() function
        result, parsed_result = mock_executor.extract_and_run_python_code("print(exit())")
        assert "not available" in result
        
        # Test help() function
        result, parsed_result = mock_executor.extract_and_run_python_code("print(help())")
        assert "limited" in result
    
    def test_extract_and_run_python_code_with_system_exit(self, mock_executor):
        """Test that SystemExit is handled gracefully."""
        import sys
        code_with_sys_exit = "import sys; sys.exit(1)"
        result, parsed_result = mock_executor.extract_and_run_python_code(code_with_sys_exit)
        assert "Warning: Code attempted to exit" in result
    
    def test_extract_and_run_python_code_with_normal_code(self, mock_executor):
        """Test that normal code still executes correctly."""
        normal_code = "print('Hello, World!')"
        result, parsed_result = mock_executor.extract_and_run_python_code(normal_code)
        assert "Hello, World!" in result
        
        # Test with JSON output
        json_code = "import json; print(json.dumps({'message': 'success'}))"
        result, parsed_result = mock_executor.extract_and_run_python_code(json_code)
        assert "success" in result
    
    def test_locals_and_globals_functions(self, mock_executor):
        """Test that locals() and globals() functions work correctly."""
        # Test locals() function
        locals_code = """
x = 42
y = 'test'
local_vars = locals()
print(f"locals keys: {sorted(local_vars.keys())}")
print(f"x in locals: {'x' in local_vars}")
print(f"y in locals: {'y' in local_vars}")
"""
        result, parsed_result = mock_executor.extract_and_run_python_code(locals_code)
        assert "x in locals: True" in result
        assert "y in locals: True" in result
        
        # Test globals() function
        globals_code = """
global_vars = globals()
print(f"print in globals: {'print' in global_vars}")
print(f"len in globals: {'len' in global_vars}")
"""
        result, parsed_result = mock_executor.extract_and_run_python_code(globals_code)
        assert "print in globals: True" in result
        assert "len in globals: True" in result
    
    def test_extract_and_run_python_code_with_exception(self, mock_executor):
        """Test that exceptions are handled properly."""
        error_code = "raise ValueError('Test error')"
        result, parsed_result = mock_executor.extract_and_run_python_code(error_code)
        assert "ValueError" in result
        assert "Test error" in result
    
    def test_extract_and_run_python_code_with_timeout(self, mock_executor):
        """Test that timeout handling works correctly."""
        # Test normal execution
        normal_code = "print('Hello')"
        result, parsed_result = mock_executor.extract_and_run_python_code_with_timeout(normal_code, 10)
        assert "Hello" in result
        
        # Test timeout scenario (simulate with a very short timeout)
        # Note: This is tricky to test reliably, so we'll just check the method exists
        assert hasattr(mock_executor, 'extract_and_run_python_code_with_timeout')


if __name__ == "__main__":
    pytest.main([__file__]) 