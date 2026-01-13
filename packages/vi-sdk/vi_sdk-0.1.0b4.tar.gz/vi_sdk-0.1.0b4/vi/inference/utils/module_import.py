#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   module_import.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK module importer module.
"""

import contextlib
import importlib
import io
import subprocess
import sys
import warnings
from pathlib import Path

from rich.progress import BarColumn, SpinnerColumn, TimeElapsedColumn
from vi.utils.graceful_exit import graceful_exit
from vi.utils.progress import ViProgress

# Cache of packages that have already been verified as available
_verified_packages: set[str] = set()


@contextlib.contextmanager
def suppress_output_and_warnings():
    """Context manager to suppress stdout, stderr, and warnings.

    Yields:
        None - control is yielded back to the caller.

    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            yield


def _find_requirements_file(dependency_group: str) -> Path | None:
    """Find the requirements file for a dependency group.

    Args:
        dependency_group: Name of the dependency group (e.g., "qwen", "llava").

    Returns:
        Path to requirements file if found, None otherwise.

    """
    # Get the vi package root directory
    vi_root = Path(__file__).parent.parent
    requirements_dir = vi_root / "requirements"

    # Look for {dependency_group}.txt
    requirements_file = requirements_dir / f"{dependency_group}.txt"

    if requirements_file.exists():
        return requirements_file

    return None


def check_imports(
    packages: str | list[str],
    dependency_group: str = "inference",
    auto_install: bool = True,
) -> None:
    """Check if packages are installed and optionally auto-install them.

    Dependencies are installed from requirements files located in
    vi/inference/requirements/{dependency_group}.txt. If the requirements
    file doesn't exist, a FileNotFoundError is raised with instructions
    on how to create it.

    This function caches which packages have been verified to avoid redundant
    checks when multiple modules share the same dependencies.

    Args:
        packages: Package name or list of package names to check.
        dependency_group: Dependency group name (e.g., "qwen", "llava").
            Must have a corresponding requirements file at
            vi/inference/requirements/{dependency_group}.txt
        auto_install: Whether to automatically install missing packages
            from the requirements file. If False, raises ImportError with
            manual installation instructions.

    Raises:
        FileNotFoundError: If requirements file doesn't exist for dependency_group.
        ImportError: If packages are not available and auto_install is False.
        RuntimeError: If auto-installation fails or packages still unavailable.

    Example:
        ```python
        # Check and auto-install Qwen dependencies
        check_imports(
            packages=["torch", "transformers", "qwen_vl_utils"],
            dependency_group="qwen",
            auto_install=True,
        )
        ```

    """
    if isinstance(packages, str):
        packages = [packages]

    # Filter out packages that have already been verified
    packages_to_check = [p for p in packages if p not in _verified_packages]

    # If all packages are already verified, skip entirely
    if not packages_to_check:
        return

    unavailable_packages = []
    with graceful_exit("Package import check cancelled by user") as handler:
        with ViProgress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.2f}%",
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
            num_packages = len(packages_to_check)
            main_task = progress.add_task(
                f"Processing {num_packages} package{'s' if num_packages > 1 else ''}...",
                total=num_packages,
            )

            for package in packages_to_check:
                # Check for keyboard interrupt
                if handler.exit_now:
                    break

                progress.update(main_task, description=f"Processing {package}...")
                task = progress.add_task(f"Checking {package}...", total=1)

                try:
                    with suppress_output_and_warnings():
                        importlib.import_module(package)

                    progress.update(
                        task, completed=1, description=f"✓ {package} available"
                    )
                    # Cache this package as verified
                    _verified_packages.add(package)
                except ImportError:
                    progress.update(
                        task, completed=1, description=f"✗ {package} not available"
                    )
                    unavailable_packages.append(package)
                progress.update(main_task, advance=1)

    # If all packages are available, we're done
    if not unavailable_packages:
        return

    # Handle unavailable packages
    if dependency_group == "inference":
        raise ImportError(
            "The base inference dependencies are not available. "
            "Please install them manually by running:"
            "\n\n  [bold cyan]$ pip install vi-sdk\\[inference][/bold cyan]\n"
        )

    # Check if requirements file exists for this dependency group
    requirements_file = _find_requirements_file(dependency_group)

    if not requirements_file:
        # No requirements file found - this is a configuration error
        raise FileNotFoundError(
            f"Requirements file not found for dependency group '{dependency_group}'.\n"
            f"Expected location: vi/inference/requirements/{dependency_group}.txt\n\n"
            "To fix this issue:\n"
            f"1. Create vi/inference/requirements/{dependency_group}.txt\n"
            "2. Add required packages to the file\n"
            "3. See vi/inference/requirements/README.md for examples\n\n"
            f"Missing packages: {', '.join(unavailable_packages)}"
        )

    if not auto_install:
        manual_install_cmd = f"pip install -r {requirements_file}"
        raise ImportError(
            f"The following packages are not available: {', '.join(unavailable_packages)}.\n"
            "Please install the required packages using your package manager or by running:"
            f"\n\n  [bold cyan]$ {manual_install_cmd}[/bold cyan]\n"
        )

    # Auto-install missing packages from requirements file
    with graceful_exit("Package installation cancelled by user") as handler:
        with ViProgress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.2f}%",
            TimeElapsedColumn(),
            transient=False,
        ) as progress:
            install_desc = f"Installing from {requirements_file.name}..."
            pip_install_cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(requirements_file),
            ]

            install_task = progress.add_task(install_desc, total=1)

            try:
                # Install dependencies
                subprocess.run(
                    pip_install_cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                # Update success message
                success_msg = (
                    f"✓ Successfully installed packages from {requirements_file.name}"
                )

                progress.update(
                    install_task,
                    completed=1,
                    description=success_msg,
                )

                # Verify installation by re-checking packages
                failed_packages = []
                for package in unavailable_packages:
                    try:
                        with suppress_output_and_warnings():
                            importlib.import_module(package)
                        # Cache this package as verified
                        _verified_packages.add(package)
                    except ImportError:
                        failed_packages.append(package)

                if failed_packages:
                    manual_cmd = f"pip install -r {requirements_file}"
                    raise RuntimeError(
                        f"Installation completed but the following packages are still unavailable: "
                        f"{', '.join(failed_packages)}.\n"
                        f"Please check your installation or try manually:\n"
                        f"  [bold cyan]$ {manual_cmd}[/bold cyan]\n"
                    )

            except subprocess.CalledProcessError as e:
                fail_msg = f"✗ Failed to install from {requirements_file.name}"
                manual_cmd = f"pip install -r {requirements_file}"

                progress.update(
                    install_task,
                    completed=1,
                    description=fail_msg,
                )
                raise RuntimeError(
                    f"Failed to install dependencies.\n"
                    f"Error: {e.stderr}\n"
                    f"Please try manually:\n"
                    f"  [bold cyan]$ {manual_cmd}[/bold cyan]\n"
                ) from e
            except Exception as e:
                if handler.exit_now:
                    raise KeyboardInterrupt from e
                raise
