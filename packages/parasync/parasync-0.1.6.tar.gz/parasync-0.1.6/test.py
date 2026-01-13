#!/usr/bin/env python3
# test_rsync_tool.py

import os
import sys
import unittest
import threading
import time
from io import StringIO
from unittest import mock

# Add source directory to sys.path if your module is stored in src folder for example.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from parasync.main import Helper, RsyncTask, RsyncParallelExecutor, progress_monitor


class TestHelperFunctions(unittest.TestCase):
    def test_split_files_by_capacity(self):
        # File information list: (path, size)
        file_info_list = [
            ("/dummy/file1", 500),
            ("/dummy/file2", 300),
            ("/dummy/file3", 200),
            ("/dummy/file4", 100),
        ]
        groups_count = 2
        groups = Helper.split_files_by_capacity(file_info_list, groups_count)

        # Combine all file paths from each group and check that all expected paths are present.
        all_paths = [path for group in groups for path in group]
        expected_paths = [entry[0] for entry in file_info_list]
        self.assertCountEqual(all_paths, expected_paths)

        # Calculate total size for each group and verify that the split is reasonably balanced.
        group_sizes = []
        for group in groups:
            size = sum(
                next(size for p, size in file_info_list if p == path) for path in group
            )
            group_sizes.append(size)
        diff = abs(group_sizes[0] - group_sizes[1])
        # The difference between groups should be small (here we accept a difference of 200 bytes or less)
        self.assertLessEqual(diff, 200)

    def test_bytes2human(self):
        # 123456789 bytes should roughly convert to a value containing "MB"
        human = Helper.bytes2human(123456789)
        self.assertIn("MB", human)

    def test_bits2human(self):
        # 12345678 bps should roughly convert to a value containing "Mbps"
        human = Helper.bits2human(12345678)
        self.assertIn("Mbps", human)


class DummyPopen:
    """
    A dummy Popen class to simulate the execution of an rsync command.
    It outputs progress lines to stdout and then terminates.
    """

    def __init__(self, stdout_data, returncode=0):
        self.stdout_data = stdout_data.splitlines(keepends=True)
        self.returncode = returncode
        self.stdout_iter = iter(self.stdout_data)
        self.stdout = self  # so that readline() can be called
        self.stderr = StringIO()

    def readline(self):
        try:
            return next(self.stdout_iter)
        except StopIteration:
            return ""  # EOF

    def wait(self):
        return self.returncode


class TestRsyncTask(unittest.TestCase):
    @mock.patch("subprocess.Popen")
    def test_run_success_with_progress(self, mock_popen):
        # Simulate stdout output from rsync with progress information.
        simulated_output = "  1,234,567   10%   1.23MB/s    0:00:12\n"
        dummy_proc = DummyPopen(simulated_output, returncode=0)
        mock_popen.return_value = dummy_proc

        # Dummy source paths (no actual files are needed for this test).
        sources = ["/dummy/path/subdir"]
        destination = "/dummy/destination"
        base_dir = "/dummy/path"

        progress_values = []

        def dummy_progress(value):
            progress_values.append(value)

        task = RsyncTask(sources, destination, base_dir, use_progress=True)
        ret = task.run(progress_callback=dummy_progress)

        # Verify that the progress callback was called with the parsed number.
        self.assertIn(1234567, progress_values)
        # Verify that the return code is as expected.
        self.assertEqual(ret, 0)

    @mock.patch("subprocess.Popen")
    def test_run_failure(self, mock_popen):
        simulated_output = "  0   0%   0.00MB/s    0:00:00\n"
        dummy_proc = DummyPopen(simulated_output, returncode=1)
        mock_popen.return_value = dummy_proc

        sources = ["/dummy/path/subdir"]
        destination = "/dummy/destination"
        base_dir = "/dummy/path"
        task = RsyncTask(sources, destination, base_dir, use_progress=False)
        ret = task.run()

        self.assertEqual(ret, 1)


class DummyTask:
    """A dummy task for testing RsyncParallelExecutor.
    It simply returns a predefined result.
    """

    def __init__(self, result, delay=0):
        self.result = result
        self.delay = delay

    def run(self, progress_callback=None):
        if self.delay:
            time.sleep(self.delay)
        if progress_callback:
            # Simulate a progress update.
            progress_callback(100)
        return self.result


class TestRsyncParallelExecutor(unittest.TestCase):
    def test_run_all(self):
        # Create several dummy tasks with predefined return codes.
        tasks = [DummyTask(0), DummyTask(0), DummyTask(1)]
        progress_updates = {}
        lock = threading.Lock()

        # Define a progress callback that stores the update per task index.
        def update_progress(task_index, value):
            with lock:
                progress_updates[task_index] = value

        executor = RsyncParallelExecutor(tasks, progress_callback=update_progress)
        results = executor.run_all()

        self.assertEqual(results, [0, 0, 1])
        # Check that each task has issued at least one progress update.
        self.assertEqual(progress_updates, {0: 100, 1: 100, 2: 100})


class TestProgressMonitor(unittest.TestCase):
    def test_progress_monitor(self):
        # Test progress_monitor in a short run.
        progress_data = {0: 500, 1: 500}
        total_bytes = 1000
        data_lock = threading.Lock()
        stop_event = threading.Event()

        output = StringIO()
        original_stdout = sys.stdout
        try:
            sys.stdout = output
            monitor_thread = threading.Thread(
                target=progress_monitor,
                args=(progress_data, total_bytes, stop_event, data_lock),
            )
            monitor_thread.start()
            time.sleep(2)
            stop_event.set()
            monitor_thread.join()
        finally:
            sys.stdout = original_stdout

        output_str = output.getvalue()
        self.assertIn("[Progress]", output_str)
        self.assertIn("100.0%", output_str)


if __name__ == "__main__":
    unittest.main()
