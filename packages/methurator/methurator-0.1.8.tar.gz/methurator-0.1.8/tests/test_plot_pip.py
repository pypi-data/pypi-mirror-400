import subprocess


def test_methurator_plot(tmp_path):
    """Test the 'methurator plot' CLI command."""

    # Define the command as a list (like in subprocess)
    cmd = [
        "methurator",
        "plot",
        "-s",
        "tests/data/methurator_summary.yml",
        "--outdir",
        str(tmp_path),
    ]

    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check that the command succeeded
    assert (
        result.returncode == 0
    ), f"Command failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    # Path of expected output
    plot1 = tmp_path / "plots/Ecoli_1x_plot.html"
    plot2 = tmp_path / "plots/Ecoli_3x_plot.html"

    # Assert that the plot was created
    assert plot1.exists(), f"{plot1} not found"
    assert plot2.exists(), f"{plot2} not found"
