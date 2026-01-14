"""Data models for DevContainer configuration generation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ContainerType(Enum):
    """Supported devcontainer types."""

    DATA_SCIENCE = "data-science"
    LLM_FINETUNING = "llm-finetuning"
    WEB_DEV = "web-dev"


@dataclass
class Mount:
    """Docker mount configuration."""

    source: str
    target: str
    type: str
    readonly: bool = False
    consistency: Optional[str] = None

    def to_string(self) -> str:
        """Convert to devcontainer.json mount string."""
        parts = [f"source={self.source}", f"target={self.target}", f"type={self.type}"]
        if self.readonly:
            parts.append("readonly")
        if self.consistency:
            parts.append(f"consistency={self.consistency}")
        return ",".join(parts)


@dataclass
class VSCodeCustomizations:
    """VS Code customizations."""

    extensions: list[str] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to devcontainer.json format."""
        return {"vscode": {"extensions": self.extensions, "settings": self.settings}}


@dataclass
class ClaudeCodeConfig:
    """Claude Code installation configuration."""

    install_method: str = "npm"
    version: Optional[str] = None
    npm_package: str = "@anthropic-ai/claude-code"
    vscode_extension: str = "Anthropic.claude-code"

    def to_dockerfile_snippet(self) -> str:
        """Generate Dockerfile commands for installation."""
        if self.version:
            return f"RUN npm install -g {self.npm_package}@{self.version}"
        return f"RUN npm install -g {self.npm_package}"

    def get_config_mount(self) -> Mount:
        """Get Claude config directory mount."""
        return Mount(
            source="${localEnv:HOME}/.claude",
            target="/home/vscode/.claude",
            type="bind",
            consistency="cached",
        )


@dataclass
class Powerlevel10kConfig:
    """Powerlevel10k installation configuration."""

    style: str = "lean"
    theme_repo: str = "https://github.com/romkatv/powerlevel10k.git"
    plugins: list[str] = field(
        default_factory=lambda: ["zsh-autosuggestions", "zsh-syntax-highlighting"]
    )
    config_file: str = ".p10k.zsh"
    disable_wizard: bool = True

    def to_dockerfile_snippet(self) -> str:
        """Generate Dockerfile commands for installation."""
        snippets = [
            # Install Zsh and Oh My Zsh
            "RUN apt-get update && apt-get install -y zsh git fonts-powerline && \\",
            "    apt-get clean && rm -rf /var/lib/apt/lists/*",
            "",
            'RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended',
            "",
            # Install Powerlevel10k
            f"RUN git clone --depth=1 {self.theme_repo} \\",
            '    ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k',
            "",
            # Install plugins
            "RUN git clone https://github.com/zsh-users/zsh-autosuggestions \\",
            '    ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions && \\',
            "    git clone https://github.com/zsh-users/zsh-syntax-highlighting \\",
            '    ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting',
            "",
            # Configure zsh
            'RUN echo \'export ZSH="$HOME/.oh-my-zsh"\' >> ~/.zshrc && \\',
            '    echo \'ZSH_THEME="powerlevel10k/powerlevel10k"\' >> ~/.zshrc && \\',
            "    echo 'plugins=(git zsh-autosuggestions zsh-syntax-highlighting)' >> ~/.zshrc && \\",
            "    echo 'source $ZSH/oh-my-zsh.sh' >> ~/.zshrc && \\",
            "    echo 'POWERLEVEL9K_DISABLE_CONFIGURATION_WIZARD=true' >> ~/.zshrc",
        ]
        return "\n".join(snippets)


@dataclass
class SSHMountConfig:
    """SSH credential mounting configuration for MacOS."""

    agent_socket_host: str = "/run/host-services/ssh-auth.sock"
    agent_socket_container: str = "/run/host-services/ssh-auth.sock"
    mount_known_hosts: bool = False
    mount_ssh_config: bool = False
    readonly: bool = True

    def to_mount_config(self) -> list[str]:
        """Generate devcontainer.json mount configuration."""
        mounts = [
            f"source={self.agent_socket_host},target={self.agent_socket_container},type=bind"
        ]
        if self.mount_known_hosts:
            mounts.append(
                "source=${localEnv:HOME}/.ssh/known_hosts,target=/home/vscode/.ssh/known_hosts,readonly,type=bind"
            )
        if self.mount_ssh_config:
            mounts.append(
                "source=${localEnv:HOME}/.ssh/config,target=/home/vscode/.ssh/config,readonly,type=bind"
            )
        return mounts

    def to_env_config(self) -> dict[str, str]:
        """Generate environment variables."""
        return {"SSH_AUTH_SOCK": self.agent_socket_container}


@dataclass
class CommonConfiguration:
    """Shared configuration across all container types."""

    claude_code: ClaudeCodeConfig = field(default_factory=ClaudeCodeConfig)
    powerlevel10k: Powerlevel10kConfig = field(default_factory=Powerlevel10kConfig)
    ssh_mount: SSHMountConfig = field(default_factory=SSHMountConfig)


@dataclass
class EnvironmentTemplate:
    """Template blueprint for a container type."""

    container_type: ContainerType
    base_image: str
    additional_packages: dict[str, list[str]] = field(default_factory=dict)
    vscode_extensions: list[str] = field(default_factory=list)
    dockerfile_template: str = ""
    devcontainer_template: str = ""
    default_settings: dict[str, Any] = field(default_factory=dict)
    common_config: CommonConfiguration = field(default_factory=CommonConfiguration)


@dataclass
class DevContainerConfig:
    """Represents a complete devcontainer configuration."""

    name: str
    container_type: ContainerType
    image: Optional[str] = None
    dockerfile: Optional[str] = None
    features: dict[str, dict[str, Any]] = field(default_factory=dict)
    mounts: list[str] = field(default_factory=list)
    container_env: dict[str, str] = field(default_factory=dict)
    customizations: dict[str, Any] = field(default_factory=dict)
    post_create_command: Optional[str] = None
    remote_user: str = "vscode"
    run_args: list[str] = field(default_factory=list)

    def validate(self) -> None:
        """Validate configuration."""
        if not self.image and not self.dockerfile:
            raise ValueError("Must specify either image or dockerfile")
        if self.image and self.dockerfile:
            raise ValueError("Cannot specify both image and dockerfile")
        if not self.name:
            raise ValueError("Name must be non-empty")
        if len(self.name) > 50:
            raise ValueError("Name must be 50 characters or less")
