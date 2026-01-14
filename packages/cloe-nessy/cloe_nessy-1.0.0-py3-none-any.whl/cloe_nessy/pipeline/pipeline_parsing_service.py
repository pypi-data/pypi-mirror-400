import os
import re
from collections import OrderedDict
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from ..logging import LoggerMixin
from ..session import SessionManager
from .actions import PipelineActionType, pipeline_actions
from .pipeline import Pipeline
from .pipeline_config import PipelineConfig, PipelineStepConfig
from .pipeline_step import PipelineStep


class PipelineParsingService:
    """A service class that parses a YAML document or string into a Pipeline object."""

    def __init__(self, custom_actions=None):
        if custom_actions is not None:
            for action in custom_actions:
                self.register_pipeline_action(action)

    @staticmethod
    def register_pipeline_action(pipeline_action_class):
        """Registers a custom pipeline action class.

        !!! note
            Registering an action enables the custom action to be used in the
            pipeline YAML definition. This is automatically called, when the
            PipelineParsingService is instantiated with (a list of) custom
            actions.
        """
        console_logger = LoggerMixin().get_console_logger()
        console_logger.info("Registering custom pipeline action [' %s ']", pipeline_action_class.name)
        pipeline_actions[pipeline_action_class.name] = pipeline_action_class

        global PipelineActionType
        PipelineActionType = Enum("PipelineActionType", pipeline_actions)

    @staticmethod
    def parse(path: Path | None = None, yaml_str: str | None = None) -> Pipeline:
        """Reads the YAML from a given Path and returns a Pipeline object.

        Args:
            path: Path to the YAML document.
            yaml_str: A string that can be parsed in YAML format.

        Raises:
            ValueError: If neither 'path' nor 'yaml_str' has been provided.

        Returns:
            Pipeline: The resulting Pipeline instance.
        """
        console_logger = LoggerMixin().get_console_logger()
        if not path and not yaml_str:
            raise ValueError("Neither 'file_path' nor 'yaml_str' was provided. Please supply one of them.")
        if path:
            path_obj = Path(path)
            with open(path_obj) as f:
                yaml_str = f.read()
        if not yaml_str:
            raise ValueError("YAML content is empty.")

        secrets_repl_yaml_str = PipelineParsingService._replace_secret_refs(yaml_str)
        fixed_yaml_str = PipelineParsingService._fix_yaml_str_with_templates(secrets_repl_yaml_str)
        config = yaml.safe_load(fixed_yaml_str)
        pipeline_config = PipelineConfig.metadata_to_instance(config)
        steps = PipelineParsingService._get_steps(pipeline_config.steps, pipeline_config.env)
        pipeline = Pipeline(name=pipeline_config.name, steps=steps)  # type: ignore
        console_logger.info("Pipeline [ '%s' ] parsed successfully with %d steps.", pipeline.name, len(pipeline.steps))
        return pipeline

    @staticmethod
    def _get_steps(
        step_configs: OrderedDict[str, PipelineStepConfig],
        pipeline_env: dict[str, str],
        last_step_name: str | None = None,
    ) -> OrderedDict[str, PipelineStep]:
        os_env = dict(os.environ)
        steps = OrderedDict()
        for step_name, step_config in step_configs.items():
            is_successor = step_config.is_successor
            context_ref = step_config.context
            if is_successor and not context_ref:
                context_ref = last_step_name
            action = PipelineActionType[step_config.action.name].value()
            step = PipelineStep(
                name=step_name,
                env=step_config.env,
                action=action,
                options=step_config.options,
                _context_ref=context_ref,
                _table_metadata_ref=step_config.table_metadata,
            )
            steps[step.name] = PipelineParsingService._resolve_env_vars(step, os_env, pipeline_env)
            last_step_name = step_name
        for step in steps.values():
            steps[step.name] = PipelineParsingService._replace_step_refs(steps, step)
        return steps

    @staticmethod
    def _replace_secret_refs(yaml_str: str) -> str:
        """Replaces secret reference placeholders in a YAML string.

        Replaces secret references with the pattern `{{secret-scope-name:secret-key}}`.
        Where scope-name is the name of the secret scope and secret-key is the key of the secret.

        Args:
            yaml_str: A string that can be parsed in YAML format.

        Returns:
            The same YAML string with secret reference placeholders replaced.
        """
        secret_ref_pattern = r"\{\{(?!(?:env|step):)([^}]+):([^}]+)\}\}"

        def replace_with_secret(match):
            secret_scope_name = match.group(1)
            secret_key = match.group(2)
            return SessionManager.get_utils().secrets.get(scope=secret_scope_name, key=secret_key)

        return re.sub(secret_ref_pattern, replace_with_secret, yaml_str)

    @staticmethod
    def _resolve_env_vars(step: PipelineStep, os_env: dict[str, str], pipeline_env: dict[str, str]) -> PipelineStep:
        """Resolves environment variable placeholders in step definition.

        Resolves environment variables with the pattern `{{env:var-name}}`,
        where the `var-name` is the name of the environment variable.

        Args:
            step: Step definition, where replacement is occurred.
            os_env: OS scope environment variable.
            pipeline_env: Pipeline scope environment variables.

        Returns:
            The same step definition with environment variable placeholders replaced.

        Raises:
            KeyError: If the specified key is not found in the environment variables.
        """
        env_var_pattern = re.compile(r"\{\{env:([A-Z_][A-Z0-9_]*)\}\}")

        def _resolve_object(obj: Any) -> Any:
            if isinstance(obj, str):
                return _resolve_string(obj)
            if isinstance(obj, list):
                return [_resolve_object(i) for i in obj]
            if isinstance(obj, dict):
                return {k: _resolve_object(v) for k, v in obj.items()}
            return obj

        def _resolve_string(value: str) -> str:
            def repl(match):
                key = match.group(1)
                if key not in effective_env:
                    raise KeyError(f"Environment variable '{key}' is not defined")
                return str(effective_env[key])

            return env_var_pattern.sub(repl, value)

        if step.options:
            effective_env = {**os_env, **pipeline_env, **step.env}
            for option, value in step.options.items():
                step.options[option] = _resolve_object(value)

        return step

    @staticmethod
    def _replace_step_refs(steps: OrderedDict[str, PipelineStep], step: PipelineStep) -> PipelineStep:
        """Replaces other steps reference placeholders in a step definition.

        Replaces other steps references with the pattern `((step:step-name))`.
        Where the `step-name` is the name of the referenced step.

        Args:
            steps: All pipeline steps definitions.
            step: Step definition, where replacement is occurred.

        Returns:
            The same step definition with referenced step names replaced.
        """
        step_ref_pattern = r"\(\(step:([^)]+)\)\)"

        def _handle_string_value(value: str, option: str):
            if match := re.match(step_ref_pattern, value):
                dependency_step_name = match.group(1)
                dependency_step = steps.get(dependency_step_name)
                step.options[option] = dependency_step
                step._predecessors.add(dependency_step_name)

        def _handle_list_value(value: list, option: str):
            for i, v in enumerate(value):
                if isinstance(v, str):
                    if match := re.match(step_ref_pattern, v):
                        dependency_step_name = match.group(1)
                        dependency_step = steps.get(dependency_step_name)
                        step.options[option][i] = dependency_step
                        step._predecessors.add(dependency_step_name)

        if step.options:
            for option, value in step.options.items():
                if isinstance(value, str):
                    _handle_string_value(value, option)
                elif isinstance(value, list):
                    _handle_list_value(value, option)

        return step

    @staticmethod
    def _fix_yaml_str_with_templates(yaml_str: str) -> str:
        """Fixes unquoted {{env:...}} templates before yaml.safe_load."""
        unquoted_template = re.compile(r"(:)\s*(\{\{env:[^}]+\}\})(?=\s*$|\s+#)", re.MULTILINE)

        def replacer(match):
            colon, template = match.groups()
            return f'{colon} "{template}"'

        return unquoted_template.sub(replacer, yaml_str)
