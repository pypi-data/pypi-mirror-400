#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import os
import threading
import time
import re
import subprocess
import logging

import psutil

logging.basicConfig(level=logging.DEBUG)


# ---------- Helper Class ----------
class Helper:
    # Function for capacity-weighted file grouping (greedy algorithm) so that
    # file sizes are divided among groups as evenly as possible.
    @staticmethod
    def split_files_by_capacity(file_info_list, groups_count):
        groups = [[] for _ in range(groups_count)]
        group_sizes = [0] * groups_count
        # Assign files sorted in descending order of size
        for path, size in sorted(file_info_list, key=lambda x: x[1], reverse=True):
            idx = group_sizes.index(min(group_sizes))
            groups[idx].append(path)
            group_sizes[idx] += size
        return groups

    @staticmethod
    def bytes2human(n):
        """
        Convert a number n (in bytes) into a human-readable string
        (e.g. 123456789 -> "117.7 MB")
        """
        symbols = ("B", "KB", "MB", "GB", "TB", "PB")
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1024**i
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return f"{value:.1f} {s}"
        return f"{n} B"

    @staticmethod
    def bits2human(n):
        """
        Convert n (in bps) into a human-readable format
        (e.g. 12345678 -> "12.3 Mbps")
        (Using base 10, conversion factor 1000)
        """
        symbols = ("bps", "Kbps", "Mbps", "Gbps", "Tbps", "Pbps")
        for s in reversed(symbols):
            factor = 1000 ** symbols.index(s)
            if n >= factor:
                value = float(n) / factor
                return f"{value:.1f} {s}"
        return f"{n} bps"


# ---------- RsyncTask Class ----------
class RsyncTask:
    """
    Represents a single rsync task.
    Each task sends one or more source files with their relative path (using the -R option).
    The transfer progress will be output by adding --info=progress2.
    """

    def __init__(
        self, sources, destination, base_dir, use_progress=False, use_compress=False
    ):
        """
        sources: List of absolute paths of files under base_dir.
        destination: Transfer destination (e.g. "user@host:/remote/path/").
        base_dir: The root directory of the source. The directory structure will be recreated starting from this root.
        use_progress: When True, add "--info=progress2" to display progress on standard output.
        use_compress: When True, add "-z" to compress file data during transfer.
        """
        self.sources = sources
        self.destination = destination
        self.base_dir = base_dir
        self.options = ["-av", "-R"]
        if use_progress:
            self.options.append("--info=progress2")
        if use_compress:
            self.options.append("-z")

    def run(self, progress_callback=None):
        """
        Run the rsync command.
        If progress_callback is provided, parse stdout and notify transferred bytes.
        Returns the rsync exit code.
        """
        # Convert absolute paths of each file to relative paths (prefixed with "./")
        rel_sources = []
        for source in self.sources:
            try:
                rel_path = os.path.relpath(source, self.base_dir)
            except Exception as e:
                logging.error(f"Error in relpath: {e}")
                rel_path = source
            rel_sources.append(os.path.join(".", rel_path))

        cmd = ["rsync"] + self.options + rel_sources + [self.destination]

        print(f"[INFO] Starting: {' '.join(cmd)} (cwd={self.base_dir})")
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=self.base_dir,
        )

        prog_re = re.compile(r"^\s*([\d,]+)")

        # Rsync prints progress updates with carriage return ("\r"), so process line by line
        while True:
            line = p.stdout.readline()
            line_str = line.rstrip("\r\n")
            if not line:
                break
            m = prog_re.match(line_str)
            if m:
                try:
                    transferred = int(m.group(1).replace(",", ""))
                    if progress_callback:
                        progress_callback(transferred)
                except ValueError:
                    pass

        p.wait()
        ret = p.returncode
        if ret == 0:
            print(f"[INFO] Completed: {' '.join(cmd)}")
        else:
            print(f"[ERROR] Exit code {ret}: {' '.join(cmd)}")
        return ret


# ---------- RsyncParallelExecutor Class (Threaded Version) ----------
class RsyncParallelExecutor:
    """
    Class to execute multiple RsyncTask objects in parallel.
    Each task runs in a separate thread, and progress updates are reported via the progress_callback.
    """

    def __init__(self, tasks, progress_callback=None):
        self.tasks = tasks
        self.progress_callback = progress_callback  # progress_update(task_index, bytes)
        self.results = [None] * len(tasks)

    def run_all(self):
        threads = []

        def worker(task, idx):
            ret = task.run(
                progress_callback=(
                    lambda val: self.progress_callback(idx, val)
                    if self.progress_callback
                    else None
                )
            )
            self.results[idx] = ret

        for idx, task in enumerate(self.tasks):
            t = threading.Thread(target=worker, args=(task, idx))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        return self.results


