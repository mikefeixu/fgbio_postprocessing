import click

from fgbio_postprocessing import simplex_filter


@click.command()
@click.option("--input_bam", required=True, help="Path to simplex BAM to be filtered")
@click.option("--duplex_bam", required=True, help="Path to duplex BAM used to identify duplex reads for removal")
@click.option("--output_filename", required=False, help="Name of output filtered BAM")
@click.option("--min_simplex_reads", required=False, default=3, type=int, help="Minimum number of simplex reads to pass filter")
def filter_simplex(input_bam, duplex_bam, output_filename, min_simplex_reads):
    """
    Filter simplex BAM to remove reads that have a duplex complement in the duplex BAM.
    """
    simplex_filter.filter_simplex_with_duplex(input_bam, duplex_bam, output_filename, min_simplex_reads)