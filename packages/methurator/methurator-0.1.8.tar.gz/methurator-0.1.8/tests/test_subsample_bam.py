import os
import pathlib
from methurator.downsample_utils.subsample_bam import subsample_bam


def test_subsample_when_percentage_is_one(tmp_path, monkeypatch):

    # Specify percentage = 1 and the bam file path
    pct = 1
    bam = pathlib.Path(__file__).parent / "data" / "Ecoli.csorted.bam"

    # Extract the sample name and create the output path
    base_name = os.path.basename(bam).replace(".bam", f"_subsample_{pct}.bam")
    output_path = os.path.join(tmp_path, "bams/", base_name)

    # Run the subsampling and get the output
    stats, output = subsample_bam(str(bam), pct, str(output_path))

    # Check that the output are the expected ones
    assert stats[0] == "Ecoli"
    assert stats[1] == 1
    assert stats[2] == 10
    assert output == str(bam)


def test_subsample_when_percentage_not_one(tmp_path, monkeypatch):
    # Specify percentage != 1 and the bam file path
    pct = 0.5
    bam = pathlib.Path(__file__).parent / "data" / "Ecoli.csorted.bam"

    # Extract the sample name and create the output path
    base_name = os.path.basename(bam).replace(".bam", f"_subsample_{pct}.bam")
    output_path = os.path.join(tmp_path, "bams/", base_name)

    # Run the subsampling and get the output
    stats, output = subsample_bam(str(bam), pct, str(tmp_path), 42)

    # Check that the output are the expected ones
    assert stats[0] == "Ecoli"
    assert stats[1] == 0.5
    assert stats[2] in (6, 8)  # ubuntu, macOS
    assert output == str(output_path)
