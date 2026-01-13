# -*- coding: utf-8 -*-
#
# Copyright 2025 NXP
#
# SPDX-License-Identifier: MIT

"""
Internal embeded MCP describe common FC operations
"""


import json
import subprocess
from typing import Any, Dict, List, Optional

from fc_mcp.mcp_base import MCPPlugin


class Plugin(MCPPlugin):
    def register_tools(self):
        def run_fc_client_command(args: List[str]) -> Dict[str, Any]:
            """
            Execute fc-client command and return parsed result.

            Args:
                args: List of command arguments for fc-client

            Returns:
                Dictionary with command result
            """
            try:
                # Run fc-client command
                cmd = ["fc-client"] + args
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )

                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                    "returncode": result.returncode,
                    "command": " ".join(cmd),
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "Command timed out",
                    "command": " ".join(cmd),
                }
            except FileNotFoundError:
                return {
                    "success": False,
                    "error": "fc-client command not found. Please ensure fc-client is installed and in PATH.",
                    "command": " ".join(cmd),
                }
            except Exception as exce:
                return {"success": False, "error": str(exce), "command": " ".join(cmd)}

        @self.mcp.tool()
        def lock(resource_id: str, verbose: int = 0) -> Dict[str, Any]:
            """
            Acquire a lock on a resource using fc-client.

            Args:
                resource_id: Unique identifier for the resource to lock (e.g., 'imx95-19x19-evk-sh62')
                verbose: Verbosity level (0-3)

            Returns:
                Dictionary with lock status and details
            """
            args = ["-p", resource_id]
            if verbose > 0:
                args.extend(["-v"] * verbose)
            args.append("lock")

            result = run_fc_client_command(args)

            return {
                "resource_id": resource_id,
                "operation": "lock",
                "success": result["success"],
                "message": result.get("stdout", result.get("error", "Unknown error")),
                "error": result.get("stderr") if not result["success"] else None,
                "command": result["command"],
            }

        @self.mcp.tool()
        def unlock(resource_id: str, verbose: int = 0) -> Dict[str, Any]:
            """
            Release a lock on a resource using fc-client.

            Args:
                resource_id: Unique identifier for the resource to unlock
                verbose: Verbosity level (0-3)

            Returns:
                Dictionary with unlock status and details
            """
            args = ["-p", resource_id]
            if verbose > 0:
                args.extend(["-v"] * verbose)
            args.append("unlock")

            result = run_fc_client_command(args)

            return {
                "resource_id": resource_id,
                "operation": "unlock",
                "success": result["success"],
                "message": result.get("stdout", result.get("error", "Unknown error")),
                "error": result.get("stderr") if not result["success"] else None,
                "command": result["command"],
            }

        @self.mcp.tool()
        def status(
            resource_id: Optional[str] = None,
            farm_type: Optional[str] = None,
            device_type: Optional[str] = None,
            peripheral_info: Optional[str] = None,
            verbose: int = 0,
            format_json: bool = True,
        ) -> Dict[str, Any]:
            """
            Check the status of resources using fc-client.

            Args:
                resource_id: Specific resource to check (optional)
                farm_type: Filter by farm type (optional)
                device_type: Filter by device type (optional)
                peripheral_info: Filter by peripheral info (optional)
                verbose: Verbosity level (0-3)
                format_json: Return JSON format

            Returns:
                Dictionary with resource status information
            """
            args = []

            if resource_id:
                args.extend(["-p", resource_id])
            if farm_type:
                args.extend(["-f", farm_type])
            if device_type:
                args.extend(["-d", device_type])
            if peripheral_info:
                args.extend(["-i", peripheral_info])

            args.append("status")

            if format_json:
                args.append("--json")

            if verbose > 0:
                args.extend(["-v"] * verbose)

            result = run_fc_client_command(args)

            if result["success"] and format_json:
                try:
                    # Parse JSON output from fc-client
                    status_data = json.loads(result["stdout"])
                    return {
                        "success": True,
                        "resources": status_data,
                        "total_resources": len(status_data)
                        if isinstance(status_data, list)
                        else 1,
                        "command": result["command"],
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Failed to parse JSON output from fc-client",
                        "raw_output": result["stdout"],
                        "command": result["command"],
                    }

            return {
                "success": result["success"],
                "message": result.get("stdout", result.get("error", "Unknown error")),
                "error": result.get("stderr") if not result["success"] else None,
                "command": result["command"],
            }

        @self.mcp.tool()
        def cluster_info(
            resource_id: Optional[str] = None, verbose: int = 0
        ) -> Dict[str, Any]:
            """
            Get cluster information using fc-client.

            Args:
                resource_id: Specific resource to get cluster info for (optional)
                verbose: Verbosity level (0-3)

            Returns:
                Dictionary with cluster information
            """
            args = []

            if resource_id:
                args.extend(["-p", resource_id])
            if verbose > 0:
                args.extend(["-v"] * verbose)

            args.append("cluster-info")

            result = run_fc_client_command(args)

            return {
                "operation": "cluster-info",
                "success": result["success"],
                "cluster_info": result.get(
                    "stdout", result.get("error", "Unknown error")
                ),
                "error": result.get("stderr") if not result["success"] else None,
                "command": result["command"],
            }

        @self.mcp.tool()
        def all_locks(verbose: int = 0) -> Dict[str, Any]:
            """
            Get lock information of resources using fc-client.
            So we can check the resource is locked by which user.

            Args:
                verbose: Verbosity level (0-3)

            Returns:
                Dictionary with all active locks information
            """
            args = []

            if verbose > 0:
                args.extend(["-v"] * verbose)

            args.append("all-locks")

            result = run_fc_client_command(args)

            return {
                "operation": "all-locks",
                "success": result["success"],
                "locks_info": result.get(
                    "stdout", result.get("error", "Unknown error")
                ),
                "error": result.get("stderr") if not result["success"] else None,
                "command": result["command"],
            }

        @self.mcp.tool()
        def advanced_features(resource_id: str) -> Dict[str, Any]:
            """
            Check advanced features of a resource using fc-client.
            This retrieves detailed resource information including supported modes like predeploy, uuu, bcu etc.
            predeploy: means the images already predeployed, you can operate uboot to load the images
            uuu: means Universal Update Utility
            bcu: means Board Remote Control Utilities

            Args:
                resource_id: Unique identifier for the resource to check

            Returns:
                Dictionary with advanced features information including supported modes
            """
            args = ["-p", resource_id, "s", "--json", "-vv"]

            result = run_fc_client_command(args)

            if result["success"]:
                try:
                    # Parse JSON output from fc-client
                    resource_data = json.loads(result["stdout"])

                    # Extract advanced features from labels
                    supported_modes = []

                    if isinstance(resource_data, list) and len(resource_data) > 0:
                        resource_info = resource_data[0]
                    elif isinstance(resource_data, dict):
                        resource_info = resource_data
                    else:
                        return {
                            "success": False,
                            "error": "Unexpected resource data format",
                            "raw_output": result["stdout"],
                            "command": result["command"],
                        }

                    # Look for labels->advanced section
                    labels = resource_info.get("labels", {})
                    if "advanced" in labels:
                        advanced_value = labels["advanced"]

                        # The advanced value should be a list of supported modes
                        if isinstance(advanced_value, list):
                            supported_modes = advanced_value
                        elif isinstance(advanced_value, str):
                            # Handle case where it might be a single string
                            supported_modes = [advanced_value]
                        else:
                            # If it's some other format, convert to string and wrap in list
                            supported_modes = [str(advanced_value)]

                    return {
                        "resource_id": resource_id,
                        "operation": "advanced_features",
                        "success": True,
                        "supported_modes": supported_modes,
                        "has_predeploy": "predeploy" in supported_modes,
                        "has_uuu": "uuu" in supported_modes,
                        "labels": labels,
                        "full_resource_info": resource_info,
                        "command": result["command"],
                    }

                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Failed to parse JSON output from fc-client",
                        "raw_output": result["stdout"],
                        "command": result["command"],
                    }
            else:
                return {
                    "resource_id": resource_id,
                    "operation": "advanced_features",
                    "success": False,
                    "error": result.get("stderr", result.get("error", "Unknown error")),
                    "command": result["command"],
                }

        @self.mcp.tool()
        def get_fc_command(
            resource_id: str,
            command: str,
            args: Optional[List[str]] = None,
            verbose: int = 0,
        ) -> Dict[str, Any]:
            """
            Generate the fc-client command string without executing it.
            Useful when users want to run commands manually.

            Args:
                resource_id: Resource identifier
                command: FC/labgrid command
                args: Additional arguments for the command
                verbose: Verbosity level (0-3)

            Returns:
                Dictionary with the formatted fc-client command
            """
            cmd_args = ["-p", resource_id]

            if verbose > 0:
                cmd_args.extend(["-v"] * verbose)

            cmd_args.append(command)

            if args:
                cmd_args.extend(args)

            full_command = "fc-client " + " ".join(cmd_args)

            return {
                "resource_id": resource_id,
                "command": command,
                "full_command": full_command,
                "success": True,
                "message": f"FC command generated for {command} on {resource_id}",
                "usage": f"Run this command in your terminal: {full_command}",
            }

        @self.mcp.tool()
        def fc_command(
            resource_id: str,
            command: str,
            args: Optional[List[str]] = None,
            verbose: int = 0,
        ) -> Dict[str, Any]:
            """
            Handle fc-client commands for labgrid operations.
            For interactive commands, returns the command for manual execution.
            For non-interactive commands, executes them and returns results.

            Args:
                resource_id: Resource identifier
                command: FC/labgrid command to execute (e.g., 'console', 'ssh', 'scp', 'power', etc.)
                args: Additional arguments for the command
                verbose: Verbosity level (0-3)

            Returns:
                Dictionary with command execution result or manual command instruction
            """
            # Interactive commands that require user to run manually in separate terminal
            interactive_commands = ["ssh", "console"]

            # Commands that might take a long time but don't require interaction
            long_running_commands = ["scp", "rsync"]

            cmd_args = ["-p", resource_id]

            cmd_args.append(command)

            if args:
                cmd_args.extend(args)

            if verbose > 0:
                cmd_args.extend(["-v"] * verbose)

            # Build the full command string
            full_command = "fc-client " + " ".join(cmd_args)

            # Check if this is an interactive command
            if command.lower() in interactive_commands:
                return {
                    "resource_id": resource_id,
                    "operation": f"fc-{command}",
                    "success": True,
                    "interactive": True,
                    "message": "Interactive command detected. Please run this command in a separate terminal session:",
                    "command_to_run": full_command,
                    "instructions": [
                        r"1. Open a new terminal session",
                        f"2. Run: {full_command}",
                        f"3. This will give you an interactive {command} session to {resource_id}",
                        r"4. Use the appropriate exit method (Escape character: Ctrl-\, 'exit') to close the session",
                    ],
                    "note": f"The {command} command requires an interactive terminal that cannot be provided through this agent interface.",
                }

            # For long-running but non-interactive commands, provide both options
            if command.lower() in long_running_commands:
                return {
                    "resource_id": resource_id,
                    "operation": f"fc-{command}",
                    "success": True,
                    "long_running": True,
                    "message": "Long-running command detected. You can either run it through the agent (may timeout) or manually:",
                    "command_to_run": full_command,
                    "options": [
                        "Option 1: Run manually in separate terminal for better control:",
                        f"  {full_command}",
                        "",
                        "Option 2: Let the agent attempt to run it (may timeout for very long operations)",
                        "  Just confirm and I'll try to execute it for you.",
                    ],
                    "recommendation": "For large file transfers or long operations, running manually is recommended.",
                }

            # For regular commands, execute normally with appropriate timeout
            timeout = 120 if command.lower() in long_running_commands else 30

            try:
                cmd = ["fc-client"] + cmd_args
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )

                return {
                    "resource_id": resource_id,
                    "operation": f"fc-{command}",
                    "success": result.returncode == 0,
                    "output": result.stdout.strip(),
                    "error": result.stderr.strip() if result.returncode != 0 else None,
                    "command": " ".join(cmd),
                    "executed_by_agent": True,
                }

            except subprocess.TimeoutExpired:
                return {
                    "resource_id": resource_id,
                    "operation": f"fc-{command}",
                    "success": False,
                    "error": f"Command timed out after {timeout} seconds. For long-running operations, consider running manually:",
                    "command_to_run_manually": full_command,
                    "command": " ".join(cmd),
                }
            except Exception as exce:
                return {
                    "resource_id": resource_id,
                    "operation": f"fc-{command}",
                    "success": False,
                    "error": str(exce),
                    "command": " ".join(cmd),
                }

        @self.mcp.tool()
        def get_console_names(resource_id: str, verbose: int = 0) -> Dict[str, Any]:
            """
            Get available console names for a resource using fc-client show command.
            Extracts console names from NetworkSerialPort resources.

            Args:
                resource_id: Unique identifier for the resource to check console names
                verbose: Verbosity level (0-3)

            Returns:
                Dictionary with available console names and their details
            """
            args = ["-p", resource_id]
            if verbose > 0:
                args.extend(["-v"] * verbose)
            args.append("show")

            result = run_fc_client_command(args)

            if not result["success"]:
                return {
                    "resource_id": resource_id,
                    "operation": "get_console_names",
                    "success": False,
                    "error": result.get("stderr", result.get("error", "Unknown error")),
                    "command": result["command"],
                }

            # Parse the output to extract console names
            output = result["stdout"]
            console_names = []
            console_details = {}

            # Look for lines that contain NetworkSerialPort information
            lines = output.split("\n")
            current_console = None

            for line in lines:
                line = line.strip()

                # Look for lines like "Acquired resource 'default' (Uranus/imx95-19x19-evk-sh62/NetworkSerialPort/default):"
                if "Acquired resource '" in line and "NetworkSerialPort" in line:
                    # Extract console name from the line
                    start_quote = line.find("Acquired resource '") + len(
                        "Acquired resource '"
                    )
                    end_quote = line.find("'", start_quote)
                    if 0 < start_quote < end_quote:
                        console_name = line[start_quote:end_quote]
                        console_names.append(console_name)
                        current_console = console_name
                        console_details[console_name] = {
                            "name": console_name,
                            "type": "NetworkSerialPort",
                            "full_path": line,
                        }

                # Look for parameter details in the following lines
                elif current_console and "'host':" in line and "'port':" in line:
                    # Try to extract host and port information
                    try:
                        # This is a simplified extraction - the line contains host and port info
                        if current_console in console_details:
                            console_details[current_console]["details"] = line.strip()
                    except:
                        pass

            # Remove duplicates while preserving order
            unique_console_names = []
            seen = set()
            for name in console_names:
                if name not in seen:
                    unique_console_names.append(name)
                    seen.add(name)

            return {
                "resource_id": resource_id,
                "operation": "get_console_names",
                "success": True,
                "console_names": unique_console_names,
                "console_count": len(unique_console_names),
                "console_details": console_details,
                "available_consoles": [
                    f"Console '{name}' - use 'fc-client -p {resource_id} console {name}' to connect"
                    for name in unique_console_names
                ],
                "command": result["command"],
                "raw_output": output if verbose > 1 else None,
            }

        @self.mcp.tool()
        def set_comment(
            resource_id: str, comment: str = "", verbose: int = 0
        ) -> Dict[str, Any]:
            """
            Set or unset a comment on a resource using fc-client.
            Use empty string to unset the comment.

            Args:
                resource_id: Unique identifier for the resource to set comment on
                comment: Comment text to set (use empty string "" to unset comment)
                verbose: Verbosity level (0-3)

            Returns:
                Dictionary with set comment operation status and details
            """
            args = ["-p", resource_id]
            if verbose > 0:
                args.extend(["-v"] * verbose)
            args.extend(["set-comment", comment])

            result = run_fc_client_command(args)

            # Determine if this was a set or unset operation
            operation_type = "unset_comment" if comment == "" else "set_comment"
            operation_desc = "unset" if comment == "" else f"set to '{comment}'"

            return {
                "resource_id": resource_id,
                "operation": operation_type,
                "comment": comment if comment != "" else None,
                "success": result["success"],
                "message": result.get("stdout", result.get("error", "Unknown error")),
                "error": result.get("stderr") if not result["success"] else None,
                "command": result["command"],
                "description": f"Comment {operation_desc} for resource {resource_id}",
            }
