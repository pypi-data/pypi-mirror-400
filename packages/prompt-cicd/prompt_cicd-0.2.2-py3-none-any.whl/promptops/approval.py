import threading
import logging
from enum import Enum, auto
from typing import Callable, Optional, Dict, Any, List
from .exceptions import ApprovalRequired

logger = logging.getLogger("promptops.approval")

class ApprovalStatus(Enum):
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()

class ApprovalManager:
    """
    Manages approval workflow for prompts or actions.
    Supports callbacks, status tracking, and extensible policies.
    """
    def __init__(self):
        self._lock = threading.RLock()
        self._approvals: Dict[str, Dict[str, Any]] = {}
        self._callbacks: List[Callable[[str, ApprovalStatus, Optional[str]], None]] = []

    def request_approval(self, item_id: str, requested_by: str, context: Optional[dict] = None):
        with self._lock:
            if item_id in self._approvals:
                logger.info(f"Approval already requested for {item_id}")
                return
            self._approvals[item_id] = {
                "status": ApprovalStatus.PENDING,
                "requested_by": requested_by,
                "context": context or {},
                "reason": None,
            }
            logger.info(f"Approval requested for {item_id} by {requested_by}")
            self._notify(item_id, ApprovalStatus.PENDING, None)

    def approve(self, item_id: str, approver: str, reason: Optional[str] = None):
        with self._lock:
            self._set_status(item_id, ApprovalStatus.APPROVED, approver, reason)

    def reject(self, item_id: str, approver: str, reason: Optional[str] = None):
        with self._lock:
            self._set_status(item_id, ApprovalStatus.REJECTED, approver, reason)

    def status(self, item_id: str) -> ApprovalStatus:
        with self._lock:
            entry = self._approvals.get(item_id)
            if not entry:
                return ApprovalStatus.PENDING
            return entry["status"]

    def enforce(self, item_id: str, env: str = "prod"):
        with self._lock:
            entry = self._approvals.get(item_id)
            if env == "prod":
                if not entry or entry["status"] != ApprovalStatus.APPROVED:
                    raise ApprovalRequired(f"{item_id} not approved for production")

    def add_callback(self, callback: Callable[[str, ApprovalStatus, Optional[str]], None]):
        """Register a callback for approval status changes."""
        with self._lock:
            self._callbacks.append(callback)

    def _set_status(self, item_id: str, status: ApprovalStatus, approver: str, reason: Optional[str]):
        entry = self._approvals.get(item_id)
        if not entry:
            logger.warning(f"No approval request found for {item_id}")
            return
        entry["status"] = status
        entry["approved_by"] = approver
        entry["reason"] = reason
        logger.info(f"{item_id} set to {status.name} by {approver}. Reason: {reason}")
        self._notify(item_id, status, reason)

    def _notify(self, item_id: str, status: ApprovalStatus, reason: Optional[str]):
        for cb in self._callbacks:
            try:
                cb(item_id, status, reason)
            except Exception as e:
                logger.error(f"Approval callback failed: {e}")


def enforce_approval(config: dict, env: str):
    """
    Legacy function for backward compatibility.
    Raises ApprovalRequired if not approved for production.
    """
    if env == "prod" and not config.get("approved", False):
        raise ApprovalRequired("Prompt not approved for production")
