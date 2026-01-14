"""
Data models for Magpie SDK
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field


class JobState(str, Enum):
    """Job execution states"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ERROR = "error"


class Job(BaseModel):
    """Represents a job definition"""
    id: str
    name: str
    description: Optional[str] = None
    script: str
    script_type: str = "inline"
    vcpus: int = Field(default=2, ge=1)
    memory_mb: int = Field(default=512, ge=128)
    environment: Dict[str, str] = Field(default_factory=dict)
    docker_image: Optional[str] = None
    stateful: bool = False
    created_at: datetime
    updated_at: datetime
    user_id: str


class JobRun(BaseModel):
    """Represents a job execution"""
    id: str
    job_id: str
    job_name: Optional[str] = None
    status: JobState
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    exit_code: Optional[int] = None
    error: Optional[str] = None
    agent_id: Optional[str] = None


class JobStatus(BaseModel):
    """Detailed job execution status"""
    request_id: str
    name: Optional[str] = None
    status: str  # not_started, in_progress, completed, error
    logs: List[str] = Field(default_factory=list)
    duration_ms: Optional[int] = Field(default=None, alias="duration")
    script_duration_ms: Optional[int] = None
    exit_code: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    vm_info: Optional[Dict[str, Any]] = None
    persist: bool = False  # VM is persistent
    ipv6_address: Optional[str] = None  # IPv6 address if ip_lease enabled
    proxy_url: Optional[str] = None  # Public URL via reverse proxy (e.g., https://xxx.app.lfg.run)


class Template(BaseModel):
    """Represents a job template"""
    id: str
    name: str
    description: Optional[str] = None
    script_type: str = "inline"
    default_vcpus: int = Field(default=2, ge=1)
    default_memory_mb: int = Field(default=512, ge=128)
    created_at: datetime
    updated_at: datetime
    user_id: str
    latest_revision: Optional["TemplateRevision"] = None


class TemplateRevision(BaseModel):
    """Represents a template revision"""
    id: str
    template_id: str
    revision: int
    script: str
    environment: Dict[str, str] = Field(default_factory=dict)
    comment: Optional[str] = None
    created_at: datetime
    created_by: str


class LogEntry(BaseModel):
    """Represents a log entry"""
    timestamp: datetime
    level: str = "info"
    message: str
    source: Optional[str] = None


class JobResult(BaseModel):
    """Represents the result of a completed job"""
    request_id: str
    name: Optional[str] = None
    status: str  # completed, failed, error
    exit_code: Optional[int] = None
    logs: List[str] = Field(default_factory=list)
    duration_ms: Optional[int] = None
    script_duration_ms: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    success: bool = False  # True if status is 'completed' and exit_code is 0
    persist: bool = False  # VM is persistent
    ipv6_address: Optional[str] = None  # IPv6 address if ip_lease enabled
    proxy_url: Optional[str] = None  # Public URL via reverse proxy (e.g., https://xxx.app.lfg.run)


class Schedule(BaseModel):
    """Represents a job schedule"""
    id: str
    job_id: str
    cron: str
    enabled: bool = True
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class PersistentVMHandle(BaseModel):
    """Represents a persistent VM created via a job"""

    request_id: str
    vm_id: Optional[str] = None
    agent_id: Optional[str] = None
    ip_address: Optional[str] = None
    proxy_url: Optional[str] = None  # Public URL via reverse proxy (e.g., https://xxx.app.lfg.run)


class SSHCommandResult(BaseModel):
    """Represents the result of executing an SSH command on a persistent VM"""

    request_id: str
    command: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    duration_ms: Optional[int] = None


# Allow forward references
Template.model_rebuild()
