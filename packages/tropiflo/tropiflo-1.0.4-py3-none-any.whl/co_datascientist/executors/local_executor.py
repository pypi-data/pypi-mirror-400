"""Local executor: run a docker image locally and collect output."""

import subprocess
import time
import logging
from .base_executor import BaseExecutor
from ..models import CodeResult
from ..settings import settings
from ..kpi_extractor import extract_kpi_from_stdout

class LocalExecutor(BaseExecutor):
    """Execute code locally by running a docker image and collecting output."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Auto-detect GPU availability once at initialization
        self._gpu_available, self._gpu_status = self._check_gpu_availability()
        if self._gpu_available:
            logging.info("GPU detected - will enable GPU support for Docker containers")
        else:
            logging.debug(f"GPU not available: {self._gpu_status}")

    @property
    def platform_name(self) -> str:
        return "local"
    
    def _check_gpu_availability(self) -> tuple[bool, str]:
        """
        Auto-detect if NVIDIA GPU and Docker GPU support are available.
        Returns (available: bool, status_message: str).
        """
        # Allow config to override auto-detection
        if self.config:
            if self.config.get('enable_gpu') is False:
                return False, "Manually disabled in config"
            if self.config.get('enable_gpu') is True:
                return True, "Manually enabled in config"
        
        # Auto-detect: Check if nvidia-smi exists and Docker supports --gpus
        try:
            # Check if nvidia-smi works (GPU exists on host)
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                timeout=2
            )
            if result.returncode != 0:
                return False, "nvidia-smi not found or failed (no NVIDIA GPU detected)"
            
            # Check if Docker supports GPU (NVIDIA Container Toolkit installed)
            result = subprocess.run(
                ["docker", "run", "--rm", "--gpus", "all", "hello-world"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "NVIDIA GPU and Docker GPU support detected"
            else:
                stderr = result.stderr.decode() if isinstance(result.stderr, bytes) else result.stderr
                return False, f"Docker --gpus flag failed (NVIDIA Container Toolkit not installed?): {stderr[:100]}"
            
        except FileNotFoundError as e:
            return False, f"Command not found: {e.filename}"
        except subprocess.SubprocessError as e:
            return False, f"Subprocess error: {str(e)[:100]}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)[:100]}"

    def execute(self, docker_image_tag: str) -> CodeResult:
        """
        Execute a docker image locally and collect output.

        Args:
            docker_image_tag: The tag of the docker image to run.

        Returns:
            CodeResult containing stdout, stderr, return_code, runtime_ms, and kpi.
        """
        start_time = time.time()
        
        # Build docker run command with optional volume mounting and GPU support
        run_cmd = ["docker", "run", "--rm"]
        
        # Add GPU support if available (auto-detected or manually enabled)
        if self._gpu_available:
            run_cmd.extend(["--gpus", "all"])
            logging.debug("Enabling GPU support for Docker container")
        
        # Add volume mount if data_volume is specified in config
        if self.config and self.config.get('data_volume'):
            data_volume = self.config['data_volume']
            logging.info(f"Mounting data volume: {data_volume} -> /data")
            run_cmd.extend(["-v", f"{data_volume}:/data"])
            run_cmd.extend(["-e", "INPUT_URI=/data"])
        
        run_cmd.append(docker_image_tag)
        logging.info(f"Running docker command: {' '.join(run_cmd)}")
        try:
            output = subprocess.run(
                run_cmd,
                capture_output=True,
                text=True,
                timeout=settings.script_execution_timeout
            )
            return_code = output.returncode
            out = output.stdout
            err = output.stderr
        except subprocess.TimeoutExpired:
            return_code = -9
            out = None
            err = f"Process timed out after {settings.script_execution_timeout} seconds"
            logging.info(f"Process timed out after {settings.script_execution_timeout} seconds")
        except Exception as e:
            return_code = -1
            out = None
            err = f"Error running docker image: {e}"
            logging.error(err)

        # Clean up empty strings
        if isinstance(out, str) and out.strip() == "":
            out = None
        if isinstance(err, str) and err.strip() == "":
            err = None

        logging.info(f"Docker execution stdout: {out}")
        logging.info(f"Docker execution stderr: {err}")

        runtime_ms = int((time.time() - start_time) * 1000)
        kpi = extract_kpi_from_stdout(out) if out else None

        # Note: Docker image cleanup is handled by workflow_runner, not by the executor
        
        return CodeResult(
            stdout=out,
            stderr=err,
            return_code=return_code,
            runtime_ms=runtime_ms,
            kpi=kpi
        )

    def is_available(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
