import os
from utils.model_finder import find_model_executable


def test_find_executable_in_subfolder(tmp_path):
    base_dir = tmp_path / "models"
    sub = base_dir / "sub1"
    sub.mkdir(parents=True)
    exe = sub / "waifu2x.exe"
    exe.write_text("")

    result = find_model_executable(str(base_dir), "waifu2x", exe_name="waifu2x.exe")
    assert result == str(exe)


def test_find_executable_in_subsubfolder(tmp_path):
    base_dir = tmp_path / "models"
    sub = base_dir / "sub1" / "sub2"
    sub.mkdir(parents=True)
    exe = sub / "model.exe"
    exe.write_text("")

    result = find_model_executable(str(base_dir), "model", exe_name="model.exe")
    assert result == str(exe)


def test_executable_not_found(tmp_path):
    base_dir = tmp_path / "models"
    base_dir.mkdir()

    result = find_model_executable(str(base_dir), "missing", exe_name="missing.exe")
    assert result is None
