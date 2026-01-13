import subprocess
import platform
from typing import Optional, Tuple, List, Union


class CommandExecutor:
    def __init__(self, verbose: bool = False, silent: bool = False):
        self.platform = platform.system()
        self.verbose = verbose
        self.silent = silent
    
    def execute(self, command: Union[str, List[str]], cwd: Optional[str] = None, shell: bool = True) -> Tuple[int, str, str]:
        if self.verbose and not self.silent:
            print(f"Executing: {command}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if self.verbose and not self.silent:
                if result.stdout:
                    print(f"STDOUT: {result.stdout}")
                if result.stderr:
                    print(f"STDERR: {result.stderr}")
            
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            if not self.silent:
                print(f"Error executing command: {e}")
            return -1, "", str(e)
    
    def execute_and_get_output(self, command: Union[str, List[str]], cwd: Optional[str] = None) -> str:
        returncode, stdout, stderr = self.execute(command, cwd)
        return stdout
    
    def set_verbose(self, verbose: bool):
        self.verbose = verbose
    
    def set_silent(self, silent: bool):
        self.silent = silent
