import docker
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Tuple

class DockerManager:
    """Manages Docker containers for Bronze to Silver Mapper."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.compose_file = project_path / 'docker-compose.yml'
        
        try:
            self.client = docker.from_env()
        except Exception as e:
            print(f"Error connecting to Docker: {e}")
            print("Make sure Docker is installed and running.")
            sys.exit(1)
    
    def _run_compose(self, command: list, capture_output=False):
        """Run docker-compose command."""
        cmd = ['docker-compose', '-f', str(self.compose_file)] + command
        
        try:
            if capture_output:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
                return result.returncode == 0, result.stdout
            else:
                result = subprocess.run(cmd, cwd=self.project_path)
                return result.returncode == 0
        except Exception as e:
            print(f"Error running docker-compose: {e}")
            return False
    
    def start(self, detached: bool = True) -> bool:
        """Start all services."""
        command = ['up', '--build']
        if detached:
            command.append('-d')
        
        return self._run_compose(command)
    
    def stop(self) -> bool:
        """Stop all services."""
        return self._run_compose(['stop'])
    
    def restart(self) -> bool:
        """Restart all services."""
        return self._run_compose(['restart'])
    
    def down(self, remove_volumes: bool = False) -> bool:
        """Stop and remove containers."""
        command = ['down']
        if remove_volumes:
            command.append('-v')
        
        return self._run_compose(command)
    
    def logs(self, follow: bool = False, tail: int = 100) -> None:
        """View logs."""
        command = ['logs', f'--tail={tail}']
        if follow:
            command.append('-f')
        
        self._run_compose(command)
    
    def status(self) -> Optional[Dict]:
        """Get status of all services."""
        success, output = self._run_compose(['ps'], capture_output=True)
        
        if success:
            return self._parse_ps_output(output)
        return None
    
    def _parse_ps_output(self, output: str) -> Dict:
        """Parse docker-compose ps output."""
        services = {}
        lines = output.strip().split('\n')
        
        for line in lines:
            if 'Up' in line or 'Exit' in line:
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    state = 'running' if 'Up' in line else 'stopped'
                    services[name] = {'state': state}
        
        return services