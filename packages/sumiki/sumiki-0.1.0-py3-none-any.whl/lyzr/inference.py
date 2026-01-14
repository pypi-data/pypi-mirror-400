"""
Inference module for agent execution
"""

from typing import Optional, Dict, Any, Iterator
from lyzr.base import BaseModule
from lyzr.responses import AgentResponse, AgentStream, TaskResponse, TaskStatus


class InferenceModule(BaseModule):
    """
    Module for managing agent inference/execution

    Handles all /v3/inference/* endpoints for running agents.
    Used internally by Agent.run() method.

    Example (Standalone):
        >>> from lyzr.http import HTTPClient
        >>> from lyzr.inference import InferenceModule
        >>> http = HTTPClient(api_key="sk-xxx")
        >>> inference = InferenceModule(http)
        >>> response = inference.chat("agent_id", "Hello", "session_123")

    Example (Through Agent):
        >>> agent = studio.get_agent("agent_id")
        >>> response = agent.run("Hello")  # Uses InferenceModule internally
    """

    def chat(
        self,
        agent_id: str,
        message: str,
        session_id: str,
        user_id: str = "default_user",
        **kwargs
    ) -> AgentResponse:
        """
        Synchronous chat with agent

        Args:
            agent_id: Agent ID to run
            message: User message
            session_id: Session ID for conversation
            user_id: User ID (default: "default_user")
            **kwargs: Additional parameters (system_prompt_variables, features, etc.)

        Returns:
            AgentResponse: Response object with agent's reply

        Raises:
            APIError: If API request fails
            ValidationError: If parameters are invalid

        Example:
            >>> response = inference.chat(
            ...     agent_id="agent_123",
            ...     message="What's the weather?",
            ...     session_id="sess_123"
            ... )
            >>> print(response.response)
        """
        payload = {
            "agent_id": agent_id,
            "session_id": session_id,
            "message": message,
            "user_id": user_id,
        }

        # Add optional parameters
        if kwargs:
            payload.update(kwargs)

        response = self._http.post("/v3/inference/chat/", json=payload)

        # Parse response into AgentResponse
        return AgentResponse(
            response=response.get("response", ""),
            session_id=session_id,
            message_id=response.get("message_id"),
            metadata=response.get("metadata"),
            tool_calls=response.get("tool_calls"),
            raw_response=response
        )

    def stream(
        self,
        agent_id: str,
        message: str,
        session_id: str,
        user_id: str = "default_user",
        **kwargs
    ) -> Iterator[AgentStream]:
        """
        Stream chat with agent

        Args:
            agent_id: Agent ID to run
            message: User message
            session_id: Session ID for conversation
            user_id: User ID (default: "default_user")
            **kwargs: Additional parameters

        Yields:
            AgentStream: Stream chunks as they arrive

        Raises:
            APIError: If API request fails

        Example:
            >>> for chunk in inference.stream("agent_123", "Tell a story", "sess_123"):
            ...     print(chunk.content, end="")
        """
        payload = {
            "agent_id": agent_id,
            "session_id": session_id,
            "message": message,
            "user_id": user_id,
        }

        if kwargs:
            payload.update(kwargs)

        # TODO: Implement actual streaming with Server-Sent Events (SSE)
        # For now, this is a placeholder that needs proper SSE handling

        try:
            import httpx

            url = self._http._build_url("/v3/inference/stream/")

            with httpx.stream(
                "POST",
                url,
                json=payload,
                headers=self._http._get_headers(),
                timeout=self._http.timeout
            ) as response:

                if response.status_code >= 400:
                    self._http._handle_error(response)

                chunk_index = 0
                full_content = []

                for line in response.iter_lines():
                    if not line or not line.strip():
                        continue

                    # Parse SSE data
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix

                        if data_str == "[DONE]":
                            # Final chunk
                            yield AgentStream(
                                content="",
                                done=True,
                                session_id=session_id,
                                chunk_index=chunk_index
                            )
                            break

                        try:
                            import json
                            data = json.loads(data_str)
                            content = data.get("content", "")
                            delta = data.get("delta", content)

                            full_content.append(content)

                            yield AgentStream(
                                content=content,
                                delta=delta,
                                done=False,
                                session_id=session_id,
                                metadata=data.get("metadata"),
                                chunk_index=chunk_index
                            )

                            chunk_index += 1

                        except json.JSONDecodeError:
                            # Skip invalid JSON
                            continue

        except Exception as e:
            # Fallback: use non-streaming endpoint
            response = self.chat(agent_id, message, session_id, user_id, **kwargs)
            yield AgentStream(
                content=response.response,
                done=True,
                session_id=session_id,
                chunk_index=0
            )

    def task(
        self,
        agent_id: str,
        message: str,
        session_id: str,
        user_id: str = "default_user",
        **kwargs
    ) -> TaskResponse:
        """
        Create a long-running task

        Args:
            agent_id: Agent ID to run
            message: User message
            session_id: Session ID for conversation
            user_id: User ID (default: "default_user")
            **kwargs: Additional parameters

        Returns:
            TaskResponse: Response with task_id for polling

        Raises:
            APIError: If API request fails

        Example:
            >>> task = inference.task("agent_123", "Analyze this data", "sess_123")
            >>> print(f"Task created: {task.task_id}")
            >>> # Poll for status
            >>> status = inference.get_task_status(task.task_id)
        """
        payload = {
            "agent_id": agent_id,
            "session_id": session_id,
            "message": message,
            "user_id": user_id,
        }

        if kwargs:
            payload.update(kwargs)

        response = self._http.post("/v3/inference/task/", json=payload)

        return TaskResponse(
            task_id=response.get("task_id", ""),
            status=response.get("status", "pending"),
            session_id=session_id,
            created_at=response.get("created_at")
        )

    def get_task_status(self, task_id: str) -> TaskStatus:
        """
        Get status of a long-running task

        Args:
            task_id: Task identifier

        Returns:
            TaskStatus: Current status of the task

        Raises:
            NotFoundError: If task doesn't exist
            APIError: If API request fails

        Example:
            >>> status = inference.get_task_status("task_abc123")
            >>> if status.is_complete():
            ...     print(status.result.response)
        """
        response = self._http.get(f"/v3/inference/task/{task_id}")

        # Parse result if completed
        result = None
        if response.get("status") == "completed" and "result" in response:
            result_data = response["result"]
            result = AgentResponse(
                response=result_data.get("response", ""),
                session_id=result_data.get("session_id", ""),
                message_id=result_data.get("message_id"),
                metadata=result_data.get("metadata"),
                tool_calls=result_data.get("tool_calls")
            )

        return TaskStatus(
            task_id=task_id,
            status=response.get("status", "unknown"),
            result=result,
            error=response.get("error"),
            progress=response.get("progress"),
            metadata=response.get("metadata")
        )

    def wait_for_task(
        self,
        task_id: str,
        poll_interval: float = 2.0,
        timeout: Optional[float] = None
    ) -> TaskStatus:
        """
        Wait for a task to complete (convenience method)

        Args:
            task_id: Task identifier
            poll_interval: Seconds between status checks (default: 2.0)
            timeout: Maximum seconds to wait (default: None = wait forever)

        Returns:
            TaskStatus: Final status when complete

        Raises:
            TimeoutError: If timeout is reached
            APIError: If API request fails

        Example:
            >>> task = inference.task("agent_123", "Long task", "sess_123")
            >>> status = inference.wait_for_task(task.task_id, timeout=60)
            >>> print(status.result.response)
        """
        import time
        start_time = time.time()

        while True:
            status = self.get_task_status(task_id)

            if status.is_complete():
                return status

            if timeout and (time.time() - start_time) > timeout:
                from lyzr.exceptions import TimeoutError
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")

            time.sleep(poll_interval)
