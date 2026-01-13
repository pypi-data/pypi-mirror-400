"""Enforce naming convention.

Revision ID: 2461610e9698
Revises: b85c3e601de4
Create Date: 2023-11-28 17:29:58.140440

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "2461610e9698"
down_revision = "b85c3e601de4"
branch_labels = None
depends_on = None

constraints = [
    (
        "workflow",
        "workflow_pkey",
        "pk_workflow",
    ),
    (
        "workflow",
        "_user_workflow_run_uc",
        "uq_workflow_name",
    ),
    (
        "workflow",
        "workflow_owner_id_fkey",
        "fk_workflow_owner_id_user_",
    ),
    (
        "user_",
        "user__pkey",
        "pk_user_",
    ),
    (
        "user_",
        "user__id__key",
        "uq_user__id_",
    ),
    (
        "user_",
        "user__email_key",
        "uq_user__email",
    ),
    (
        "user_token",
        "user_token_pkey",
        "pk_user_token",
    ),
    (
        "user_token",
        "user_token_token_key",
        "uq_user_token_token",
    ),
    (
        "user_token",
        "user_token_user_id_fkey",
        "fk_user_token_user_id_user_",
    ),
    (
        "interactive_session",
        "interactive_session_pkey",
        "pk_interactive_session",
    ),
    (
        "interactive_session",
        "_interactive_session_uc",
        "uq_interactive_session_name",
    ),
    (
        "interactive_session",
        "interactive_session_owner_id_fkey",
        "fk_interactive_session_owner_id_user_",
    ),
    (
        "job",
        "job_pkey",
        "pk_job",
    ),
    (
        "job_cache",
        "job_cache_pkey",
        "pk_job_cache",
    ),
    (
        "job_cache",
        "job_cache_job_id_fkey",
        "fk_job_cache_job_id_job",
    ),
    (
        "audit_log",
        "audit_log_pkey",
        "pk_audit_log",
    ),
    (
        "audit_log",
        "audit_log_user_id_fkey",
        "fk_audit_log_user_id_user_",
    ),
    (
        "user_resource",
        "user_resource_pkey",
        "pk_user_resource",
    ),
    (
        "user_resource",
        "user_resource_resource_id_fkey",
        "fk_user_resource_resource_id_resource",
    ),
    (
        "user_resource",
        "user_resource_user_id_fkey",
        "fk_user_resource_user_id_user_",
    ),
    (
        "resource",
        "resource_pkey",
        "pk_resource",
    ),
    (
        "resource",
        "resource_name_key",
        "uq_resource_name",
    ),
    (
        "workflow_session",
        "workflow_session_pkey",
        "pk_workflow_session",
    ),
    (
        "workflow_session",
        "workflow_session_session_id_fkey",
        "fk_workflow_session_session_id_interactive_session",
    ),
    (
        "workflow_session",
        "workflow_session_workflow_id_fkey",
        "fk_workflow_session_workflow_id_workflow",
    ),
    (
        "workspace_retention_rule",
        "workspace_retention_rule_pkey",
        "pk_workspace_retention_rule",
    ),
    (
        "workspace_retention_rule",
        "_workspace_retention_rule_uc",
        "uq_workspace_retention_rule_workflow_id",
    ),
    (
        "workspace_retention_rule",
        "workspace_retention_rule_workflow_id_fkey",
        "fk_workspace_retention_rule_workflow_id_workflow",
    ),
    (
        "workflow_resource",
        "workflow_resource_pkey",
        "pk_workflow_resource",
    ),
    (
        "workflow_resource",
        "workflow_resource_resource_id_fkey",
        "fk_workflow_resource_resource_id_resource",
    ),
    (
        "workflow_resource",
        "workflow_resource_workflow_id_fkey",
        "fk_workflow_resource_workflow_id_workflow",
    ),
    (
        "interactive_session_resource",
        "interactive_session_resource_pkey",
        "pk_interactive_session_resource",
    ),
    (
        "interactive_session_resource",
        "interactive_session_resource_resource_id_fkey",
        "fk_interactive_session_resource_resource_id_resource",
    ),
    (
        "interactive_session_resource",
        "interactive_session_resource_session_id_fkey",
        "fk_interactive_session_resource_session_id_interactive_session",
    ),
    (
        "workspace_retention_audit_log",
        "workspace_retention_audit_log_pkey",
        "pk_workspace_retention_audit_log",
    ),
    (
        "workspace_retention_audit_log",
        "workspace_retention_audit_log_workspace_retention_rule_id_fkey",
        "fk_workspace_retention_audit_log_workspace_retention_ru_7253",
    ),
]


def upgrade():
    """Upgrade to 2461610e9698."""
    for table, prev_name, new_name in constraints:
        op.execute(
            f"ALTER TABLE __reana.{table} RENAME CONSTRAINT {prev_name} TO {new_name}"
        )


def downgrade():
    """Downgrade to b85c3e601de4."""
    for table, prev_name, new_name in constraints:
        op.execute(
            f"ALTER TABLE __reana.{table} RENAME CONSTRAINT {new_name} TO {prev_name}"
        )
