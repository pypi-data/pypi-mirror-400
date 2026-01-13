import os
import urllib.request
import subprocess
from methurator.config_utils.config_formatter import GENOME_URLS
from tqdm import tqdm
from methurator.config_utils.verbose_utils import vprint


class DownloadProgressBar(tqdm):
    def update_to(self, blocks=1, block_size=1, total_size=None):
        if total_size is not None:
            self.total = total_size
        self.update(blocks * block_size - self.n)


def get_reference(configs):

    # Download the reference genome
    url = GENOME_URLS[configs.genome]
    os.makedirs(configs.outdir, exist_ok=True)
    gz_path = os.path.join(configs.outdir, f"{configs.genome}.fa.gz")
    fasta_path = os.path.join(configs.outdir, f"{configs.genome}.fa")

    vprint(
        f"[bold]Downloading reference genome[/bold] [green]'{configs.genome}'...[/green]",
        True,
    )
    with DownloadProgressBar(
        unit="B", unit_scale=True, miniters=1, desc="Downloading"
    ) as t:
        urllib.request.urlretrieve(url, gz_path, reporthook=t.update_to)
    vprint(f"🗜️  Extracting {gz_path}...", configs.verbose)
    subprocess.run(["gunzip", "-f", gz_path], check=True)
    vprint(f"✅ Reference genome ready: {fasta_path}", True)

    return fasta_path
