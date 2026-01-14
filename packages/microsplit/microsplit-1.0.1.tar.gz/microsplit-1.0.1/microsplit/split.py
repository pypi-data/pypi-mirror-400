import logging
import os
import signal
import sys
import time
from multiprocessing import Queue

from microsplit.auxiliary import partitionning
from microsplit.bam import read_bam_pair
from microsplit.fastq import write_fastq_pair
from microsplit.processmanager import ProcessManager

logger = logging.getLogger(__name__)


def phred_to_ascii(quality):
    """
    # Convert quality scores to ASCII characters
    Examples
    --------
    >>> phred_to_ascii([0, 1, 2])
    '!"#'
    >>> phred_to_ascii([30, 31, 32, 33])
    '?@AB'
    >>> phred_to_ascii([])
    ''
    """
    return "".join(chr(q + 33) for q in quality)


def build_cigar_tuple(cigar):
    """
    Parse CIGAR string into tuples of operations and lengths.

    Examples
    --------
    >>> build_cigar_tuple("10M1I5M2D3S")
    [['M', 'I', 'M', 'D', 'S'], [10, 1, 5, 2, 3]]
    >>> build_cigar_tuple("5S95M")
    [['S', 'M'], [5, 95]]
    >>> build_cigar_tuple("100M")
    [['M'], [100]]
    >>> build_cigar_tuple("")
    [[], []]
    >>> build_cigar_tuple("5H10M5H")
    [['H', 'M', 'H'], [5, 10, 5]]
    >>> build_cigar_tuple("10MXXX")  # non-CIGAR ignored
    [['M'], [10]]
    """
    import re

    cigar_tuples = [[], []]

    for match in re.finditer(r"(\d+)([MIDNSHP=X])", cigar):
        times = int(match.group(1))
        code = match.group(2)
        cigar_tuples[0].append(code)
        cigar_tuples[1].append(times)
    return cigar_tuples


def write_read(name, sequence, quality, start, stop):
    """
    write a sequence

    Examples
    --------
    >>> write_read("@r1", "ACGT", "IIII", 1, 3)
    '@r1\\nCG\\n+\\nII\\n'
    >>> write_read("@r1", "ACGT", "IIII", 0, 4)
    '@r1\\nACGT\\n+\\nIIII\\n'
    """
    return (
        name
        + "\n"
        + sequence[start:stop]
        + "\n"
        + "+"
        + "\n"
        + quality[start:stop]
        + "\n"
    )


def soft_clip_sequence(name, sequence, quality_str, index, len_add):
    """
    write a sequence with soft clipped
    """
    write_read(
        name=name, sequence=sequence, quality=quality_str, start=0, stop=index + len_add
    )


def mapped_sequence(name, sequence, quality_str, index):
    """
    write a mapped sequence
    """
    write_read(
        name=name,
        sequence=sequence,
        quality=quality_str,
        start=index,
        stop=len(sequence),
    )


def count_len(cigar_ops, cigar_lens):
    """
    Calculates the length consumed in the read (ignores D, N, H, P)
    and also returns the qpos_before positions (read coordinates
    at the start of each CIGAR operator).

    Parameters
    ----------
    cigar_ops : list of str
        CIGAR operations, e.g. ['S','M','S'].
    cigar_lens : list of int
        Corresponding lengths, e.g. [1,2,1].

    Returns
    -------
    qpos_before : list of int
        Read positions before each CIGAR op.
    qpos : int
        Total length consumed in the read.

    Examples
    --------
    >>> qpos_before, qpos = count_len(['M', 'I', 'D', 'S'], [5, 2, 3, 4])
    >>> qpos_before
    [0, 5, 7, 7]
    >>> qpos
    11
    >>> count_len(['N', 'H', 'P'], [10, 5, 2])
    ([0, 0, 0], 0)
    """
    qpos_before = []
    qpos = 0
    for op, ln in zip(cigar_ops, cigar_lens):
        qpos_before.append(qpos)
        if op in ("M", "I", "S", "=", "X"):
            qpos += ln
        # D, N, H, P doesn't consume the read (len)
    return qpos_before, qpos


