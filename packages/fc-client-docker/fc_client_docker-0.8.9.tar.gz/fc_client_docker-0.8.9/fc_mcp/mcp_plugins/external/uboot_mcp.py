# -*- coding: utf-8 -*-
#
# Copyright 2025 NXP
#
# SPDX-License-Identifier: MIT

"""
External sample MCP describe how to retrieve U-Boot configuration references for board predeploy operations.
"""


import os
import stat
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
import yaml
from bs4 import BeautifulSoup

from fc_common.config import Config
from fc_mcp.mcp_base import MCPPlugin


class Plugin(MCPPlugin):
    def __init__(self, mcp):
        super().__init__(mcp)
        user_config = Config.load_user_config()
        self.predeploy_knowledge_url = user_config.get("PREDEPLOY_KNOWLEDGE_URL", "")
        self.boards_config_dir = os.environ.get("BOARDS_CONFIG", "")

    def register_tools(self):
        @self.mcp.tool()
        def get_board_server_ip(resource_id: str) -> Dict[str, Any]:
            """
            Get the board server IP address from the board's remote configuration file.

            This function reads the board's remote YAML configuration file and extracts
            the NFS server IP address from the options section.

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')

            Returns:
                Dictionary with board server IP information or error details

            Examples:
                - get_board_server_ip("imx95-19x19-evk-sh62")
            """
            if not self.boards_config_dir:
                return {
                    "resource_id": resource_id,
                    "operation": "get_board_server_ip",
                    "success": False,
                    "error": "BOARDS_CONFIG environment variable is not set",
                }

            # Construct the remote config file path
            remote_config_file = os.path.join(
                self.boards_config_dir, f"{resource_id}_remote.yaml"
            )

            if not os.path.exists(remote_config_file):
                return {
                    "resource_id": resource_id,
                    "operation": "get_board_server_ip",
                    "success": False,
                    "error": f"Remote configuration file not found: {remote_config_file}",
                    "suggestion": f"Ensure the file {resource_id}_remote.yaml exists in {self.boards_config_dir}",
                }

            try:
                with open(remote_config_file, "r", encoding="utf-8") as f_config:
                    config_data = yaml.safe_load(f_config)

                if not config_data:
                    return {
                        "resource_id": resource_id,
                        "operation": "get_board_server_ip",
                        "success": False,
                        "error": f"Configuration file is empty: {remote_config_file}",
                    }

                # Extract nfs_server from options
                options = config_data.get("options", {})
                if not options:
                    return {
                        "resource_id": resource_id,
                        "operation": "get_board_server_ip",
                        "success": False,
                        "error": "No 'options' section found in configuration file",
                        "config_file": remote_config_file,
                    }

                nfs_server = options.get("nfs_server")
                if not nfs_server:
                    return {
                        "resource_id": resource_id,
                        "operation": "get_board_server_ip",
                        "success": False,
                        "error": "No 'nfs_server' key found in options section",
                        "config_file": remote_config_file,
                        "available_options": list(options.keys()),
                    }

                return {
                    "resource_id": resource_id,
                    "operation": "get_board_server_ip",
                    "success": True,
                    "board_server_ip": nfs_server,
                    "config_file": remote_config_file,
                    "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

            except yaml.YAMLError as exce:
                return {
                    "resource_id": resource_id,
                    "operation": "get_board_server_ip",
                    "success": False,
                    "error": f"Failed to parse YAML file: {str(exce)}",
                    "config_file": remote_config_file,
                }
            except Exception as exce:
                return {
                    "resource_id": resource_id,
                    "operation": "get_board_server_ip",
                    "success": False,
                    "error": f"Unexpected error: {str(exce)}",
                    "config_file": remote_config_file,
                }

        @self.mcp.tool()
        def get_uboot_config_uri(
            resource_id: str,
            board_server_ip: str,
            uboot_uri: Optional[str] = None,
            dtb_uri: Optional[str] = None,
            kernel_uri: Optional[str] = None,
            rootfs_uri: Optional[str] = None,
            script_name: Optional[str] = None,
        ) -> Dict[str, Any]:
            """
            Generate commands and executable script for uboot configure (NO UUU/USB boot).

            This function provides step-by-step commands to prepare artifacts on the board
            server and U-Boot console commands for manual execution to upgrade kernel
            image, device tree, and rootfs via TFTP/NFS.

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                board_server_ip: Board server IP address (e.g., '192.168.100.180')
                uboot_uri: U-boot image URI (local path or URL) - OPTIONAL
                dtb_uri: Device tree blob URI (local path or URL) - OPTIONAL
                kernel_uri: Kernel image URI (local path or URL) - OPTIONAL
                rootfs_uri: Root filesystem URI (local path or URL) - OPTIONAL
                script_name: Custom name for the generated script (optional)

            Returns:
                Dictionary with preparation commands, U-Boot console commands, and generated script info

            Note:
                - This method does NOT use UUU or USB boot
                - Upgrades are done via U-Boot console using TFTP/NFS
                - At least one of the URI parameters should be provided
                - Each URI can be either a local file path or a URL
                - URLs are detected automatically (http://, https://, ftp://)
                - Step 1: Prepare artifacts on the board server (automated via script)
                - Step 2: Reset U-Boot environment to defaults
                - Step 3: Execute commands manually on the board's U-Boot console
                - An executable script is always generated for Step 1

            Examples:
                - Local files: uboot_uri="./imx-boot.bin", kernel_uri="./Image.bin"
                - URLs: dtb_uri="http://server.com/device-tree.dtb"
                - Mixed: kernel_uri="/local/Image.bin", rootfs_uri="http://server.com/rootfs.tar.zst"
                - Custom script: script_name="prepare_artifacts.sh"
            """
            # Validate that at least one URI is provided
            if not any([uboot_uri, dtb_uri, kernel_uri, rootfs_uri]):
                return {
                    "resource_id": resource_id,
                    "operation": "get_uboot_config_uri",
                    "success": False,
                    "error": "At least one of uboot_uri, dtb_uri, kernel_uri, or rootfs_uri must be provided",
                }

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Build download_custom_image.sh arguments
            download_args = self._build_download_custom_image_args(
                resource_id,
                uboot_uri=uboot_uri,
                dtb_uri=dtb_uri,
                kernel_uri=kernel_uri,
                rootfs_uri=rootfs_uri,
            )

            # Generate Step 1: Preparation command
            preparation_command = f"download_custom_image.sh {download_args}"

            # Generate Step 2: U-Boot environment reset commands
            uboot_reset_commands = ["env default -a", "saveenv", "reset"]

            # Generate Step 3: U-Boot console commands based on provided URIs
            uboot_commands = []

            # Set kernel image path if provided
            if kernel_uri:
                kernel_filename = os.path.basename(kernel_uri)
                uboot_commands.append(
                    f"setenv image {board_server_ip}:{resource_id}_{kernel_filename}"
                )

            # Set device tree blob path if provided
            if dtb_uri:
                dtb_filename = os.path.basename(dtb_uri)
                uboot_commands.append(
                    f"setenv fdtfile {board_server_ip}:{resource_id}_{dtb_filename}"
                )

            # Set NFS root path if rootfs provided
            if rootfs_uri:
                uboot_commands.append(f"setenv nfsroot /nfsroot/{resource_id}")

            # Set serverip after nfsroot
            uboot_commands.append(f"setenv serverip {board_server_ip}")

            # Save environment
            uboot_commands.append("saveenv")

            # Add reset command to reboot with new configuration
            uboot_commands.append("reset")
            # Build component list
            components = []
            if uboot_uri:
                components.append(f"U-Boot: {os.path.basename(uboot_uri)}")
            if kernel_uri:
                components.append(f"Kernel: {os.path.basename(kernel_uri)}")
            if dtb_uri:
                components.append(f"DTB: {os.path.basename(dtb_uri)}")
            if rootfs_uri:
                components.append(f"RootFS: {os.path.basename(rootfs_uri)}")

            # Format U-Boot reset commands for display
            uboot_reset_commands_display = "\n".join(
                [f"u-boot=> {cmd}" for cmd in uboot_reset_commands]
            )

            # Generate STEP 2.5: Bootloader flashing commands (if uboot_uri provided)
            uboot_flash_commands = []
            uboot_flash_commands_display = ""

            if uboot_uri:
                uboot_filename = os.path.basename(uboot_uri)
                uboot_flash_commands = [
                    f"dhcp ${{loadaddr}} {board_server_ip}:work/{resource_id}_{uboot_filename}",
                    "mmc dev",
                    "mmc write ${loadaddr} 0x40 0x2000",
                    "reset",
                ]
                uboot_flash_commands_display = "\n".join(
                    [f"u-boot=> {cmd}" for cmd in uboot_flash_commands]
                )

            # Format U-Boot commands for display
            uboot_commands_display = "\n".join(
                [f"u-boot=> {cmd}" for cmd in uboot_commands]
            )

            # Build instructions list
            instructions = [
                "=" * 70,
                "U-BOOT CONSOLE DIRECT UPGRADE (NO UUU)",
                "=" * 70,
                "",
                "STEP 1: Prepare artifacts on board server",
                "-" * 70,
                "Execute this command in your terminal:",
                "",
                preparation_command,
                "",
                "=" * 70,
                "STEP 2: Reset U-Boot environment to defaults",
                "-" * 70,
                "Connect to the board's U-Boot console and execute these commands:",
                "",
                uboot_reset_commands_display,
                "",
                "IMPORTANT: The 'reset' command will reboot the board.",
                "           After the board reboots, enter U-Boot console again",
                "           before proceeding to the next step.",
                "",
            ]

            # Add STEP 2.5 only if uboot_uri is provided
            if uboot_uri:
                instructions.extend(
                    [
                        "=" * 70,
                        "STEP 2.5: Flash new bootloader (OPTIONAL - USE WITH CAUTION)",
                        "-" * 70,
                        "⚠️  WARNING: This step will update the bootloader on the board!",
                        "⚠️  RISK: Flashing bootloader may brick the board if interrupted.",
                        "⚠️  SKIP this step if the current bootloader works fine.",
                        "",
                        "Only proceed if:",
                        "  • You need a newer bootloader version for compatibility",
                        "  • The board has BCU (Board Control Unit) for recovery",
                        "  • You understand the risks and have admin support available",
                        "",
                        "If you choose to proceed, execute these commands in U-Boot console:",
                        "",
                        uboot_flash_commands_display,
                        "",
                        "After flashing completes:",
                        "  • Execute: reset",
                        "  • Wait for board to reboot",
                        "  • Enter U-Boot console again before proceeding to Step 3",
                        "",
                        "⚠️  If the board fails to boot after this step, contact your admin",
                        "    for manual recovery (especially for boards without BCU).",
                        "",
                    ]
                )

            instructions.extend(
                [
                    "=" * 70,
                    "STEP 3: Execute U-Boot configuration commands",
                    "-" * 70,
                    "After the board has rebooted and you've entered U-Boot console again,",
                    "execute these commands:",
                    "",
                    uboot_commands_display,
                    "",
                    "=" * 70,
                    "",
                    "Note: This method uses TFTP/NFS, NOT UUU or USB boot",
                    "=" * 70,
                ]
            )

            result = {
                "resource_id": resource_id,
                "operation": "get_uboot_config_uri",
                "success": True,
                "board_server_ip": board_server_ip,
                "generated_at": current_time,
                "method": "U-Boot Console (NO UUU/USB boot)",
                "components": components,
                "instructions": instructions,
                "step1_preparation_command": preparation_command,
                "step2_uboot_reset_commands": uboot_reset_commands,
                "step2_uboot_reset_commands_formatted": uboot_reset_commands_display,
                "step3_uboot_commands": uboot_commands,
                "step3_uboot_commands_formatted": uboot_commands_display,
            }

            # Add bootloader flashing info if applicable
            if uboot_uri:
                result["step2_5_uboot_flash_commands"] = uboot_flash_commands
                result[
                    "step2_5_uboot_flash_commands_formatted"
                ] = uboot_flash_commands_display
                result[
                    "step2_5_warning"
                ] = "Bootloader flashing is OPTIONAL and RISKY - skip if current bootloader works"

            # Always generate script
            script_result = self._generate_preparation_script(
                resource_id=resource_id,
                preparation_command=preparation_command,
                uboot_reset_commands=uboot_reset_commands,
                uboot_commands=uboot_commands,
                uboot_flash_commands=uboot_flash_commands if uboot_uri else [],
                board_server_ip=board_server_ip,
                components=components,
                current_time=current_time,
                script_name=script_name,
            )
            result.update(script_result)

            return result

        @self.mcp.tool()
        def get_uboot_config_nexus(
            resource_id: str, build: str = "Linux_Factory", build_number: str = "668"
        ) -> Dict[str, Any]:
            """
            This is for Nexus plan deploy with predeployed images.
            Get U-Boot configuration reference for board predeploy operations.
            Fetches the appropriate U-Boot environment configuration from the TFTP server
            and provides formatted usage instructions.

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                build: Build type (default: 'Linux_Factory')
                build_number: Build number (default: '668')

            Returns:
                Dictionary with U-Boot configuration and usage instructions
            """

            try:
                # Fetch available config files
                board_name = (
                    resource_id.rsplit("-", 1)[0] if "-" in resource_id else resource_id
                )
                available_files = self._fetch_directory_listing()

                if not available_files:
                    return {
                        "board_name": board_name,
                        "operation": "get_uboot_config_nexus",
                        "success": False,
                        "error": "No U-Boot configuration files found on the server",
                        "server_url": self.predeploy_knowledge_url,
                    }

                # Find the appropriate config file for the board
                config_file = self._find_board_config_file(board_name, available_files)

                if not config_file:
                    available_boards = [
                        f.replace("_uboot_env_daily.txt", "") for f in available_files
                    ]
                    return {
                        "board_name": board_name,
                        "operation": "get_uboot_config_nexus",
                        "success": False,
                        "error": f"No configuration found for board '{board_name}'",
                        "available_boards": sorted(available_boards),
                        "suggestion": "Check the board name against the available boards list",
                    }

                # Fetch the config file content
                config_content = self._fetch_uboot_config(config_file)

                # Format the configuration
                formatted_config = self._format_uboot_config(
                    board_name, build, build_number, config_content
                )

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                return {
                    "board_name": board_name,
                    "operation": "get_uboot_config_nexus",
                    "success": True,
                    "config_file_used": config_file,
                    "server_url": self.predeploy_knowledge_url + config_file,
                    "retrieved_at": current_time,
                    "build_info": {
                        "build": build,
                        "build_number": build_number,
                        "board": board_name,
                    },
                    "uboot_config": formatted_config,
                    "usage_instructions": [
                        "1. Boot the board and interrupt U-Boot to get to the U-Boot prompt",
                        "2. First, reset U-Boot environment to defaults:",
                        "   - Execute: env default -a",
                        "   - Execute: saveenv",
                        "   - Execute: reset",
                        "3. After the board reboots, enter U-Boot console again",
                        "4. Copy and paste the U-Boot commands below one by one",
                        "5. Use 'saveenv' command to save the environment to persistent storage",
                        "6. Use 'reset' or 'boot' command to continue with the new configuration",
                    ],
                    "important_notes": [
                        "• MUST reset U-Boot environment before applying new configuration",
                        "• MUST execute 'reset' command after 'env default -a' and 'saveenv'",
                        "• MUST enter U-Boot console again after the board reboots",
                        f"• Ensure build {build} #{build_number} artifacts are available",
                        "• Make sure network connectivity is properly configured",
                        "• Backup current U-Boot environment before applying changes",
                        "• Verify all paths and URLs are accessible from the target board",
                    ],
                    "troubleshooting": {
                        "if_commands_fail": "Check network connectivity and server accessibility",
                        "if_files_not_found": f"Verify build {build} #{build_number} is available on the server",
                        "if_boot_fails": "Check U-Boot environment variables and file paths",
                        "if_network_issues": "Verify IP configuration and TFTP server accessibility",
                    },
                }

            except Exception as exce:
                return {
                    "board_name": board_name,
                    "operation": "get_uboot_config_nexus",
                    "success": False,
                    "error": f"Failed to get U-Boot configuration: {str(exce)}",
                    "fallback_manual_steps": [
                        f"1. Open browser and go to {self.predeploy_knowledge_url}",
                        f"2. Look for file containing '{board_name}' in the name",
                        "3. Download the appropriate *_uboot_env_daily.txt file",
                        f"4. Replace placeholders with build={build}, build_number={build_number}",
                        "5. Reset U-Boot environment: env default -a, then saveenv, then reset",
                        "6. After the board reboots, enter U-Boot console again",
                        "7. Apply the configuration manually in U-Boot prompt",
                    ],
                }

        @self.mcp.tool()
        def list_available_boards() -> Dict[str, Any]:
            """
            List all available boards that have U-Boot configurations.
            Fetches the directory listing from TFTP server and extracts board names.

            Returns:
                Dictionary with list of available boards and their config files
            """

            try:
                available_files = self._fetch_directory_listing()

                if not available_files:
                    return {
                        "operation": "list_available_boards",
                        "success": False,
                        "error": "No U-Boot configuration files found on the server",
                        "server_url": self.predeploy_knowledge_url,
                    }

                boards = []
                for filename in available_files:
                    if filename not in ["template_uboot_env_daily.txt", "template.txt"]:
                        board_name = filename.replace("_uboot_env_daily.txt", "")
                        boards.append(
                            {"board_name": board_name, "config_file": filename}
                        )

                boards.sort(key=lambda x: x["board_name"])

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                return {
                    "operation": "list_available_boards",
                    "success": True,
                    "server_url": self.predeploy_knowledge_url,
                    "retrieved_at": current_time,
                    "total_boards": len(boards),
                    "available_boards": boards,
                    "board_names_only": [board["board_name"] for board in boards],
                    "usage_tip": "Use any of these board names with get_uboot_config() function",
                }

            except Exception as exce:
                return {
                    "operation": "list_available_boards",
                    "success": False,
                    "error": f"Failed to list available boards: {str(exce)}",
                    "fallback_manual_steps": [
                        f"1. Open browser and go to {self.predeploy_knowledge_url}",
                        "2. Look for files ending with '_uboot_env_daily.txt'",
                        "3. Extract board names from filenames (remove '_uboot_env_daily.txt' suffix)",
                    ],
                }

    def _generate_preparation_script(
        self,
        resource_id: str,
        preparation_command: str,
        uboot_reset_commands: List[str],
        uboot_commands: List[str],
        uboot_flash_commands: List[str],
        board_server_ip: str,
        components: List[str],
        current_time: str,
        script_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate an executable bash script for preparing artifacts on the board server.
        """
        # Generate script filename
        if script_name is None:
            script_name = f"prepare_uboot_artifacts_{resource_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sh"
        elif not script_name.endswith(".sh"):
            script_name += ".sh"

        # Format U-Boot reset commands for script output
        escaped_reset_commands = [
            cmd.replace("$", "\\$") for cmd in uboot_reset_commands
        ]
        uboot_reset_commands_echo = "\n".join(
            [f'echo "u-boot=> {cmd}"' for cmd in escaped_reset_commands]
        )

        # Format U-Boot commands for script output (to be echoed)
        # Escape $ signs so they print literally instead of being interpreted by bash
        escaped_commands = [cmd.replace("$", "\\$") for cmd in uboot_commands]
        uboot_commands_echo = "\n".join(
            [f'echo "u-boot=> {cmd}"' for cmd in escaped_commands]
        )

        # Build script content
        script_content = f"""#!/bin/bash
# Auto-generated U-Boot preparation script
# Resource: {resource_id}
# Board Server IP: {board_server_ip}
# Generated on: {current_time}
#
# Components to be prepared:
# {chr(10).join(['# - ' + comp for comp in components])}

set -e  # Exit on any error

echo "=========================================="
echo "U-Boot Artifacts Preparation"
echo "Resource: {resource_id}"
echo "Board Server IP: {board_server_ip}"
echo "=========================================="

# STEP 1: Prepare artifacts on board server
echo ""
echo "STEP 1: Uploading artifacts to board server..."
echo "Executing: {preparation_command}"
echo ""

{preparation_command}

echo ""
echo "=========================================="
echo "SUCCESS: Artifacts prepared on board server!"
echo "=========================================="
echo ""

echo "STEP 2: Reset U-Boot environment to defaults"
echo "----------------------------------------"
echo "Connect to the board's U-Boot console and execute these commands:"
echo ""
{uboot_reset_commands_echo}
echo ""
echo "IMPORTANT: The 'reset' command will reboot the board."
echo "           After the board reboots, enter U-Boot console again"
echo "           before proceeding to the next step."
echo ""
"""

        # Add STEP 2.5 for bootloader flashing if uboot flash commands provided
        if uboot_flash_commands:
            escaped_flash_commands = [
                cmd.replace("$", "\\$") for cmd in uboot_flash_commands
            ]
            uboot_flash_commands_echo = "\n".join(
                [f'echo "u-boot=> {cmd}"' for cmd in escaped_flash_commands]
            )

            script_content += f"""echo "=========================================="
echo "STEP 2.5: Flash new bootloader (OPTIONAL - USE WITH CAUTION)"
echo "----------------------------------------"
echo "⚠️  WARNING: This step will update the bootloader on the board!"
echo "⚠️  RISK: Flashing bootloader may brick the board if interrupted."
echo "⚠️  SKIP this step if the current bootloader works fine."
echo ""
echo "Only proceed if:"
echo "  • You need a newer bootloader version for compatibility"
echo "  • The board has BCU (Board Control Unit) for recovery"
echo "  • You understand the risks and have admin support available"
echo ""
echo "If you choose to proceed, execute these commands in U-Boot console:"
echo ""
{uboot_flash_commands_echo}
echo ""
echo "After flashing completes:"
echo "  • Execute: reset"
echo "  • Wait for board to reboot"
echo "  • Enter U-Boot console again before proceeding to Step 3"
echo ""
echo "⚠️  If the board fails to boot after this step, contact your admin"
echo "    for manual recovery (especially for boards without BCU)."
echo ""
"""
        script_content += f"""echo "=========================================="
echo "STEP 3: Execute U-Boot configuration commands"
echo "----------------------------------------"
echo "After the board has rebooted and you've entered U-Boot console again,"
echo "execute these commands:"
echo ""
{uboot_commands_echo}
echo ""
echo "Note: This method uses TFTP/NFS, NOT UUU or USB boot"
echo "=========================================="
"""

        try:
            # Write script file
            with open(script_name, "w", encoding="utf-8") as f_script:
                f_script.write(script_content)

            # Make script executable
            current_permissions = os.stat(script_name).st_mode
            os.chmod(script_name, current_permissions | stat.S_IEXEC)

            script_path = os.path.abspath(script_name)

            return {
                "script_generated": True,
                "script_path": script_path,
                "script_name": script_name,
                "script_message": f"Preparation script generated successfully: {script_name}",
                "script_execution_instructions": [
                    "=" * 70,
                    "SCRIPT EXECUTION INSTRUCTIONS",
                    "=" * 70,
                    "",
                    "1. Open a new terminal session",
                    f"2. Navigate to the script location: cd {os.path.dirname(script_path) or '.'}",
                    f"3. Execute the script: ./{script_name}",
                    "",
                    "The script will automatically upload artifacts to the board server.",
                    "After successful execution, follow the U-Boot console commands shown.",
                    "",
                    "IMPORTANT: You must reset U-Boot environment first (Step 2),",
                    "           execute 'reset' command to reboot the board,",
                    "           then enter U-Boot console again before executing Step 3 commands.",
                    "=" * 70,
                ],
            }

        except PermissionError:
            return {
                "script_generated": False,
                "script_error": f"Permission denied: Cannot create script file {script_name}",
                "script_suggestion": "Try running from a directory where you have write permissions, or specify a different script_name",
            }
        except Exception as exce:
            return {
                "script_generated": False,
                "script_error": f"Failed to create script: {str(exce)}",
            }

    def _fetch_directory_listing(self) -> List[str]:
        """Fetch and parse the directory listing from TFTP server"""
        response = requests.get(self.predeploy_knowledge_url, timeout=30)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch directory listing: HTTP {response.status_code}"
            )

        soup = BeautifulSoup(response.text, "html.parser")

        files = []
        for link in soup.find_all("a"):  # pylint: disable=not-an-iterable
            href = link.get("href")
            if href and href.endswith("_uboot_env_daily.txt"):
                files.append(href)

        return files

    def _fetch_uboot_config(self, filename: str) -> str:
        """Fetch the content of a specific U-Boot config file"""
        file_url = f"{self.predeploy_knowledge_url}{filename}"
        response = requests.get(file_url, timeout=30)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch file {filename}: HTTP {response.status_code}"
            )

        return response.text

    def _find_board_config_file(
        self, board_name: str, available_files: List[str]
    ) -> Optional[str]:
        """Find the appropriate config file for the given board name"""
        # Normalize board name
        normalized_board = board_name.lower().replace("-", "").replace("_", "")

        # Try exact match first
        for filename in available_files:
            file_board = (
                filename.replace("_uboot_env_daily.txt", "")
                .replace("-", "")
                .replace("_", "")
            )
            if normalized_board == file_board.lower():
                return filename

        # Try partial match
        for filename in available_files:
            file_board = filename.replace("_uboot_env_daily.txt", "")
            if normalized_board in file_board.lower().replace("-", "").replace("_", ""):
                return filename

        return None

    def _format_uboot_config(
        self, board_name: str, build: str, build_number: str, config_content: str
    ) -> str:
        """Format the U-Boot configuration with variable substitution"""

        # Replace placeholders in config content
        formatted_content = config_content.replace("${BUILD}", build)
        formatted_content = formatted_content.replace("${BUILD_NUMBER}", build_number)
        formatted_content = formatted_content.replace("${BOARD}", board_name)

        return formatted_content.strip()
