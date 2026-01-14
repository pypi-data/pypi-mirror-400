def read_to_tuple(read):
    """
    Examples
    --------
    >>> class _R:
    ...     def __init__(self, n, seq, qual, cig):
    ...         self.query_name = n
    ...         self.query_sequence = seq
    ...         self.query_qualities = qual
    ...         self.cigarstring = cig
    ...
    >>> r = _R("r1", "ACGT", [30, 31, 32, 33], "4M")
    >>> read_to_tuple(r)
    ['r1', 'ACGT', [30, 31, 32, 33], '4M']
    """
    return [
        read.query_name,
        read.query_sequence,
        read.query_qualities,
        read.cigarstring,
    ]


def read_bam_pair(bam_for_file, bam_rev_file, input_queue, num_processes):
    """
    Read simultaneously two BAM files and put read pairs into an input queue.

    Parameters:
        bam_for_file (str): Path to the forward BAM file.
        bam_rev_file (str): Path to the reverse BAM file.
        Input_Queue (Queue): Queue to store read pairs.
        TFrag (int): Number of fragmenting threads.
    """
    import sys

    import pysam

    try:
        with (
            pysam.AlignmentFile(bam_for_file, "rb") as bam_for,
            pysam.AlignmentFile(bam_rev_file, "rb") as bam_rev,
        ):
            for read_for, read_rev in zip(bam_for, bam_rev):
                if read_for and read_rev:
                    # Convert read objects to serializable format
                    input_queue.put([read_to_tuple(read_for), read_to_tuple(read_rev)])
    except Exception as e:
        print(f"Error: with {bam_for_file} or {bam_rev_file}, {e}")
        sys.exit(1)
    finally:
        for _ in range(num_processes):
            input_queue.put(None)