def process_cigard(read_data, seed_size, len_add):
    """
    Extract fragments in the FastQ format from read
    Extract mapped fragments and non mapped fragment

    Parameters:
        read (tuple): The read from which to extract information.
        seed_size (int): The minimum size of a segment to be considered for extraction.
        len_add (int): Number of base pairs added to the neoformed fragment after completion of soft clipping.

    Returns:
        tuple: A tuple containing the read name and a list of FastQ format strings.

    Examples
    --------
    Cas sans soft-clip:
    >>> name, seq, qual, cig = "@r", "ACGT", [40,40,40,40], "4M"
    >>> n, frags = process_cigard((name, seq, qual, cig), seed_size=0, len_add=0)
    >>> n
    '@r'
    >>> frags == ['@r\\nACGT\\n+\\nIIII\\n']
    True
    >>> # Un soft-clip en tête (ex: 2S2M, len_add=1):
    >>> name, seq, qual, cig = "@r", "ACGT", [30,31,32,33], "2S2M"
    >>> n, frags = process_cigard((name, seq, qual, cig), seed_size=0, len_add=1)
    >>> len(frags)
    2
    >>> frags
    ['@r\\nACG\\n+\\n?@A\\n', '@r\\nCGT\\n+\\n@AB\\n']
    >>> frags[0].startswith('@r\\n') or frags[0].startswith('@r\\n')  # labels M/S ordonnés selon le CIGAR
    True
    >>> # Deux soft-clips (ex: 1S2M1S, seed_size=1):
    >>> name, seq, qual, cig = "@r", "ACGT", [30,30,30,30], "1S2M1S"
    >>> n, frags = process_cigard((name, seq, qual, cig), seed_size=1, len_add=0)
    >>> len(frags)
    3
    >>> # Deux soft-clips (ex: 1S2M1S, seed_size=2):
    >>> name, seq, qual, cig = "@r", "ACGT", [30,30,30,30], "1S2M1S"
    >>> n, frags = process_cigard((name, seq, qual, cig), seed_size=2, len_add=0)
    >>> len(frags)
    1
    >>> frags
    ['@r\\nCG\\n+\\n??\\n']
    >>> # Deux soft-clips (ex: 1S2M1S, seed_size=3):
    >>> name, seq, qual, cig = "@r", "ACGT", [30,30,30,30], "1S2M1S"
    >>> n, frags = process_cigard((name, seq, qual, cig), seed_size=3, len_add=0)
    >>> len(frags)
    1
    >>> frags
    ['@r\\nACGT\\n+\\n????\\n']
    """
    name, sequence, quality, cigar = read_data
    quality_str = phred_to_ascii(quality)

    # Build_cigar_tuple retourne [ops_list, lens_list]
    cigar_ops, cigar_lens = build_cigar_tuple(cigar)

    # Intra reads coordinates
    qpos_before, q_pos = count_len(cigar_ops, cigar_lens)
    read_len = len(sequence)

    soft_clip_indices = [i for i, x in enumerate(cigar_ops) if x in ["S"]]

    def make_frag(start: int, stop: int):
        """
        Builds a FastQ fragment:
            - clamp start/stop in [0, read_len]
            - filter if length < seed_size
            - returns None if fragment is invalid
        """
        s = max(0, min(read_len, start))
        e = max(0, min(read_len, stop))
        if e <= s:
            return None
        if seed_size and (e - s) < seed_size:
            return None
        return write_read(f"{name}", sequence, quality_str, s, e)

    # Case 0 : No soft-clipping
    if len(soft_clip_indices) == 0:
        return name, [write_read(name, sequence, quality_str, 0, len(sequence))]

    # Case 1 : One soft-clip
    if len(soft_clip_indices) == 1:
        i = soft_clip_indices[0]

        if i == 0:
            # soft-clip first
            index = cigar_lens[i]
            frag1 = make_frag(0, index + len_add)
            frag2 = make_frag(index - len_add, read_len)
        else:
            # soft-clip end
            index = qpos_before[i]
            frag1 = make_frag(0, index + len_add)
            frag2 = make_frag(index - len_add, read_len)

        frags = [f for f in (frag1, frag2) if f is not None]

        # If everything were filtered
        if not frags:
            if not seed_size or read_len >= seed_size:
                return name, [write_read(name, sequence, quality_str, 0, read_len)]
        return name, frags

    # Case 2 : Two soft-clips (S ... M ... S)
    if len(soft_clip_indices) == 2:
        i0, i1 = soft_clip_indices

        ln0 = cigar_lens[i0]
        # fin du premier soft-clip en coordonnées read
        if i0 == 0:
            index1_end = ln0
        else:
            index1_end = qpos_before[i0] + ln0

        # début du second soft-clip en coordonnées read
        index2_start = qpos_before[i1]

        fragS1 = make_frag(0, index1_end + len_add)
        fragM = make_frag(index1_end - len_add, index2_start + len_add)
        fragS2 = make_frag(index2_start - len_add, read_len)

        frags = [f for f in (fragS1, fragM, fragS2) if f is not None]

        if not frags:
            if not seed_size or read_len >= seed_size:
                return name, [write_read(name, sequence, quality_str, 0, read_len)]
        return name, frags

    # > 2 soft-clips : garde-fou
    raise ValueError(
        f"More than two soft clipped segments found in CIGAR string ({cigar}) for read {name}. problem with mapping ?"
    )


