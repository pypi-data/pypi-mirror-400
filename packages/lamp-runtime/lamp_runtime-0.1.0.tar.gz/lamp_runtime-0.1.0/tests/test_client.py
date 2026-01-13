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

import argparse
import asyncio
import sys
import time
from contextlib import contextmanager
from lamp_runtime import SandboxClient

from agent_sandbox import Sandbox as aioClient

POD_NAME_ANNOTATION = "agents.x-k8s.io/pod-name"


@contextmanager
def timer(name: str):
    """Context manager to measure and print execution time"""
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"✓ {name} (took {elapsed:.2f}s)")


async def main(template_name: str, gateway_name: str | None, api_url: str | None, namespace: str, server_port: int):
    """
    Tests the Sandbox client by creating a sandbox, running a command,
    and then cleaning up.

    Args:
        template_name: The name of the sandbox template to use
        gateway_name: The name of the Gateway resource (for production mode)
        api_url: Direct URL to router (for custom routing)
        namespace: Kubernetes namespace for the sandbox
        server_port: Port the sandbox container listens on
    """

    print("=" * 80)
    print("SANDBOX CLIENT TEST")
    print("=" * 80)
    print(f"Configuration:")
    print(f"  Namespace:      {namespace}")
    print(f"  Server Port:    {server_port}")
    print(f"  Template Name:  {template_name}")

    if gateway_name:
        print(f"  Mode:           Gateway Discovery ({gateway_name})")
    elif api_url:
        print(f"  Mode:           Direct API URL ({api_url})")
    else:
        print(f"  Mode:           Local Port-Forward (Dev Mode)")
    print("=" * 80)

    test_passed = True
    error_message = None

    try:
        print("\n[Step 1/5] Creating Sandbox...")
        # Initialize Client with Keyword Arguments for safety
        start_time = time.time()
        with SandboxClient(
            template_name=template_name,
            namespace=namespace,
            gateway_name=gateway_name,
            api_url=api_url,
            server_port=server_port
        ) as sandbox:
            elapsed_time = time.time() - start_time
            print(f"✓ Sandbox created successfully (took {elapsed_time:.2f}s)")

            print("\n[Step 2/5] Sandbox Information:")
            print(f"  Sandbox Name:   {sandbox.sandbox_name}")
            print(f"  Pod Name:       {sandbox.pod_name}")
            print(f"  Namespace:      {sandbox.namespace}")
            print(f"  Template Name:  {sandbox.template_name}")
            print(f"  Gateway Name:   {sandbox.gateway_name if hasattr(sandbox, 'gateway_name') else 'N/A'}")
            print(f"  Base URL:       {sandbox.base_url if hasattr(sandbox, 'base_url') else 'N/A'}")
            print(f"  Server Port:    {sandbox.server_port if hasattr(sandbox, 'server_port') else 'N/A'}")
            if sandbox.annotations:
                print(f"  Annotations:    {sandbox.annotations}")

            print("\n[Step 3/5] Testing Pod Name Discovery...")
            assert sandbox.annotations is not None, "Sandbox annotations were not stored on the client"

            pod_name_annotation = sandbox.annotations.get(POD_NAME_ANNOTATION)

            if pod_name_annotation:
                print(f"  ✓ Pod name from annotation: {pod_name_annotation}")
                assert sandbox.pod_name == pod_name_annotation, \
                    f"Expected pod_name to be '{pod_name_annotation}', but got '{sandbox.pod_name}'"
            else:
                print(f"  ⚠ Pod name annotation not found, using sandbox name: {sandbox.sandbox_name}")
                assert sandbox.pod_name == sandbox.sandbox_name, \
                    f"Expected pod_name to be '{sandbox.sandbox_name}', but got '{sandbox.pod_name}'"

            # Initialize the AIO Sandbox client using pod name, namespace and server port
            # This constructs the Kubernetes internal DNS name
            print("\n[Step 4/5] Connecting to Sandbox Runtime...")
            base_url = f"http://{sandbox.sandbox_name}.{sandbox.namespace}.svc.cluster.local:{sandbox.server_port}"
            print(f"  Base URL: {base_url}")

            try:
                client = aioClient(base_url=base_url)
                print("  ✓ Connected to sandbox runtime")
            except Exception as e:
                print(f"  ✗ Failed to connect: {e}")
                raise

            # Test 1: Get the home directory
            print("\n[Step 5/5] Running Sandbox Tests...")
            print("  Test 1: Getting home directory...")
            try:
                with timer("    Home directory retrieved"):
                    home_dir = client.sandbox.get_context().home_dir
                print(f"    Home directory: {home_dir}")
            except Exception as e:
                print(f"    ✗ Failed to get home directory: {e}")
                raise

            # Test 2: Run a shell command
            print("  Test 2: Running shell command (ls -la)...")
            try:
                with timer("    Command executed successfully"):
                    result = client.shell.exec_command(command="ls -la", timeout=10)
                print(f"    Output (first 500 chars):\n{result.data.output[:500]}")
            except Exception as e:
                print(f"    ✗ Failed to execute command: {e}")
                raise

            # Test 3: Read a file
            print(f"  Test 3: Reading file ({home_dir}/.bashrc)...")
            try:
                with timer("    File read successfully"):
                    content = client.file.read_file(file=f"{home_dir}/.bashrc")
                print(f"    File size: {len(content.data.content)} bytes")
                print(f"    Content (first 200 chars):\n{content.data.content[:200]}")
            except Exception as e:
                print(f"    ✗ Failed to read file: {e}")
                raise

            # Test 4: Take a screenshot
            print("  Test 4: Taking browser screenshot...")
            screenshot_path = "sandbox_screenshot.png"
            try:
                with timer("    Screenshot saved"):
                    with open(screenshot_path, "wb") as f:
                        for chunk in client.browser.screenshot():
                            f.write(chunk)
                print(f"    Saved to: {screenshot_path}")
            except Exception as e:
                print(f"    ⚠ Screenshot failed (this is optional): {e}")

            print("\n" + "=" * 80)
            print("ALL TESTS PASSED!")
            print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("TEST INTERRUPTED BY USER")
        print("=" * 80)
        test_passed = False
        error_message = "Test interrupted by user"
        sys.exit(1)
    except Exception as e:
        print("\n\n" + "=" * 80)
        print("TEST FAILED")
        print("=" * 80)
        print(f"Error: {type(e).__name__}: {e}")
        test_passed = False
        error_message = str(e)
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        # The __exit__ method of the Sandbox class will handle cleanup.
    finally:
        print("\n" + "=" * 80)
        if test_passed:
            print("TEST SUMMARY: ✓ PASSED")
        else:
            print("TEST SUMMARY: ✗ FAILED")
            if error_message:
                print(f"Reason: {error_message}")
        print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the Sandbox client.")

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

    args = parser.parse_args()

    try:
        asyncio.run(main(
            template_name=args.template_name,
            gateway_name=args.gateway_name,
            api_url=args.api_url,
            namespace=args.namespace,
            server_port=args.server_port
        ))
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)
