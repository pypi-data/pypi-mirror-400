import pytest
from castana import BaseProbe


class ConcreteProbe(BaseProbe):
    def check(self):
        return "OK"


class TestBaseProbeValidation:

    def test_name_must_be_string(self):
        with pytest.raises(TypeError) as exc_info:
            ConcreteProbe(name=123)
        
        error_msg = str(exc_info.value)
        assert "name must be str" in error_msg
        assert "got int" in error_msg

    def test_name_cannot_be_empty(self):
        with pytest.raises(ValueError) as exc_info:
            ConcreteProbe(name="")
        
        error_msg = str(exc_info.value)
        assert "name cannot be empty" in error_msg

    def test_timeout_must_be_number(self):
        with pytest.raises(TypeError) as exc_info:
            ConcreteProbe(name="test", timeout="5")
        
        error_msg = str(exc_info.value)
        assert "timeout must be number" in error_msg
        assert "got str" in error_msg

    def test_timeout_must_be_positive(self):
        with pytest.raises(ValueError) as exc_info:
            ConcreteProbe(name="test", timeout=0)
        
        error_msg = str(exc_info.value)
        assert "timeout must be positive" in error_msg
        
        with pytest.raises(ValueError):
            ConcreteProbe(name="test", timeout=-1)

    def test_component_type_must_be_string(self):
        with pytest.raises(TypeError) as exc_info:
            ConcreteProbe(name="test", component_type=123)
        
        error_msg = str(exc_info.value)
        assert "component_type must be str" in error_msg

    def test_critical_must_be_bool(self):
        with pytest.raises(TypeError) as exc_info:
            ConcreteProbe(name="test", critical="false")
        
        error_msg = str(exc_info.value)
        assert "critical must be bool" in error_msg
        assert "got str" in error_msg

    def test_retry_attempts_must_be_int(self):
        with pytest.raises(TypeError) as exc_info:
            ConcreteProbe(name="test", retry_attempts=2.5)
        
        error_msg = str(exc_info.value)
        assert "retry_attempts must be int" in error_msg
        assert "got float" in error_msg

    def test_retry_attempts_must_be_non_negative(self):
        with pytest.raises(ValueError) as exc_info:
            ConcreteProbe(name="test", retry_attempts=-1)
        
        error_msg = str(exc_info.value)
        assert "retry_attempts must be non-negative" in error_msg

    def test_retry_delay_must_be_number(self):
        with pytest.raises(TypeError) as exc_info:
            ConcreteProbe(name="test", retry_delay="0.5")
        
        error_msg = str(exc_info.value)
        assert "retry_delay must be number" in error_msg
        assert "got str" in error_msg

    def test_retry_delay_must_be_non_negative(self):
        with pytest.raises(ValueError) as exc_info:
            ConcreteProbe(name="test", retry_delay=-0.5)
        
        error_msg = str(exc_info.value)
        assert "retry_delay must be non-negative" in error_msg

    def test_valid_parameters_work(self):
        probe = ConcreteProbe(
            name="test-probe",
            timeout=10.0,
            component_type="datastore",
            critical=False,
            retry_attempts=3,
            retry_delay=0.5,
        )
        
        assert probe.name == "test-probe"
        assert probe.timeout == 10.0
        assert probe.component_type == "datastore"
        assert probe.critical is False
        assert probe.retry_attempts == 3
        assert probe.retry_delay == 0.5

    def test_int_timeout_is_converted_to_float(self):
        probe = ConcreteProbe(name="test", timeout=5)
        assert isinstance(probe.timeout, float)
        assert probe.timeout == 5.0
