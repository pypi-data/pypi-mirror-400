"""
Auto-detect Python environment (version, packages) for Docker generation.
Users don't need to configure anything - we snapshot their current working environment.
"""

import subprocess
import sys
import logging
import re
from pathlib import Path
from typing import Optional, Set


class EnvironmentDetector:
    """Detect Python version and dependencies from user's current environment."""
    
    def __init__(self, working_directory: str):
        self.working_directory = Path(working_directory)
    
    def _filter_tropiflo_from_requirements(self, requirements: list[str]) -> list[str]:
        """
        Filter out tropiflo and its dependencies from any requirements list.
        SAFETY: Even if user accidentally adds tropiflo to requirements.txt, we remove it.
        
        Args:
            requirements: List of requirement strings
            
        Returns:
            Filtered list without tropiflo/co-datascientist
        """
        tropiflo_deps = self._get_tropiflo_dependencies()
        
        # Packages to always exclude from Docker containers
        EXCLUDE_PACKAGES = {
            # Tropiflo itself (runs on HOST, orchestrates Docker)
            'co-datascientist',
            'tropiflo',
            
            # Backend frameworks (user's scripts don't run web servers)
            'uvicorn', 'starlette', 'fastapi', 'gunicorn',
            
            # MCP server (for IDE integration, not for running code)
            'mcp',
            
            # CLI/terminal UI (tropiflo handles this on host)
            'rich', 'cyclopts', 'typer',
            
            # Keyring dependencies (auth handled on host)
            'secretstorage', 'jeepney',
            
            # Development/debugging tools
            'ipython', 'pytest', 'twine', 'debugpy',
        }
        
        all_excluded = EXCLUDE_PACKAGES | tropiflo_deps
        
        filtered = []
        for req in requirements:
            req = req.strip()
            if not req:
                continue
            
            # Extract package name (before ==, >=, etc.)
            package_name = req.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('[')[0].lower().strip()
            
            # Skip if it's a tropiflo/dev package
            if package_name in all_excluded:
                logging.debug(f"   Filtering out: {req}")
                continue
            
            filtered.append(req)
        
        return filtered
    
    def _get_tropiflo_dependencies(self) -> Set[str]:
        """
        Get tropiflo's own dependencies so we can exclude them from the container.
        These packages are only installed because tropiflo is installed on the host.
        
        Returns:
            Set of package names that are tropiflo's dependencies
        """
        try:
            # Try to get tropiflo's metadata
            import importlib.metadata as metadata
            
            try:
                # Try 'tropiflo' first (PyPI name)
                dist = metadata.distribution('tropiflo')
            except metadata.PackageNotFoundError:
                try:
                    # Try 'co-datascientist' as fallback
                    dist = metadata.distribution('co-datascientist')
                except metadata.PackageNotFoundError:
                    # If tropiflo isn't installed (shouldn't happen), return empty set
                    logging.debug("   Could not find tropiflo package metadata")
                    return set()
            
            # Parse dependencies from metadata
            deps = set()
            if dist.requires:
                for req in dist.requires:
                    # Extract package name (before version specifiers)
                    # E.g., "click>=8.1.8" -> "click"
                    package_name = re.split(r'[><=!;]', req)[0].strip().lower()
                    deps.add(package_name)
            
            logging.debug(f"   Tropiflo dependencies to exclude: {sorted(deps)}")
            return deps
            
        except Exception as e:
            logging.debug(f"   Could not get tropiflo dependencies: {e}")
            return set()
    
    def detect_python_version(self) -> str:
        """
        Detect Python version from current environment.
        
        Returns:
            Python version string like "3.10", "3.11", etc.
        """
        try:
            # Use the Python that's currently running (user's environment)
            version_info = sys.version_info
            # Return major.minor (e.g., "3.10")
            python_version = f"{version_info.major}.{version_info.minor}"
            logging.info(f"Detected Python version: {python_version}")
            return python_version
        except Exception as e:
            logging.warning(f"Failed to detect Python version: {e}, defaulting to 3.10")
            return "3.10"
    
    def detect_requirements(self) -> list[str]:
        """
        Detect requirements for Docker container.
        
        Strategy:
        1. Check if requirements.txt exists in user's project → use it (RECOMMENDED)
        2. Otherwise, use pip freeze from the currently active environment (fallback)
        3. Always filter out tropiflo/co-datascientist (runs on HOST, not in Docker)
        
        Returns:
            List of requirement strings (e.g., ["pandas==1.5.0", "numpy>=1.20.0"])
        """
        # Strategy 1: Use existing requirements.txt if present (RECOMMENDED)
        req_file = self.working_directory / "requirements.txt"
        if req_file.exists():
            logging.info("Found requirements.txt in project")
            try:
                requirements = req_file.read_text().strip().split('\n')
                # Filter out empty lines and comments
                requirements = [
                    req.strip() 
                    for req in requirements 
                    if req.strip() and not req.strip().startswith('#')
                ]
                if requirements:
                    # ALWAYS filter tropiflo even from requirements.txt (safety check)
                    filtered = self._filter_tropiflo_from_requirements(requirements)
                    logging.info(f"Using {len(filtered)} packages from requirements.txt")
                    if len(filtered) < len(requirements):
                        logging.info(f"   (Filtered out {len(requirements) - len(filtered)} tropiflo/dev packages)")
                    return filtered
            except Exception as e:
                logging.warning(f"Failed to read requirements.txt: {e}")
        
        # Strategy 2: Fallback to pip freeze from active environment
        logging.info("No requirements.txt found. Using pip freeze (may include extra packages).")
        logging.info("TIP: Create requirements.txt with only the packages you need for faster builds!")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                check=True
            )
            
            requirements = result.stdout.strip().split('\n')
            
            # Filter out problematic entries first
            clean_requirements = []
            for req in requirements:
                req = req.strip()
                if not req:
                    continue
                
                # Skip comments (from pip freeze editable installs)
                if req.startswith('#'):
                    continue
                
                # Skip editable installs
                if req.startswith('-e') or 'editable' in req.lower():
                    continue
                
                # Skip conda build artifacts
                if '/croot/' in req or '@ file://' in req:
                    continue
                
                # Skip local paths
                if req.startswith('/') or req.startswith('./') or req.startswith('file://'):
                    continue
                
                clean_requirements.append(req)
            
            # Now filter tropiflo and dev packages
            filtered_requirements = self._filter_tropiflo_from_requirements(clean_requirements)
            
            skipped = len(requirements) - len(filtered_requirements)
            logging.info(f"Captured {len(filtered_requirements)} packages from active environment")
            logging.info(f"   (filtered out {skipped} editable/tropiflo/dev packages)")
            return filtered_requirements
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to run pip freeze: {e}")
            return []
        except Exception as e:
            logging.error(f"Error detecting requirements: {e}")
            return []
    
    def detect_data_path(self) -> Optional[str]:
        """
        Try to detect if user is loading data from a specific directory.
        This is optional and helps with auto-mounting volumes.
        
        Returns:
            Path to data directory if detected, None otherwise
        """
        # Common data directory names
        data_dirs = ['data', 'dataset', 'datasets', 'input', 'Data']
        
        for dirname in data_dirs:
            data_path = self.working_directory / dirname
            if data_path.exists() and data_path.is_dir():
                # Check if it has files
                if list(data_path.iterdir()):
                    logging.info(f"Detected data directory: {dirname}/")
                    return str(data_path.absolute())
        
        return None
    
    def get_environment_snapshot(self) -> dict:
        """
        Get complete snapshot of user's environment for Docker generation.
        
        Returns:
            Dictionary with python_version, requirements, and optional data_path
        """
        snapshot = {
            'python_version': self.detect_python_version(),
            'requirements': self.detect_requirements(),
            'data_path': self.detect_data_path(),
        }
        
        logging.info("Environment snapshot:")
        logging.info(f"   Python: {snapshot['python_version']}")
        logging.info(f"   Packages: {len(snapshot['requirements'])} detected")
        if snapshot['data_path']:
            logging.info(f"   Data: {snapshot['data_path']}")
        
        return snapshot

