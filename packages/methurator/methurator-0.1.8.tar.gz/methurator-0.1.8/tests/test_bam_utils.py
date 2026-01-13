import pytest
from methurator.config_utils.config_formatter import ConfigFormatter
from methurator.config_utils.validation_utils import ensure_coordinated_sorted
import pathlib


@pytest.fixture
def bam_file(tmp_path):
    bam_path = pathlib.Path(__file__).parent / "data" / "Ecoli.unsorted.bam"
    return str(bam_path)


def test_file_not_found():
    configs = ConfigFormatter(**{"bam": "does_not_exist.bam", "verbose": False})
    with pytest.raises(Exception):
        ensure_coordinated_sorted(bam_file, configs)


def test_unsorted_bam_triggers_sort(monkeypatch, bam_file):
    calls = []
    configs = ConfigFormatter(**{"bam": bam_file, "verbose": False})

    def fake_run(*args, **kwargs):
        calls.append(args[0])

    monkeypatch.setattr("subprocess.run", fake_run)

    result = ensure_coordinated_sorted(bam_file, configs)

    assert calls, "samtools not called for unsorted BAM"
    assert result.endswith(".csorted.bam")
