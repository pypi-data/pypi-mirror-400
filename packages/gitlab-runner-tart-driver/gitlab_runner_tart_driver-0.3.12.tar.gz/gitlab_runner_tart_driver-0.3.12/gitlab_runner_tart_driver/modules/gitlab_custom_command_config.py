from typing import Optional

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class GitLabCustomCommandConfig(BaseSettings):
    """Config parameters needed throughout the process read from the environment"""

    ci_job_image: Optional[str] = None
    ci_pipeline_id: Optional[str] = None
    ci_job_id: Optional[str] = None
    ci_concurrent_id: Optional[str] = None
    ci_concurrent_project_id: Optional[str] = None
    ci_runner_short_token: Optional[str] = None
    ci_project_name: Optional[str] = None
    ci_registry: Optional[str] = None
    ci_registry_user: Optional[str] = None
    ci_registry_password: Optional[str] = None

    tart_registry_username: Optional[str] = None
    tart_registry_password: Optional[str] = None
    tart_registry: Optional[str] = None

    tart_ssh_username: Optional[str] = "admin"
    tart_ssh_password: Optional[str] = "admin"
    tart_max_vm_count: Optional[int] = 2
    tart_pull_policy: Optional[str] = "if-not-present"
    tart_executor_softnet_enabled: Optional[str] = "false"
    tart_executor_headless: Optional[str] = "true"
    tart_executor_vnc_enabled: Optional[str] = "false"
    tart_executor_install_gitlab_runner: Optional[str] = "false"
    tart_executor_shell: Optional[str] = "/bin/zsh"
    tart_executor_timeout: Optional[int] = 60
    tart_executor_display: Optional[str] = "1920x1200"

    model_config = SettingsConfigDict(env_prefix="CUSTOM_ENV_")

    def vm_name(self):
        """Creates a unique name for a VM"""
        return f"{self.vm_name_prefix}-{self.ci_project_name}-{self.ci_pipeline_id}-{self.ci_job_id}-{self.ci_concurrent_id}"

    @property
    def vm_name_prefix(self):
        return "grtd"

    @property
    def softnet_enabled(self) -> bool:
        return self.tart_executor_softnet_enabled.lower() == "true"

    @property
    def vnc_enabled(self) -> bool:
        return self.tart_executor_vnc_enabled.lower() == "true"

    @property
    def headless(self) -> bool:
        return self.tart_executor_headless.lower() == "true"

    @property
    def shell(self) -> Optional[str]:
        return self.tart_executor_shell

    @property
    def display(self) -> Optional[str]:
        return self.tart_executor_display

    @property
    def install_gitlab_runner(self) -> bool:
        return self.tart_executor_install_gitlab_runner.lower() == "true"

    @property
    def timeout(self) -> Optional[int]:
        return self.tart_executor_timeout

    @property
    def ssh_username(self) -> Optional[str]:
        return self.tart_ssh_username

    @property
    def ssh_password(self) -> Optional[str]:
        return self.tart_ssh_password

    @property
    def pull_policy(self) -> Optional[str]:
        return self.tart_pull_policy

    @property
    def registry_username(self) -> Optional[str]:
        return self.tart_registry_username

    @property
    def registry_password(self) -> Optional[str]:
        return self.tart_registry_password

    @property
    def registry(self) -> Optional[str]:
        return self.tart_registry
