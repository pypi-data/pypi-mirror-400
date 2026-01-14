"""
Hakalab Framework - Framework completo de pruebas funcionales
"""

__version__ = "1.2.23"
__author__ = "Felipe Farias"
__email__ = "felipe.farias@hakalab.com"
__description__ = "Framework completo de pruebas funcionales con Playwright y Behave"

from .core.element_locator import ElementLocator
from .core.variable_manager import VariableManager
from .core.report_generator import ReportGenerator
from .core.step_suggester import StepSuggester
from .core.environment_config import (
    FrameworkConfig,
    setup_framework_context,
    setup_scenario_context
)

# Integraciones
from .integrations.jira_integration import JiraIntegration
from .integrations.xray_integration import XrayIntegration

__all__ = [
    "ElementLocator",
    "VariableManager", 
    "ReportGenerator",
    "StepSuggester",
    "FrameworkConfig",
    "setup_framework_context",
    "setup_scenario_context",
    "JiraIntegration",
    "XrayIntegration"
]