"""Tests for promptops.approval module."""

import pytest
from unittest.mock import Mock

from promptops.approval import (
    ApprovalManager,
    ApprovalStatus,
    enforce_approval,
)
from promptops.exceptions import ApprovalRequired


class TestApprovalStatus:
    """Tests for ApprovalStatus enum."""

    def test_status_values(self):
        """Test that all status values exist."""
        assert ApprovalStatus.PENDING
        assert ApprovalStatus.APPROVED
        assert ApprovalStatus.REJECTED


class TestApprovalManager:
    """Tests for ApprovalManager class."""

    @pytest.fixture
    def manager(self):
        """Create a fresh ApprovalManager for each test."""
        return ApprovalManager()

    def test_request_approval(self, manager):
        """Test requesting approval for an item."""
        manager.request_approval("item-1", "user@example.com")
        assert manager.status("item-1") == ApprovalStatus.PENDING

    def test_request_approval_with_context(self, manager):
        """Test requesting approval with context."""
        context = {"reason": "Production deployment"}
        manager.request_approval("item-1", "user@example.com", context=context)
        assert manager.status("item-1") == ApprovalStatus.PENDING

    def test_duplicate_request_ignored(self, manager):
        """Test that duplicate requests are ignored."""
        manager.request_approval("item-1", "user1@example.com")
        manager.request_approval("item-1", "user2@example.com")
        # Should still be pending, not create a new request
        assert manager.status("item-1") == ApprovalStatus.PENDING

    def test_approve_item(self, manager):
        """Test approving an item."""
        manager.request_approval("item-1", "requester@example.com")
        manager.approve("item-1", "approver@example.com", "Looks good")
        assert manager.status("item-1") == ApprovalStatus.APPROVED

    def test_reject_item(self, manager):
        """Test rejecting an item."""
        manager.request_approval("item-1", "requester@example.com")
        manager.reject("item-1", "approver@example.com", "Not ready")
        assert manager.status("item-1") == ApprovalStatus.REJECTED

    def test_status_unknown_item(self, manager):
        """Test status for unknown item returns PENDING."""
        assert manager.status("unknown-item") == ApprovalStatus.PENDING

    def test_enforce_in_dev_env(self, manager):
        """Test enforce does not raise in dev environment."""
        # Should not raise even without approval
        manager.enforce("item-1", env="dev")

    def test_enforce_in_prod_without_approval(self, manager):
        """Test enforce raises in prod without approval."""
        manager.request_approval("item-1", "user@example.com")
        with pytest.raises(ApprovalRequired):
            manager.enforce("item-1", env="prod")

    def test_enforce_in_prod_with_approval(self, manager):
        """Test enforce passes in prod with approval."""
        manager.request_approval("item-1", "user@example.com")
        manager.approve("item-1", "approver@example.com")
        # Should not raise
        manager.enforce("item-1", env="prod")

    def test_callback_on_request(self, manager):
        """Test callback is called when approval is requested."""
        callback = Mock()
        manager.add_callback(callback)
        manager.request_approval("item-1", "user@example.com")
        callback.assert_called_once_with("item-1", ApprovalStatus.PENDING, None)

    def test_callback_on_approve(self, manager):
        """Test callback is called when item is approved."""
        callback = Mock()
        manager.add_callback(callback)
        manager.request_approval("item-1", "user@example.com")
        callback.reset_mock()
        manager.approve("item-1", "approver@example.com", "Approved!")
        callback.assert_called_once_with("item-1", ApprovalStatus.APPROVED, "Approved!")

    def test_callback_on_reject(self, manager):
        """Test callback is called when item is rejected."""
        callback = Mock()
        manager.add_callback(callback)
        manager.request_approval("item-1", "user@example.com")
        callback.reset_mock()
        manager.reject("item-1", "approver@example.com", "Rejected!")
        callback.assert_called_once_with("item-1", ApprovalStatus.REJECTED, "Rejected!")

    def test_callback_exception_handled(self, manager):
        """Test that callback exceptions are handled gracefully."""
        def bad_callback(item_id, status, reason):
            raise RuntimeError("Callback error")
        
        manager.add_callback(bad_callback)
        # Should not raise despite callback error
        manager.request_approval("item-1", "user@example.com")


class TestEnforceApproval:
    """Tests for enforce_approval legacy function."""

    def test_approved_config(self):
        """Test approved config does not raise."""
        config = {"approved": True}
        # Should not raise
        enforce_approval(config, "prod")

    def test_unapproved_config_in_prod(self):
        """Test unapproved config raises in prod."""
        config = {"approved": False}
        with pytest.raises(ApprovalRequired):
            enforce_approval(config, "prod")

    def test_unapproved_config_in_dev(self):
        """Test unapproved config does not raise in dev."""
        config = {"approved": False}
        # Should not raise in dev
        enforce_approval(config, "dev")

    def test_missing_approved_key_in_prod(self):
        """Test missing approved key raises in prod."""
        config = {}
        with pytest.raises(ApprovalRequired):
            enforce_approval(config, "prod")
