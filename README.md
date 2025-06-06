## How to Run Fusion2X

1. Download/extract Fusion2X.
2. Double-click `run_fusion2x.bat` (Windows) or run `bash run_fusion2x.sh` (Mac/Linux).
   - These scripts set up a virtual environment and start the GUI via `gui.py`.
   - The first run may take a few minutes while dependencies and models are downloaded.
   - All dependencies, models, and FFmpeg will be installed automatically in the `.venv` and `models/` folders.
   - You can also run `python gui.py` directly if you manage your own environment.
3. The Fusion2X GUI will launch. All logs are saved in `logs/`.


## To update Fusion2X


- Run `update_fusion2x.bat` (Windows) or `bash update_fusion2x.sh` (Mac/Linux)
  from the Fusion2X folder. The script will clone the official repository if it
  is missing, then pull the newest code and refresh all Python dependencies in
  the `.venv` environment.

## Troubleshooting


If Fusion2X fails to start on Windows with an error about `vcruntime140.dll`
or `vcruntime140_1.dll`, run `run_fusion2x.bat` again. The batch script now
executes `python install_fusion2x.py`, which downloads and installs the
Microsoft Visual C++ runtime silently if it is missing. You can also run the
installer manually with `python install_fusion2x.py`.

### "The process crashed (0xC0000005)" error

If a model process exits with code `0xC0000005`, it usually means there is a
problem with the underlying GPU or runtime libraries. To resolve this:

1. **Update GPU drivers** – install the latest drivers for your graphics card
   from the vendor's website (NVIDIA, AMD or Intel).
2. **Install the Microsoft Visual C++ Redistributable** – on Windows make sure
   the [Visual C++ Runtime](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist)
   is installed.

After installing the required drivers and runtime components, try running
Fusion2X again.

