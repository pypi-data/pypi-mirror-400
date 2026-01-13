# -*- coding: utf-8 -*-
#
# Copyright 2025 NXP
#
# SPDX-License-Identifier: MIT

import shlex
from importlib.metadata import entry_points
from typing import Optional


class MCPPlugin:
    def __init__(self, mcp):
        self.mcp = mcp
        self.register_tools()

    def register_tools(self):
        pass

    @staticmethod
    def load_plugins(mcp):
        for entry_point in entry_points(group="fc.mcp.plugins"):
            plugin_class = entry_point.load()
            plugin_class(mcp)

    def _build_download_custom_image_args(self, resource_id: str, **kwargs) -> str:
        """
        Build download_custom_image.sh arguments, intelligently detecting URLs vs local paths.

        Args:
            resource_id: Resource identifier
            **kwargs: Can contain uboot_uri, dtb_uri, kernel_uri, rootfs_uri
                     (each can be URL or local path)

        Returns:
            Formatted command line arguments for download_custom_image.sh
        """
        args = [f"-p {resource_id}"]

        # Map of parameter names to their command-line flags
        param_map = {
            "uboot_uri": ("--uboot", "--uboot-url"),
            "dtb_uri": ("--dtb", "--dtb-url"),
            "kernel_uri": ("--kernel", "--kernel-url"),
            "rootfs_uri": ("--rootfs", "--rootfs-url"),
        }

        for param, (local_flag, url_flag) in param_map.items():
            value = kwargs.get(param)
            if value:
                flag = url_flag if self._is_url(value) else local_flag
                args.append(f"{flag} {self._escape_bash_arg(value)}")

        return " \\\n    ".join(args)

    def _is_url(self, uri: Optional[str]) -> bool:
        """
        Check if a URI is a URL.

        Args:
            uri: URI string (can be URL or local path)

        Returns:
            True if URI is a URL, False otherwise
        """
        if not uri:
            return False
        return uri.startswith(("http://", "https://", "ftp://"))

    def _escape_bash_arg(self, arg: str) -> str:
        """
        Safely escape arguments for bash commands.
        """
        return shlex.quote(str(arg))
