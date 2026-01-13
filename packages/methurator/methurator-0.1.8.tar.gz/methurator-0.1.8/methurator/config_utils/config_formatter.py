GENOME_URLS = {
    "hg19": "https://hgdownload.soe.ucsc.edu/goldenPath/hg19/bigZips/hg19.fa.gz",
    "hg38": "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz",
    "GRCh38": "http://ftp.ensembl.org/pub/release-109/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz",
    "GRCh37": "http://ftp.ensembl.org/pub/release-109/fasta/homo_sapiens/dna/Homo_sapiens.GRCh37.dna.primary_assembly.fa.gz",
    "mm10": "https://hgdownload.soe.ucsc.edu/goldenPath/mm10/bigZips/mm10.fa.gz",
    "mm39": "https://hgdownload.soe.ucsc.edu/goldenPath/mm39/bigZips/mm39.fa.gz",
}


class ConfigFormatter:

    def __init__(self, **kwargs):
        self.bam = kwargs.get("bam")
        self.outdir = kwargs.get("outdir")
        self.fasta = kwargs.get("fasta")
        self.genome = kwargs.get("genome")
        self.downsampling_percentages = kwargs.get("downsampling_percentages")
        self.minimum_coverage = kwargs.get("minimum_coverage")
        self.rrbs = kwargs.get("rrbs")
        self.threads = kwargs.get("threads")
        self.keep_temporary_files = kwargs.get("keep_temporary_files")
        self.summary = kwargs.get("summary")
        self.verbose = kwargs.get("verbose")
