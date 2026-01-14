from collections import OrderedDict
from collections.abc import Callable
from typing import Any, Self

from .pipeline import Pipeline
from .pipeline_step import PipelineStep


class PipelineBuilder:
    """Fluent API builder for creating Nessy pipelines programmatically.

    This class provides a chainable interface for building pipelines using method calls
    instead of YAML configuration. It dynamically creates methods for all available
    PipelineActions.

    Example:
        ```python
        pipeline = (PipelineBuilder("My Pipeline")
            .read_files(location="data/*.csv", extension="csv")
            .transform_clean_column_names()
            .transform_filter(condition="amount > 1000")
            .write_catalog_table(catalog="prod", schema="sales", table="results")
            .build())

        pipeline.run()
        ```
    """

    def __init__(self, name: str) -> None:
        """Initialize the pipeline builder.

        Args:
            name: The name of the pipeline.
        """
        self.name = name
        self.steps: OrderedDict[str, PipelineStep] = OrderedDict()
        self._step_counter = 0

    def __getattr__(self, name: str) -> Callable[..., "PipelineBuilder"]:
        """Dynamically create methods for pipeline actions.

        This method is called when an attribute that doesn't exist is accessed.
        It converts method calls like `read_files()` into the corresponding PipelineAction.

        Args:
            name: The method name being called.

        Returns:
            A callable that adds the corresponding pipeline step.

        Raises:
            AttributeError: If the method name doesn't correspond to a known action.
        """
        # Lazy import to avoid circular import issues
        from .actions import pipeline_actions

        # Convert method name to action name (e.g., read_files -> READ_FILES)
        action_name = name.upper()

        if action_name in pipeline_actions:
            action_class = pipeline_actions[action_name]

            def method(**kwargs: Any) -> "PipelineBuilder":
                return self._add_step(action_class, **kwargs)

            return method

        raise AttributeError(
            f"PipelineBuilder has no method '{name}'. Available actions: {list(pipeline_actions.keys())}"
        )

    def _add_step(self, action_class: type, step_name: str | None = None, **options: Any) -> Self:
        """Add a step to the pipeline.

        Args:
            action_class: The PipelineAction class to instantiate.
            step_name: Optional custom name for the step.
            **options: Options to pass to the action.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If a step with the given name already exists.
        """
        if step_name is None:
            step_name = f"step_{self._step_counter:03d}_{action_class.__name__}"

        # Validate that step name is unique
        if step_name in self.steps:
            raise ValueError(
                f"A step with name '{step_name}' already exists in the pipeline. "
                f"Please provide a unique step_name. "
                f"Existing steps: {list(self.steps.keys())}"
            )

        # Convert any PipelineBuilder instances in options to PipelineStep references
        options = self._convert_builder_references(options)

        # Set up context reference to previous step
        context_ref = None
        if self.steps:
            context_ref = list(self.steps.keys())[-1]

        step = PipelineStep(name=step_name, action=action_class(), options=options, _context_ref=context_ref)

        # Remove any predecessors that are from already-executed external pipelines
        # (these steps have results but aren't in our pipeline)
        external_predecessors = set()
        for pred_name in step._predecessors:
            if pred_name not in self.steps and pred_name != context_ref:
                # Check if this is a reference to an executed step from options
                for opt_val in options.values():
                    if isinstance(opt_val, PipelineStep) and opt_val.name == pred_name:
                        # This is an external executed step, remove from predecessors
                        external_predecessors.add(pred_name)
                        break

        step._predecessors -= external_predecessors

        self.steps[step_name] = step
        self._step_counter += 1
        return self

    def _convert_builder_references(self, options: dict[str, Any]) -> dict[str, Any]:
        """Convert any PipelineBuilder instances in options to PipelineStep references.

        This method recursively processes options to find PipelineBuilder instances and
        converts them to their last step's PipelineStep reference. This allows users to
        pass PipelineBuilder instances directly to actions that expect PipelineStep references.

        Handles PipelineBuilder instances in:
        - Direct values
        - Lists
        - Nested dictionaries

        Args:
            options: Dictionary of options that may contain PipelineBuilder instances.

        Returns:
            Dictionary with PipelineBuilder instances converted to PipelineStep references.

        Raises:
            ValueError: If a PipelineBuilder has no steps.
        """
        converted = {}
        for key, value in options.items():
            converted[key] = self._convert_value(value, key)
        return converted

    def _convert_value(self, value: Any, context: str = "") -> Any:
        """Recursively convert a value, handling PipelineBuilder instances.

        When a PipelineBuilder is passed as a value, it is executed immediately
        and its last step is returned as the reference. This allows the pipeline
        to be run before the main pipeline that references it.

        Args:
            value: The value to convert.
            context: Context string for error messages (e.g., key name).

        Returns:
            The converted value.
        """
        if isinstance(value, PipelineBuilder):
            # Build and run the referenced pipeline immediately
            pipeline = value.build()
            if not pipeline.steps:
                context_msg = f" in '{context}'" if context else ""
                raise ValueError(f"PipelineBuilder{context_msg} must have at least one step")

            # Run the pipeline to populate the results
            pipeline.run()

            # Get the last step which now has results
            last_step_name = list(pipeline.steps.keys())[-1]
            last_step = pipeline.steps[last_step_name]

            # Clear predecessors since this step is already executed and has its result
            # This prevents the main pipeline from trying to resolve dependencies
            # that don't exist in its own step dictionary
            last_step._predecessors = set()
            last_step._context_ref = None

            return last_step
        if isinstance(value, dict):
            # Recursively convert nested dictionaries
            return {k: self._convert_value(v, f"{context}.{k}" if context else k) for k, v in value.items()}
        if isinstance(value, list):
            # Recursively convert lists
            return [
                self._convert_value(item, f"{context}[{i}]" if context else f"[{i}]") for i, item in enumerate(value)
            ]
        return value

    def build(self) -> Pipeline:
        """Build the pipeline from the configured steps.

        Returns:
            A Pipeline object ready for execution.
        """
        return Pipeline(name=self.name, steps=self.steps)

    def run(self) -> None:
        """Build and run the pipeline immediately.

        This is a convenience method equivalent to calling build().run().
        """
        pipeline = self.build()
        pipeline.run()
