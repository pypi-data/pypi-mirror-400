"""
Resource classes for Magpie SDK
"""

import time
import json
import hashlib
from typing import Optional, Dict, Any, List, Generator
from datetime import datetime

from .models import (
    Job,
    JobRun,
    JobStatus,
    JobResult,
    Template,
    LogEntry,
    JobState,
    PersistentVMHandle,
    SSHCommandResult,
)
from .exceptions import TimeoutError

# Default proxy domain for public URLs
PROXY_DOMAIN = "app.lfg.run"


def generate_subdomain(request_id: str) -> str:
    """Generate a subdomain from a request ID."""
    # Use first 12 chars of the request_id for a short, unique subdomain
    return request_id[:12].lower().replace("_", "-")


def generate_proxy_url(request_id: str, port: int = 8080) -> str:
    """Generate a proxy URL for a job."""
    subdomain = generate_subdomain(request_id)
    return f"https://{subdomain}.{PROXY_DOMAIN}"


class JobsResource:
    """Resource for managing jobs"""
    
    def __init__(self, client):
        self.client = client
    
    def run(
        self,
        name: str,
        script: str,
        description: Optional[str] = None,
        script_type: str = "inline",
        vcpus: int = 2,
        memory_mb: int = 512,
        environment: Optional[Dict[str, str]] = None,
        docker_image: Optional[str] = None,
        stateful: bool = False,
        workspace_id: Optional[str] = None,
        workspace_size_gb: Optional[int] = None,
        persist: bool = False,
        ip_lease: bool = False,
    ) -> Dict[str, Any]:
        """
        Create and run a new job (asynchronous - returns immediately).

        Args:
            name: Job name
            script: Script content to execute
            description: Optional job description
            script_type: Type of script (inline, python, docker)
            vcpus: Number of vCPUs
            memory_mb: Memory in MB
            environment: Environment variables
            docker_image: Docker image to use
            stateful: Whether the job should persist state
            workspace_id: Workspace ID for stateful jobs (reuse existing workspace)
            workspace_size_gb: Workspace size in GB for stateful jobs
            persist: Keep VM alive after job completes (for persistent sessions)
            ip_lease: Expose IPv6 IP address for VM access

        Returns:
            Dictionary with request_id, status, and message
        """
        data = {
            "name": name,
            "script": script,
            "type": script_type,
            "vcpus": vcpus,
            "memory_mb": memory_mb,
            "environment": environment or {},
            "stateful": stateful,
            "persist": persist,
            "ip_lease": ip_lease,
        }

        if description:
            data["description"] = description
        if docker_image:
            data["docker_image"] = docker_image
        if workspace_id:
            data["workspace_id"] = workspace_id
        if workspace_size_gb:
            data["workspace_size_gb"] = workspace_size_gb

        response = self.client._make_request("POST", "/api/v1/jobs", data=data)
        return response

    def create_persistent_vm(
        self,
        name: str,
        script: str,
        description: Optional[str] = None,
        script_type: str = "inline",
        vcpus: int = 2,
        memory_mb: int = 512,
        environment: Optional[Dict[str, str]] = None,
        stateful: bool = False,
        workspace_id: Optional[str] = None,
        workspace_size_gb: Optional[int] = None,
        poll_timeout: int = 180,
        poll_interval: int = 2,
        register_proxy: bool = False,
        proxy_port: int = 8080,
    ) -> PersistentVMHandle:
        """
        Create a persistent VM with IPv6 lease and return its handle.

        Args:
            name: Job name
            script: Setup script to run
            description: Optional description
            script_type: Script type (inline, python, etc.)
            vcpus: Number of vCPUs
            memory_mb: Memory in MB
            environment: Environment variables
            stateful: Whether to use stateful workspace
            workspace_id: Existing workspace ID
            workspace_size_gb: Workspace size in GB
            poll_timeout: Max time to wait for VM info
            poll_interval: Poll interval in seconds
            register_proxy: If True, register a public proxy URL for the VM
            proxy_port: Port to proxy to on the VM (default: 8080)

        Returns:
            PersistentVMHandle with request_id, vm_id, ip_address, and proxy_url
        """

        response = self.run(
            name=name,
            script=script,
            description=description,
            script_type=script_type,
            vcpus=vcpus,
            memory_mb=memory_mb,
            environment=environment,
            stateful=stateful,
            workspace_id=workspace_id,
            workspace_size_gb=workspace_size_gb,
            persist=True,
            ip_lease=True,
        )

        request_id = response.get("request_id")
        handle = PersistentVMHandle(request_id=request_id)

        vm_info = self.get_vm_info(request_id, poll_timeout=poll_timeout, poll_interval=poll_interval)
        if vm_info:
            handle.vm_id = vm_info.get("vm_id")
            handle.agent_id = vm_info.get("agent_id")
            handle.ip_address = (
                vm_info.get("ip_address")
                or vm_info.get("ipv6_address")
                or vm_info.get("ipv4_address")
            )

            # Generate proxy URL if requested and we have an IPv6 address
            # Note: No registration needed - the proxy server automatically looks up
            # the job's IPv6 by subdomain (derived from request_id)
            if register_proxy and handle.ip_address:
                handle.proxy_url = generate_proxy_url(request_id)

        return handle
    
    def get(self, job_id: str) -> Job:
        """Get job details."""
        response = self.client._make_request("GET", f"/api/v1/jobs/{job_id}")
        return Job(**response)
    
    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        template_id: Optional[str] = None
    ) -> List[Job]:
        """List all jobs."""
        params = {
            "page": page,
            "page_size": page_size,
        }
        if template_id:
            params["template_id"] = template_id
        
        response = self.client._make_request("GET", "/api/v1/jobs", params=params)
        return [Job(**job) for job in response.get("jobs", [])]
    
    def update(
        self,
        job_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        script: Optional[str] = None,
        vcpus: Optional[int] = None,
        memory_mb: Optional[int] = None,
        environment: Optional[Dict[str, str]] = None,
    ) -> Job:
        """Update a job."""
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if script is not None:
            data["script"] = script
        if vcpus is not None:
            data["vcpus"] = vcpus
        if memory_mb is not None:
            data["memory_mb"] = memory_mb
        if environment is not None:
            data["environment"] = environment
        
        response = self.client._make_request("PUT", f"/api/v1/jobs/{job_id}", data=data)
        return Job(**response)
    
    def delete(self, job_id: str) -> None:
        """Delete a job."""
        self.client._make_request("DELETE", f"/api/v1/jobs/{job_id}")

    def execute(
        self,
        job_id: str,
        environment: Optional[Dict[str, str]] = None
    ) -> JobRun:
        """
        Execute an existing job definition.

        Args:
            job_id: ID of the job definition to execute
            environment: Override environment variables for this run

        Returns:
            JobRun object with execution details
        """
        data = {}
        if environment:
            data["environment"] = environment
        
        response = self.client._make_request("POST", f"/api/v1/jobs/{job_id}/run", data=data)
        return JobRun(**response)
    
    def get_status(self, run_id: str) -> JobStatus:
        """Get the status of a job run."""
        response = self.client._make_request("GET", f"/api/v1/jobs/{run_id}/status")
        return JobStatus(**response)
    
    def get_logs(self, run_id: str) -> List[LogEntry]:
        """Get logs for a job run."""
        response = self.client._make_request("GET", f"/api/v1/jobs/{run_id}/logs")
        logs = response.get("logs", [])

        result = []
        for log in logs:
            if isinstance(log, str):
                # Simple string log
                result.append(LogEntry(
                    timestamp=datetime.now(),
                    message=log,
                    level="info"
                ))
            else:
                # Structured log
                result.append(LogEntry(**log))

        return result

    def get_vm_info(self, run_id: str, poll_timeout: int = 120, poll_interval: int = 2) -> Dict[str, Any]:
        """
        Get VM information for a persistent job, including IPv6 address.

        This method polls the agent for VM info until IPv6 is available or timeout.
        Only works for jobs with persist=True and ip_lease=True.

        Args:
            run_id: ID of the job run (request_id)
            poll_timeout: Maximum time to poll for IPv6 in seconds (default: 120)
            poll_interval: Time between polls in seconds (default: 2)

        Returns:
            Dictionary with vm_id, agent_id, and ip_address (IPv6)

        Example:
            >>> result = client.jobs.run_and_wait(
            ...     name="Test",
            ...     script="echo test",
            ...     persist=True,
            ...     ip_lease=True
            ... )
            >>> vm_info = client.jobs.get_vm_info(result.request_id)
            >>> print(f"IPv6: {vm_info['ip_address']}")
        """
        start_time = time.time()

        while True:
            response = self.client._make_request("GET", f"/api/v1/jobs/{run_id}/vm-info")

            # If we have an IPv6 address, return immediately
            if response.get('ip_address'):
                return response

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed >= poll_timeout:
                # Return what we have, even without IPv6
                return response

            # Wait before next poll
            time.sleep(poll_interval)

    def ssh(self, run_id: str, command: str, timeout: int = 30) -> SSHCommandResult:
        """Execute an SSH command on a persistent VM identified by job ID."""

        if not command or not command.strip():
            raise ValueError("command is required")

        payload: Dict[str, Any] = {"command": command}
        if timeout and timeout > 0:
            payload["timeout_seconds"] = timeout

        response = self.client._make_request("POST", f"/api/v1/jobs/{run_id}/ssh", data=payload)

        return SSHCommandResult(
            request_id=run_id,
            command=command,
            exit_code=response.get("exit_code", 0),
            stdout=response.get("stdout", ""),
            stderr=response.get("stderr", ""),
            duration_ms=response.get("duration_ms"),
        )

    def get_proxy_url(self, request_id: str) -> str:
        """
        Get the proxy URL for a job (does not register, just generates the URL).

        Args:
            request_id: The job's request ID

        Returns:
            The proxy URL string (e.g., https://abc123def456.app.lfg.run)
        """
        return generate_proxy_url(request_id)

    def stream_logs(self, run_id: str) -> Generator[LogEntry, None, None]:
        """
        Stream logs by polling (WebSocket not implemented).

        Yields:
            LogEntry objects as they arrive
        """
        raise NotImplementedError("Log streaming not implemented. Use get_logs() instead.")
    
    def cancel(self, run_id: str) -> None:
        """Cancel a running job."""
        self.client._make_request("POST", f"/api/v1/jobs/{run_id}/cancel")
    
    def wait_for_completion(
        self,
        run_id: str,
        timeout: int = 300,
        poll_interval: int = 2
    ) -> JobStatus:
        """
        Wait for a job to complete.

        Args:
            run_id: ID of the job run
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds

        Returns:
            Final job status

        Raises:
            TimeoutError: If job doesn't complete within timeout
        """
        start_time = time.time()

        while True:
            status = self.get_status(run_id)

            if status.status in [JobState.COMPLETED, JobState.FAILED, JobState.ERROR, JobState.CANCELLED]:
                return status

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(f"Job {run_id} did not complete within {timeout} seconds")

            time.sleep(poll_interval)

    def get_result(self, run_id: str) -> JobResult:
        """
        Get the result of a completed job.

        Args:
            run_id: ID of the job run

        Returns:
            JobResult with status, exit code, and logs

        Example:
            >>> result = client.jobs.get_result("req_123")
            >>> if result.success:
            ...     print("Job succeeded!")
            ...     for log in result.logs:
            ...         print(log)
            ... else:
            ...     print(f"Job failed with exit code {result.exit_code}")
        """
        status = self.get_status(run_id)

        # Determine if the job was successful
        success = (
            status.status.lower() == "completed" and
            (status.exit_code == 0 or status.exit_code is None)
        )

        # Generate proxy URL if we have an IPv6 address
        proxy_url = None
        if status.ipv6_address and status.persist:
            proxy_url = generate_proxy_url(run_id)

        return JobResult(
            request_id=status.request_id,
            name=status.name,
            status=status.status,
            exit_code=status.exit_code,
            logs=status.logs,
            duration_ms=status.duration_ms,
            script_duration_ms=status.script_duration_ms,
            started_at=status.started_at,
            completed_at=status.completed_at,
            error_message=status.error_message,
            success=success,
            persist=status.persist,
            ipv6_address=status.ipv6_address,
            proxy_url=proxy_url,
        )

    def run_and_wait(
        self,
        name: str,
        script: str,
        description: Optional[str] = None,
        script_type: str = "inline",
        vcpus: int = 2,
        memory_mb: int = 512,
        environment: Optional[Dict[str, str]] = None,
        docker_image: Optional[str] = None,
        stateful: bool = False,
        workspace_id: Optional[str] = None,
        workspace_size_gb: Optional[int] = None,
        persist: bool = False,
        ip_lease: bool = False,
        timeout: int = 300,
        poll_interval: int = 2,
    ) -> JobResult:
        """
        Create a job, wait for it to complete, and return the result (synchronous).

        This is a convenience method that combines run(), wait_for_completion(),
        and get_result() into a single call.

        Args:
            name: Job name
            script: Script content to execute
            description: Optional job description
            script_type: Type of script (inline, python, docker)
            vcpus: Number of vCPUs
            memory_mb: Memory in MB
            environment: Environment variables
            docker_image: Docker image to use
            stateful: Whether the job should persist state
            workspace_id: Workspace ID for stateful jobs (reuse existing workspace)
            workspace_size_gb: Workspace size in GB for stateful jobs
            persist: Keep VM alive after job completes (for persistent sessions)
            ip_lease: Expose IPv6 IP address for VM access
            timeout: Maximum time to wait for completion in seconds
            poll_interval: Time between status checks in seconds

        Returns:
            JobResult with the final status, logs, and exit code

        Raises:
            TimeoutError: If job doesn't complete within timeout

        Example:
            >>> result = client.jobs.run_and_wait(
            ...     name="Hello World",
            ...     script="echo 'Hello!' && exit 0"
            ... )
            >>> if result.success:
            ...     print("Job completed successfully!")
            ...     for log in result.logs:
            ...         print(log)
            ... else:
            ...     print(f"Job failed: {result.error_message}")
        """
        # Create and run the job
        response = self.run(
            name=name,
            script=script,
            description=description,
            script_type=script_type,
            vcpus=vcpus,
            memory_mb=memory_mb,
            environment=environment,
            docker_image=docker_image,
            stateful=stateful,
            workspace_id=workspace_id,
            workspace_size_gb=workspace_size_gb,
            persist=persist,
            ip_lease=ip_lease,
        )

        request_id = response.get("request_id")

        # Wait for completion
        self.wait_for_completion(request_id, timeout=timeout, poll_interval=poll_interval)

        # Get and return the result
        return self.get_result(request_id)

    def send_command(
        self,
        run_id: str,
        script: str,
        workspace_id: Optional[str] = None
    ) -> JobRun:
        """
        Send a new command to a stateful job.

        This creates a new job execution that runs in the same workspace
        as the original stateful job, allowing you to continue working
        with persisted state.

        Args:
            run_id: ID of the original stateful job run
            script: New script/command to execute
            workspace_id: Optional workspace ID (if not provided, will use the workspace from run_id)

        Returns:
            JobRun object for the new command execution

        Example:
            >>> # Create initial stateful job
            >>> job = client.jobs.create(
            ...     name="my-workspace",
            ...     script="echo 'hello' > data.txt",
            ...     stateful=True
            ... )
            >>> run = client.jobs.run(job.id)
            >>>
            >>> # Send additional commands to the same workspace
            >>> run2 = client.jobs.send_command(run.id, "cat data.txt")
            >>> run3 = client.jobs.send_command(run.id, "echo 'world' >> data.txt")
        """
        # Extract workspace_id if not provided
        if workspace_id is None:
            # Try to get workspace ID from the job details
            try:
                job_details = self.client._make_request("GET", f"/api/v1/jobs/{run_id}/details")
                workspace_id = job_details.get("workspace_id") or run_id
            except:
                # Fallback: use the run_id as workspace_id
                workspace_id = run_id

        # Submit a new stateful job with the same workspace
        data = {
            "script": script,
            "type": "inline",
            "stateful": True,
            "workspace_id": workspace_id,
        }

        response = self.client._make_request("POST", "/api/v1/jobs", data=data)
        return JobRun(**response)


