from hakalab_framework.core.environment_config import (
    setup_framework_context,
    setup_scenario_context,
    cleanup_scenario_context,
    cleanup_framework_context
)

def before_all(context):
    setup_framework_context(context)

def before_scenario(context, scenario):
    setup_scenario_context(context, scenario)

def after_scenario(context, scenario):
    cleanup_scenario_context(context, scenario)

def after_all(context):
    cleanup_framework_context(context)