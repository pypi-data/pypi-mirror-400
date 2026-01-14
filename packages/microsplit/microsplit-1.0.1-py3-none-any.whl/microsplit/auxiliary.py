def signal_handler(sig, frame, out_f, out_r):
    """
    Handle termination signals to gracefully terminate processes.

    Parameters:
        sig (int): Signal number.
        frame (frame object): Current stack frame.
        outF (subprocess.Popen): Process for the forward output.
        outR (subprocess.Popen): Process for the reverse output.
    """
    import sys

    out_f.terminate()
    out_r.terminate()
    sys.exit()


def partitionning(num_processes):
    """
    Partition the number of threads for writing and fragmenting.

    Examples
    --------
    >>> partitionning(4)   # 4 // 4 = 1 => compute = 4 - 2 = 2
    Traceback (most recent call last):
    ...
    ValueError: Invalid configuration: num_processes=4 (< 6). Run with --threads >= 6 (recommended: >= 8).
    >>> partitionning(6)   # 5 // 4 = 1 => compute = 3
    (1, 4)
    >>> partitionning(8)   # 8 // 4 = 2 => compute = 8 - 4 = 4
    (2, 4)
    """
    if num_processes < 6:
        raise ValueError(
            f"Invalid configuration: num_processes={num_processes} (< 6). "
            "Run with --threads >= 6 (recommended: >= 8)."
        )

    write_processes = num_processes // 4
    compute_processes = num_processes - (write_processes * 2)

    if write_processes < 1:
        raise RuntimeError(
            f"Internal error: write_processes={write_processes}. "
            "This should not happen for num_processes >= 6."
        )
    if compute_processes < 1:
        raise RuntimeError(
            f"Internal error: compute_processes={compute_processes}. "
            "This should not happen for num_processes >= 6."
        )

    return write_processes, compute_processes


def check_data(data):
    for element in data[0]:
        if element is None:
            return False
    for element in data[1]:
        if element is None:
            return False
    return True
