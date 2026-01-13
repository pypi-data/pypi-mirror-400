import subprocess
import sys


def test_module_entrypoint() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "musicxml_to_motif"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "musicxml-to-motif" in result.stdout