# ---------- Progress Monitor ----------
def progress_monitor(progress_data, total_bytes, stop_event, data_lock):
    """
    Display information such as transferred bytes, transfer rate, CPU usage, etc., every second.
    progress_data: A dictionary mapping task_index -> transferred bytes.
    total_bytes: Total bytes of all files to be transferred.
    data_lock: A lock to protect access to progress_data.
    """
    prev_time = time.time()
    prev_transferred = 0

    while not stop_event.is_set():
        now = time.time()
        dt = now - prev_time if now - prev_time > 0 else 1
        with data_lock:
            transferred = sum(progress_data.values())
        delta_bytes = transferred - prev_transferred
        speed_bps = (delta_bytes / dt) * 8
        speed_hr = Helper.bits2human(speed_bps)
        cpu_usage = psutil.cpu_percent(interval=0.0)
        pct = (transferred / total_bytes * 100) if total_bytes > 0 else 0
        transferred_hr = Helper.bytes2human(transferred)
        total_hr = Helper.bytes2human(total_bytes)
        sys.stdout.write(
            f"\r[Progress] {transferred_hr}/{total_hr} ({pct:.1f}%) Rate: {speed_hr}   CPU: {cpu_usage:.1f}%"
        )
        sys.stdout.flush()
        prev_time = now
        prev_transferred = transferred
        time.sleep(1)
    sys.stdout.write("\n")


# ---------- Argument Parsing ----------
def parse_args():
    parser = argparse.ArgumentParser(
        description="A tool to transfer all files under a specified directory to a remote location using rsync."
    )
    parser.add_argument(
        "local_dir",
        help="The root source directory (all files underneath will be transferred).",
    )
    parser.add_argument(
        "remote_path",
        help='Transfer destination (e.g. "rsync://host/path/").',
    )
    parser.add_argument(
        "--max-procs",
        type=int,
        default=None,
        help="Number of rsync processes to run in parallel (if not specified, the number of CPU cores is used).",
    )
    parser.add_argument(
        "--suspend-threshold",
        type=float,
        default=80.0,
        help="Pause rsync if CPU usage is above this threshold (default: 80.0).",
    )
    parser.add_argument(
        "--resume-threshold",
        type=float,
        default=60.0,
        help="Resume rsync if CPU usage is below this threshold (default: 60.0).",
    )
    parser.add_argument(
        "--compress",
        "-z",
        action="store_true",
        help="Compress file data during transfer.",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Display overall transfer progress (total bytes, transfer rate, CPU usage, etc.) every second.",
    )
    return parser.parse_args()


# ---------- Main Function ----------
def main():
    args = parse_args()

    # Convert local_dir to an absolute path if given as a relative path
    local_dir = os.path.abspath(args.local_dir)
    if not os.path.isdir(local_dir):
        print(f"[ERROR] The specified local directory does not exist: {local_dir}")
        sys.exit(1)

    if not args.remote_path.startswith("rsync://"):
        print(
            f"[ERROR] The specified remote path does not start with 'rsync://': {args.remote_path}"
        )
        sys.exit(1)

    # Create a list of tuples for all files under local_dir with (absolute_file_path, file_size)
    file_info = []
    total_bytes = 0
    for root, _, files in os.walk(local_dir):
        for f in files:
            abs_path = os.path.join(root, f)
            try:
                size = os.path.getsize(abs_path)
                total_bytes += size
            except OSError:
                size = 0
            file_info.append((abs_path, size))

    if not file_info:
        print("[ERROR] No files found to transfer.")
        sys.exit(1)

    # Determine the number of parallel tasks; if max_procs is not specified, use the number of CPU cores.
    max_procs = args.max_procs if args.max_procs is not None else os.cpu_count() - 1
    logging.info(f"Number of CPU cores: {max_procs}")
    num_groups = min(len(file_info), max_procs)
    groups = Helper.split_files_by_capacity(file_info, num_groups)

    # Create RsyncTask instances
    use_progress = args.progress
    use_compress = args.compress
    tasks = [
        RsyncTask(
            sources=group,
            destination=args.remote_path,
            base_dir=local_dir,
            use_progress=use_progress,
            use_compress=use_compress,
        )
        for group in groups
    ]

    # Shared progress information (transferred bytes for each task)
    progress_data = {}
    data_lock = threading.Lock()

    def update_progress(task_index, bytes_value):
        with data_lock:
            progress_data[task_index] = max(
                progress_data.get(task_index, 0), bytes_value
            )

    # Start the progress display thread
    prog_stop_event = threading.Event()
    if args.progress:
        prog_thread = threading.Thread(
            target=progress_monitor,
            args=(progress_data, total_bytes, prog_stop_event, data_lock),
        )
        prog_thread.start()

    # Record the start time of the transfer
    start_time = time.time()

    # Execute each task in parallel using RsyncParallelExecutor
    executor = RsyncParallelExecutor(
        tasks, progress_callback=update_progress if args.progress else None
    )
    results = executor.run_all()

    # Record the end time of all rsync tasks
    end_time = time.time()
    duration = end_time - start_time if end_time - start_time > 0 else 1.0

    if args.progress:
        prog_stop_event.set()
        prog_thread.join()

    if all(r == 0 for r in results):
        print("\n[INFO] All rsync tasks completed successfully.")
    else:
        print("\n[WARNING] Some rsync tasks encountered errors.")
        sys.exit(1)

    # Display the transfer summary
    file_count = len(file_info)
    transferred_bytes = total_bytes  # Total bytes intended for transfer
    avg_speed_bps = (transferred_bytes * 8) / duration  # Average transfer speed (bps)
    transferred_hr = Helper.bytes2human(transferred_bytes)
    speed_hr = Helper.bits2human(avg_speed_bps)
    print(
        f"\n[Summary] Transferred file count: {file_count} files, "
        f"Data transferred: {transferred_hr}, "
        f"Average transfer speed: {speed_hr} (Total time: {duration:.1f} seconds)"
    )


if __name__ == "__main__":
    main()
