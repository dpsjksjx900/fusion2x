import os
import sys
import json
import subprocess
from utils import env_setup

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "utils"))
)  # noqa: E402
from PyQt5.QtWidgets import (  # noqa: E402
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QComboBox,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QCheckBox,
    QGroupBox,
)

from utils.logger import get_logger  # noqa: E402
from utils.logfile_utils import make_log_filename
gui_log_path = os.path.join("logs", "gui.log")
os.makedirs("logs", exist_ok=True)
logger = get_logger(gui_log_path, module_name="GUI")
env_setup.ensure_vc_runtime(logger)




# Model options (update if you add more in handlers)
UPSCALE_MODELS = [
    "waifu2x-ncnn-vulkan",
    "realesrgan-ncnn-vulkan",
    "realcugan-ncnn-vulkan",
    "realsr-ncnn-vulkan",
    "srmd-ncnn-vulkan"
]
INTERP_MODELS = [
    "rife-ncnn-vulkan"
]
VIDEO_OUTPUT_FORMATS = ["mp4", "gif", "webm", "avi", "mov", "mkv"]
IMAGE_OUTPUT_FORMATS = ["png", "jpg"]


class Fusion2XGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.log_path = make_log_filename()
        self.logger = get_logger(self.log_path, module_name="GUI")
        self.setWindowTitle("Fusion2X - Video AI Processing")
        self.resize(750, 520)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Input/output fields
        file_layout = QHBoxLayout()
        self.input_line = DropLineEdit(on_drop_callback=self.on_input_drop)
        input_btn = QPushButton("Browse Input")
        input_btn.clicked.connect(self.browse_input)
        file_layout.addWidget(QLabel("Input file:"))
        file_layout.addWidget(self.input_line)
        file_layout.addWidget(input_btn)

        out_layout = QHBoxLayout()
        self.output_line = QLineEdit()
        output_btn = QPushButton("Browse Output Dir")
        output_btn.clicked.connect(self.browse_output)
        out_layout.addWidget(QLabel("Output directory:"))
        out_layout.addWidget(self.output_line)
        out_layout.addWidget(output_btn)

        format_layout = QHBoxLayout()
        self.video_output_combo = QComboBox()
        self.video_output_combo.addItems(VIDEO_OUTPUT_FORMATS)
        format_layout.addWidget(QLabel("Video output format:"))
        format_layout.addWidget(self.video_output_combo)
        self.image_output_combo = QComboBox()
        self.image_output_combo.addItems(IMAGE_OUTPUT_FORMATS)
        format_layout.addWidget(QLabel("Image output format:"))
        format_layout.addWidget(self.image_output_combo)

        # Processing option groups
        self.upscale_group = self.make_upscale_group()
        self.interp_group = self.make_interp_group()

        # Run button and log
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.run_fusion2x)
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        # Layout
        layout.addLayout(file_layout)
        layout.addLayout(out_layout)
        layout.addLayout(format_layout)
        layout.addWidget(self.upscale_group)
        layout.addWidget(self.interp_group)
        layout.addWidget(self.run_btn)
        layout.addWidget(QLabel("Status Log:"))
        layout.addWidget(self.log_box)
        self.setLayout(layout)

    def make_upscale_group(self):
        group = QGroupBox("Upscaling")
        group.setCheckable(True)
        group.setChecked(True)
        layout = QVBoxLayout()

        self.upscale_model_combo = QComboBox()
        self.upscale_model_combo.addItems(UPSCALE_MODELS)
        self.upscale_model_combo.setCurrentIndex(0)
        layout.addWidget(QLabel("Upscaling Model:"))
        layout.addWidget(self.upscale_model_combo)

        hl = QHBoxLayout()
        hl.addWidget(QLabel("Scale:"))
        self.upscale_scale = QSpinBox()
        self.upscale_scale.setRange(1, 8)
        self.upscale_scale.setValue(2)
        hl.addWidget(self.upscale_scale)

        hl.addWidget(QLabel("Noise Level:"))
        self.upscale_noise = QSpinBox()
        self.upscale_noise.setRange(0, 3)
        self.upscale_noise.setValue(2)
        hl.addWidget(self.upscale_noise)

        layout.addLayout(hl)

        self.upscale_threads = QSpinBox()
        self.upscale_threads.setRange(1, 16)
        self.upscale_threads.setValue(2)
        layout.addWidget(QLabel("Threads:"))
        layout.addWidget(self.upscale_threads)

        self.upscale_gpu = QSpinBox()
        self.upscale_gpu.setRange(0, 7)
        self.upscale_gpu.setValue(0)
        layout.addWidget(QLabel("GPU ID:"))
        layout.addWidget(self.upscale_gpu)

        group.setLayout(layout)
        return group

    def make_interp_group(self):
        group = QGroupBox("Interpolation")
        group.setCheckable(True)
        group.setChecked(True)
        layout = QVBoxLayout()

        self.interp_model_combo = QComboBox()
        self.interp_model_combo.addItems(INTERP_MODELS)
        layout.addWidget(QLabel("Interpolation Model:"))
        layout.addWidget(self.interp_model_combo)

        hl = QHBoxLayout()
        hl.addWidget(QLabel("Times:"))
        self.interp_times = QSpinBox()
        self.interp_times.setRange(2, 8)
        self.interp_times.setValue(2)
        hl.addWidget(self.interp_times)

        hl.addWidget(QLabel("Threads:"))
        self.interp_threads = QSpinBox()
        self.interp_threads.setRange(1, 16)
        self.interp_threads.setValue(4)
        hl.addWidget(self.interp_threads)

        hl.addWidget(QLabel("GPU ID:"))
        self.interp_gpu = QSpinBox()
        self.interp_gpu.setRange(0, 7)
        self.interp_gpu.setValue(0)
        hl.addWidget(self.interp_gpu)

        layout.addLayout(hl)

        self.tta_checkbox = QCheckBox("Enable TTA Mode")
        self.uhd_checkbox = QCheckBox("Enable UHD Mode")
        layout.addWidget(self.tta_checkbox)
        layout.addWidget(self.uhd_checkbox)

        group.setLayout(layout)
        return group

    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select input file")
        if path:
            self.input_line.setText(path)
            # Set output dir to input file's folder (only if output is blank)
            if not self.output_line.text().strip():
                self.output_line.setText(os.path.dirname(path))

    def on_input_drop(self, path):
        # When file is dropped, set output directory if not already set
        if not self.output_line.text().strip():
            self.output_line.setText(os.path.dirname(path))

    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select output directory")
        if path:
            self.output_line.setText(path)


    def run_fusion2x(self):
        input_path = self.input_line.text().strip()
        output_path = self.output_line.text().strip()
        if not input_path or not output_path:
            self.log_box.append("[ERROR] Please select both an input file and an output directory before running.")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Input/Output Missing", "Please select both an input file and an output directory before running.")
            return

        config = self.collect_config()
        config["log_path"] = self.log_path  # Pass log path to receiver
        self.logger.info("User clicked Run. Collected config:")
        self.logger.info(json.dumps(config, indent=2))
        self.log_box.clear()
        self.log_box.append("Starting Fusion2X...")

        try:
            env = os.environ.copy()
            env["FUSION2X_LOG_PATH"] = self.log_path
            proc = subprocess.Popen(
                [sys.executable, "receiver.py"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                env=env
            )
            stdout, stderr = proc.communicate(json.dumps(config).encode('utf-8'))
            if stderr:
                self.log_box.append("[stderr]\n" + stderr.decode())
                self.logger.error(f"Receiver.py stderr: {stderr.decode()}")
            try:
                result = json.loads(stdout.decode())
                self.logger.info(f"Receiver.py output: {result}")
                if result.get("status") == "success":
                    self.log_box.append("Done!\nOutput: " + str(result.get("output_path")))
                    self.log_box.append("Log: " + str(result.get("log_path", self.log_path)))
                else:
                    self.log_box.append("[ERROR] " + result.get("message", "Unknown error"))
                    self.log_box.append("Log: " + str(result.get("log_path", self.log_path)))
            except Exception as e:
                self.log_box.append("Raw output:\n" + stdout.decode())
                self.logger.error(f"Failed to parse receiver output: {e}")
        except Exception as e:
            self.logger.error(f"Exception in GUI: {e}")
            self.log_box.append("[Exception] " + str(e))



    def collect_config(self):
        # Core config (input/output/task)
        up_enabled = self.upscale_group.isChecked()
        interp_enabled = self.interp_group.isChecked()
        if up_enabled and interp_enabled:
            task = "both"
        elif up_enabled:
            task = "upscaling"
        elif interp_enabled:
            task = "interpolation"
        else:
            task = "upscaling"
        input_path = self.input_line.text()
        output_path = self.output_line.text()
        input_format = os.path.splitext(input_path)[1][1:] if "." in input_path else "mp4"
        video_formats = ["mp4", "avi", "mkv", "mov", "webm", "gif"]
        if input_format in video_formats:
            output_format = self.video_output_combo.currentText()
        else:
            output_format = self.image_output_combo.currentText()

        config = {
            "task": task,
            "input_format": input_format,
            "output_format": output_format,
            "input_path": input_path,
            "output_path": output_path
        }

        if up_enabled:
            config["upscaling"] = {
                "enabled": True,
                "model_name": self.upscale_model_combo.currentText(),
                "params": {
                    "scale": self.upscale_scale.value(),
                    "noise_level": self.upscale_noise.value(),
                    "output_format": self.image_output_combo.currentText(),
                    "gpu_id": self.upscale_gpu.value(),
                    "threads": self.upscale_threads.value()
                }
            }

        if interp_enabled:
            config["interpolation"] = {
                "enabled": True,
                "model_name": self.interp_model_combo.currentText(),
                "params": {
                    "times": self.interp_times.value(),
                    "output_format": self.image_output_combo.currentText(),
                    "threads": self.interp_threads.value(),
                    "gpu_id": self.interp_gpu.value(),
                    "tta_mode": self.tta_checkbox.isChecked(),
                    "uhd_mode": self.uhd_checkbox.isChecked()
                }
            }
        # Add misc options as needed
        config["misc"] = {
            "keep_temp": False,
            "log_level": "info",
            "overwrite": True,
            "batch": False
        }
        return config


class DropLineEdit(QLineEdit):
    def __init__(self, *args, on_drop_callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.on_drop_callback = on_drop_callback

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            path = url.toLocalFile()
            self.setText(path)
            if self.on_drop_callback:
                self.on_drop_callback(path)
            event.acceptProposedAction()
        else:
            event.ignore()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Fusion2XGUI()
    window.show()
    sys.exit(app.exec_())
