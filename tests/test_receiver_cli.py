import sys
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
