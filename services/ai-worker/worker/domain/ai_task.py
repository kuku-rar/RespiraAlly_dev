"""
AI Task Domain Model

Pure Python data class representing AI processing tasks.
Contains business logic for task validation, processing workflow, and result handling.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
import hashlib
import json


class TaskType(Enum):
    TEXT_ONLY = "text_only"
    AUDIO_STT_LLM_TTS = "audio_stt_llm_tts"
    AUDIO_STT_LLM = "audio_stt_llm"
    LLM_TTS = "llm_tts"


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingStep(Enum):
    STT = "stt"  # Speech to Text
    LLM = "llm"  # Language Model Processing
    TTS = "tts"  # Text to Speech
    NOTIFICATION = "notification"


@dataclass
class TaskResult:
    """Individual step result within a task"""
    step: ProcessingStep
    status: TaskStatus
    output: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def mark_started(self) -> None:
        """Mark step as started"""
        self.started_at = datetime.utcnow()
        self.status = TaskStatus.PROCESSING

    def mark_completed(self, output: str, metadata: Dict[str, Any] = None) -> None:
        """Mark step as completed with output"""
        self.completed_at = datetime.utcnow()
        self.status = TaskStatus.COMPLETED
        self.output = output
        if metadata:
            self.metadata.update(metadata)

        if self.started_at:
            self.processing_time_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)

    def mark_failed(self, error_message: str) -> None:
        """Mark step as failed with error"""
        self.completed_at = datetime.utcnow()
        self.status = TaskStatus.FAILED
        self.error_message = error_message

        if self.started_at:
            self.processing_time_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "step": self.step.value,
            "status": self.status.value,
            "output": self.output,
            "metadata": self.metadata,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class AITask:
    """AI processing task domain object"""
    task_id: str
    patient_id: str
    task_type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    input_text: Optional[str] = None
    audio_bucket: Optional[str] = None
    audio_object: Optional[str] = None
    audio_duration_ms: Optional[int] = None
    line_user_id: Optional[str] = None
    processing_steps: List[TaskResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    task_metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create_text_task(cls, patient_id: str, input_text: str, line_user_id: Optional[str] = None) -> 'AITask':
        """Create a text-only processing task"""
        task_id = cls._generate_task_id(patient_id, input_text)

        task = cls(
            task_id=task_id,
            patient_id=patient_id,
            task_type=TaskType.TEXT_ONLY,
            input_text=input_text,
            line_user_id=line_user_id
        )

        # Add LLM processing step
        task.processing_steps.append(TaskResult(step=ProcessingStep.LLM, status=TaskStatus.PENDING))
        task.processing_steps.append(TaskResult(step=ProcessingStep.NOTIFICATION, status=TaskStatus.PENDING))

        return task

    @classmethod
    def create_audio_task(cls, patient_id: str, audio_bucket: str, audio_object: str,
                         audio_duration_ms: int = None, line_user_id: Optional[str] = None) -> 'AITask':
        """Create a full audio processing task (STT -> LLM -> TTS)"""
        task_id = cls._generate_task_id(patient_id, audio_object)

        task = cls(
            task_id=task_id,
            patient_id=patient_id,
            task_type=TaskType.AUDIO_STT_LLM_TTS,
            audio_bucket=audio_bucket,
            audio_object=audio_object,
            audio_duration_ms=audio_duration_ms,
            line_user_id=line_user_id
        )

        # Add all processing steps
        task.processing_steps.append(TaskResult(step=ProcessingStep.STT, status=TaskStatus.PENDING))
        task.processing_steps.append(TaskResult(step=ProcessingStep.LLM, status=TaskStatus.PENDING))
        task.processing_steps.append(TaskResult(step=ProcessingStep.TTS, status=TaskStatus.PENDING))
        task.processing_steps.append(TaskResult(step=ProcessingStep.NOTIFICATION, status=TaskStatus.PENDING))

        return task

    @staticmethod
    def _generate_task_id(patient_id: str, content: str) -> str:
        """Generate unique task ID"""
        timestamp = datetime.utcnow().isoformat()
        hash_content = f"{patient_id}_{content}_{timestamp}"
        return hashlib.md5(hash_content.encode()).hexdigest()[:16]

    def validate_input(self) -> List[str]:
        """Validate task input data"""
        errors = []

        if not self.patient_id:
            errors.append("patient_id is required")

        if self.task_type == TaskType.TEXT_ONLY:
            if not self.input_text or not self.input_text.strip():
                errors.append("input_text is required for text-only tasks")

        elif self.task_type in [TaskType.AUDIO_STT_LLM_TTS, TaskType.AUDIO_STT_LLM]:
            if not self.audio_bucket:
                errors.append("audio_bucket is required for audio tasks")
            if not self.audio_object:
                errors.append("audio_object is required for audio tasks")

        return errors

    def start_processing(self) -> None:
        """Mark task as started"""
        self.status = TaskStatus.PROCESSING
        self.started_at = datetime.utcnow()

    def get_current_step(self) -> Optional[TaskResult]:
        """Get the current processing step"""
        for step_result in self.processing_steps:
            if step_result.status == TaskStatus.PENDING:
                return step_result
        return None

    def start_step(self, step: ProcessingStep) -> Optional[TaskResult]:
        """Start a specific processing step"""
        for step_result in self.processing_steps:
            if step_result.step == step and step_result.status == TaskStatus.PENDING:
                step_result.mark_started()
                return step_result
        return None

    def complete_step(self, step: ProcessingStep, output: str, metadata: Dict[str, Any] = None) -> bool:
        """Complete a specific processing step"""
        for step_result in self.processing_steps:
            if step_result.step == step and step_result.status == TaskStatus.PROCESSING:
                step_result.mark_completed(output, metadata or {})

                # Update task-level data based on step
                if step == ProcessingStep.STT:
                    self.input_text = output
                elif step == ProcessingStep.LLM:
                    self.task_metadata['ai_response'] = output
                elif step == ProcessingStep.TTS:
                    self.task_metadata['response_audio_url'] = output

                return True
        return False

    def fail_step(self, step: ProcessingStep, error_message: str) -> bool:
        """Mark a specific processing step as failed"""
        for step_result in self.processing_steps:
            if step_result.step == step and step_result.status == TaskStatus.PROCESSING:
                step_result.mark_failed(error_message)
                self.fail_task(error_message)
                return True
        return False

    def complete_task(self) -> None:
        """Mark entire task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def fail_task(self, error_message: str) -> None:
        """Mark entire task as failed"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.task_metadata['error_message'] = error_message

    def is_all_steps_completed(self) -> bool:
        """Check if all processing steps are completed"""
        return all(step.status == TaskStatus.COMPLETED for step in self.processing_steps)

    def has_failed_steps(self) -> bool:
        """Check if any processing step has failed"""
        return any(step.status == TaskStatus.FAILED for step in self.processing_steps)

    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of processing steps"""
        step_summary = {}
        total_processing_time = 0

        for step_result in self.processing_steps:
            step_summary[step_result.step.value] = {
                "status": step_result.status.value,
                "processing_time_ms": step_result.processing_time_ms,
                "error": step_result.error_message
            }
            if step_result.processing_time_ms:
                total_processing_time += step_result.processing_time_ms

        return {
            "steps": step_summary,
            "total_processing_time_ms": total_processing_time,
            "success_rate": len([s for s in self.processing_steps if s.status == TaskStatus.COMPLETED]) / len(self.processing_steps)
        }

    def create_notification_payload(self) -> Dict[str, Any]:
        """Create notification payload for web-app"""
        base_payload = {
            "task_id": self.task_id,
            "patient_id": self.patient_id,
            "status": self.status.value,
            "task_type": self.task_type.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processing_summary": self.get_processing_summary()
        }

        # Add step-specific outputs
        if self.input_text:
            base_payload["user_transcript"] = self.input_text

        if self.task_metadata.get('ai_response'):
            base_payload["ai_response"] = self.task_metadata['ai_response']

        if self.task_metadata.get('response_audio_url'):
            base_payload["response_audio_url"] = self.task_metadata['response_audio_url']

        if self.audio_object:
            base_payload["original_file"] = self.audio_object

        if self.task_metadata.get('error_message'):
            base_payload["error_message"] = self.task_metadata['error_message']

        return base_payload

    def estimate_completion_time(self) -> Optional[int]:
        """Estimate remaining completion time in milliseconds"""
        if self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return 0

        # Simple estimation based on task type
        estimates = {
            TaskType.TEXT_ONLY: 2000,  # 2 seconds
            TaskType.AUDIO_STT_LLM_TTS: 8000,  # 8 seconds
            TaskType.AUDIO_STT_LLM: 5000,  # 5 seconds
        }

        base_estimate = estimates.get(self.task_type, 5000)

        # Adjust based on audio duration if available
        if self.audio_duration_ms and self.task_type in [TaskType.AUDIO_STT_LLM_TTS, TaskType.AUDIO_STT_LLM]:
            # Longer audio takes more time to process
            audio_factor = min(self.audio_duration_ms / 60000, 3.0)  # Cap at 3x for very long audio
            base_estimate = int(base_estimate * audio_factor)

        return base_estimate

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "task_id": self.task_id,
            "patient_id": self.patient_id,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "input_text": self.input_text,
            "audio_bucket": self.audio_bucket,
            "audio_object": self.audio_object,
            "audio_duration_ms": self.audio_duration_ms,
            "line_user_id": self.line_user_id,
            "processing_steps": [step.to_dict() for step in self.processing_steps],
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "task_metadata": self.task_metadata,
            "estimated_completion_time_ms": self.estimate_completion_time()
        }