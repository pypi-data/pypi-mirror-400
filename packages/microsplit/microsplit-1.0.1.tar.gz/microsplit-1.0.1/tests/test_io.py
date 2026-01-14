import sys
import types
import queue
import io

from microsplit.bam import read_bam_pair, read_to_tuple
import microsplit.fastq as fastq


def test_read_bam_pair_nominal(monkeypatch):
    """Test nominal de read_bam_pair avec pysam mocké et sentinelles."""

    # Faux read pysam-like
    class DummyRead:
        def __init__(self, name, seq, qual, cig):
            self.query_name = name
            self.query_sequence = seq
            self.query_qualities = qual
            self.cigarstring = cig

    # Stockage des "fichiers"
    data = {
        "F.bam": [DummyRead("r1", "AC", [30, 30], "2M")],
        "R.bam": [DummyRead("r1", "TG", [31, 31], "2M")],
    }

    class DummyAF:
        def __init__(self, path, mode):
            self.path = path

        def __enter__(self):
            self._it = iter(data[self.path])
            return self

        def __iter__(self):
            return self._it

        def __exit__(self, exc_type, exc, tb):
            return False

    dummy_pysam = types.SimpleNamespace(AlignmentFile=DummyAF)
    monkeypatch.setitem(sys.modules, "pysam", dummy_pysam)

    q = queue.Queue()
    num_proc = 2

    read_bam_pair("F.bam", "R.bam", q, num_proc)

    items = []
    none_count = 0
    while none_count < num_proc:
        x = q.get()
        items.append(x)
        if x is None:
            none_count += 1

    # Premier élément: la paire sérialisée
    pair = items[0]
    assert pair[0] == ["r1", "AC", [30, 30], "2M"]
    assert pair[1] == ["r1", "TG", [31, 31], "2M"]
    # Puis exactement num_proc sentinelles
    assert items.count(None) == num_proc


def test_read_bam_pair_error_injects_sentinels(monkeypatch):
    """En cas d'erreur pysam, read_bam_pair doit sys.exit(1) ET pousser les sentinelles."""

    class DummyAF:
        def __init__(self, path, mode):
            raise RuntimeError("boom")

    dummy_pysam = types.SimpleNamespace(AlignmentFile=DummyAF)
    monkeypatch.setitem(sys.modules, "pysam", dummy_pysam)

    q = queue.Queue()
    num_proc = 3

    try:
        read_bam_pair("F.bam", "R.bam", q, num_proc)
    except SystemExit as e:
        assert e.code == 1
    else:
        # Si pas de SystemExit, c'est un échec
        assert False, "SystemExit(1) attendu"

    # On doit quand même avoir les sentinelles
    items = [q.get() for _ in range(num_proc)]
    assert all(x is None for x in items)


def test_write_fastq_pair_nominal(monkeypatch, tmp_path):
    """Test nominal de write_fastq_pair avec open_output mocké et buffers mémoire."""

    # Dummy proc pour capturer ce qui est écrit
    class DummyProc:
        def __init__(self):
            self.stdin = io.BytesIO()
            self.waited = False
            self.terminated = False

        def wait(self):
            self.waited = True

        def terminate(self):
            self.terminated = True

    procs = {}

    def fake_open_output(of, or_, wp):
        pf = DummyProc()
        pr = DummyProc()
        procs["f"] = pf
        procs["r"] = pr
        return pf, pr

    monkeypatch.setattr(fastq, "open_output", fake_open_output)

    q = queue.Queue()
    # Une paire de reads déjà formatés en FastQ (F/R) puis une sentinelle
    q.put((["@F\nAC\n+\nII\n"], ["@R\nTG\n+\nII\n"]))
    q.put(None)

    fastq.write_fastq_pair(
        q,
        str(tmp_path / "out_F.fq.gz"),
        str(tmp_path / "out_R.fq.gz"),
        num_process=1,
        write_processes=4,
    )

    pf = procs["f"]
    pr = procs["r"]

    # Vérifie que la séquence a été écrite dans les bons buffers
    assert pf.stdin.getvalue() == b"@F\nAC\n+\nII\n"
    assert pr.stdin.getvalue() == b"@R\nTG\n+\nII\n"
    # Vérifie que ensure_ending a bien fait son travail
    assert pf.waited and pf.terminated
    assert pr.waited and pr.terminated


def test_write_fastq_pair_nominal(monkeypatch, tmp_path):
    """Test nominal de write_fastq_pair avec open_output et ensure_ending mockés."""

    import io
    import queue
    import microsplit.fastq as fastq

    # Dummy proc pour capturer ce qui est écrit
    class DummyProc:
        def __init__(self):
            self.stdin = io.BytesIO()
            self.waited = False
            self.terminated = False

        def wait(self):
            self.waited = True

        def terminate(self):
            self.terminated = True

    procs = {}

    def fake_open_output(of, or_, wp):
        pf = DummyProc()
        pr = DummyProc()
        procs["f"] = pf
        procs["r"] = pr
        return pf, pr

    captured = {}

    def fake_ensure_ending(of, or_):
        # On lit les buffers AVANT fermeture réelle
        captured["f"] = of.stdin.getvalue()
        captured["r"] = or_.stdin.getvalue()
        # On simule le comportement attendu sans casser BytesIO
        of.wait()
        or_.wait()
        of.terminate()
        or_.terminate()

    monkeypatch.setattr(fastq, "open_output", fake_open_output)
    monkeypatch.setattr(fastq, "ensure_ending", fake_ensure_ending)

    q = queue.Queue()
    # Une paire de reads déjà formatés en FastQ (F/R) puis une sentinelle
    q.put((["@F\nAC\n+\nII\n"], ["@R\nTG\n+\nII\n"]))
    q.put(None)

    fastq.write_fastq_pair(
        q,
        str(tmp_path / "out_F.fq.gz"),
        str(tmp_path / "out_R.fq.gz"),
        num_process=1,
        write_processes=4,
    )

    # Vérifie que la séquence a été écrite dans les bons buffers
    assert captured["f"] == b"@F\nAC\n+\nII\n"
    assert captured["r"] == b"@R\nTG\n+\nII\n"

    # Vérifie que le protocole de fin a été respecté côté dummy
    pf = procs["f"]
    pr = procs["r"]
    assert pf.waited and pf.terminated
    assert pr.waited and pr.terminated
