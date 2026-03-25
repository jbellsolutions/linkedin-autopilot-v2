#!/usr/bin/env python3
"""LinkedIn Autopilot - Interactive Setup Wizard.

Run this script to configure your LinkedIn Autopilot instance.
It will walk you through business identity, content preferences,
API keys, and generate all configuration files.

Usage:
    python setup.py
"""

from setup.wizard import run_wizard

if __name__ == "__main__":
    run_wizard()
