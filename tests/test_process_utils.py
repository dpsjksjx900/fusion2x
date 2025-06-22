import types
import subprocess
import pytest

from utils import process_utils
from utils import env_setup

class DummyLogger:
    def info(self, *a, **k):
        pass
    def error(self, *a, **k):
        pass
    def warning(self, *a, **k):
        pass

def test_run_model_command_missing_runtime(monkeypatch):
    result = types.SimpleNamespace(returncode=3221225477, stdout='', stderr='')
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: result)
    monkeypatch.setattr(env_setup, 'vc_runtime_installed', lambda: False)
    monkeypatch.setattr(env_setup, 'vulkan_available', lambda: True)
    with pytest.raises(RuntimeError) as exc:
        process_utils.run_model_command(['fake'], DummyLogger())
    assert 'Visual C++ Runtime' in str(exc.value)

def test_run_model_command_gpu_issue(monkeypatch):
    result = types.SimpleNamespace(returncode=3221225477, stdout='', stderr='')
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: result)
    monkeypatch.setattr(env_setup, 'vc_runtime_installed', lambda: True)
    monkeypatch.setattr(env_setup, 'vulkan_available', lambda: False)
    with pytest.raises(RuntimeError) as exc:
        process_utils.run_model_command(['fake'], DummyLogger())
    assert 'Vulkan drivers' in str(exc.value)


def test_run_model_command_unknown_issue(monkeypatch):
    result = types.SimpleNamespace(returncode=3221225477, stdout='', stderr='')
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: result)
    monkeypatch.setattr(env_setup, 'vc_runtime_installed', lambda: True)
    monkeypatch.setattr(env_setup, 'vulkan_available', lambda: True)
    with pytest.raises(RuntimeError) as exc:
        process_utils.run_model_command(['fake'], DummyLogger())
    assert 'graphics drivers' in str(exc.value)
utils/env_setup.py
