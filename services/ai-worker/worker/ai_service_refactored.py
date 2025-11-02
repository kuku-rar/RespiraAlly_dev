"""
Refactored AI Service

This service uses pure domain objects instead of raw dictionaries and procedural code.
It demonstrates the same refactoring principles applied to the ai-worker service.

Business logic has been moved into the domain objects themselves,
while this service orchestrates the AI pipeline workflow.
"""

import json
from typing import Dict, Any, Optional
from domain.ai_task import AITask, ProcessingStep, TaskStatus
from domain.chat_session import ChatSession, MessageType
from mappers.task_mapper import TaskMapper
from mappers.chat_mapper import ChatMapper
from llm_app.llm_service import LLMService
from stt_app.stt_service import STTService
from tts_app.tts_service import TTSService


class AIServiceRefactored:
    """
    Refactored AI Service using domain objects

    This service coordinates the AI pipeline (STT -> LLM -> TTS) but delegates
    business logic to domain objects and maintains clean separation of concerns.
    """

    def __init__(self):
        self.llm_service = LLMService()
        self.stt_service = STTService()
        self.tts_service = TTSService()

    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an AI task using domain-driven workflow

        This method demonstrates how domain objects encapsulate business logic
        while the service orchestrates the workflow.
        """
        # 1. Convert raw task data to domain object
        ai_task = TaskMapper.rabbitmq_to_domain(task_data)

        # 2. Validate task using domain logic
        validation_errors = ai_task.validate_input()
        if validation_errors:
            ai_task.fail_task(f"Validation failed: {'; '.join(validation_errors)}")
            return TaskMapper.domain_to_notification(ai_task)

        # 3. Start processing
        ai_task.start_processing()

        try:
            # 4. Execute processing pipeline based on task type
            if ai_task.task_type.value.startswith('audio'):
                self._process_audio_pipeline(ai_task)
            else:
                self._process_text_pipeline(ai_task)

            # 5. Mark task as completed if all steps succeeded
            if ai_task.is_all_steps_completed():
                ai_task.complete_task()
            elif ai_task.has_failed_steps():
                ai_task.fail_task("One or more processing steps failed")

        except Exception as e:
            ai_task.fail_task(f"Unexpected error: {str(e)}")

        # 6. Return notification payload
        return TaskMapper.domain_to_notification(ai_task)

    def _process_audio_pipeline(self, ai_task: AITask) -> None:
        """Process audio task pipeline: STT -> LLM -> TTS -> Notification"""

        # Step 1: Speech to Text
        stt_step = ai_task.start_step(ProcessingStep.STT)
        if stt_step:
            try:
                transcript = self.stt_service.transcribe_audio(
                    ai_task.audio_bucket, ai_task.audio_object
                )
                if not transcript:
                    ai_task.fail_step(ProcessingStep.STT, "STT service returned empty transcript")
                    return

                ai_task.complete_step(ProcessingStep.STT, transcript)

            except Exception as e:
                ai_task.fail_step(ProcessingStep.STT, f"STT processing failed: {str(e)}")
                return

        # Step 2: LLM Processing
        self._process_llm_step(ai_task)

        # Step 3: Text to Speech (if LLM succeeded)
        if ai_task.task_metadata.get('ai_response'):
            self._process_tts_step(ai_task)

    def _process_text_pipeline(self, ai_task: AITask) -> None:
        """Process text-only task pipeline: LLM -> Notification"""
        self._process_llm_step(ai_task)

    def _process_llm_step(self, ai_task: AITask) -> None:
        """Process LLM step using domain task data"""
        llm_step = ai_task.start_step(ProcessingStep.LLM)
        if not llm_step:
            return

        try:
            # Convert domain task to LLM service format
            llm_task_data = self._convert_to_llm_format(ai_task)

            # Generate AI response
            ai_response = self.llm_service.generate_response(llm_task_data)
            if not ai_response:
                ai_task.fail_step(ProcessingStep.LLM, "LLM service returned empty response")
                return

            # Store response with metadata
            llm_metadata = {
                "input_length": len(ai_task.input_text or ""),
                "output_length": len(ai_response),
                "model_used": "health_bot"  # Could be extracted from LLM service
            }

            ai_task.complete_step(ProcessingStep.LLM, ai_response, llm_metadata)

        except Exception as e:
            ai_task.fail_step(ProcessingStep.LLM, f"LLM processing failed: {str(e)}")

    def _process_tts_step(self, ai_task: AITask) -> None:
        """Process TTS step using AI response from task"""
        tts_step = ai_task.start_step(ProcessingStep.TTS)
        if not tts_step:
            return

        try:
            ai_response = ai_task.task_metadata.get('ai_response')
            if not ai_response:
                ai_task.fail_step(ProcessingStep.TTS, "No AI response available for TTS")
                return

            # Synthesize speech
            audio_url, duration_ms = self.tts_service.synthesize_text(ai_response)
            if not audio_url:
                ai_task.fail_step(ProcessingStep.TTS, "TTS service returned empty audio URL")
                return

            # Store TTS result with metadata
            tts_metadata = {
                "audio_duration_ms": duration_ms,
                "text_length": len(ai_response)
            }

            ai_task.complete_step(ProcessingStep.TTS, audio_url, tts_metadata)

        except Exception as e:
            ai_task.fail_step(ProcessingStep.TTS, f"TTS processing failed: {str(e)}")

    def _convert_to_llm_format(self, ai_task: AITask) -> Dict[str, Any]:
        """Convert domain AITask to LLM service format"""
        llm_data = {
            "patient_id": ai_task.patient_id,
            "text": ai_task.input_text
        }

        if ai_task.line_user_id:
            llm_data["line_user_id"] = ai_task.line_user_id

        if ai_task.audio_object:
            llm_data["object_name"] = ai_task.audio_object

        return llm_data

    def finalize_user_session(self, user_id: str) -> None:
        """
        Finalize a user's chat session using domain logic

        This demonstrates how session management is delegated to domain objects
        """
        try:
            # Create or load chat session
            session = ChatSession.create_new_session(user_id)

            # Check if session should be finalized using domain logic
            if session.should_finalize():
                session.finalize_session()

                # Delegate actual cleanup to existing service
                self.llm_service.finalize_user_session_now(user_id)

                print(f"✅ Session finalized for user {user_id}")
            else:
                print(f"ℹ️ Session for user {user_id} is not ready for finalization")

        except Exception as e:
            print(f"⚠️ Error finalizing session for user {user_id}: {e}")

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task status (placeholder for future implementation)

        In a full implementation, this would load the task from a repository
        """
        # TODO: Implement task persistence and retrieval
        # For now, return None to indicate task not found
        return None

    def get_user_session_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Get user session metrics using domain logic

        This demonstrates how analytics can be calculated by domain objects
        """
        try:
            # In a full implementation, this would load from a repository
            session = ChatSession.create_new_session(user_id)

            return {
                "user_id": user_id,
                "session_metrics": session.calculate_session_metrics(),
                "needs_health_followup": session.needs_health_followup(),
                "is_idle": session.is_idle(),
                "should_finalize": session.should_finalize()
            }

        except Exception as e:
            return {
                "user_id": user_id,
                "error": str(e),
                "session_metrics": {}
            }


# Global instance for backward compatibility
ai_service_refactored = AIServiceRefactored()


def process_text_task_refactored(task_data: Dict[str, Any]) -> str:
    """
    Refactored text processing function using domain objects

    This replaces the original process_text_task function
    """
    result = ai_service_refactored.process_task(task_data)

    if result.get('status') == 'completed':
        return result.get('ai_response', 'No response generated')
    else:
        error_msg = result.get('error_message', 'Unknown error')
        raise Exception(f"Text processing failed: {error_msg}")


def process_audio_task_refactored(patient_id: str, audio_duration_ms: int, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Refactored audio processing function using domain objects

    This replaces the original process_audio_task function
    """
    # Add missing fields to task_data
    task_data['patient_id'] = patient_id
    if audio_duration_ms:
        task_data['duration_ms'] = audio_duration_ms

    return ai_service_refactored.process_task(task_data)