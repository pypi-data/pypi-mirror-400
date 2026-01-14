# Core modules
from .element_locator import ElementLocator
from .variable_manager import VariableManager
from .report_generator import ReportGenerator
from .step_suggester import StepSuggester
from .screenshot_manager import (
    take_screenshot,
    take_screenshot_on_failure,
    take_step_screenshot,
    cleanup_old_screenshots,
    cleanup_directories,
    get_screenshots_summary
)
from .environment_config import (
    FrameworkConfig,
    setup_framework_context,
    setup_scenario_context
)

__all__ = [
    'ElementLocator',
    'VariableManager', 
    'ReportGenerator',
    'StepSuggester',
    'FrameworkConfig',
    'setup_framework_context',
    'setup_scenario_context', 
    'take_screenshot',
    'take_screenshot_on_failure',
    'take_step_screenshot',
    'cleanup_old_screenshots',
    'cleanup_directories',
    'get_screenshots_summary'
]