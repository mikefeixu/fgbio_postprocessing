#!/usr/bin/env python3

import re
import sys
import pysam
import os

def parse_qname(qname):
    """
    Parse the QNAME to extract key information for detecting complementary reads.
    Expected format: consensus_read_REF1+REF2_POS1_POS2_POS3_POS4_ORIENTATION

    :param qname: string
    :return: tuple (normalized_ref_pair, normalized_position_pair, orientation)
    """
    parts = qname.split("_")

    if len(parts) != 8:
        return None

    ref_pair = parts[2]  # Example: GGA+AAT
    pos1, pos2, pos3, pos4 = parts[3], parts[4], parts[5], parts[6]
    orientation = parts[7]  # Important for complementary detection

    ref1, ref2 = ref_pair.split("+")
    pos_pair1 = (pos1, pos2)
    pos_pair2 = (pos3, pos4)

    forward_key = (ref1, ref2, pos_pair1, pos_pair2)
    reverse_key = (ref2, ref1, pos_pair2, pos_pair1)

    return forward_key, reverse_key

def load_duplex_keys(duplex_bam):
    """
    Load forward and reverse keys from a duplex BAM file to identify duplex-supported reads.
    
    :param duplex_bam: string
    :return: set of duplex keys
    """
    duplex_keys = set()
    
    if not os.path.isfile(duplex_bam):
        sys.stderr.write(f"Duplex BAM file {duplex_bam} does not exist.\n")
        sys.exit(1)
    
    with pysam.AlignmentFile(duplex_bam, "rb") as bamfile:
        for read in bamfile.fetch():
            parsed_qnames = parse_qname(read.query_name)
            if parsed_qnames:
                forward_key, reverse_key = parsed_qnames
                duplex_keys.add(forward_key)
                duplex_keys.add(reverse_key)
    
    return duplex_keys

def filter_simplex_with_duplex(input_bam, duplex_bam, output_filename, min_simplex_reads):
    """
    Filter a DRAGEN UMI-collapsed BAM to exclude simplex reads that have a duplex complement in another BAM.

    :param input_bam: string
    :param duplex_bam: string
    :param output_filename: string
    :param min_simplex_reads: int
    """
    if not os.path.isfile(input_bam):
        sys.stderr.write(f"Input BAM file {input_bam} does not exist.\n")
        sys.exit(1)

    if not output_filename:
        base = os.path.basename(input_bam)
        output_filename = os.path.splitext(base)[0] + "_simplex_filtered.bam"
    
    # Load duplex keys from the duplex BAM
    duplex_keys = load_duplex_keys(duplex_bam)
    
    bamfile = pysam.AlignmentFile(input_bam, "rb")
    simplex = pysam.AlignmentFile(output_filename, "wb", template=bamfile)
    
    total_reads = 0
    total_filtered = 0
    total_retained = 0
    
    # Filter reads based on the duplex BAM
    for read in bamfile.fetch():
        total_reads += 1
        
        qname = read.query_name
        parsed_qnames = parse_qname(qname)
        if not parsed_qnames:
            continue
        
        forward_key, reverse_key = parsed_qnames
        
        # Check if the read has a duplex complement
        if forward_key in duplex_keys or reverse_key in duplex_keys:
            total_filtered += 1
            continue
        
        # Extract XV and XW tags
        if not read.has_tag("XV") or not read.has_tag("XW"):
            continue
        
        xv_tag = read.get_tag("XV")  # Total supporting fragments
        xw_tag = read.get_tag("XW")  # Duplex fragments

        # Keep simplex reads that don't have a duplex counterpart and meet criteria
        if xv_tag >= min_simplex_reads and xw_tag == 0:
            simplex.write(read)
            total_retained += 1
    
    bamfile.close()
    simplex.close()

    # Index the output BAM file
    try:
        pysam.index(output_filename, re.sub(".bam$", "", output_filename) + ".bai")
    except Exception as e:
        sys.stderr.write(f"Could not index simplex BAM file {output_filename}. Error: {e}\n")
    
    # Log statistics
    print(f"Total Reads Processed: {total_reads}")
    print(f"Total Reads Retained: {total_retained}")
    print(f"Total Reads Filtered: {total_filtered}")
    
    if total_retained == 0:
        sys.stderr.write("⚠ WARNING: No reads were retained. Over-filtering may have occurred.\n")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.stderr.write("Usage: python3 filter_simplex_with_duplex.py <input_bam> <duplex_bam> <output_bam> <min_simplex_reads>\n")
        sys.exit(1)

    input_bam = sys.argv[1]
    duplex_bam = sys.argv[2]
    output_bam = sys.argv[3]
    min_simplex_reads = int(sys.argv[4])

    filter_simplex_with_duplex(input_bam, duplex_bam, output_bam, min_simplex_reads)
