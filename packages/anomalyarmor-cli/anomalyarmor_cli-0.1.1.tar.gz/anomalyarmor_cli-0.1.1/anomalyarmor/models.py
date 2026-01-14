"""Data models for the Armor SDK."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Asset(BaseModel):
    """An asset (table, view, etc.) in AnomalyArmor."""

    id: str = Field(..., description="Public UUID of the asset")
    qualified_name: str = Field(..., description="Fully qualified name")
    name: str = Field(..., description="Display name")
    asset_type: str = Field(default="table", description="Type: table, view, etc.")
    source_type: str | None = Field(None, description="Database type")
    is_active: bool = Field(default=True, description="Whether monitoring is active")
    created_at: datetime | None = Field(None, description="Creation time")
    updated_at: datetime | None = Field(None, description="Last update time")

    # Extended fields (only in detail view)
    database_name: str | None = Field(None, description="Database name")
    schema_name: str | None = Field(None, description="Schema name")
    table_name: str | None = Field(None, description="Table name")
    description: str | None = Field(None, description="Asset description")
    row_count: int | None = Field(None, description="Approximate row count")
    size_bytes: int | None = Field(None, description="Storage size")


class FreshnessStatus(BaseModel):
    """Freshness status for an asset."""

    asset_id: str = Field(..., description="Asset public UUID")
    qualified_name: str = Field(..., description="Asset qualified name")
    status: str = Field(..., description="Status: fresh, stale, unknown, disabled")
    last_update_time: datetime | None = Field(None, description="Last update time")
    staleness_threshold_hours: int | None = Field(None, description="Threshold hours")
    hours_since_update: float | None = Field(None, description="Hours since update")
    is_stale: bool = Field(..., description="Whether asset is stale")
    checked_at: datetime = Field(..., description="Check timestamp")


class FreshnessSummary(BaseModel):
    """Summary of freshness across assets."""

    total_assets: int = Field(..., description="Total monitored assets")
    fresh_count: int = Field(..., description="Fresh assets")
    stale_count: int = Field(..., description="Stale assets")
    unknown_count: int = Field(..., description="Unknown freshness")
    disabled_count: int = Field(..., description="Disabled monitoring")
    freshness_rate: float = Field(..., description="Percentage fresh")


class SchemaChange(BaseModel):
    """A schema change detected on an asset."""

    id: str = Field(..., description="Change ID")
    asset_id: str = Field(..., description="Asset public UUID")
    qualified_name: str = Field(..., description="Asset qualified name")
    change_type: str = Field(..., description="Type of change")
    severity: str = Field(..., description="Severity level")
    column_name: str | None = Field(None, description="Affected column")
    old_value: str | None = Field(None, description="Previous value")
    new_value: str | None = Field(None, description="New value")
    detected_at: datetime = Field(..., description="Detection time")
    acknowledged: bool = Field(default=False, description="Acknowledged status")


class SchemaSummary(BaseModel):
    """Summary of schema changes."""

    total_changes: int = Field(..., description="Total changes")
    unacknowledged: int = Field(..., description="Unacknowledged")
    critical_count: int = Field(..., description="Critical severity")
    warning_count: int = Field(..., description="Warning severity")
    info_count: int = Field(..., description="Info severity")
    last_check: datetime | None = Field(None, description="Last check time")


class LineageNode(BaseModel):
    """A node in the lineage graph."""

    id: str = Field(..., description="Asset public UUID")
    qualified_name: str = Field(..., description="Asset qualified name")
    name: str = Field(..., description="Display name")
    asset_type: str = Field(default="table", description="Asset type")
    source_type: str | None = Field(None, description="Database type")


class LineageEdge(BaseModel):
    """An edge in the lineage graph."""

    source: str = Field(..., description="Source qualified name")
    target: str = Field(..., description="Target qualified name")
    edge_type: str = Field(default="data_flow", description="Relationship type")
    confidence: float = Field(default=1.0, description="Confidence score")


class LineageGraph(BaseModel):
    """Lineage graph for an asset."""

    root: LineageNode = Field(..., description="The queried asset")
    upstream: list[LineageNode] = Field(
        default_factory=list, description="Dependencies"
    )
    downstream: list[LineageNode] = Field(
        default_factory=list, description="Dependents"
    )
    edges: list[LineageEdge] = Field(default_factory=list, description="All edges")


class Alert(BaseModel):
    """An alert instance."""

    id: str = Field(..., description="Alert ID")
    rule_id: str | None = Field(None, description="Rule ID")
    rule_name: str | None = Field(None, description="Rule name")
    asset_id: str | None = Field(None, description="Asset public UUID")
    qualified_name: str | None = Field(None, description="Asset qualified name")
    severity: str = Field(default="info", description="Severity level")
    status: str = Field(default="triggered", description="Alert status")
    message: str = Field(..., description="Alert message")
    triggered_at: datetime = Field(..., description="Trigger time")
    resolved_at: datetime | None = Field(None, description="Resolution time")


class AlertSummary(BaseModel):
    """Summary of alerts."""

    total_rules: int = Field(..., description="Total rules")
    active_rules: int = Field(..., description="Active rules")
    recent_alerts: int = Field(..., description="Recent alerts")
    unresolved_alerts: int = Field(..., description="Unresolved alerts")


class AlertRule(BaseModel):
    """An alert rule configuration."""

    id: str = Field(..., description="Rule public UUID")
    name: str = Field(..., description="Rule name")
    description: str | None = Field(None, description="Description")
    rule_type: str = Field(..., description="Rule type")
    severity: str = Field(default="warning", description="Severity")
    enabled: bool = Field(default=True, description="Is enabled")
    created_at: datetime | None = Field(None, description="Creation time")


class APIKey(BaseModel):
    """An API key."""

    id: str = Field(..., description="Key public UUID")
    name: str = Field(..., description="Key name")
    key_prefix: str = Field(..., description="Key prefix")
    key_suffix: str = Field(..., description="Key suffix")
    display_key: str = Field(..., description="Masked key")
    scope: str = Field(default="read-only", description="Permission scope")
    rate_limit_per_min: int = Field(..., description="Rate limit")
    burst_limit: int = Field(..., description="Burst limit")
    created_at: datetime | None = Field(None, description="Creation time")
    last_used_at: datetime | None = Field(None, description="Last use time")
    revoked_at: datetime | None = Field(None, description="Revocation time")
    is_active: bool = Field(default=True, description="Is active")


class CreatedAPIKey(APIKey):
    """A newly created API key (includes full key)."""

    key: str = Field(..., description="Full API key (shown once)")


# ============================================================================
# TECH-646: Intelligence Q&A Models
# ============================================================================


class IntelligenceSourceInfo(BaseModel):
    """Source information for knowledge base context."""

    asset_id: int = Field(..., description="Internal asset ID")
    asset_name: str = Field(..., description="Asset display name")
    domain: str | None = Field(None, description="Knowledge domain")
    generated_at: str | None = Field(None, description="KB generation timestamp")
    token_count: int = Field(0, description="Token count for this source")
    was_regenerated: bool = Field(False, description="Whether KB was regenerated")


class TokenUsage(BaseModel):
    """Token usage information from LLM call."""

    tokens_in: int = Field(0, description="Input tokens")
    tokens_out: int = Field(0, description="Output tokens")
    tokens_total: int = Field(0, description="Total tokens")
    cost_usd: float = Field(0.0, description="Estimated cost in USD")


class IntelligenceAnswer(BaseModel):
    """Response from intelligence Q&A."""

    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer")
    confidence: str = Field(default="medium", description="Confidence level")
    sources: list[IntelligenceSourceInfo] = Field(
        default_factory=list, description="Source knowledge bases used"
    )
    token_usage: TokenUsage = Field(
        default_factory=lambda: TokenUsage(
            tokens_in=0, tokens_out=0, tokens_total=0, cost_usd=0.0
        ),
        description="Token usage breakdown",
    )


class IntelligenceGenerateResult(BaseModel):
    """Result of triggering intelligence generation."""

    job_id: str = Field(..., description="Job ID for tracking progress")
    asset_id: str = Field(..., description="Asset public UUID")
    status: str = Field(default="started", description="Job status")
    message: str = Field(
        default="Intelligence generation started",
        description="Status message",
    )


# ============================================================================
# TECH-646: Tags Models
# ============================================================================


class Tag(BaseModel):
    """A tag applied to an asset."""

    id: str = Field(..., description="Tag public UUID")
    name: str = Field(..., description="Tag name")
    category: str = Field(default="business", description="Tag category")
    description: str | None = Field(None, description="Tag description")
    object_path: str | None = Field(None, description="Object path")
    object_type: str | None = Field(None, description="Object type")
    created_at: datetime | None = Field(None, description="Creation time")


class BulkApplyResult(BaseModel):
    """Result of bulk tag apply operation."""

    applied: int = Field(..., description="Number of tags applied")
    failed: int = Field(default=0, description="Number of failures")
    total: int = Field(..., description="Total operations attempted")


# ============================================================================
# TECH-646: Badges Models
# ============================================================================


class Badge(BaseModel):
    """A report badge for data observability."""

    id: str = Field(..., description="Badge public UUID")
    label: str = Field(..., description="Badge label")
    asset_id: str | None = Field(None, description="Associated asset ID")
    tag_filters: list[str] = Field(default_factory=list, description="Tag filters")
    schema_drift_enabled: bool = Field(default=True, description="Monitor schema drift")
    freshness_enabled: bool = Field(default=True, description="Monitor freshness")
    include_upstream: bool = Field(default=False, description="Include upstream deps")
    is_active: bool = Field(default=True, description="Whether badge is active")
    badge_url: str | None = Field(None, description="Public badge URL")
    created_at: datetime | None = Field(None, description="Creation time")
    updated_at: datetime | None = Field(None, description="Last update time")


# ============================================================================
# TECH-646: Alert Destination Models
# ============================================================================


class AlertDestination(BaseModel):
    """An alert destination (Slack, email, webhook, etc.)."""

    id: str = Field(..., description="Destination public UUID")
    name: str = Field(..., description="Destination name")
    destination_type: str = Field(..., description="Type: email, slack, webhook, etc.")
    is_active: bool = Field(default=True, description="Is active")
    is_verified: bool = Field(default=False, description="Is verified")
    created_at: datetime | None = Field(None, description="Creation time")