def read_name(base_name, tag_i, tag_j):
    """
    Construit un header de paire à partir d'un nom de read et de deux tags.

    base_name : nom logique du read (avec ou sans '@')
    tag_i, tag_j : identifiants de fragments, typiquement 'F0', 'R1', etc.

    Retour:
        '@<base_name>:[<tag_i>,<tag_j>]'

    Examples
    --------
    >>> read_name("READ", "F0", "R1")
    '@READ:[F0,R1]'
    >>> read_name("@READ", "F0", "F1")  # lstrippage du '@' d'entrée
    '@READ:[F0,F1]'
    >>> read_name("@READ", "X", "Y")
    '@READ:[X,Y]'
    """
    base = base_name.lstrip("@")
    return f"@{base}:[{tag_i},{tag_j}]"


def gen_read_pairs(data, seed_size, len_add):
    """
    Génère deux chaînes FastQ (forward/reverse) à partir d’un couple de reads bruts.

    Étapes:
      1. `process_cigard` est appelé sur le read forward et le read reverse.
         Il renvoie:
            - un nom (avec '@'),
            - une liste de fragments au format FastQ complet:
              '@name_suffix\\nSEQ\\n+\\nQUAL\\n'
      2. Si le nombre total de fragments (F + R) <= 2:
            -> on renvoie simplement (frag_forward_0, frag_reverse_0)
      3. Si > 2:
            - On construit une liste de fragments annotés:
                ('F' ou 'R', index_local, SEQ, QUAL)
            - On prend toutes les combinaisons de 2 fragments (i, j).
            - Pour chaque paire:
                * header commun = '@READ:[<origin_i><i>,<origin_j><j>]'
                * sortie forward = header + fragment_i (seq/qual)
                * sortie reverse = header + fragment_j (seq/qual)
            - On concatène tous les couples dans deux grandes chaînes:
                [fastq_forward, fastq_reverse]

    Hypothèse simplificatrice:
      - Les noms forward et reverse d'origine sont identiques (mates d'une même paire).

    Examples
    --------
    Cas simple sans soft-clip: 1 fragment forward, 1 fragment reverse.
    >>> rf = ("@READ", "AC", [30, 30], "2M")
    >>> rr = ("@READ", "TG", [30, 30], "2M")
    >>> F, R = gen_read_pairs((rf, rr), seed_size=0, len_add=0)
    >>> F
    '@READ\\nAC\\n+\\n??\\n'
    >>> R
    '@READ\\nTG\\n+\\n??\\n'

    Cas combinatoire:
      - forward: CIGAR '1S3M' -> 2 fragments: F0, F1
      - reverse: CIGAR '2M'   -> 1 fragment: R0
      -> Total 3 fragments => combinaisons:
           (F0,F1), (F0,R0), (F1,R0)
      -> Headers:
           @READ:[F0,F1]
           @READ:[F0,R0]
           @READ:[F1,R0]
      -> Pas de duplication de '@', tags explicites F/R.

    >>> rf = ("@READ", "ABCD", [28,28,28,28], "1S3M")
    >>> rr = ("@READ", "WXYZ", [29,29,29,29], "2M")
    >>> F, R = gen_read_pairs((rf, rr), seed_size=0, len_add=0)
    >>> # On a bien 3 paires => 3 headers
    >>> F.count('@READ:['), R.count('@READ:[')
    (3, 3)
    >>> # Vérifie la présence des tags attendus
    >>> '@READ:[F0,F1]' in F
    True
    >>> '@READ:[F0,R0]' in F
    True
    >>> '@READ:[F1,R0]' in F
    True
    >>> '@READ:[F0,F1]' in R and '@READ:[F0,R0]' in R and '@READ:[F1,R0]' in R
    True
    >>> # Vérifie que chaque bloc est un FastQ bien formé et sans '@@'
    >>> '@@' in F or '@@' in R
    False
    >>> F
    '@READ:[F0,F1]\\nA\\n+\\n=\\n@READ:[F0,R0]\\nA\\n+\\n=\\n@READ:[F1,R0]\\nBCD\\n+\\n===\\n'
    >>> R
    '@READ:[F0,F1]\\nBCD\\n+\\n===\\n@READ:[F0,R0]\\nWXYZ\\n+\\n>>>>\\n@READ:[F1,R0]\\nWXYZ\\n+\\n>>>>\\n'

    Cas combinatoire symétrique (2 fragments forward, 2 fragments reverse).
    >>> rf = ("@READ", "ABCDE", [30]*5, "1S4M")
    >>> rr = ("@READ", "VWXYZ", [31]*5, "1S4M")
    >>> F, R = gen_read_pairs((rf, rr), seed_size=0, len_add=0)
    >>> # 2 fragments F + 2 fragments R => C(4,2) = 6 paires
    >>> F.count('@READ:['), R.count('@READ:[')
    (6, 6)
    """
    from itertools import combinations

    read_for_data, read_rev_data = data
    name_for, fragment_for_list = process_cigard(read_for_data, seed_size, len_add)
    name_rev, fragment_rev_list = process_cigard(read_rev_data, seed_size, len_add)

    # Nom de base commun (les deux mates ont le même ID logique)
    base = name_for.lstrip("@")

    total_fragments = len(fragment_for_list) + len(fragment_rev_list)

    # Cas simple: 1 fragment F + 1 fragment R
    if total_fragments <= 2:
        # On suppose ici que process_cigard renvoie exactement 1 frag par côté
        return [fragment_for_list[0], fragment_rev_list[0]]

    # Cas combinatoire: on annote chaque fragment avec son origine (F/R) et un index local
    def _to_entries(frag_list, origin):
        """
        Transforme une liste de FastQ en tuples (origin, idx, seq, qual).
        frag = '@smth\\nSEQ\\n+\\nQUAL\\n'
        """
        entries = []
        for idx, frag in enumerate(frag_list):
            lines = frag.strip().split("\n")
            if len(lines) != 4 or lines[2] != "+":
                raise ValueError("Fragment FastQ invalide dans process_cigard.")
            seq = lines[1]
            qual = lines[3]
            entries.append((origin, idx, seq, qual))
        return entries

    for_entries = _to_entries(fragment_for_list, "F")
    rev_entries = _to_entries(fragment_rev_list, "R")
    all_entries = for_entries + rev_entries

    fastq_forward = []
    fastq_reverse = []

    # Toutes les combinaisons uniques (i < j)
    for (o1, i1, s1, q1), (o2, i2, s2, q2) in combinations(all_entries, 2):
        tag_i = f"{o1}{i1}"
        tag_j = f"{o2}{i2}"
        header = read_name(base, tag_i, tag_j)

        fastq_forward.append(f"{header}\n{s1}\n+\n{q1}\n")
        fastq_reverse.append(f"{header}\n{s2}\n+\n{q2}\n")

    return ["".join(fastq_forward), "".join(fastq_reverse)]


