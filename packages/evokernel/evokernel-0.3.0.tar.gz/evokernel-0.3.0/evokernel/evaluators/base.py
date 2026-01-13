"""Base class for evaluator templates."""

from pathlib import Path

from jinja2 import Environment, PackageLoader


class EvaluatorTemplate:
    """Base class for Jinja2-based evaluator templates."""

    name: str
    template_name: str

    def __init__(self):
        self.env = Environment(
            loader=PackageLoader("evokernel.evaluators", "templates"),
            keep_trailing_newline=True,
        )

    def render(self, **kwargs) -> str:
        """Render the template with given parameters."""
        template = self.env.get_template(self.template_name)
        return template.render(**kwargs)

    def write_to(self, output_path: Path, **kwargs):
        """Write rendered template to file."""
        output_path.write_text(self.render(**kwargs))
