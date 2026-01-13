import subprocess
import os


def subsample_bam(bam_path, percentage, output_dir, seed=42):
    """
    Subsamples a BAM file using samtools according to a percentage.
    """

    # Create bams directory to store the bam files
    bam_dir = os.path.join(output_dir, "bams")
    os.makedirs(bam_dir, exist_ok=True)

    # Round the downsampling percentage and init the output bam name
    round_pct = round(percentage, 2)
    output_path = bam_path

    # If percentage is different than 1, then subsample
    if percentage != 1:

        # Extract the sample name and create the output path
        base_name = os.path.basename(bam_path).replace(
            ".bam", f"_subsample_{round_pct:.1f}.bam"
        )
        output_path = os.path.join(bam_dir, base_name)

        # Subsample BAM using samtools
        cmd = [
            "samtools",
            "view",
            "-s",
            str(round_pct),
            "--subsample-seed",
            str(seed),
            "-b",
            bam_path,
            "-o",
            output_path,
        ]
        subprocess.run(cmd, check=True)

    # Index the subsampled BAM
    cmd2 = ["samtools", "index", output_path]
    subprocess.run(cmd2, check=True)

    # Count reads in the subsampled BAM
    read_count = int(
        subprocess.run(
            ["samtools", "view", "-c", output_path], capture_output=True, text=True
        ).stdout.strip()
    )

    # Extract the name and save it in the stats list
    sample_name = os.path.basename(bam_path).split(".", 1)[0]
    sample_stats = [sample_name, round_pct, read_count]
    return sample_stats, output_path
