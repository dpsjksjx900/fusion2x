import os
from pathlib import Path
import builtins

import core.operator as operator


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


def test_process_request_returns_existing_output(tmp_path, monkeypatch):
    # Prepare input image
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    img = input_dir / "test.png"
    img.write_text("data")

    output_dir = tmp_path / "out"
    output_dir.mkdir()

    temp_dir = tmp_path / "temp"

    # Patch utilities used in process_request
    def fake_create_temp_folder(*args, **kwargs):
        temp_dir.mkdir(exist_ok=True)
        return str(temp_dir)
    monkeypatch.setattr(operator, "create_temp_folder", fake_create_temp_folder)

    def fake_process_image(frame_dir, output_path, logger=None):
        Path(output_path).write_text("processed")
    monkeypatch.setattr(operator, "process_image", fake_process_image)

    monkeypatch.setattr(operator, "run_upscaling", lambda *a, **k: {"success": True})
    monkeypatch.setattr(operator, "run_interpolation", lambda *a, **k: {"success": True})
    monkeypatch.setattr(operator, "get_logger", lambda *a, **k: dummy_logger())

    request = {
        "input_path": str(img),
        "input_format": "png",
        "task": "upscaling",
        "upscaling": {"enabled": False},
        "interpolation": {"enabled": False},
        "output_format": "png",
        "output_path": str(output_dir),
        "log_path": str(tmp_path / "log.txt"),
    }

    result = operator.process_request(request)

    assert result["status"] == "success"
    assert Path(result["output_path"]).exists()
    files = list(output_dir.iterdir())
    assert len(files) == 1
    assert files[0] == Path(result["output_path"])


def test_process_request_respects_output_format(tmp_path, monkeypatch):
    input_dir = tmp_path / "input2"
    input_dir.mkdir()
    img = input_dir / "orig.png"
    img.write_text("data")

    output_dir = tmp_path / "out2"
    output_dir.mkdir()

    temp_dir = tmp_path / "temp2"

    def fake_create_temp_folder(*args, **kwargs):
        temp_dir.mkdir(exist_ok=True)
        return str(temp_dir)
    monkeypatch.setattr(operator, "create_temp_folder", fake_create_temp_folder)

    def fake_process_image(frame_dir, output_path, logger=None):
        Path(output_path).write_text("processed")
    monkeypatch.setattr(operator, "process_image", fake_process_image)

    monkeypatch.setattr(operator, "run_upscaling", lambda *a, **k: {"success": True})
    monkeypatch.setattr(operator, "run_interpolation", lambda *a, **k: {"success": True})
    monkeypatch.setattr(operator, "get_logger", lambda *a, **k: dummy_logger())

    request = {
        "input_path": str(img),
        "input_format": "png",
        "output_format": "jpg",
        "task": "upscaling",
        "upscaling": {"enabled": False},
        "interpolation": {"enabled": False},
        "output_path": str(output_dir),
        "log_path": str(tmp_path / "log2.txt"),
    }

    result = operator.process_request(request)

    assert result["status"] == "success"
    assert Path(result["output_path"]).exists()
    assert Path(result["output_path"]).suffix == ".jpg"
    assert Path(result["output_path"]).parent == output_dir
