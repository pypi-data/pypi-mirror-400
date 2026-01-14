"""GCloud executor: push docker image to Artifact Registry and run as Cloud Run Job."""

import subprocess
import time
import logging
import datetime as dt
from typing import Optional, List
from .base_executor import BaseExecutor
from ..models import CodeResult
from ..settings import settings
from ..kpi_extractor import extract_kpi_from_stdout


class GCloudExecutor(BaseExecutor):
    """Execute code on Google Cloud by pushing docker image to Artifact Registry and running as Cloud Run Job."""

    def __init__(self, python_path: str = "python", config: dict = None):
        """Initialize GCloud executor.
        
        Args:
            python_path: Ignored for cloud executors.
            config: Configuration dictionary with 'gcloud' key containing:
                - project_id: GCP project ID (required)
                - region: GCP region (default: us-central1)
                - repo: Artifact Registry repo name (default: co-datascientist-repo)
                - job_name: Cloud Run Job name (default: co-datascientist-job)
                - cleanup_job: Whether to delete the Cloud Run Job after execution (default: True)
                - cleanup_remote_image: Whether to delete the remote image after execution (default: True)
                - data_volume: GCS bucket for data (optional, e.g., "gs://my-bucket" or "my-bucket")
        """
        super().__init__(python_path, config)
        
        # Extract gcloud-specific config
        # Support both nested format (legacy) and flat format with mode field
        if "gcloud" in self.config:
            # Legacy nested format: config['gcloud']['project_id']
            gcloud_config = self.config["gcloud"]
        elif self.config.get("mode") == "gcloud":
            # New flat format with mode: config['project_id']
            gcloud_config = self.config
        else:
            # Fallback to entire config
            gcloud_config = self.config
        
        # Required config
        if not gcloud_config.get("project_id"):
            raise ValueError("GCloudExecutor requires 'project_id' in config")
        
        self.project_id = gcloud_config["project_id"]
        self.region = gcloud_config.get("region", "us-central1")
        self.repo = gcloud_config.get("repo", "co-datascientist-repo")
        self.job_name = gcloud_config.get("job_name", "co-datascientist-job")
        # Default: DON'T cleanup jobs (reuse them for speed), but DO cleanup images (save storage)
        self.cleanup_job = gcloud_config.get("cleanup_job", False)  # Changed default to False for speed
        self.cleanup_remote_image = gcloud_config.get("cleanup_remote_image", True)
        
        # Data volume support (GCS bucket)
        data_volume = gcloud_config.get("data_volume")
        if data_volume:
            # Extract bucket name from gs:// URL if provided
            if data_volume.startswith("gs://"):
                self.gcs_bucket = data_volume.replace("gs://", "").split("/")[0]
            else:
                self.gcs_bucket = data_volume
            logging.info(f"GCS data volume configured: {self.gcs_bucket}")
        else:
            self.gcs_bucket = None

    @property
    def platform_name(self) -> str:
        return "gcloud"

    def _run_command(
        self,
        cmd: List[str],
        check: bool = True,
        capture: bool = False,
        timeout: Optional[int] = None,
        suppress_output: bool = False
    ) -> subprocess.CompletedProcess:
        """Run a shell command with logging.
        
        Args:
            suppress_output: If True, redirect stdout and stderr to devnull to silence all output
        """
        logging.debug(f"Running command: {' '.join(cmd)}")
        try:
            if suppress_output:
                # Completely silence the command
                result = subprocess.run(
                    cmd,
                    check=check,
                    text=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=timeout
                )
            else:
                result = subprocess.run(
                    cmd,
                    check=check,
                    text=True,
                    capture_output=capture,
                    timeout=timeout
                )
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {' '.join(cmd)}")
            logging.error(f"stderr: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")
            raise
        except subprocess.TimeoutExpired:
            logging.error(f"Command timed out: {' '.join(cmd)}")
            raise

    def _ensure_repo(self) -> None:
        """Create Artifact Registry repo if missing (no-op if exists)."""
        logging.info(f"Ensuring Artifact Registry repo exists: {self.repo}")
        self._run_command(
            [
                "gcloud", "artifacts", "repositories", "create", self.repo,
                "--repository-format=docker",
                f"--location={self.region}",
                f"--project={self.project_id}",
                "--quiet"
            ],
            check=False,
            suppress_output=True  # Silence "ALREADY_EXISTS" errors
        )

    def _job_exists(self, job_name: str) -> bool:
        """Return True if Cloud Run Job exists."""
        result = self._run_command(
            [
                "gcloud", "run", "jobs", "describe", job_name,
                f"--region={self.region}",
                f"--project={self.project_id}"
            ],
            check=False,
            suppress_output=True  # Suppress "Cannot find job" errors
        )
        return result.returncode == 0

    def _latest_execution(self, job_name: str) -> Optional[str]:
        """Get the name of the latest execution for a job."""
        result = self._run_command(
            [
                "gcloud", "run", "jobs", "executions", "list",
                "--job", job_name,
                f"--region={self.region}",
                f"--project={self.project_id}",
                "--format=value(name)",
                "--limit=1"
            ],
            capture=True
        )
        name = (result.stdout or "").strip()
        return name or None

    def _collect_stdout(self, job_name: str, execution: str) -> str:
        """Fetch stdout logs for a given execution with retry logic."""
        logging.info(f"Collecting logs for execution: {execution}")
        
        # Retry up to 3 times with 10 second delays (logs can be slow to propagate)
        for attempt in range(3):
            if attempt > 0:
                logging.info(f"Retry {attempt}/2: Waiting for logs to appear...")
                time.sleep(10)
            
            # Try plain text (textPayload) first
            result = self._run_command(
                [
                    "gcloud", "logging", "read",
                    f'resource.type="cloud_run_job" '
                    f'AND resource.labels.job_name="{job_name}" '
                    f'AND labels."run.googleapis.com/execution_name"="{execution}"',
                    f"--project={self.project_id}",
                    "--limit=100000",
                    "--format=value(textPayload)",
                ],
                check=False,
                capture=True,
                timeout=300  # 5 minutes for log collection
            )
            
            payload = result.stdout or ""
            
            if not payload.strip():
                # Fallback: JSON (covers structured logs)
                logging.info("No textPayload found, trying JSON format")
                result = self._run_command(
                    [
                        "gcloud", "logging", "read",
                        f'resource.type="cloud_run_job" '
                        f'AND resource.labels.job_name="{job_name}" '
                        f'AND labels."run.googleapis.com/execution_name"="{execution}"',
                        f"--project={self.project_id}",
                        "--limit=100000",
                        "--format=json",
                    ],
                    check=False,
                    capture=True,
                    timeout=300
                )
                payload = result.stdout or ""
            
            # If we got logs, return them
            if payload.strip():
                logging.info(f"Successfully collected logs ({len(payload)} bytes)")
                return payload
        
        # After all retries, return whatever we have (might be empty)
        logging.warning(f"Failed to collect logs after 3 attempts")
        return payload

    def _push_image(self, local_tag: str, remote_tag: str) -> None:
        """Tag and push image to Artifact Registry."""
        logging.info(f"Pushing image from {local_tag} to {remote_tag}")
        print(f"   Pushing Docker image to Cloud...")
        
        # Configure docker auth (suppress credential warnings)
        self._run_command(
            ["gcloud", "auth", "configure-docker", f"{self.region}-docker.pkg.dev", "--quiet"],
            timeout=60,
            suppress_output=True
        )
        
        # Tag the image (silent)
        self._run_command(
            ["docker", "tag", local_tag, remote_tag],
            timeout=60,
            suppress_output=True
        )
        
        # Push the image (silent - no layer spam)
        self._run_command(
            ["docker", "push", remote_tag],
            timeout=1800,  # 30 minutes for push
            suppress_output=True
        )
        logging.info(f"Successfully pushed image to {remote_tag}")

    def _create_or_update_job(self, job_name: str, image: str) -> None:
        """Create or update Cloud Run Job with optional GCS volume mount."""
        exists = self._job_exists(job_name)
        op = "update" if exists else "create"
        
        logging.info(f"{'Updating' if exists else 'Creating'} Cloud Run Job: {job_name}")
        
        cmd = [
            "gcloud", "run", "jobs", op, job_name,
            "--image", image,
            f"--region={self.region}",
            f"--project={self.project_id}",
            "--quiet"
        ]
        
        # Add GCS volume mount if configured
        if self.gcs_bucket:
            logging.info(f"Configuring GCS volume mount for bucket: {self.gcs_bucket}")
            volume_name = "data-volume"
            mount_path = "/data"
            
            # Add volume from GCS bucket
            cmd.extend([
                f"--add-volume=name={volume_name},type=cloud-storage,bucket={self.gcs_bucket}",
                f"--add-volume-mount=volume={volume_name},mount-path={mount_path}"
            ])
            
            # Set environment variable to point to mounted path
            cmd.extend([
                "--set-env-vars", "INPUT_URI=/data"
            ])
            
            logging.info(f"Volume mount: gs://{self.gcs_bucket} -> {mount_path}")
        
        self._run_command(cmd, timeout=300, suppress_output=True)  # 5 minutes, silent
        logging.info(f"Successfully {op}d Cloud Run Job: {job_name}")

    def _execute_job(self, job_name: str, timeout_seconds: int) -> int:
        """Execute the Cloud Run Job and wait for completion.
        
        Returns:
            Return code (0 for success, non-zero for failure)
        """
        logging.info(f"Executing Cloud Run Job: {job_name}")
        
        print(f"   Running job on Cloud Run...")
        result = self._run_command(
            [
                "gcloud", "run", "jobs", "execute", job_name,
                f"--region={self.region}",
                f"--project={self.project_id}",
                "--wait",
                "--quiet"
            ],
            check=False,
            timeout=timeout_seconds + 300,  # Add 5 minutes buffer for overhead
            suppress_output=True  # Suppress all execution spinners
        )
        
        return result.returncode

    def _cleanup_job(self, job_name: str) -> None:
        """Delete the Cloud Run Job."""
        logging.info(f"Deleting Cloud Run Job: {job_name}")
        self._run_command(
            [
                "gcloud", "run", "jobs", "delete", job_name,
                f"--region={self.region}",
                f"--project={self.project_id}",
                "--quiet"
            ],
            check=False,
            timeout=120,
            suppress_output=True  # Silent cleanup
        )

    def _cleanup_image(self, image: str) -> None:
        """Delete the remote image from Artifact Registry."""
        logging.info(f"Deleting remote image: {image}")
        self._run_command(
            [
                "gcloud", "artifacts", "docker", "images", "delete",
                image,
                "--delete-tags",
                "--quiet"
            ],
            check=False,
            timeout=120,
            suppress_output=True  # Silent cleanup
        )

    def execute(self, docker_image_tag: str) -> CodeResult:
        """
        Execute a docker image on Google Cloud Run and collect output.

        Args:
            docker_image_tag: The tag of the local docker image to run.

        Returns:
            CodeResult containing stdout, stderr, return_code, runtime_ms, and kpi.
        """
        start_time = time.time()
        
        # Use UNIQUE job name per execution to avoid conflicts in parallel mode
        # Append docker_image_tag to ensure uniqueness
        job_name = f"{self.job_name}-{docker_image_tag}"
        
        # Construct remote image path
        ar_image = f"{self.region}-docker.pkg.dev/{self.project_id}/{self.repo}/{docker_image_tag}"
        
        logging.info(f"Starting GCloud execution for image: {docker_image_tag}")
        logging.info(f"Project: {self.project_id}, Region: {self.region}, Job: {job_name}")
        
        out = None
        err = None
        return_code = -1
        
        try:
            # Set project (suppress output)
            self._run_command(
                ["gcloud", "config", "set", "project", self.project_id, "--quiet"],
                timeout=30,
                suppress_output=True
            )
            
            # Enable required APIs (no-op if already enabled, suppress output)
            logging.info("Ensuring required GCP APIs are enabled")
            self._run_command(
                [
                    "gcloud", "services", "enable",
                    "artifactregistry.googleapis.com",
                    "run.googleapis.com",
                    "--quiet"
                ],
                check=False,
                timeout=120,
                suppress_output=True
            )
            
            # Ensure Artifact Registry repo exists
            self._ensure_repo()
            
            # Push image to Artifact Registry
            self._push_image(docker_image_tag, ar_image)
            
            # Create or update Cloud Run Job
            self._create_or_update_job(job_name, ar_image)
            
            # Execute the job
            return_code = self._execute_job(job_name, settings.script_execution_timeout)
            
            # Wait for logs to propagate to Cloud Logging (logs can take 10-30s after job completes)
            print("   Collecting logs from Cloud Run...")
            logging.info("Waiting for logs to propagate to Cloud Logging...")
            time.sleep(15)  # Give logs time to propagate
            
            # Collect logs
            exec_name = self._latest_execution(job_name)
            if exec_name:
                logging.info(f"Latest execution: {exec_name}")
                out = self._collect_stdout(job_name, exec_name)
                
                if not out or not out.strip():
                    out = None
                    err = "No output collected from Cloud Run Job"
                    logging.warning(err)
            else:
                err = "Could not determine latest execution; no logs collected"
                logging.error(err)
            
            logging.info(f"Job execution completed with return code: {return_code}")
            
        except subprocess.TimeoutExpired:
            return_code = -9
            out = None
            err = f"Process timed out after {settings.script_execution_timeout} seconds"
            logging.error(err)
        except Exception as e:
            return_code = -1
            out = None
            err = f"Error running Cloud Run Job: {str(e)}"
            logging.error(err)
        finally:
            # Cleanup remote resources only (local image cleanup is handled by workflow_runner)
            try:
                if self.cleanup_job:
                    self._cleanup_job(job_name)
                
                if self.cleanup_remote_image:
                    self._cleanup_image(ar_image)
                    
            except Exception as e:
                logging.warning(f"Error during cleanup: {e}")

        # Clean up empty strings
        if isinstance(out, str) and out.strip() == "":
            out = None
        if isinstance(err, str) and err.strip() == "":
            err = None

        logging.info(f"GCloud execution stdout: {out}")
        logging.info(f"GCloud execution stderr: {err}")

        runtime_ms = int((time.time() - start_time) * 1000)
        kpi = extract_kpi_from_stdout(out) if out else None

        return CodeResult(
            stdout=out,
            stderr=err,
            return_code=return_code,
            runtime_ms=runtime_ms,
            kpi=kpi
        )

    def is_available(self) -> bool:
        """Check if gcloud CLI and Docker are available."""
        try:
            # Check if config is properly set
            if not self.config or not self.config.get("gcloud"):
                return False
            
            # Check gcloud
            result = subprocess.run(
                ["gcloud", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                return False
            
            # Check docker
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
            
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

