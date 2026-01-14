#!/usr/bin/env python3
"""
YGG CLI - Command line interface for YGG platform

Usage:
    ygg env <project_id> <env>                    # Export environment as .env format
    cat .env | ygg env <project_id> <env>         # Import environment from stdin
    ygg db <project_id> <env>                      # Export database schema in B3 format
    ygg fbuild <project_id> <env> --branch <branch>  # Trigger frontend build
"""

import os
import sys
import argparse
import requests
from typing import Optional, Dict, Any

# API base URL - always uses production API
YGG_API_BASE_URL = "https://ygg-api.kluglabs.net"


class YGGCLI:
    """YGG CLI client"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YGG CLI client
        
        Args:
            api_key: YGG API key (defaults to YGG_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("YGG_API_KEY")
        if not self.api_key:
            print("Error: YGG_API_KEY environment variable is required", file=sys.stderr)
            sys.exit(1)
        
        # Always use the production API base URL
        self.base_url = YGG_API_BASE_URL.rstrip("/")
        # Base headers - Content-Type will be set per request
        self.base_headers = {
            "X-YGG-API-KEY": self.api_key,
        }
        self.headers = {
            **self.base_headers,
            "Content-Type": "application/json",
        }
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        text: bool = False
    ) -> Any:
        """
        Make a request to the YGG API
        
        Args:
            method: HTTP method
            endpoint: API endpoint path
            data: Optional request body data
            text: If True, return response as text instead of JSON
            
        Returns:
            Response data (JSON or text)
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method == "POST":
                if text:
                    # For text/plain content (like .env import)
                    headers = {**self.base_headers, "Content-Type": "text/plain"}
                    response = requests.post(url, data=data, headers=headers, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=self.headers, timeout=30)
            elif method == "PATCH":
                response = requests.patch(url, json=data, headers=self.headers, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            if text:
                return response.text
            else:
                return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"API request failed: {e}"
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    if "message" in error_data:
                        error_msg = error_data["message"]
                    elif "error" in error_data:
                        error_msg = error_data["error"]
                except:
                    error_msg = e.response.text or error_msg
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"Error: Request failed: {e}", file=sys.stderr)
            sys.exit(1)
    
    def env_export(self, project_id: str, env: str) -> None:
        """
        Export environment as .env format
        
        Args:
            project_id: Project ID
            env: Environment name
        """
        # Try CLI-specific endpoint first, fall back to standard endpoint
        try:
            result = self._request("GET", f"/v1/cli/projects/{project_id}/envs/{env}/export", text=True)
            print(result, end="")
        except SystemExit:
            # Fall back to standard endpoint and convert to .env format
            try:
                env_data = self._request("GET", f"/v1/projects/{project_id}/envs/{env}")
                self._print_env_format(env_data)
            except SystemExit:
                sys.exit(1)
    
    def env_import(self, project_id: str, env: str) -> None:
        """
        Import environment from stdin (.env format)
        
        Args:
            project_id: Project ID
            env: Environment name
        """
        # Read .env content from stdin
        env_content = sys.stdin.read()
        
        if not env_content.strip():
            print("Error: No input provided", file=sys.stderr)
            sys.exit(1)
        
        # Try CLI-specific endpoint first
        try:
            result = self._request("POST", f"/v1/cli/projects/{project_id}/envs/{env}/import", data=env_content, text=True)
            print(result, end="")
        except SystemExit:
            # Fall back to parsing .env and using standard PATCH endpoint
            try:
                entries = self._parse_env_format(env_content)
                set_entries = {}
                for key, value in entries.items():
                    set_entries[key] = {"type": "config", "value": value}
                
                result = self._request("PATCH", f"/v1/projects/{project_id}/envs/{env}", data={"set": set_entries})
                print(f"Successfully imported {len(set_entries)} environment variables", file=sys.stderr)
            except SystemExit:
                sys.exit(1)
    
    def db_schema(self, project_id: str, env: str) -> None:
        """
        Export database schema in B3 format
        
        Args:
            project_id: Project ID
            env: Environment name
        """
        result = self._request("GET", f"/v1/cli/projects/{project_id}/db/{env}/schema", text=True)
        print(result, end="")
    
    def mkproj(self, project_id: str) -> None:
        """
        Create a new project
        
        Args:
            project_id: Project ID (used as name)
        """
        result = self._request("POST", f"/v1/projects", data={"name": project_id})
        print(f"Created project: {result.get('project_id', project_id)}", file=sys.stderr)
        print(result.get('project_id', project_id))
    
    def mkenv(self, project_id: str, env: str) -> None:
        """
        Create a new environment
        
        Args:
            project_id: Project ID
            env: Environment name
        """
        # Create empty environment by updating it
        result = self._request("PATCH", f"/v1/projects/{project_id}/envs/{env}", data={"set": {}})
        print(f"Created environment: {project_id}/{env}", file=sys.stderr)
    
    def rm_project(self, project_id: str) -> None:
        """
        Delete a project
        
        Args:
            project_id: Project ID
        """
        self._request("DELETE", f"/v1/projects/{project_id}")
        print(f"Deleted project: {project_id}", file=sys.stderr)
    
    def rm_env(self, project_id: str, env: str) -> None:
        """
        Delete an environment
        
        Args:
            project_id: Project ID
            env: Environment name
        """
        self._request("DELETE", f"/v1/projects/{project_id}/envs/{env}")
        print(f"Deleted environment: {project_id}/{env}", file=sys.stderr)
    
    def mv_project(self, old_project_id: str, new_project_id: str) -> None:
        """
        Rename a project (creates new project, copies data, deletes old)
        
        Args:
            old_project_id: Current project ID
            new_project_id: New project ID
        """
        # Use rename endpoint if available, otherwise copy + delete
        try:
            result = self._request("POST", f"/v1/cli/projects/{old_project_id}/rename", data={"new_project_id": new_project_id})
            print(f"Renamed project: {old_project_id} -> {new_project_id}", file=sys.stderr)
            print(result.get('project_id', new_project_id))
        except SystemExit:
            # Fallback: manual copy + delete
            print(f"Warning: Rename endpoint not available, using copy+delete method", file=sys.stderr)
            # Get old project
            old_project = self._request("GET", f"/v1/projects/{old_project_id}")
            # Create new project
            new_project = self._request("POST", f"/v1/projects", data={"name": new_project_id})
            new_project_id_actual = new_project.get('project_id', new_project_id)
            
            # Copy environments
            envs = self._request("GET", f"/v1/projects/{old_project_id}/envs")
            for env_data in envs:
                env_name = env_data.get('env')
                # Create environment in new project
                self._request("PATCH", f"/v1/projects/{new_project_id_actual}/envs/{env_name}", 
                             data={"set": env_data.get('entries', {})})
            
            # Delete old project
            self._request("DELETE", f"/v1/projects/{old_project_id}")
            print(f"Renamed project: {old_project_id} -> {new_project_id_actual}", file=sys.stderr)
            print(new_project_id_actual)
    
    def mv_env(self, project_id: str, old_env: str, new_env: str) -> None:
        """
        Rename an environment within the same project
        
        Args:
            project_id: Project ID
            old_env: Current environment name
            new_env: New environment name
        """
        # Use rename endpoint if available, otherwise copy + delete
        try:
            result = self._request("POST", f"/v1/cli/projects/{project_id}/envs/{old_env}/rename", 
                                  data={"new_env": new_env})
            print(f"Renamed environment: {project_id}/{old_env} -> {project_id}/{new_env}", file=sys.stderr)
        except SystemExit:
            # Fallback: manual copy + delete
            # Get old environment
            old_env_data = self._request("GET", f"/v1/projects/{project_id}/envs/{old_env}")
            # Create new environment
            self._request("PATCH", f"/v1/projects/{project_id}/envs/{new_env}", 
                        data={"set": old_env_data.get('entries', {})})
            # Delete old environment
            self._request("DELETE", f"/v1/projects/{project_id}/envs/{old_env}")
            print(f"Renamed environment: {project_id}/{old_env} -> {project_id}/{new_env}", file=sys.stderr)
    
    def fbuild(self, project_id: str, env: str, branch: str, version: Optional[str] = None) -> None:
        """
        Trigger a frontend build
        
        Args:
            project_id: Project ID
            env: Environment name
            branch: Git branch name (required)
            version: Optional version number (e.g., "5.2.12")
        """
        payload = {
            "branch": branch
        }
        if version:
            payload["version"] = version
        
        result = self._request("POST", f"/v1/projects/{project_id}/envs/{env}/builds", data=payload)
        
        build_id = result.get("build_id", "unknown")
        status = result.get("status", "unknown")
        message = result.get("message", "Build triggered")
        
        print(f"Build triggered: {build_id}", file=sys.stderr)
        print(f"Status: {status}", file=sys.stderr)
        print(f"Message: {message}", file=sys.stderr)
        print(build_id)
    
    def ls(self) -> None:
        """
        List all projects and their environments
        """
        # Get all projects
        projects = self._request("GET", "/v1/projects")
        
        if not projects:
            print("No projects found", file=sys.stderr)
            return
        
        # Sort projects by project_id
        projects_sorted = sorted(projects, key=lambda p: p.get('project_id', ''))
        
        for project in projects_sorted:
            project_id = project.get('project_id', 'unknown')
            project_name = project.get('name', project_id)
            status = project.get('status', 'active')
            
            # Print project info
            status_indicator = "✓" if status == "active" else "✗"
            print(f"{status_indicator} {project_id} ({project_name})")
            
            # Get environments for this project
            try:
                envs = self._request("GET", f"/v1/projects/{project_id}/envs")
                if envs:
                    # Sort environments by name
                    envs_sorted = sorted(envs, key=lambda e: e.get('env', ''))
                    for env in envs_sorted:
                        env_name = env.get('env', 'unknown')
                        entry_count = len(env.get('entries', {}))
                        print(f"  └─ {env_name} ({entry_count} vars)")
                else:
                    print(f"  └─ (no environments)")
            except SystemExit:
                # If we can't access environments, just skip them
                print(f"  └─ (environments not accessible)")
    
    def _print_env_format(self, env_data: Dict[str, Any]) -> None:
        """
        Convert environment data to .env format
        
        Args:
            env_data: Environment data from API
        """
        entries = env_data.get("entries", {})
        
        for key, entry in sorted(entries.items()):
            if entry.get("type") == "secret_ref":
                # For secret references, we can't output the actual value
                # Output a comment instead
                print(f"# {key}=<secret_ref:{entry.get('secret_id', 'unknown')}>")
            elif entry.get("type") == "config":
                value = entry.get("value", "")
                # Escape special characters in .env format
                value = value.replace("\\", "\\\\").replace("\n", "\\n").replace("\"", "\\\"")
                # Quote if contains spaces or special chars
                if " " in value or "=" in value or "#" in value:
                    value = f'"{value}"'
                print(f"{key}={value}")
    
    def _parse_env_format(self, content: str) -> Dict[str, str]:
        """
        Parse .env format content into key-value pairs
        
        Args:
            content: .env file content
            
        Returns:
            Dictionary of key-value pairs
        """
        entries = {}
        
        for line in content.splitlines():
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Parse KEY=VALUE format
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                # Unescape special characters
                value = value.replace("\\n", "\n").replace("\\\"", "\"").replace("\\\\", "\\")
                
                entries[key] = value
        
        return entries


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="YGG Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ygg ls                                  # List all projects and environments
  ygg env proj_123 dev                    # Export environment as .env
  cat .env | ygg env proj_123 prod        # Import environment from stdin
  ygg db proj_123 dev                     # Export database schema
  ygg mkproj P1                           # Create project P1
  ygg mkenv P1 dev                        # Create environment dev in project P1
  ygg rm P1                               # Delete project P1
  ygg rm P1 dev                           # Delete environment dev in project P1
  ygg mv P1 P2                            # Rename project P1 to P2
  ygg mv P1 dev dev2                      # Rename environment dev to dev2 in project P1
  ygg fbuild proj_123 dev --branch main   # Trigger frontend build for main branch
  ygg fbuild proj_123 prod --branch release --version 1.0.0  # Build with version
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # env command
    env_parser = subparsers.add_parser("env", help="Environment management")
    env_parser.add_argument("project_id", help="Project ID")
    env_parser.add_argument("env", help="Environment name")
    
    # db command
    db_parser = subparsers.add_parser("db", help="Database schema export")
    db_parser.add_argument("project_id", help="Project ID")
    db_parser.add_argument("env", help="Environment name")
    
    # mkproj command
    mkproj_parser = subparsers.add_parser("mkproj", help="Create a new project")
    mkproj_parser.add_argument("project_id", help="Project ID (used as name)")
    
    # mkenv command
    mkenv_parser = subparsers.add_parser("mkenv", help="Create a new environment")
    mkenv_parser.add_argument("project_id", help="Project ID")
    mkenv_parser.add_argument("env", help="Environment name")
    
    # rm command (can delete project or environment)
    rm_parser = subparsers.add_parser("rm", help="Delete a project or environment")
    rm_parser.add_argument("project_id", help="Project ID")
    rm_parser.add_argument("env", nargs="?", help="Environment name (optional, if not provided, deletes project)")
    
    # mv command (can rename project or environment)
    mv_parser = subparsers.add_parser("mv", help="Rename a project or environment")
    mv_parser.add_argument("project_id", help="Project ID or old project ID")
    mv_parser.add_argument("target", help="New project ID, or old env name if renaming env")
    mv_parser.add_argument("new_env", nargs="?", help="New environment name (if renaming env)")
    
    # ls command
    ls_parser = subparsers.add_parser("ls", help="List all projects and environments")
    
    # fbuild command
    fbuild_parser = subparsers.add_parser("fbuild", help="Trigger a frontend build")
    fbuild_parser.add_argument("project_id", help="Project ID")
    fbuild_parser.add_argument("env", help="Environment name")
    fbuild_parser.add_argument("--branch", required=True, help="Git branch name (required)")
    fbuild_parser.add_argument("--version", help="Optional version number (e.g., 5.2.12)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize CLI client
    cli = YGGCLI()
    
    # Execute command
    if args.command == "env":
        # Check if stdin has data (for import)
        if sys.stdin.isatty():
            # No stdin, export
            cli.env_export(args.project_id, args.env)
        else:
            # Has stdin, import
            cli.env_import(args.project_id, args.env)
    elif args.command == "db":
        cli.db_schema(args.project_id, args.env)
    elif args.command == "mkproj":
        cli.mkproj(args.project_id)
    elif args.command == "mkenv":
        cli.mkenv(args.project_id, args.env)
    elif args.command == "rm":
        if args.env:
            # Delete environment
            cli.rm_env(args.project_id, args.env)
        else:
            # Delete project
            cli.rm_project(args.project_id)
    elif args.command == "mv":
        if args.new_env:
            # Rename environment: mv project_id old_env new_env
            cli.mv_env(args.project_id, args.target, args.new_env)
        else:
            # Rename project: mv old_project_id new_project_id
            cli.mv_project(args.project_id, args.target)
    elif args.command == "ls":
        cli.ls()
    elif args.command == "fbuild":
        cli.fbuild(args.project_id, args.env, args.branch, args.version)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

