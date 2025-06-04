import subprocess
from handlers import upscaling_handler, interpolation_handler


def dummy_logger():
    class Dummy:
        def info(self, *args, **kwargs):
            pass
        def error(self, *args, **kwargs):
            pass
        def warning(self, *args, **kwargs):
            pass
        def debug(self, *args, **kwargs):
            pass
    return Dummy()


def test_upscaling_success(monkeypatch):
    def fake_model(frame_dir, params, logger):
        pass
    monkeypatch.setitem(upscaling_handler.MODEL_REGISTRY, "test-model", (fake_model, []))
    res = upscaling_handler.run_upscaling("frames", {"model_name": "test-model", "params": {}}, dummy_logger())
    assert res["success"] is True


def test_upscaling_called_process_error(monkeypatch):
    def fake_model(frame_dir, params, logger):
        raise subprocess.CalledProcessError(returncode=1, cmd="x", stderr="err")
    monkeypatch.setitem(upscaling_handler.MODEL_REGISTRY, "err-model", (fake_model, []))
    res = upscaling_handler.run_upscaling("frames", {"model_name": "err-model", "params": {}}, dummy_logger())
    assert res["success"] is False
    assert res["message"] == "err"


def test_interpolation_success(monkeypatch):
    def fake_model(frame_dir, params, logger):
        pass
    monkeypatch.setitem(interpolation_handler.MODEL_REGISTRY, "test-model", (fake_model, []))
    res = interpolation_handler.run_interpolation("frames", {"model_name": "test-model", "params": {}}, dummy_logger())
    assert res["success"] is True


def test_interpolation_called_process_error(monkeypatch):
    def fake_model(frame_dir, params, logger):
        raise subprocess.CalledProcessError(returncode=1, cmd="x", stderr="bad")
    monkeypatch.setitem(interpolation_handler.MODEL_REGISTRY, "err-model", (fake_model, []))
    res = interpolation_handler.run_interpolation("frames", {"model_name": "err-model", "params": {}}, dummy_logger())
    assert res["success"] is False
    assert res["message"] == "bad"