def process_items(input_queue, output_queue, seed_size, len_add):
    """
    Process items from the input queue, split the reads based on CIGAR strings, and put the results into the output queue.

    Parameters:
        input_queue (Queue): Queue to get read pairs.
        output_queue (Queue): Queue to put processed read pairs.
        seed_size (int): The minimum size of a segment to be considered for extraction.

    Examples
    --------
    """

    from microsplit.auxiliary import check_data

    fastq_forward = ""
    fastq_reverse = ""
    try:
        while True:
            data = input_queue.get()

            if data is None:
                output_queue.put(None)
                break

            if check_data(data):
                if data[1][0] != data[0][0]:
                    print(data[1][0], " ", data[0][0], flush=True)
                    raise ValueError(
                        "Names of two BAM files aren't the same !! Please check your BAM files. "
                    )

                fastq_forward, fastq_reverse = gen_read_pairs(data, seed_size, len_add)
                if fastq_forward and fastq_reverse:
                    output_queue.put([fastq_forward, fastq_reverse])
                else:
                    raise ValueError("Error in process_items: FastQ strings are empty.")
    except ValueError as e:
        print(f"Error in process_items: {e}")
        sys.exit(1)


def communicate(write_processes, compute_processes):
    print(
        f"There is {write_processes} write threads per files and {compute_processes} fragmenting threads.",
        flush=True,
    )


