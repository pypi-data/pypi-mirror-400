"""DevContainer configuration generator."""

import json
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape


class DevContainerGenerator:
    """Generator for devcontainer configurations using Jinja2 templates."""

    def __init__(self, templates_dir: Optional[str] = None) -> None:
        """Initialize the generator with Jinja2 environment.

        Args:
            templates_dir: Path to templates directory (defaults to package templates)
        """
        if templates_dir is None:
            # Use package-relative path
            package_dir = Path(__file__).parent
            self.templates_dir = package_dir / "templates"
        else:
            self.templates_dir = Path(templates_dir)

        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(),
        )

    def generate(
        self,
        container_type: str,
        output_dir: str = ".",
        dry_run: bool = False,
        force: bool = False,
        **config: Any,
    ) -> None:
        """Generate devcontainer configuration.

        Args:
            container_type: Type of container (data-science, llm-finetuning, web-dev)
            output_dir: Output directory for .devcontainer folder
            dry_run: If True, show what would be generated without writing files
            force: If True, overwrite existing .devcontainer directory
            **config: Additional configuration variables for templates

        Raises:
            FileExistsError: If .devcontainer exists and force is False
            ValueError: If generated JSON is invalid
        """
        output_path = Path(output_dir) / ".devcontainer"

        # Check if .devcontainer already exists
        if output_path.exists() and not force:
            raise FileExistsError(
                f".devcontainer directory already exists at {output_path}. "
                "Use --force to overwrite."
            )

        if dry_run:
            self._dry_run(container_type, output_path, **config)
            return

        # Remove existing if force is True
        if output_path.exists() and force:
            import shutil

            shutil.rmtree(output_path)

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            # Render devcontainer.json
            template = self.env.get_template(f"{container_type}/devcontainer.json.j2")
            devcontainer_json = template.render(**config)

            # Validate JSON
            json.loads(devcontainer_json)  # Raises if invalid

            (output_path / "devcontainer.json").write_text(devcontainer_json)

            # Render Dockerfile
            template = self.env.get_template(f"{container_type}/Dockerfile.j2")
            dockerfile = template.render(**config)
            (output_path / "Dockerfile").write_text(dockerfile)

            # Copy p10k config
            p10k_template = self.env.get_template("common/p10k-lean.zsh")
            p10k_config = p10k_template.render()
            (output_path / ".p10k.zsh").write_text(p10k_config)

        except Exception as e:
            # Rollback on failure
            if output_path.exists():
                import shutil

                shutil.rmtree(output_path)
            raise e

    def _dry_run(self, container_type: str, output_path: Path, **config: Any) -> None:
        """Show what would be generated without writing files.

        Args:
            container_type: Type of container
            output_path: Output directory path
            **config: Configuration variables
        """
        print(f"Would create .devcontainer directory at: {output_path}")
        print(f"Container type: {container_type}")
        print(f"Configuration: {config}")
        print("\nFiles that would be created:")
        print(f"  - {output_path / 'devcontainer.json'}")
        print(f"  - {output_path / 'Dockerfile'}")
        print(f"  - {output_path / '.p10k.zsh'}")
