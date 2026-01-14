def open_output(output_forward, output_reverse, write_processes):
    """
    Open output files for writing with pigz compression.

    Parameters:
        write_processes (int): Number of threads for writing.
        output_forward (str): Path to the forward output file.
        output_reverse (str): Path to the reverse output file.

    Returns:
        out_f (subprocess.Popen): Process for the forward output.
        out_r (subprocess.Popen): Process for the reverse output.
    """
    import signal
    import subprocess

    from microsplit.auxiliary import signal_handler

    write_processes = int(write_processes / 2)
    # Open output files for writing
    out_f = subprocess.Popen(
        args=["pigz", "-c", "-p", str(write_processes)],
        stdin=subprocess.PIPE,
        stdout=open(file=output_forward, mode="wt"),
    )
    out_r = subprocess.Popen(
        ["pigz", "-c", "-p", str(write_processes)],
        stdin=subprocess.PIPE,
        stdout=open(file=output_reverse, mode="wt"),
    )

    # Register signal handlers
    signal.signal(
        signal.SIGINT,
        lambda sig, frame: signal_handler(
            sig=sig, frame=frame, out_f=out_f, out_r=out_r
        ),
    )
    signal.signal(
        signal.SIGTSTP,
        lambda sig, frame: signal_handler(
            sig=sig, frame=frame, out_f=out_f, out_r=out_r
        ),
    )
    return out_f, out_r


def write_fastq_pair(
    output_queue, output_forward, output_reverse, num_process, write_processes
):
    """
    Write FastQ file pairs to the output using data from the output queue.

    Parameters:
        output_queue (Queue): Queue to get processed read pairs.
        out_f (subprocess.Popen): Process for the forward output.
        out_r (subprocess.Popen): Process for the reverse output.
        num_process (int): Number of fragmenting threads.
    """
    import sys

    out_f, out_r = open_output(output_forward, output_reverse, write_processes)
    while num_process > 0:
        try:
            data = output_queue.get()
            if data is None:
                num_process -= 1
            else:
                if out_f.stdin is not None and out_r.stdin is not None:
                    out_f.stdin.write("".join(data[0]).encode("utf-8"))
                    out_r.stdin.write("".join(data[1]).encode("utf-8"))
                else:
                    raise ValueError("Error: pigz process is not running.")
        except Exception as e:
            print(f"Error in write_pairs: {e}")
            manage_pigz_errors(out_f, out_r, output_forward, output_reverse)
            sys.exit(1)
    ensure_ending(out_f, out_r)


def ensure_ending(out_f, out_r):
    if out_f.stdin is not None:
        out_f.stdin.close()
    if out_r.stdin is not None:
        out_r.stdin.close()
    out_f.wait()
    out_r.wait()
    out_f.terminate()
    out_r.terminate()


def manage_pigz_errors(out_f, out_r, output_forward, output_reverse):
    """
    Manage pigz process termination and check for errors.

    Examples
    --------
    >>> class _P:
    ...     def __init__(self, rc): self.stdin=None; self.returncode=rc; self.waited=False; self.terminated=False
    ...     def wait(self): self.waited=True
    ...     def terminate(self): self.terminated=True
    ...
    >>> pf, pr = _P(0), _P(0)
    >>> manage_pigz_errors(pf, pr, 'F.fq.gz', 'R.fq.gz')
    >>> pf.waited and pr.waited and pf.terminated and pr.terminated
    True
    >>> pf, pr = _P(1), _P(2)
    >>> manage_pigz_errors(pf, pr, 'F.fq.gz', 'R.fq.gz')  # doctest: +ELLIPSIS
    Error in pigz command for file F.fq.gz
    Error in pigz command for file R.fq.gz
    """
    if out_f.stdin is not None:
        out_f.stdin.close()
    if out_r.stdin is not None:
        out_r.stdin.close()
    out_f.wait()
    out_r.wait()

    if out_f.returncode != 0:
        print(f"Error in pigz command for file {output_forward}")
    if out_r.returncode != 0:
        print(f"Error in pigz command for file {output_reverse}")
    out_f.terminate()
    out_r.terminate()