def cut(args):
    """
    Main function to orchestrate the reading, processing, and writing of BAM files to FastQ.

    Parameters:
        args (argparse.Namespace): Namespace object containing command-line arguments.
    """

    bam_for_file = args.bam_for_file
    bam_rev_file = args.bam_rev_file
    output_forward = args.output_forward
    output_reverse = args.output_reverse
    num_threads = args.num_threads
    seed_size = args.seed_size
    len_add = args.lenght_added

    if not os.path.exists(bam_for_file) or not os.path.exists(bam_rev_file):
        logger.error("BAM file does not exist.")
        sys.exit(1)

    input_queue = Queue()
    output_queue = Queue()

    try:
        write_processes, compute_processes = partitionning(num_threads)
    except ValueError:
        print("ERROR: {e}", file=sys.stderr)
        return 2

    manager = ProcessManager()
    # Set up signal handlers
    signal.signal(signal.SIGINT, manager.handle_signal)
    signal.signal(signal.SIGTERM, manager.handle_signal)

    try:
        # Start worker processes
        manager.start_worker(
            target=read_bam_pair,
            args=(bam_for_file, bam_rev_file, input_queue, compute_processes),
        )
        # Process for processing items
        [
            manager.start_worker(
                target=process_items,
                args=(input_queue, output_queue, seed_size, len_add),
            )
            for _ in range(compute_processes)
        ]
        # Process for writing pairs
        manager.start_worker(
            target=write_fastq_pair,
            args=(
                output_queue,
                output_forward,
                output_reverse,
                compute_processes,
                write_processes,
            ),
        )
        # Monitor processes
        while manager.running():
            if not manager.check_processes():
                sys.exit(1)
            time.sleep(1)

    except Exception as e:
        print(f"Error in cut: {e}")
        manager.shutdown()
        sys.exit(1)
    finally:
        manager.shutdown()
