# -*- coding: utf-8 -*-
#
# Copyright 2025 NXP
#
# SPDX-License-Identifier: MIT

"""
External sample MCP describe how to flash boards with uuu-based flashing operations.
"""


import os
import stat
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, Optional

from fc_mcp.mcp_base import MCPPlugin


class Plugin(MCPPlugin):
    def register_tools(self):
        @self.mcp.tool()
        def boot_mode_switch(
            resource_id: str, boot_mode: str, verbose: int = 0
        ) -> Dict[str, Any]:
            """
            Switch boot mode for a resource using fc-client command.

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                boot_mode: Boot mode to switch to ('usb', 'sd', 'emmc', or ...)
                verbose: Verbosity level (0-3)

            Returns:
                Dictionary with operation result and status information
            """

            # Build verbose flags for fc-client commands
            verbose_flags = ("-v " * verbose).strip() if verbose > 0 else ""

            # Get current timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create environment setup script
            env_setup_script = """
if [ -f "/opt/fc_env/env.sh" ]; then
    source /opt/fc_env/env.sh
elif [ -f "$HOME/.fc_env/env.sh" ]; then
    source ~/.fc_env/env.sh
else
    echo "ERROR: Neither /opt/fc_env/env.sh nor ~/.fc_env/env.sh found!"
    exit 1
fi
"""

            # Build the fc-client command with proper spacing
            if verbose_flags:
                fc_command = f"fc-client -p {resource_id} -c $BOARDS_CONFIG/{resource_id}_remote.yaml boot_sw {boot_mode} {verbose_flags}"
            else:
                fc_command = f"fc-client -p {resource_id} -c $BOARDS_CONFIG/{resource_id}_remote.yaml boot_sw {boot_mode}"

            # Combine environment setup and fc-client command
            full_command = env_setup_script + "\n" + fc_command

            try:
                # Record start time
                start_time = time.time()

                # Execute the command using bash
                result = subprocess.run(
                    ["bash", "-c", full_command],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )

                # Calculate execution time
                end_time = time.time()
                execution_time = end_time - start_time
                if result.returncode == 0:
                    return {
                        "resource_id": resource_id,
                        "operation": "boot_mode_switch",
                        "success": True,
                        "boot_mode": boot_mode,
                        "executed_at": current_time,
                        "message": f"Successfully switched {resource_id} to {boot_mode} boot mode",
                        "command_executed": fc_command,
                        "stdout": result.stdout.strip() if result.stdout else "",
                        "execution_time": f"{execution_time:.2f} seconds",
                    }

                return {
                    "resource_id": resource_id,
                    "operation": "boot_mode_switch",
                    "success": False,
                    "boot_mode": boot_mode,
                    "error": f"Command failed with return code {result.returncode}",
                    "command_executed": fc_command,
                    "stderr": result.stderr.strip() if result.stderr else "",
                    "stdout": result.stdout.strip() if result.stdout else "",
                    "troubleshooting": [
                        f"• Ensure resource {resource_id} is locked and accessible",
                        "• Check that FC environment is properly configured",
                        "• Verify the resource configuration file exists",
                        "• Check network connectivity to the resource",
                    ],
                }
            except subprocess.TimeoutExpired:
                return {
                    "resource_id": resource_id,
                    "operation": "boot_mode_switch",
                    "success": False,
                    "boot_mode": boot_mode,
                    "error": "Command timed out after 120 seconds",
                    "command_executed": fc_command,
                    "troubleshooting": [
                        "• Check network connectivity to the resource",
                        "• Verify the resource is responsive",
                        "• Try again with increased verbosity for more details",
                    ],
                }
            except Exception as exce:
                return {
                    "resource_id": resource_id,
                    "operation": "boot_mode_switch",
                    "success": False,
                    "boot_mode": boot_mode,
                    "error": f"Unexpected error: {str(exce)}",
                    "command_executed": fc_command,
                    "fallback_manual_command": [
                        "If automatic execution fails, run these commands manually:",
                        "source /opt/fc_env/env.sh || source ~/.fc_env/env.sh",
                        fc_command,
                    ],
                }

        @self.mcp.tool()
        def flash_usb_boot_nexus(
            resource_id: str,
            release_build_plan: str,
            build_number: str,
            verbose: int = 0,
            script_name: Optional[str] = None,
        ) -> Dict[str, Any]:
            """
            Flash/burn/deploy image using USB Boot with Nexus plan.

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                release_build_plan: Release build plan
                (e.g.,
                'Linux_Factory',
                'Linux_Factory_Dev',
                'Linux_Factory_Rebase',
                'Linux_IMX952_Bringup'
                )
                build_number: Build number for the release (e.g., '668')
                verbose: Verbosity level (0-3)
                script_name: Custom name for the generated script (optional)

            Returns:
                Dictionary with script generation result and execution instructions
            """
            return self._generate_flash_script(
                resource_id=resource_id,
                flash_type="usb_boot_nexus",
                verbose=verbose,
                script_name=script_name,
                release_build_plan=release_build_plan,
                build_number=build_number,
            )

        @self.mcp.tool()
        def flash_usb_boot_uri(
            resource_id: str,
            uboot_uri: Optional[str] = None,
            dtb_uri: Optional[str] = None,
            kernel_uri: Optional[str] = None,
            rootfs_uri: Optional[str] = None,
            verbose: int = 0,
            script_name: Optional[str] = None,
        ) -> Dict[str, Any]:
            """
            Flash/burn/deploy image using USB Boot with flexible URIs (local paths or URLs).

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                uboot_uri: U-boot image URI (local path or URL)
                dtb_uri: Device tree blob URI (local path or URL)
                kernel_uri: Kernel image URI (local path or URL)
                rootfs_uri: Root filesystem URI (local path or URL) (OPTIONAL - can be None/omitted)
                verbose: Verbosity level (0-3)
                script_name: Custom name for the generated script (optional)

            Returns:
                Dictionary with script generation result and execution instructions

            Note:
                - Each URI parameter can be either a local file path or a URL
                - URLs are detected automatically (http://, https://, ftp://)
                - You can mix local paths and URLs (e.g., local dtb with URL rootfs)
                - The rootfs_uri parameter is optional
                - At least uboot_uri, dtb_uri, and kernel_uri must be provided

            Examples:
                - Local files: uboot_uri="/path/to/u-boot.bin"
                - URLs: uboot_uri="http://server.com/images/u-boot.bin"
                - Mixed: dtb_uri="/local/file.dtb", rootfs_uri="http://server.com/rootfs.tar.gz"
            """
            return self._generate_flash_script(
                resource_id=resource_id,
                flash_type="usb_boot_uri",
                verbose=verbose,
                script_name=script_name,
                uboot_uri=uboot_uri,
                dtb_uri=dtb_uri,
                kernel_uri=kernel_uri,
                rootfs_uri=rootfs_uri,
            )

        @self.mcp.tool()
        def flash_non_usb_boot_uri(
            resource_id: str,
            uboot_uri: Optional[str] = None,
            rootfs_uri: Optional[str] = None,
            boot_target: str = "sd",
            verbose: int = 0,
            script_name: Optional[str] = None,
        ) -> Dict[str, Any]:
            """
            Flash/burn/deploy image using Non-USB Boot with flexible URIs (local paths or URLs).

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                uboot_uri: U-boot image URI - can be local path or URL (OPTIONAL - can be None/omitted)
                rootfs_uri: Root filesystem URI (.wic.zst format) - can be local path or URL (OPTIONAL - can be None/omitted)
                boot_target: Boot target ('sd' or 'emmc')
                verbose: Verbosity level (0-3)
                script_name: Custom name for the generated script (optional)

            Returns:
                Dictionary with script generation result and execution instructions

            Note:
                - At least one of uboot_uri or rootfs_uri must be provided
                - Each URI parameter can be either a local file path or a URL
                - URLs are detected automatically (http://, https://, ftp://)
                - Local files will be uploaded to the server via download_custom_image.sh
                - URLs will be used directly in the fc-client bootstrap command
                - If both are provided, both u-boot and rootfs will be flashed
                - If only one is provided, only that component will be flashed

            Examples:
                - URL: uboot_uri="https://server.com/imx-boot.bin"
                - Local: uboot_uri="/home/user/imx-boot.bin"
                - Mixed: uboot_uri="/local/imx-boot.bin", rootfs_uri="https://server.com/rootfs.wic.zst"
            """
            return self._generate_flash_script(
                resource_id=resource_id,
                flash_type="non_usb_boot_uri",
                verbose=verbose,
                script_name=script_name,
                uboot_uri=uboot_uri,
                rootfs_uri=rootfs_uri,
                boot_target=boot_target,
            )

    def _generate_flash_script(
        self,
        resource_id: str,
        flash_type: str,
        verbose: int = 0,
        script_name: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Internal method to generate flash scripts for different scenarios.
        """
        # Validate required parameters based on flash type
        validation_error = self._validate_flash_parameters(flash_type, **kwargs)
        if validation_error:
            return {
                "resource_id": resource_id,
                "operation": f"flash_{flash_type}",
                "success": False,
                "error": validation_error,
            }

        # Generate script filename
        if script_name is None:
            script_name = f"flash_{flash_type}_{resource_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sh"
        elif not script_name.endswith(".sh"):
            script_name += ".sh"

        # Build verbose flags
        verbose_flags = ("-v " * verbose).strip() if verbose > 0 else ""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check for missing rootfs and prepare warnings
        warnings = []
        if flash_type == "usb_boot_uri":
            if not kwargs.get("rootfs_uri"):
                warnings.append(
                    "No rootfs specified - will use previous rootfs deployed in NFS server"
                )
        elif flash_type == "non_usb_boot_uri":
            if not kwargs.get("rootfs_uri"):
                warnings.append(
                    "The rootfs may not be available - only u-boot will be flashed"
                )

        # Generate script content based on flash type
        script_content = self._get_script_content(
            resource_id, flash_type, verbose_flags, current_time, **kwargs
        )

        try:
            # Write and make executable
            with open(script_name, "w", encoding="utf-8") as f_script:
                f_script.write(script_content)

            current_permissions = os.stat(script_name).st_mode
            os.chmod(script_name, current_permissions | stat.S_IEXEC)

            script_path = os.path.abspath(script_name)

            result = {
                "resource_id": resource_id,
                "operation": f"flash_{flash_type}",
                "success": True,
                "script_generated": True,
                "script_path": script_path,
                "script_name": script_name,
                "generated_at": current_time,
                "flash_type": flash_type,
                "message": f"Flash script generated successfully: {script_name}",
                "execution_instructions": [
                    "1. Open a new terminal session",
                    f"2. Navigate to the script location: cd {os.path.dirname(script_path)}",
                    f"3. Execute the script: ./{script_name}",
                    "",
                    "The script will handle the complete flashing workflow automatically.",
                ],
            }

            # Add warnings if any
            if warnings:
                result["warnings"] = warnings

            return result

        except PermissionError:
            return {
                "resource_id": resource_id,
                "operation": f"flash_{flash_type}",
                "success": False,
                "error": f"Permission denied: Cannot create script file {script_name}",
                "suggestion": "Try running from a directory where you have write permissions, or specify a different script_name",
            }
        except Exception as exce:
            return {
                "resource_id": resource_id,
                "operation": f"flash_{flash_type}",
                "success": False,
                "error": f"Failed to create script: {str(exce)}",
            }

    def _validate_flash_parameters(self, flash_type: str, **kwargs) -> Optional[str]:
        """
        Validate required parameters for each flash type.
        """
        if flash_type == "usb_boot_nexus":
            required = ["release_build_plan", "build_number"]
        elif flash_type == "usb_boot_uri":
            # At least uboot_uri, dtb_uri, and kernel_uri must be provided
            required = ["uboot_uri", "dtb_uri", "kernel_uri"]
        elif flash_type == "non_usb_boot_uri":
            # At least one of uboot_uri or rootfs_uri must be provided
            if not kwargs.get("uboot_uri") and not kwargs.get("rootfs_uri"):
                return "At least one of uboot_uri or rootfs_uri must be provided"
            return None
        else:
            return f"Unknown flash type: {flash_type}"

        missing = [param for param in required if not kwargs.get(param)]
        if missing:
            return f"Missing required parameters: {', '.join(missing)}"

        return None

    def _format_fc_command(self, base_command: str, verbose_flags: str) -> str:
        """
        Helper to format fc-client commands with proper verbose flag placement.
        """
        if verbose_flags:
            return f"{base_command} {verbose_flags}"
        return base_command

    def _get_script_content(
        self,
        resource_id: str,
        flash_type: str,
        verbose_flags: str,
        current_time: str,
        **kwargs,
    ) -> str:
        """
        Generate script content based on flash type and parameters.
        """
        base_header = f"""#!/bin/bash
# Auto-generated flash script
# Resource: {resource_id}
# Flash Type: {flash_type}
# Generated on: {current_time}

set -e  # Exit on any error

echo "=========================================="
echo "Flash/Burn/Deploy Image Workflow"
echo "Resource: {resource_id}"
echo "Type: {flash_type}"
echo "=========================================="

# Environment setup
echo "Setting up environment..."
if [ -f "/opt/fc_env/env.sh" ]; then
    source /opt/fc_env/env.sh
elif [ -f "$HOME/.fc_env/env.sh" ]; then
    source ~/.fc_env/env.sh
else
    echo "ERROR: FC environment not found!"
    exit 1
fi

"""

        if flash_type == "usb_boot_nexus":
            boot_cmd = self._format_fc_command(
                f'fc-client -p {resource_id} -c "$BOARDS_CONFIG/{resource_id}_remote.yaml" boot_sw usb',
                verbose_flags,
            )
            bootstrap_cmd = self._format_fc_command(
                f"fc-client -p {resource_id} bootstrap {resource_id}_cmd.txt",
                verbose_flags,
            )

            return (
                base_header
                + f"""# USB Boot - Nexus Plan
echo "Step 1: Downloading yocto image from nexus..."
download_yocto_image.sh {resource_id} {self._escape_bash_arg(kwargs['release_build_plan'])} {self._escape_bash_arg(kwargs['build_number'])} nexus

echo "Step 2: Switch to USB boot..."
{boot_cmd}

echo "Step 3: Bootstrapping device..."
{bootstrap_cmd}

echo "SUCCESS: USB Boot Nexus flash completed!"
"""
            )

        if flash_type == "usb_boot_uri":
            boot_cmd = self._format_fc_command(
                f'fc-client -p {resource_id} -c "$BOARDS_CONFIG/{resource_id}_remote.yaml" boot_sw usb',
                verbose_flags,
            )
            bootstrap_cmd = self._format_fc_command(
                f"fc-client -p {resource_id} bootstrap {resource_id}_cmd.txt",
                verbose_flags,
            )

            download_args = self._build_download_custom_image_args(
                resource_id, **kwargs
            )

            return (
                base_header
                + f"""# USB Boot - URI (URLs and/or Local Files)
echo "Step 1: Downloading/setting up custom images..."
download_custom_image.sh {download_args}

echo "Step 2: Switch to USB boot..."
{boot_cmd}

echo "Step 3: Bootstrapping device..."
{bootstrap_cmd}

echo "SUCCESS: USB Boot URI flash completed!"
"""
            )

        if flash_type == "non_usb_boot_uri":
            boot_target = kwargs.get("boot_target", "sd")
            usb_boot_cmd = self._format_fc_command(
                f'fc-client -p {resource_id} -c "$BOARDS_CONFIG/{resource_id}_remote.yaml" boot_sw usb',
                verbose_flags,
            )
            target_boot_cmd = self._format_fc_command(
                f'fc-client -p {resource_id} -c "$BOARDS_CONFIG/{resource_id}_remote.yaml" boot_sw {boot_target}',
                verbose_flags,
            )

            uboot_uri = kwargs.get("uboot_uri")
            rootfs_uri = kwargs.get("rootfs_uri")

            # Determine if we need to download local files
            has_local_files = False
            uboot_is_local = uboot_uri and not self._is_url(uboot_uri)
            rootfs_is_local = rootfs_uri and not self._is_url(rootfs_uri)

            if uboot_is_local or rootfs_is_local:
                has_local_files = True

            script_content = (
                base_header + "# Non-USB Boot - URI (URLs and/or Local Files)"
            )

            # Step 1: Download local files if needed
            if has_local_files:
                download_args = [f"-p {resource_id}"]

                # Always add --uboot (use actual file if local, /dev/null if URL or not provided)
                if uboot_is_local:
                    download_args.append(f"--uboot {self._escape_bash_arg(uboot_uri)}")
                else:
                    download_args.append("--uboot /dev/null")

                # Add dummy dtb and kernel (required by download_custom_image.sh)
                download_args.append("--dtb /dev/null")
                download_args.append("--kernel /dev/null")

                # Add rootfs if it's a local file
                if rootfs_is_local:
                    download_args.append(
                        f"--rootfs {self._escape_bash_arg(rootfs_uri)}"
                    )

                download_cmd = "download_custom_image.sh " + " \\\n    ".join(
                    download_args
                )

                script_content += f"""echo "Step 1: Uploading local files to server..."
{download_cmd}

echo "Step 2: Initial USB boot..."
{usb_boot_cmd}

"""
                step_num = 3
            else:
                script_content += f"""echo "Step 1: Initial USB boot..."
{usb_boot_cmd}

"""
                step_num = 2

            # Determine bootstrap command and file paths
            # For local files, use server paths; for URLs, use URLs directly
            if uboot_uri and rootfs_uri:
                # Both provided
                if uboot_is_local:
                    uboot_path = (
                        f"/tftpboot/work/{resource_id}_{os.path.basename(uboot_uri)}"
                    )
                else:
                    uboot_path = uboot_uri

                if rootfs_is_local:
                    rootfs_path = (
                        f"/tftpboot/{resource_id}_{os.path.basename(rootfs_uri)}"
                    )
                else:
                    rootfs_path = rootfs_uri

                bootstrap_cmd = self._format_fc_command(
                    f'fc-client -p {resource_id} bootstrap "-b {boot_target}_all {self._escape_bash_arg(uboot_path)} {self._escape_bash_arg(rootfs_path)}"',
                    verbose_flags,
                )
                step_desc = f"Bootstrapping u-boot and rootfs to {boot_target}_all"

            elif uboot_uri:
                # Only uboot provided
                if uboot_is_local:
                    uboot_path = (
                        f"/tftpboot/work/{resource_id}_{os.path.basename(uboot_uri)}"
                    )
                else:
                    uboot_path = uboot_uri

                bootstrap_cmd = self._format_fc_command(
                    f'fc-client -p {resource_id} bootstrap "-b {boot_target} {self._escape_bash_arg(uboot_path)}"',
                    verbose_flags,
                )
                step_desc = f"Bootstrapping u-boot to {boot_target}"

            elif rootfs_uri:
                # Only rootfs provided
                if rootfs_is_local:
                    rootfs_path = (
                        f"/tftpboot/{resource_id}_{os.path.basename(rootfs_uri)}"
                    )
                else:
                    rootfs_path = rootfs_uri

                bootstrap_cmd = self._format_fc_command(
                    f'fc-client -p {resource_id} bootstrap "-b {boot_target}_all {self._escape_bash_arg(rootfs_path)}"',
                    verbose_flags,
                )
                step_desc = f"Bootstrapping rootfs to {boot_target}_all"

            script_content += f"""echo "Step {step_num}: {step_desc}..."
{bootstrap_cmd}

echo "Step {step_num + 1}: Switching to {boot_target} boot..."
{target_boot_cmd}

echo "SUCCESS: Non-USB Boot URI flash completed!"
"""
            return script_content

        return base_header + "echo 'Unknown flash type'"
