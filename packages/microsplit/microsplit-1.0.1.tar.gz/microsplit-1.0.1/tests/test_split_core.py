import microsplit.split as S


def test_partitionning_basic():
    assert S.partitionning(6) == (1, 4)
    assert S.partitionning(8) == (2, 4)


def test_phred_to_ascii_roundtrip():
    q = [0, 1, 2, 30]
    s = S.phred_to_ascii(q)
    assert s == '!"?#' or len(s) == len(q)


def test_build_cigar_tuple():
    ops, lens = S.build_cigar_tuple("5S10M2D3S")
    assert ops == ["S", "M", "D", "S"]
    assert lens == [5, 10, 2, 3]


def test_process_cigard_no_softclip():
    n, frags = S.process_cigard(("@r", "AC", [30, 30], "2M"), 0, 0)
    assert n == "@r"
    assert frags == ["@r\nAC\n+\n??\n"]


def test_process_cigard_one_softclip():
    n, frags = S.process_cigard(("@r", "ACGT", [30, 31, 32, 33], "2S2M"), 0, 0)
    assert len(frags) == 2


def test_gen_read_pairs_simple():
    rf = ("@READ", "AC", [30, 30], "2M")
    rr = ("@READ", "TG", [30, 30], "2M")
    F, R = S.gen_read_pairs((rf, rr), 0, 0)
    assert "@READ" in F and "AC" in F
    assert "@READ" in R and "TG" in R


def test_gen_read_pairs_combinatorial():
    rf = ("@READ", "ABCD", [30, 30, 30, 30], "1S3M")
    rr = ("@READ", "WXYZ", [11, 11, 11, 11], "2M")
    F, R = S.gen_read_pairs((rf, rr), 0, 0)
    # 3 paires -> 3 headers
    assert F.count("@READ:[") == 3
    assert R.count("@READ:[") == 3
    assert "@@" not in F and "@@" not in R
