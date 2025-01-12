import os
import shutil
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


def get_script_dir():
    return Path(__file__).parent.resolve()


def setup_target_dir():
    target_dir = (
        get_script_dir().parent / "src" / "static" / "vendor" / "tts-sherpa-onnx"
    )

    if not target_dir.exists():
        raise RuntimeError(f"Target directory does not exist: {target_dir}")
    if not os.access(target_dir, os.W_OK):
        raise RuntimeError(f"Target directory is not writable: {target_dir}")

    return target_dir


def download_file(url, target_file, tmp_file, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"Downloading {target_file.name}...")
            urllib.request.urlretrieve(url, tmp_file)

            if not os.path.exists(tmp_file):
                raise RuntimeError(f"Download file not found: {tmp_file}")
            if os.path.getsize(tmp_file) == 0:
                raise RuntimeError(f"Downloaded file is empty: {tmp_file}")

            shutil.move(tmp_file, target_file)
            print(f"Download completed successfully to: {target_file}")
            return True

        except Exception as e:
            if attempt < max_retries - 1:
                print(
                    f"Download failed, retrying (attempt {attempt + 1} of {max_retries})..."
                )
                time.sleep(2)
            else:
                print(f"Error downloading {url}: {str(e)}", file=sys.stderr)
                return False


def main():
    files = {
        "sherpa-onnx-wasm-main-tts.data": "https://huggingface.co/spaces/k2-fsa/web-assembly-tts-sherpa-onnx-en/resolve/main/sherpa-onnx-wasm-main-tts.data",  # noqa: E501
        "sherpa-onnx-wasm-main.wasm": "https://huggingface.co/spaces/k2-fsa/web-assembly-tts-sherpa-onnx-en/resolve/main/sherpa-onnx-wasm-main.wasm",  # noqa: E501
        "sherpa-onnx-wasm-main-tts.wasm": "https://huggingface.co/spaces/k2-fsa/web-assembly-tts-sherpa-onnx-en/resolve/main/sherpa-onnx-wasm-main-tts.wasm",  # noqa: E501
    }

    try:
        target_dir = setup_target_dir()

        print("Pulling Wasm client side TTS...")

        with tempfile.TemporaryDirectory() as temp_dir:
            for filename, url in files.items():
                target_file = target_dir / filename

                if target_file.exists():
                    print(f"File already exists at: {target_file}")
                    print("Skipping download")
                    continue

                tmp_file = Path(temp_dir) / f"{filename}.tmp"

                if not download_file(url, target_file, tmp_file):
                    return 1

        print("All downloads completed successfully!")
        return 0

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
