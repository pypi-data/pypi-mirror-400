"""Validator toggle configuration."""

from dataclasses import dataclass


@dataclass
class ValidatorToggles:
    """Control which validators are enabled."""
    structure: bool = False      # Opt-in (too opinionated)
    line_limits: bool = True     # Enabled by default
    one_per_file: bool = True    # Enabled by default
