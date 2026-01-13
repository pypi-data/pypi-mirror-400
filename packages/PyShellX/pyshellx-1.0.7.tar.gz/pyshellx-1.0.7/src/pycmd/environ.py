import os
from typing import Dict, Any, List, Optional, Callable, Union
from .executor import CommandExecutor
from .program import Program

ARGS = globals().get("ARGS", {})  # 获取所有命令行参数


class Environment:
    def __init__(self, verbose: bool = False, silent: bool = False, **kwargs):
        self.executor = CommandExecutor(verbose=verbose, silent=silent)
        self.variables = {}
        self.targets = []
        self.verbose = verbose
        self.silent = silent

        for key, value in kwargs.items():
            self.variables[key] = value

    def __getitem__(self, key: str) -> Any:
        return self.variables.get(key)

    def __setitem__(self, key: str, value: Any):
        self.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def Command(
        self,
        target: Union[str, List[str]],
        source: Union[str, List[str]],
        action: Union[str, Callable],
    ) -> str:
        if isinstance(target, list):
            target = target[0] if target else ""
        if isinstance(source, str):
            source = [source]

        self.targets.append({"target": target, "source": source, "action": action})
        return target

    def Execute(self, command: Union[str, List[str]], cwd: Optional[str] = None) -> str:
        return self.executor.execute_and_get_output(command, cwd)

    def Build(self):
        for target_info in self.targets:
            target = target_info["target"]
            action = target_info["action"]

            if not self.silent:
                print(f"Building: {target}")

            if callable(action):
                action(target, target_info["source"], self)
            else:
                returncode, stdout, stderr = self.executor.execute(action)
                if returncode != 0:
                    if not self.silent:
                        print(f"Error building {target}: {stderr}")
                else:
                    if self.verbose and not self.silent:
                        print(f"Success: {stdout}")

    def Clone(self, **kwargs) -> "Environment":
        new_env = Environment(
            verbose=self.verbose, silent=self.silent, **self.variables
        )
        for key, value in kwargs.items():
            new_env[key] = value
        return new_env

    def Append(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.variables:
                if isinstance(self.variables[key], list):
                    if isinstance(value, list):
                        self.variables[key].extend(value)
                    else:
                        self.variables[key].append(value)
                elif isinstance(self.variables[key], str):
                    self.variables[key] += f" {value}"
            else:
                self.variables[key] = value

    def PrependENVPath(self, key: str, value: str):
        if "ENV" not in self.variables:
            self.variables["ENV"] = {}
        if key in self.variables["ENV"]:
            self.variables["ENV"][
                key
            ] = f"{value}{os.pathsep}{self.variables['ENV'][key]}"
        else:
            self.variables["ENV"][key] = value

    def Program(
        self, name: str, commands: Optional[List[Union[str, Dict[str, str]]]] = None
    ) -> Program:
        program = Program(name, self)
        if commands:
            program.add_commands(commands)
        return program
    
    def Run(self, commands: List[Union[str, Dict[str, str]]]):
        for cmd in commands:
            if isinstance(cmd, dict):
                command = cmd.get("command", "")
                desc = cmd.get("description", "")
                if desc and not self.silent:
                    print(f"[{desc}]")
                output = self.Execute(command)
                if output and not self.silent:
                    print(output.strip())
            else:
                output = self.Execute(cmd)
                if output and not self.silent:
                    print(output.strip())