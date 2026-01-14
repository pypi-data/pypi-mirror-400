"""Certbot authenticator plugin for Aerix's HTTP-01 responder."""
from __future__ import annotations

import logging
import os
import subprocess
from typing import Dict, Iterable, List

from acme import challenges
from certbot import achallenges
from certbot import errors
from certbot import interfaces
from certbot.plugins import common
import zope.interface


AERIX_BASE_PATH = "/var/lib/aerix"


@zope.interface.provider(interfaces.IPluginFactory)
@zope.interface.implementer(interfaces.IAuthenticator)
class AerixAuthenticator(common.Plugin, interfaces.Authenticator):
    """Write HTTP-01 validation files for Aerix to serve."""

    logger = logging.getLogger(__name__)

    description = "Authenticate HTTP-01 challenges using Aerix's built-in responder"

    def __init__(self, config, name):
        super().__init__(config, name)
        self._created_files: Dict[achallenges.AnnotatedChallenge, str] = {}
        self._debug_enabled: bool = getattr(config, "aerix_debug", False)
        self._restart_service: str = "aerix"

    def prepare(self) -> None:
        """Validate that the Aerix challenge base path is available."""

        if not os.path.exists(AERIX_BASE_PATH):
            try:
                os.makedirs(AERIX_BASE_PATH, exist_ok=True)
            except OSError as exc:
                raise errors.PluginError(
                    f"Could not create Aerix ACME base directory {AERIX_BASE_PATH}: {exc}"
                ) from exc
        if not os.path.isdir(AERIX_BASE_PATH):
            raise errors.PluginError(
                f"Aerix ACME base path {AERIX_BASE_PATH} is not a directory"
            )

    def more_info(self) -> str:
        return (
            "Stores HTTP-01 validation files in Aerix's ACME directory so they "
            "are served automatically before routing or redirects."
        )

    @classmethod
    def add_parser_arguments(cls, add) -> None:
        add(
            "debug",
            action="store_true",
            default=False,
            help=(
                "Enable verbose Aerix authenticator logging (helpful for "
                "debugging challenge placement)"
            ),
        )

    @classmethod
    def inject_parser_options(cls, parser, name):
        """Register parser options via Certbot's helper."""

        return common.Plugin.inject_parser_options.__func__(cls, parser, name)

    def get_chall_pref(self, domain: str) -> List[challenges.HTTP01]:
        return [challenges.HTTP01]

    def perform(self, achalls: Iterable[achallenges.AnnotatedChallenge]):
        responses: List[challenges.HTTP01Response] = []
        for achall in achalls:
            if not achall.chall.good_token:
                raise errors.PluginError(
                    "ACME token failed challenge validation; refusing to write challenge file"
                )

            token = achall.chall.encode("token")
            validation = achall.validation(achall.account_key)
            file_path = self._write_challenge_file(AERIX_BASE_PATH, achall.domain, token, validation)
            self._created_files[achall] = file_path
            self._log_debug(
                "Wrote challenge for %s to %s (content starts with token: %s)",
                achall.domain,
                file_path,
                validation.startswith(f"{token}."),
            )
            responses.append(achall.response(achall.account_key))
        return responses

    def cleanup(self, achalls: Iterable[achallenges.AnnotatedChallenge]):
        removed_any = False
        for achall in achalls:
            file_path = self._created_files.pop(achall, None)
            if not file_path:
                continue
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self._log_debug("Removed challenge file %s", file_path)
                    removed_any = True
                    parent = os.path.dirname(file_path)
                    while parent.startswith(AERIX_BASE_PATH) and os.path.isdir(parent):
                        try:
                            os.rmdir(parent)
                        except OSError:
                            break
                        parent = os.path.dirname(parent)
            except OSError as exc:
                self.logger.debug("Failed to clean up %s: %s", file_path, exc)
        if removed_any and self._is_renewal():
            self._restart_aerix_service()

    def _write_challenge_file(self, base_path: str | bytes, domain: str | bytes, token: str | bytes, content: str) -> str:
        base_path_str = self._normalize_path_segment(base_path)
        domain_str = self._normalize_path_segment(domain)
        token_str = self._normalize_path_segment(token)
        self._validate_token(token_str)

        domain_dir = os.path.join(base_path_str, domain_str)
        file_path = os.path.join(domain_dir, token_str)
        try:
            os.makedirs(domain_dir, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as challenge_file:
                challenge_file.write(content)
        except OSError as exc:
            raise errors.PluginError(
                f"Could not write challenge file for {domain} to {file_path}: {exc}"
            ) from exc
        return file_path

    @staticmethod
    def _normalize_path_segment(segment: str | bytes) -> str:
        """Ensure path segments are usable string values."""

        if isinstance(segment, bytes):
            return os.fsdecode(segment)

        path = os.fspath(segment)
        if isinstance(path, bytes):
            return os.fsdecode(path)
        return path

    @staticmethod
    def _validate_token(token: str) -> None:
        """Validate ACME token characters to avoid malformed filesystem entries."""

        if not token:
            raise errors.PluginError("Empty ACME token; refusing to write challenge file")

        if token != token.strip():
            raise errors.PluginError(
                "Whitespace found in ACME token; refusing to write challenge file"
            )

        try:
            token.encode("ascii")
        except UnicodeEncodeError as exc:
            raise errors.PluginError(
                "Non-ASCII characters detected in ACME token; refusing to write challenge file"
            ) from exc

        separators = {os.sep}
        if os.altsep:
            separators.add(os.altsep)
        if any(sep and sep in token for sep in separators):
            raise errors.PluginError(
                "Path separators detected in ACME token; refusing to write challenge file"
            )

        normalized = os.path.normpath(token)
        if os.path.isabs(token) or normalized.startswith("..") or normalized in {".", ".."}:
            raise errors.PluginError(
                "Path traversal detected in ACME token; refusing to write challenge file"
            )

    def _log_debug(self, message: str, *args) -> None:
        if self._debug_enabled:
            self.logger.info(message, *args)
        else:
            self.logger.debug(message, *args)

    def _restart_aerix_service(self) -> None:
        """Restart the Aerix systemd service after successful cleanup."""

        try:
            subprocess.run(
                ["systemctl", "reload", self._restart_service],
                check=True,
                capture_output=True,
                text=True,
            )
            self._log_debug("Restarted service %s", self._restart_service)
        except (OSError, subprocess.CalledProcessError) as exc:
            stderr = getattr(exc, "stderr", "") or ""
            raise errors.PluginError(
                f"Failed to restart service {self._restart_service}: {stderr or exc}"
            ) from exc

    def _is_renewal(self) -> bool:
        """Return True when Certbot is running in renew mode."""

        verb = getattr(self.config, "verb", None)
        if isinstance(verb, str) and verb.lower() == "renew":
            return True

        return bool(getattr(self.config, "renew", False))
