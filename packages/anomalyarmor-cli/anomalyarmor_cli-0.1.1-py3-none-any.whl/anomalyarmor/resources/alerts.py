"""Alerts resource for the Armor SDK."""

from __future__ import annotations

import builtins
from typing import Any

from anomalyarmor.models import Alert, AlertDestination, AlertRule, AlertSummary
from anomalyarmor.resources.base import BaseResource


class AlertsResource(BaseResource):
    """Resource for interacting with alerts.

    Example:
        >>> from anomalyarmor import Client
        >>> client = Client()
        >>>
        >>> # Get summary
        >>> summary = client.alerts.summary()
        >>> if summary.unresolved_alerts > 0:
        ...     print(f"You have {summary.unresolved_alerts} unresolved alerts")
        >>>
        >>> # List critical alerts
        >>> critical = client.alerts.list(severity="critical")
        >>>
        >>> # List alert rules
        >>> rules = client.alerts.rules()
        >>>
        >>> # Create destination and rule (TECH-646)
        >>> dest = client.alerts.create_destination(
        ...     name="Slack #alerts",
        ...     destination_type="slack",
        ...     config={"webhook_url": "https://..."}
        ... )
        >>> rule = client.alerts.create_rule(
        ...     name="Critical Alerts",
        ...     destination_ids=[dest.id],
        ...     severities=["critical"]
        ... )
    """

    def summary(self) -> AlertSummary:
        """Get a summary of alerts and rules.

        Returns:
            AlertSummary with counts
        """
        response = self._get("/alerts/summary")
        return AlertSummary.model_validate(response.get("data", {}))

    def list(
        self,
        status: str | None = None,
        severity: str | None = None,
        asset_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> builtins.list[Alert]:
        """List alerts with optional filters.

        Args:
            status: Filter by status ("triggered", "acknowledged", "resolved")
            severity: Filter by severity ("info", "warning", "critical")
            asset_id: Filter by asset UUID or qualified name
            limit: Maximum number of results (default 50, max 100)
            offset: Number of results to skip

        Returns:
            List of Alert objects
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if severity:
            params["severity"] = severity
        if asset_id:
            params["asset_id"] = asset_id

        response = self._get("/alerts", params=params)
        data = response.get("data", {}).get("data", [])
        return [Alert.model_validate(item) for item in data]

    def rules(
        self,
        enabled_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> builtins.list[AlertRule]:
        """List alert rules.

        Args:
            enabled_only: Only return enabled rules
            limit: Maximum number of results (default 50, max 100)
            offset: Number of results to skip

        Returns:
            List of AlertRule objects
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if enabled_only:
            params["enabled_only"] = True

        response = self._get("/alerts/rules", params=params)
        data = response.get("data", {}).get("data", [])
        return [AlertRule.model_validate(item) for item in data]

    # =========================================================================
    # TECH-646: Alert Rules CRUD
    # =========================================================================

    def create_rule(
        self,
        name: str,
        destination_ids: builtins.list[str],
        description: str | None = None,
        is_active: bool = True,
        event_types: builtins.list[str] | None = None,
        severities: builtins.list[str] | None = None,
        tag_filter_mode: str | None = None,
        tag_filter_tags: builtins.list[str] | None = None,
    ) -> AlertRule:
        """Create a new alert rule.

        Args:
            name: Rule name
            destination_ids: List of destination UUIDs to send alerts to
            description: Optional rule description
            is_active: Whether the rule is active (default True)
            event_types: Event types to alert on (e.g., ["freshness_alert", "schema_drift"])
            severities: Severity levels to alert on (e.g., ["critical", "warning"])
            tag_filter_mode: Tag filter mode ("any" or "all")
            tag_filter_tags: List of tags to filter by

        Returns:
            Created AlertRule object

        Example:
            >>> rule = client.alerts.create_rule(
            ...     name="Critical Freshness Alerts",
            ...     destination_ids=["dest-uuid-1"],
            ...     event_types=["freshness_alert"],
            ...     severities=["critical"]
            ... )
            >>> print(f"Created rule: {rule.id}")
        """
        payload = {
            "name": name,
            "destination_ids": destination_ids,
            "is_active": is_active,
        }
        if description:
            payload["description"] = description
        if event_types:
            payload["event_types"] = event_types
        if severities:
            payload["severities"] = severities
        if tag_filter_mode:
            payload["tag_filter_mode"] = tag_filter_mode
        if tag_filter_tags:
            payload["tag_filter_tags"] = tag_filter_tags

        response = self._post("/alerts/rules", json=payload)
        return AlertRule.model_validate(response.get("data", {}))

    def get_rule(self, rule_id: str) -> AlertRule:
        """Get a specific alert rule by ID.

        Args:
            rule_id: Rule public UUID

        Returns:
            AlertRule object

        Example:
            >>> rule = client.alerts.get_rule("rule-uuid")
            >>> print(f"Rule: {rule.name}, Active: {rule.is_active}")
        """
        response = self._get(f"/alerts/rules/{rule_id}")
        return AlertRule.model_validate(response.get("data", {}))

    def delete_rule(self, rule_id: str) -> bool:
        """Delete an alert rule.

        Args:
            rule_id: Rule public UUID

        Returns:
            True if deleted successfully

        Example:
            >>> client.alerts.delete_rule("rule-uuid")
        """
        self._delete(f"/alerts/rules/{rule_id}")
        return True

    # =========================================================================
    # TECH-646: Alert Destinations CRUD
    # =========================================================================

    def list_destinations(
        self,
        active_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> builtins.list[AlertDestination]:
        """List alert destinations.

        Args:
            active_only: Only return active destinations
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of AlertDestination objects

        Example:
            >>> destinations = client.alerts.list_destinations()
            >>> for dest in destinations:
            ...     print(f"{dest.name} ({dest.destination_type})")
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if active_only:
            params["active_only"] = True

        response = self._get("/alerts/destinations", params=params)
        data = response.get("data", {}).get("destinations", [])
        return [AlertDestination.model_validate(item) for item in data]

    def create_destination(
        self,
        name: str,
        destination_type: str,
        config: dict[str, Any],
    ) -> AlertDestination:
        """Create a new alert destination.

        Args:
            name: Destination name
            destination_type: Type: email, slack, webhook, teams, pagerduty
            config: Configuration dict (varies by type)
                - email: {"email": "user@example.com"} or {"recipients": ["email1", "email2"]}
                - slack: {"webhook_url": "https://hooks.slack.com/..."}
                - webhook: {"url": "https://...", "headers": {...}}
                - teams: {"webhook_url": "https://..."}
                - pagerduty: {"api_token": "...", "routing_key": "..."}

        Returns:
            Created AlertDestination

        Example:
            >>> dest = client.alerts.create_destination(
            ...     name="Slack #alerts",
            ...     destination_type="slack",
            ...     config={"webhook_url": "https://hooks.slack.com/..."}
            ... )
            >>> print(f"Created: {dest.id}")
        """
        payload = {
            "name": name,
            "destination_type": destination_type,
            "config": config,
        }
        response = self._post("/alerts/destinations", json=payload)
        return AlertDestination.model_validate(response.get("data", {}))

    def get_destination(self, destination_id: str) -> AlertDestination:
        """Get a specific alert destination by ID.

        Args:
            destination_id: Destination public UUID

        Returns:
            AlertDestination object

        Example:
            >>> dest = client.alerts.get_destination("dest-uuid")
            >>> print(f"{dest.name}: {dest.destination_type}")
        """
        response = self._get(f"/alerts/destinations/{destination_id}")
        return AlertDestination.model_validate(response.get("data", {}))

    def delete_destination(self, destination_id: str) -> bool:
        """Delete an alert destination.

        Args:
            destination_id: Destination public UUID

        Returns:
            True if deleted successfully

        Example:
            >>> client.alerts.delete_destination("dest-uuid")
        """
        self._delete(f"/alerts/destinations/{destination_id}")
        return True
