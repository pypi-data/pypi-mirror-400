#!/usr/bin/env python3
# Copyright 2025 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Performance benchmark script for Sandbox client.
Runs multiple test iterations and collects timing statistics.
"""

import argparse
import asyncio
import sys
import time
import statistics
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
from pathlib import Path
import re

from test_client import main as test_main


@dataclass
class BenchmarkResult:
    """Stores timing results for a single test run"""
    iteration: int
    sandbox_creation_time: float = 0.0
    test1_time: float = 0.0
    test2_time: float = 0.0
    test3_time: float = 0.0
    test4_time: float = 0.0
    total_time: float = 0.0
    success: bool = True
    error_message: str = ""


@dataclass
class BenchmarkStats:
    """Aggregated statistics across all runs"""
    iterations: int
    successful_runs: int
    failed_runs: int

    # Sandbox creation stats
    sandbox_creation_times: List[float] = field(default_factory=list)
    sandbox_creation_mean: float = 0.0
    sandbox_creation_median: float = 0.0
    sandbox_creation_min: float = 0.0
    sandbox_creation_max: float = 0.0
    sandbox_creation_stddev: float = 0.0

    # Test 1 stats
    test1_times: List[float] = field(default_factory=list)
    test1_mean: float = 0.0
    test1_median: float = 0.0

    # Test 2 stats
    test2_times: List[float] = field(default_factory=list)
    test2_mean: float = 0.0
    test2_median: float = 0.0

    # Test 3 stats
    test3_times: List[float] = field(default_factory=list)
    test3_mean: float = 0.0
    test3_median: float = 0.0

    # Test 4 stats
    test4_times: List[float] = field(default_factory=list)
    test4_mean: float = 0.0
    test4_median: float = 0.0

    # Total time stats
    total_times: List[float] = field(default_factory=list)
    total_mean: float = 0.0
    total_median: float = 0.0
    total_min: float = 0.0
    total_max: float = 0.0

    def calculate(self):
        """Calculate statistics from collected timing data"""
        if self.sandbox_creation_times:
            self.sandbox_creation_mean = statistics.mean(self.sandbox_creation_times)
            self.sandbox_creation_median = statistics.median(self.sandbox_creation_times)
            self.sandbox_creation_min = min(self.sandbox_creation_times)
            self.sandbox_creation_max = max(self.sandbox_creation_times)
            if len(self.sandbox_creation_times) > 1:
                self.sandbox_creation_stddev = statistics.stdev(self.sandbox_creation_times)

        if self.test1_times:
            self.test1_mean = statistics.mean(self.test1_times)
            self.test1_median = statistics.median(self.test1_times)

        if self.test2_times:
            self.test2_mean = statistics.mean(self.test2_times)
            self.test2_median = statistics.median(self.test2_times)

        if self.test3_times:
            self.test3_mean = statistics.mean(self.test3_times)
            self.test3_median = statistics.median(self.test3_times)

        if self.test4_times:
            self.test4_mean = statistics.mean(self.test4_times)
            self.test4_median = statistics.median(self.test4_times)

        if self.total_times:
            self.total_mean = statistics.mean(self.total_times)
            self.total_median = statistics.median(self.total_times)
            self.total_min = min(self.total_times)
            self.total_max = max(self.total_times)


class OutputCapture:
    """Captures stdout to extract timing information"""
    def __init__(self, silent: bool = False):
        self.lines = []
        self.original_stdout = None
        self.silent = silent

    def write(self, text):
        """Capture text while also writing to original stdout"""
        self.lines.append(text)
        if self.original_stdout and not self.silent:
            self.original_stdout.write(text)

    def flush(self):
        """Flush the output"""
        if self.original_stdout and not self.silent:
            self.original_stdout.flush()

    def __enter__(self):
        self.original_stdout = sys.stdout
        sys.stdout = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.original_stdout

    def get_output(self):
        """Get captured output as a single string"""
        return ''.join(self.lines)


def parse_timing_from_output(output: str) -> BenchmarkResult:
    """Extract timing information from test output"""
    result = BenchmarkResult(iteration=0)

    # Pattern to match timing output: "✓ Description (took X.XXs)"
    time_pattern = r'✓\s+(.+?)\s+\(took\s+([\d.]+)s\)'

    for match in re.finditer(time_pattern, output):
        description = match.group(1)
        timing = float(match.group(2))

        if 'Sandbox created successfully' in description:
            result.sandbox_creation_time = timing
        elif 'Home directory retrieved' in description:
            result.test1_time = timing
        elif 'Command executed successfully' in description:
            result.test2_time = timing
        elif 'File read successfully' in description:
            result.test3_time = timing
        elif 'Screenshot saved' in description:
            result.test4_time = timing

    # Check if test passed
    if 'TEST SUMMARY: ✓ PASSED' in output:
        result.success = True
    elif 'TEST SUMMARY: ✗ FAILED' in output:
        result.success = False
        # Try to extract error message
        error_match = re.search(r'Reason: (.+)', output)
        if error_match:
            result.error_message = error_match.group(1)

    return result


async def run_single_test(iteration: int, template_name: str, gateway_name: str | None,
                         api_url: str | None, namespace: str, server_port: int,
                         verbose: bool = False, log_file = None) -> BenchmarkResult:
    """Run a single test iteration and capture timing"""
    if verbose:
        print(f"\n{'=' * 80}")
        print(f"BENCHMARK ITERATION {iteration}")
        print(f"{'=' * 80}")
    else:
        print(f"[{iteration}] Running test...", end=" ", flush=True)

    start_time = time.time()
    captured_output = ""

    try:
        with OutputCapture(silent=not verbose) as capture:
            await test_main(
                template_name=template_name,
                gateway_name=gateway_name,
                api_url=api_url,
                namespace=namespace,
                server_port=server_port
            )

        captured_output = capture.get_output()
        result = parse_timing_from_output(captured_output)
        result.iteration = iteration
        result.total_time = time.time() - start_time

        # Always log to file if provided
        if log_file:
            log_file.write(f"\n{'=' * 80}\n")
            log_file.write(f"ITERATION {iteration} - {'PASS' if result.success else 'FAIL'} ({result.total_time:.2f}s)\n")
            log_file.write(f"{'=' * 80}\n")
            log_file.write(captured_output)
            log_file.write("\n")
            log_file.flush()

        if not verbose:
            if result.success:
                print(f"✓ PASS ({result.total_time:.2f}s)")
            else:
                print(f"✗ FAIL ({result.total_time:.2f}s)")
                print(f"\nFailed iteration {iteration} - See log file for details")

    except Exception as e:
        result = BenchmarkResult(
            iteration=iteration,
            success=False,
            error_message=str(e),
            total_time=time.time() - start_time
        )

        # Log error to file
        if log_file:
            log_file.write(f"\n{'=' * 80}\n")
            log_file.write(f"ITERATION {iteration} - ERROR ({result.total_time:.2f}s)\n")
            log_file.write(f"{'=' * 80}\n")
            log_file.write(f"Error: {e}\n")
            if captured_output:
                log_file.write(f"\nCaptured output:\n")
                log_file.write(captured_output)
            log_file.write("\n")
            log_file.flush()

        if not verbose:
            print(f"✗ ERROR ({result.total_time:.2f}s)")
            print(f"\nError in iteration {iteration} - See log file for details")

    return result


async def run_benchmark(iterations: int, template_name: str, gateway_name: str | None,
                       api_url: str | None, namespace: str, server_port: int,
                       delay_between_runs: float = 0.0, verbose: bool = False,
                       log_dir: str | None = None) -> BenchmarkStats:
    """Run multiple test iterations and collect statistics"""

    # Setup log file
    log_file = None
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = log_path / f"benchmark_{timestamp}.log"
        log_file = open(log_filename, 'w', encoding='utf-8')
        print(f"Logging to: {log_filename}")

    try:
        header = f"""
{'=' * 80}
BENCHMARK RUN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}
Configuration:
  Iterations:     {iterations}
  Template:       {template_name}
  Namespace:      {namespace}
  Gateway:        {gateway_name or 'N/A'}
  API URL:        {api_url or 'N/A'}
  Server Port:    {server_port}
  Delay:          {delay_between_runs}s
{'=' * 80}
"""
        print(header)
        if log_file:
            log_file.write(header)
            log_file.flush()

        results: List[BenchmarkResult] = []

        for i in range(1, iterations + 1):
            result = await run_single_test(
                iteration=i,
                template_name=template_name,
                gateway_name=gateway_name,
                api_url=api_url,
                namespace=namespace,
                server_port=server_port,
                verbose=verbose,
                log_file=log_file
            )
            results.append(result)

            # Add delay between runs if specified
            if delay_between_runs > 0 and i < iterations:
                print(f"\nWaiting {delay_between_runs}s before next iteration...")
                await asyncio.sleep(delay_between_runs)

        # Aggregate statistics
        stats = BenchmarkStats(
            iterations=iterations,
            successful_runs=sum(1 for r in results if r.success),
            failed_runs=sum(1 for r in results if not r.success)
        )

        # Collect timing data from successful runs
        for result in results:
            if result.success:
                if result.sandbox_creation_time > 0:
                    stats.sandbox_creation_times.append(result.sandbox_creation_time)
                if result.test1_time > 0:
                    stats.test1_times.append(result.test1_time)
                if result.test2_time > 0:
                    stats.test2_times.append(result.test2_time)
                if result.test3_time > 0:
                    stats.test3_times.append(result.test3_time)
                if result.test4_time > 0:
                    stats.test4_times.append(result.test4_time)
                if result.total_time > 0:
                    stats.total_times.append(result.total_time)

        stats.calculate()

        return stats, log_file
    finally:
        # Don't close log_file here - let caller handle it after printing stats
        pass


def print_statistics(stats: BenchmarkStats, log_file=None):
    """Print formatted benchmark statistics"""
    output = []
    output.append(f"\n{'=' * 80}")
    output.append("BENCHMARK RESULTS")
    output.append(f"{'=' * 80}")
    output.append(f"Total Iterations:    {stats.iterations}")
    output.append(f"Successful Runs:     {stats.successful_runs}")
    output.append(f"Failed Runs:         {stats.failed_runs}")
    output.append(f"Success Rate:        {stats.successful_runs/stats.iterations*100:.1f}%")
    output.append(f"{'=' * 80}\n")

    if stats.sandbox_creation_times:
        output.append("Sandbox Creation Time:")
        output.append(f"  Mean:              {stats.sandbox_creation_mean:.2f}s")
        output.append(f"  Median:            {stats.sandbox_creation_median:.2f}s")
        output.append(f"  Min:               {stats.sandbox_creation_min:.2f}s")
        output.append(f"  Max:               {stats.sandbox_creation_max:.2f}s")
        if stats.sandbox_creation_stddev > 0:
            output.append(f"  Std Dev:           {stats.sandbox_creation_stddev:.2f}s")
        output.append("")

    if stats.test1_times:
        output.append("Test 1 - Get Home Directory:")
        output.append(f"  Mean:              {stats.test1_mean:.2f}s")
        output.append(f"  Median:            {stats.test1_median:.2f}s")
        output.append("")

    if stats.test2_times:
        output.append("Test 2 - Shell Command:")
        output.append(f"  Mean:              {stats.test2_mean:.2f}s")
        output.append(f"  Median:            {stats.test2_median:.2f}s")
        output.append("")

    if stats.test3_times:
        output.append("Test 3 - Read File:")
        output.append(f"  Mean:              {stats.test3_mean:.2f}s")
        output.append(f"  Median:            {stats.test3_median:.2f}s")
        output.append("")

    if stats.test4_times:
        output.append("Test 4 - Screenshot:")
        output.append(f"  Mean:              {stats.test4_mean:.2f}s")
        output.append(f"  Median:            {stats.test4_median:.2f}s")
        output.append("")

    if stats.total_times:
        output.append("Total Execution Time:")
        output.append(f"  Mean:              {stats.total_mean:.2f}s")
        output.append(f"  Median:            {stats.total_median:.2f}s")
        output.append(f"  Min:               {stats.total_min:.2f}s")
        output.append(f"  Max:               {stats.total_max:.2f}s")
        output.append("")

    output.append(f"{'=' * 80}")

    # Print to console
    for line in output:
        print(line)

    # Write to log file if provided
    if log_file:
        log_file.write('\n'.join(output) + '\n')
        log_file.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Performance benchmark for Sandbox client."
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Number of test iterations to run (default: 5)"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay in seconds between test runs (default: 0)"
    )

    parser.add_argument(
        "--template-name",
        default="python-sandbox-template",
        help="The name of the sandbox template to use"
    )

    parser.add_argument(
        "--gateway-name",
        default=None,
        help="The name of the Gateway resource"
    )

    parser.add_argument(
        "--api-url",
        default=None,
        help="Direct URL to router"
    )

    parser.add_argument(
        "--namespace",
        default="default",
        help="Namespace to create sandbox in"
    )

    parser.add_argument(
        "--server-port",
        type=int,
        default=8888,
        help="Port the sandbox container listens on"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output (show all test logs)"
    )

    parser.add_argument(
        "--log-dir",
        default="./benchmark_logs",
        help="Directory to store benchmark logs (default: ./benchmark_logs)"
    )

    args = parser.parse_args()

    log_file = None
    try:
        stats, log_file = asyncio.run(run_benchmark(
            iterations=args.iterations,
            template_name=args.template_name,
            gateway_name=args.gateway_name,
            api_url=args.api_url,
            namespace=args.namespace,
            server_port=args.server_port,
            delay_between_runs=args.delay,
            verbose=args.verbose,
            log_dir=args.log_dir
        ))

        print_statistics(stats, log_file)

        # Exit with error code if any tests failed
        sys.exit(0 if stats.failed_runs == 0 else 1)

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nBenchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Close log file
        if log_file:
            log_file.close()
