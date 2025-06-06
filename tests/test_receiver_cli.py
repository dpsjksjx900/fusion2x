import sys
import types
import json
import pytest
import receiver


def test_parse_cli_args_and_build_json(monkeypatch):
    argv = ["receiver.py", "--task", "upscaling", "--input_path", "in.png",
            "--output_path", "out", "--input_format", "png", "--output_format",
            "png"]
    monkeypatch.setattr(sys, "argv", argv)
    args = receiver.parse_cli_args()
    req = receiver.build_json_from_args(args)
    assert req == {
        "task": "upscaling",
        "input_format": "png",
        "output_format": "png",
        "input_path": "in.png",
        "output_path": "out",
    }


def test_build_json_omits_none(monkeypatch):
    argv = ["receiver.py", "--task", "upscaling", "--input_path", "f.png",
            "--input_format", "png", "--output_format", "png"]
    monkeypatch.setattr(sys, "argv", argv)
    args = receiver.parse_cli_args()
    req = receiver.build_json_from_args(args)
    assert "output_path" not in req


def test_receiver_main_cli_success(monkeypatch, tmp_path, capsys):
    input_file = tmp_path / "img.png"
    input_file.write_text("data")
    output_dir = tmp_path / "out"
    output_dir.mkdir()

    argv = [
        "receiver.py",
        "--task",
        "upscaling",
        "--input_path",
        str(input_file),
        "--output_path",
        str(output_dir),
        "--input_format",
        "png",
        "--output_format",
        "png",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    # Skip validation of extra blocks
    monkeypatch.setattr(receiver, "validate_json_request", lambda req: (True, ""))
    dummy_operator = types.SimpleNamespace(process_request=lambda req: {"status": "success", "output_path": "done"})
    monkeypatch.setitem(sys.modules, "core.operator", dummy_operator)
    # Run main
    receiver.main()
    out = capsys.readouterr().out.strip()
    result = json.loads(out)
    assert result["status"] == "success"
    assert result["log_path"]


def test_receiver_main_cli_missing_argument(monkeypatch, tmp_path, capsys):
    input_file = tmp_path / "img.png"
    input_file.write_text("data")
    argv = [
        "receiver.py",
        "--task",
        "upscaling",
        "--input_path",
        str(input_file),
        # missing input_format
        "--output_format",
        "png",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit):
        receiver.main()
    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    assert data["status"] == "error"
    assert "input_format" in data["message"]
