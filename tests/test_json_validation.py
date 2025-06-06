import utils.json_utils as ju


def test_invalid_video_output_for_image_input():
    req = {"task": "upscaling", "input_format": "png", "output_format": "mp4", "input_path": "x"}
    valid, reason = ju.validate_json_request(req)
    assert not valid
    assert "image input" in reason


def test_invalid_image_output_for_video_input():
    req = {"task": "upscaling", "input_format": "gif", "output_format": "jpg", "input_path": "x"}
    valid, reason = ju.validate_json_request(req)
    assert not valid
    assert "video input" in reason

