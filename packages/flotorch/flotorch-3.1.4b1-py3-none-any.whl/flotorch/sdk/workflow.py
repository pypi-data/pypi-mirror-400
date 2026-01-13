import time
from typing import Any, Dict, List, Optional, Union

from flotorch.sdk.utils.http_utils import http_get, http_post
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import ObjectCreation, Error
from flotorch.sdk.utils import session_utils

JSONInput = Union[str, Dict[str, Any], List[Any]]


logger = get_logger()
class FlotorchWorkflow:
    """
    Simple helper to trigger a workflow run and poll its session until final outputs are ready.
    """

    def __init__(self, base_url: str, api_key: str, workflow_name: str) -> None:
        if not base_url or not base_url.strip():
            raise ValueError("Base URL cannot be empty.")
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty.")
        if not workflow_name or not workflow_name.strip():
            raise ValueError("Workflow name cannot be empty.")

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.workflow_name = workflow_name
        self._sink_authors: Optional[List[str]] = None
        self._last_invocation_id: Optional[str] = None

        logger.info(ObjectCreation(
            class_name="FlotorchWorkflow",
            extras={
            "base_url":self.base_url,
            "workflow_name":self.workflow_name
            }
        ))

    def run(self, input_data: JSONInput) -> Dict[str, Any]:
        """
        Trigger the configured workflow with the provided input payload.
        The input can be a string or JSON-serializable object.

        Returns the JSON response from the workflow run endpoint.
        """
        url = f"{self.base_url}/v1/workflows/{self.workflow_name}/run"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            response = http_post(url, headers=headers, json={"input": input_data})
            invocation_id = response.get("invocationId") or response.get("invocationid")
            if invocation_id:
                self._last_invocation_id = invocation_id
            return response
        except Exception as exc:
            logger.error(Error(operation="FlotorchWorkflow.run", error=exc))
            raise

    def get_final_result(
        self,
        invocation_id: Optional[str] = None,
        *,
        interval_sec: float = 2.0,
        timeout_sec: float = 600.0,
        window: int = 200,
    ) -> Dict[str, Any]:
        """
        Poll the workflow session until each sink agent has produced an assistant response.

        Args:
            invocation_id: The session / invocation ID returned by run(). If omitted,
                the last invocation triggered via run() is used.
            interval_sec: Delay between poll attempts.
            timeout_sec: Maximum time to wait before giving up.
            window: Number of recent events to fetch from the session.
        """
        session_id = invocation_id or self._last_invocation_id
        if not session_id:
            raise ValueError(
                "Invocation ID is required. Call run() first or pass invocation_id explicitly."
            )

        try:
            target_authors = self._get_sink_authors()
            if not target_authors:
                raise ValueError("Unable to determine sink agents for the workflow.")

            logger.info(
                f"Polling session {session_id} for final outputs from authors: {target_authors}"
            )
            deadline = time.time() + timeout_sec
            final_events: Dict[str, Optional[Dict[str, Any]]] = {
                author: None for author in target_authors
            }
            last_session_data: Optional[Dict[str, Any]] = None

            while time.time() < deadline:
                session_data = session_utils.get_session(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    uid=session_id,
                    num_recent_events=window,
                )
                last_session_data = session_data
                events = session_data.get("events", []) or []

                for author in target_authors:
                    event = self._latest_assistant_event_by_author(events, author)
                    if event:
                        final_events[author] = event

                if all(final_events.values()):
                    return {
                        "status": "ok",
                        "final_events": final_events,
                        "final_text": {
                            author: self._text_from_event(final_events[author])
                            for author in target_authors
                        },
                        "raw": session_data,
                    }

                time.sleep(interval_sec)

            return {
                "status": "timeout",
                "final_events": final_events,
                "final_text": {
                    author: self._text_from_event(final_events[author])
                    for author in target_authors
                },
                "raw": last_session_data,
            }
        except Exception as exc:
            logger.error(Error(operation="FlotorchWorkflow.get_final_result", error=exc))
            raise

    def _get_sink_authors(self) -> List[str]:
        if self._sink_authors is None:
            config = self._fetch_workflow_config()
            self._sink_authors = self._extract_sink_authors(config)
        return self._sink_authors

    def _fetch_workflow_config(self) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/workflows/{self.workflow_name}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        return http_get(url, headers=headers)

    @staticmethod
    def _extract_sink_authors(workflow_json: Dict[str, Any]) -> List[str]:
        nodes = {
            node.get("id"): node
            for node in workflow_json.get("nodes", [])
            if isinstance(node, dict) and node.get("id")
        }
        edges = [
            edge
            for edge in workflow_json.get("edges", [])
            if isinstance(edge, dict)
        ]

        out_adj: Dict[str, List[str]] = {}
        for edge in edges:
            source = edge.get("sourceNodeId")
            target = edge.get("targetNodeId")
            if source and target:
                out_adj.setdefault(source, []).append(target)

        sink_authors: List[str] = []
        for node_id, node in nodes.items():
            if node.get("type") != "AGENT":
                continue

            outgoing = out_adj.get(node_id, [])
            leads_to_agent = any(
                nodes.get(target, {}).get("type") == "AGENT" for target in outgoing
            )
            if leads_to_agent:
                continue

            callable_name = node.get("callableName", "")
            author = callable_name.split(":")[0].replace("-", "_")
            sink_authors.append(author)

        return sink_authors

    @staticmethod
    def _latest_assistant_event_by_author(
        events: List[Dict[str, Any]],
        author: str,
    ) -> Optional[Dict[str, Any]]:
        matching = [
            event
            for event in events
            if event.get("author") == author
            and (event.get("content") or {}).get("role") == "assistant"
        ]
        if not matching:
            return None

        matching.sort(key=lambda evt: evt.get("timestamp", ""))
        return matching[-1]

    @staticmethod
    def _text_from_event(event: Optional[Dict[str, Any]]) -> Optional[str]:
        if not event:
            return None
        parts = (event.get("content") or {}).get("parts") or []
        if not parts or not isinstance(parts[0], dict):
            return None
        return parts[0].get("text")