class TemplatesResource:
    """Resource for managing job templates"""
    
    def __init__(self, client):
        self.client = client
    
    def create(
        self,
        name: str,
        script: str,
        description: Optional[str] = None,
        script_type: str = "inline",
        vcpus: int = 2,
        memory_mb: int = 512,
        environment: Optional[Dict[str, str]] = None,
    ) -> Template:
        """Create a new job template."""
        data = {
            "name": name,
            "description": description,
            "script_type": script_type,
            "vcpus": vcpus,
            "memory_mb": memory_mb,
            "script": script,
            "environment": environment or {},
        }
        
        response = self.client._make_request("POST", "/api/v1/job-templates", data=data)
        return Template(**response)
    
    def get(self, template_id: str) -> Template:
        """Get template details."""
        response = self.client._make_request("GET", f"/api/v1/job-templates/{template_id}")
        return Template(**response)
    
    def list(self, page: int = 1, page_size: int = 20) -> List[Template]:
        """List all templates."""
        params = {
            "page": page,
            "page_size": page_size,
        }
        
        response = self.client._make_request("GET", "/api/v1/job-templates", params=params)
        templates = response if isinstance(response, list) else response.get("templates", [])
        return [Template(**template) for template in templates]
    
    def update(
        self,
        template_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        script: Optional[str] = None,
        vcpus: Optional[int] = None,
        memory_mb: Optional[int] = None,
        environment: Optional[Dict[str, str]] = None,
        comment: Optional[str] = None,
    ) -> Template:
        """Update a template."""
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if script is not None:
            data["script"] = script
        if vcpus is not None:
            data["vcpus"] = vcpus
        if memory_mb is not None:
            data["memory_mb"] = memory_mb
        if environment is not None:
            data["environment"] = environment
        if comment:
            data["comment"] = comment
        
        response = self.client._make_request("PUT", f"/api/v1/job-templates/{template_id}", data=data)
        return Template(**response)
    
    def delete(self, template_id: str) -> None:
        """Delete a template."""
        self.client._make_request("DELETE", f"/api/v1/job-templates/{template_id}")
    
    def run(
        self,
        template_id: str,
        environment: Optional[Dict[str, str]] = None
    ) -> JobRun:
        """Run a job from a template."""
        data = {}
        if environment:
            data["environment"] = environment
        
        response = self.client._make_request("POST", f"/api/v1/job-templates/{template_id}/run", data=data)
        return JobRun(**response)
