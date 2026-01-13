"""
SudoDog Shadow Agent Scanner

Detect unmonitored AI agents running on your machine.
"""

from .scanner import scan_for_shadow_agents, DetectedAgent, format_report, export_json

__all__ = ['scan_for_shadow_agents', 'DetectedAgent', 'format_report', 'export_json']
