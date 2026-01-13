import pytest
from insyt_secure.executor.code_executor import CodeExecutor

def test_extract_and_run_python_code():
    executor = CodeExecutor(
        mqtt_broker="localhost",
        mqtt_port=1883,
        mqtt_username="test",
        mqtt_password="test",
        subscribe_topic="test.topic"
    )
    test_code = """  python
print({'test': 'success'})
  """
    result, parsed_result = executor.extract_and_run_python_code(test_code)
    assert parsed_result == {'test': 'success'}