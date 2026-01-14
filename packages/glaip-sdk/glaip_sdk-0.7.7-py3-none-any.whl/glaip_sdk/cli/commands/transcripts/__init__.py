"""Transcript CLI commands package.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from glaip_sdk.cli.commands.transcripts._common import transcripts_group
from glaip_sdk.cli.commands.transcripts.clear import transcripts_clear
from glaip_sdk.cli.commands.transcripts.detail import transcripts_detail

# Import helper functions from original file for backward compatibility
# NOTE: Transcripts migration is deferred per spec (see resource-command-alignment/spec.md).
# NOTE: Migration is tracked in ../observability/transcript-storage-viewer-services/spec.md (Phase 0).
# This package currently re-exports from transcripts_original.py until the migration is completed.
from glaip_sdk.cli.commands.transcripts_original import (  # noqa: E402, type: ignore
    _abbreviate_path,
    _build_table,
    _build_viewer_context,
    _coerce_timestamp_to_float,
    _collect_targets,
    _confirm_deletion,
    _decode_transcript,
    _emit_warnings,
    _format_duration,
    _format_timestamp,
    _format_timestamp_display,
    _handle_clear_result,
    _launch_transcript_viewer,
    _load_transcript_text,
    _maybe_launch_transcript_viewer,
    _parse_event_received_timestamp,
    _parse_transcript_line,
    _print_snapshot,
    _render_deletion_preview,
    _render_detail_view,
    _render_history_overview,
    _render_transcript_display,
    _resolve_transcript_path,
    _row_label,
    _should_exit_for_targets,
    _should_use_transcript_viewer,
    _transcripts_payload,
    _validate_clear_options,
    console,
    sys,
)

# Import functions from other modules for test compatibility
from glaip_sdk.cli.transcript.history import load_history_snapshot  # noqa: E402
from glaip_sdk.cli.transcript.viewer import run_viewer_session  # noqa: E402
from glaip_sdk.utils.rendering.layout.panels import create_final_panel  # noqa: E402

__all__ = [
    "transcripts_group",
    "transcripts_clear",
    "transcripts_detail",
    "_abbreviate_path",
    "_build_table",
    "_build_viewer_context",
    "_coerce_timestamp_to_float",
    "_collect_targets",
    "_confirm_deletion",
    "_decode_transcript",
    "_emit_warnings",
    "_format_duration",
    "_format_timestamp",
    "_format_timestamp_display",
    "_handle_clear_result",
    "_launch_transcript_viewer",
    "_load_transcript_text",
    "_maybe_launch_transcript_viewer",
    "_parse_event_received_timestamp",
    "_parse_transcript_line",
    "_print_snapshot",
    "_render_deletion_preview",
    "_render_detail_view",
    "_render_history_overview",
    "_render_transcript_display",
    "_resolve_transcript_path",
    "_row_label",
    "_should_exit_for_targets",
    "_should_use_transcript_viewer",
    "_transcripts_payload",
    "_validate_clear_options",
    "console",
    "sys",
    "load_history_snapshot",
    "run_viewer_session",
    "create_final_panel",
]
