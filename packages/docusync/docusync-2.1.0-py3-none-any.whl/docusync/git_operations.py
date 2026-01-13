"""Git operations for DocuSync."""

import os
import subprocess
from pathlib import Path

from docusync.constants import GIT_COMMAND_TIMEOUT
from docusync.exceptions import GitError
from docusync.logger import USER_LOG


class GitManager:
    """Handles all Git operations."""

    def __init__(
        self,
        default_pat_token_env: str | None = None,
        default_ssh_key_path: str | None = None,
    ) -> None:
        """Initialize GitManager.

        :param default_pat_token_env: Default environment variable name containing PAT token
        :param default_ssh_key_path: Default path to SSH private key
        """
        self.default_pat_token_env = default_pat_token_env
        self.default_ssh_key_path = default_ssh_key_path

    def clone_repository(
        self,
        clone_url: str,
        destination: Path,
        depth: int = 1,
        pat_token_env: str | None = None,
        ssh_key_path: str | None = None,
    ) -> None:
        """Clone a Git repository.

        :param clone_url: Repository URL to clone
        :param destination: Destination path
        :param depth: Clone depth (default: 1 for shallow clone)
        :param pat_token_env: Environment variable for PAT token (overrides default)
        :param ssh_key_path: Path to SSH key (overrides default)
        :raises GitError: If cloning fails
        """
        pat_token = self._get_pat_token(pat_token_env)

        auth_url = self._inject_auth_token(clone_url, pat_token)

        ssh_key = ssh_key_path or self.default_ssh_key_path

        USER_LOG.progress_message("Cloning", clone_url)

        cmd = [
            "git",
            "clone",
            "--depth",
            str(depth),
            auth_url,
            str(destination),
        ]

        returncode, stdout, stderr = self._run_command(
            cmd, ssh_key_path=ssh_key
        )

        if returncode != 0:
            clean_error = stderr.replace(auth_url, clone_url)
            raise GitError(f"Failed to clone {clone_url}: {clean_error}")

        USER_LOG.debug(f"Clone output: {stdout}")
        USER_LOG.success(f"Cloned successfully: {clone_url}")

    def _get_pat_token(self, pat_token_env: str | None = None) -> str | None:
        """Get PAT token from environment variable.

        :param pat_token_env: Environment variable name, uses default if not provided
        :returns: PAT token or None if not configured
        """
        env_var = pat_token_env or self.default_pat_token_env

        if env_var:
            token = os.getenv(env_var)
            if token:
                USER_LOG.debug(f"PAT token loaded from {env_var}")
                return token
            else:
                USER_LOG.debug(f"PAT token env variable {env_var} not set")
        return None

    def _inject_auth_token(self, url: str, pat_token: str | None) -> str:
        """Inject PAT token into HTTPS URL.

        :param url: Original clone URL
        :param pat_token: PAT token to inject
        :returns: URL with token injected (if applicable)
        """
        if pat_token and url.startswith("https://"):
            # Format: https://token@github.com/owner/repo.git
            return url.replace("https://", f"https://{pat_token}@")
        return url

    def _run_command(
        self,
        cmd: list[str],
        cwd: Path | None = None,
        ssh_key_path: str | None = None,
    ) -> tuple[int, str, str]:
        USER_LOG.command_output(" ".join(cmd))

        # Copy environment and configure SSH if needed
        env = os.environ.copy()

        if ssh_key_path:
            expanded_path = os.path.expanduser(ssh_key_path)
            # Use GIT_SSH_COMMAND to specify SSH key
            # -o IdentitiesOnly=yes ensures only this key is used
            env["GIT_SSH_COMMAND"] = (
                f"ssh -i {expanded_path} " f"-o IdentitiesOnly=yes"
            )
            USER_LOG.debug(f"Using SSH key: {expanded_path}")

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=GIT_COMMAND_TIMEOUT,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as e:
            raise GitError(f"Git command timed out: {' '.join(cmd)}") from e
        except Exception as e:
            raise GitError(f"Failed to run git command: {e}") from e
        finally:
            env.clear()
            del env
