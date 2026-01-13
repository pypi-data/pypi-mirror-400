from typing import Dict, Any, List, Optional, Callable, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .environ import Environment


class Program:
    def __init__(self, name: str, env: 'Environment'):
        self.name = name
        self.env = env
        self.commands = []
        self.preactions = []
        self.postactions = []
        self.executed = False
        self.success = True
    
    def add_command(self, command: Union[str, List[str]], description: str = ""):
        self.commands.append({
            'command': command,
            'description': description
        })
        return self
    
    def add_commands(self, commands: List[Union[str, Dict[str, str]]]):
        for cmd in commands:
            if isinstance(cmd, dict):
                self.add_command(cmd.get('command', ''), cmd.get('description', ''))
            else:
                self.add_command(cmd)
        return self
    
    def add_preaction(self, action: Union[str, Callable], description: str = ""):
        self.preactions.append({
            'action': action,
            'description': description
        })
        return self
    
    def add_postaction(self, action: Union[str, Callable], description: str = ""):
        self.postactions.append({
            'action': action,
            'description': description
        })
        return self
    
    def execute(self) -> bool:
        if self.executed:
            if not self.env.silent:
                print(f"Program '{self.name}' already executed")
            return self.success
        
        if not self.env.silent:
            print(f"\n=== Executing Program: {self.name} ===")
        
        if self.preactions:
            if not self.env.silent:
                print(f"--- Running Preactions ---")
            if not self._execute_actions(self.preactions, "Preaction"):
                self.success = False
                self.executed = True
                return False
        
        for i, cmd_info in enumerate(self.commands, 1):
            command = cmd_info['command']
            description = cmd_info['description']
            
            if not self.env.silent:
                if description:
                    print(f"[{i}/{len(self.commands)}] {description}")
                else:
                    print(f"[{i}/{len(self.commands)}] {command}")
            
            returncode, stdout, stderr = self.env.executor.execute(command)
            
            if returncode != 0:
                if not self.env.silent:
                    print(f"Error executing command: {stderr}")
                self.success = False
                self.executed = True
                return False
            else:
                if self.env.verbose and stdout and not self.env.silent:
                    print(f"Output: {stdout.strip()}")
        
        if self.postactions:
            if not self.env.silent:
                print(f"--- Running Postactions ---")
            if not self._execute_actions(self.postactions, "Postaction"):
                self.success = False
                self.executed = True
                return False
        
        self.executed = True
        if not self.env.silent:
            print(f"=== Program '{self.name}' completed successfully ===\n")
        return True
    
    def _execute_actions(self, actions: List[Dict], action_type: str) -> bool:
        for i, action_info in enumerate(actions, 1):
            action = action_info['action']
            description = action_info['description']
            
            if not self.env.silent:
                if description:
                    print(f"  [{action_type} {i}/{len(actions)}] {description}")
                elif isinstance(action, str):
                    print(f"  [{action_type} {i}/{len(actions)}] {action}")
                else:
                    print(f"  [{action_type} {i}/{len(actions)}] <callable>")
            
            if callable(action):
                try:
                    result = action(self.env)
                    if result is False:
                        if not self.env.silent:
                            print(f"Error: {action_type} returned False")
                        return False
                except Exception as e:
                    if not self.env.silent:
                        print(f"Error executing {action_type}: {e}")
                    return False
            else:
                returncode, stdout, stderr = self.env.executor.execute(action)
                if returncode != 0:
                    if not self.env.silent:
                        print(f"Error executing {action_type}: {stderr}")
                    return False
                else:
                    if self.env.verbose and stdout and not self.env.silent:
                        print(f"Output: {stdout.strip()}")
        
        return True
    
    def __str__(self):
        return f"Program('{self.name}', {len(self.commands)} commands)"