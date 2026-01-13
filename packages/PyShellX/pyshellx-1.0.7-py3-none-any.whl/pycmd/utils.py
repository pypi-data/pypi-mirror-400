import os
import shutil
import subprocess
from typing import Optional, List
from pathlib import Path


class ExecutableFile:
    @staticmethod
    def is_executable_in_path(executable: str) -> bool:
        """
        Check if an executable is available in PATH.

        Args:
            executable: Name of the executable to check

        Returns:
            True if executable is found in PATH, False otherwise
        """
        path_env = os.environ.get("PATH", "")
        paths = path_env.split(os.pathsep)

        for path in paths:
            exe_path = Path(path) / executable
            if exe_path.is_file() and os.access(exe_path, os.X_OK):
                return True

            if os.name == "nt":
                for ext in [".exe", ".bat", ".cmd"]:
                    exe_with_ext = Path(path) / f"{executable}{ext}"
                    if exe_with_ext.is_file():
                        return True

        return False

    @staticmethod
    def find_executable(executable: str) -> Optional[str]:
        """
        Find the full path of an executable in PATH.

        Args:
            executable: Name of the executable to find

        Returns:
            Full path to executable if found, None otherwise
        """
        path_env = os.environ.get("PATH", "")
        paths = path_env.split(os.pathsep)

        for path in paths:
            exe_path = Path(path) / executable
            if exe_path.is_file() and os.access(exe_path, os.X_OK):
                return str(exe_path)

            if os.name == "nt":
                for ext in [".exe", ".bat", ".cmd"]:
                    exe_with_ext = Path(path) / f"{executable}{ext}"
                    if exe_with_ext.is_file():
                        return str(exe_with_ext)

        return None

    @staticmethod
    def is_executable_in_directory(directory: str, executable: str) -> bool:
        """
        Check if an executable exists in a specific directory.

        Args:
            directory: Directory path to check
            executable: Name of the executable to check

        Returns:
            True if executable is found in directory, False otherwise
        """
        dir_path = Path(directory)
        if not dir_path.is_dir():
            return False

        exe_path = dir_path / executable
        if exe_path.is_file() and os.access(exe_path, os.X_OK):
            return True

        if os.name == "nt":
            for ext in [".exe", ".bat", ".cmd"]:
                exe_with_ext = dir_path / f"{executable}{ext}"
                if exe_with_ext.is_file():
                    return True

        return False

    @staticmethod
    def can_run_executable(executable: str, directory: Optional[str] = None) -> bool:
        """
        Check if an executable can be run via subprocess.

        Args:
            executable: Name or path of the executable
            directory: Optional directory to check first before PATH

        Returns:
            True if executable can be run, False otherwise
        """
        if directory and ExecutableFile.is_executable_in_directory(
            directory, executable
        ):
            return True

        if ExecutableFile.is_executable_in_path(executable):
            return True

        exe_path = Path(executable)
        if exe_path.is_file() and os.access(exe_path, os.X_OK):
            return True

        return False

    @staticmethod
    def try_run_executable(
        executable: str,
        args: Optional[List[str]] = None,
        directory: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        Try to run an executable and return success status and output.

        Args:
            executable: Name or path of the executable
            args: Optional list of arguments to pass
            directory: Optional directory to prepend to PATH

        Returns:
            Tuple of (success, output/error_message)
        """
        if args is None:
            args = []

        env = os.environ.copy()

        if directory:
            dir_path = Path(directory).resolve()
            if dir_path.is_dir():
                env["PATH"] = str(dir_path) + os.pathsep + env.get("PATH", "")

        try:
            result = subprocess.run(
                [executable] + args, env=env, capture_output=True, text=True, timeout=5
            )
            return True, result.stdout if result.returncode == 0 else result.stderr
        except FileNotFoundError:
            return False, f"Executable not found: {executable}"
        except subprocess.TimeoutExpired:
            return False, f"Execution timeout: {executable}"
        except Exception as e:
            return False, f"Error running {executable}: {str(e)}"

    @staticmethod
    def get_executable_version(
        executable: str, version_arg: str = "--version", directory: Optional[str] = None
    ) -> Optional[str]:
        """
        Get version information from an executable.

        Args:
            executable: Name or path of the executable
            version_arg: Argument to get version (default: --version)
            directory: Optional directory to prepend to PATH

        Returns:
            Version string if successful, None otherwise
        """
        success, output = ExecutableFile.try_run_executable(
            executable, [version_arg], directory
        )
        if success:
            return output.strip().split("\n")[0] if output else None
        return None

    @staticmethod
    def find_toolchain_executables(
        toolchain_dir: str, executables: List[str]
    ) -> dict[str, bool]:
        """
        Check which executables from a list are available in a toolchain directory.

        Args:
            toolchain_dir: Directory containing toolchain executables
            executables: List of executable names to check

        Returns:
            Dictionary mapping executable names to availability status
        """
        result = {}
        for exe in executables:
            result[exe] = ExecutableFile.is_executable_in_directory(toolchain_dir, exe)
        return result


def main():
    print("=== Windows Executable Utilities Examples ===\n")

    print("Example 1: Check if common Windows executables are in PATH")
    common_exes = ["python", "cmd", "powershell", "notepad", "git"]
    for exe in common_exes:
        found = ExecutableFile.is_executable_in_path(exe)
        status = "✓ Found" if found else "✗ Not found"
        print(f"  {exe:15} : {status}")
    print()

    print("Example 2: Find full paths of executables")
    for exe in ["python", "git", "arm-none-eabi-gcc"]:
        path = ExecutableFile.find_executable(exe)
        if path:
            print(f"  {exe:20} -> {path}")
        else:
            print(f"  {exe:20} -> Not found")
    print()

    print("Example 3: Check ARM GCC toolchain in specific directory")
    toolchain_dirs = [
        r"C:\Program Files (x86)\GNU Arm Embedded Toolchain\10 2021.10\bin",
        r"C:\ARM\bin",
        r"D:\ARM_GCC\bin",
    ]

    for toolchain_dir in toolchain_dirs:
        if Path(toolchain_dir).exists():
            print(f"  Checking: {toolchain_dir}")
            gcc_found = ExecutableFile.is_executable_in_directory(
                toolchain_dir, "arm-none-eabi-gcc"
            )
            print(f"    arm-none-eabi-gcc: {'Found' if gcc_found else 'Not found'}")
            break
    else:
        print("  No ARM toolchain directory found")
    print()

    print("Example 4: Try to run Python and get version")
    success, output = ExecutableFile.try_run_executable("python", ["--version"])
    if success:
        print(f"  Python version: {output.strip()}")
    else:
        print(f"  Error: {output}")
    print()

    print("Example 5: Get version from various toolchain compilers")
    compilers = [
        ("gcc", "--version"),
        ("clang", "--version"),
        ("cl", None),
        ("armcc", "--version_number"),
    ]

    for compiler, version_arg in compilers:
        if version_arg:
            version = ExecutableFile.get_executable_version(compiler, version_arg)
        else:
            version = (
                ExecutableFile.get_executable_version(compiler)
                if ExecutableFile.is_executable_in_path(compiler)
                else None
            )

        if version:
            print(f"  {compiler:10} : {version[:60]}...")
        else:
            print(f"  {compiler:10} : Not found")
    print()

    print("Example 6: Check Keil ARM toolchain executables")
    keil_dir = r"C:\Keil_v5\ARM\ARMCLANG\bin"
    keil_executables = ["armclang", "armlink", "armar", "fromelf"]

    if Path(keil_dir).exists():
        print(f"  Checking Keil directory: {keil_dir}")
        result = ExecutableFile.find_toolchain_executables(keil_dir, keil_executables)
        for exe, found in result.items():
            status = "✓" if found else "✗"
            print(f"    {status} {exe}")
    else:
        print(f"  Keil directory not found: {keil_dir}")
    print()

    print("Example 7: Check GNU ARM toolchain executables")
    arm_gcc_dir = r"C:\Program Files (x86)\GNU Arm Embedded Toolchain\10 2021.10\bin"
    arm_executables = [
        "arm-none-eabi-gcc",
        "arm-none-eabi-g++",
        "arm-none-eabi-ld",
        "arm-none-eabi-as",
        "arm-none-eabi-ar",
        "arm-none-eabi-objcopy",
    ]

    if Path(arm_gcc_dir).exists():
        print(f"  Checking ARM GCC directory: {arm_gcc_dir}")
        result = ExecutableFile.find_toolchain_executables(arm_gcc_dir, arm_executables)
        for exe, found in result.items():
            status = "✓" if found else "✗"
            print(f"    {status} {exe}")
    else:
        print(f"  ARM GCC directory not found: {arm_gcc_dir}")
    print()

    print("Example 8: Test running compiler from custom directory")
    custom_toolchain = r"C:\ARM_Toolchains\gcc-arm\bin"
    if Path(custom_toolchain).exists():
        print(f"  Testing compiler from: {custom_toolchain}")
        success, output = ExecutableFile.try_run_executable(
            "arm-none-eabi-gcc", ["--version"], custom_toolchain
        )
        if success:
            print(f"  Success: {output.split()[0] if output else 'No output'}")
        else:
            print(f"  Failed: {output}")
    else:
        print(f"  Custom toolchain directory not found")
    print()

    print("Example 9: Check MSVC compiler (Visual Studio)")
    msvc_executables = ["cl", "link", "lib", "nmake"]
    print("  Checking MSVC tools in PATH:")
    for exe in msvc_executables:
        found = ExecutableFile.is_executable_in_path(exe)
        status = "✓" if found else "✗"
        path = ExecutableFile.find_executable(exe) if found else "Not in PATH"
        print(f"    {status} {exe:10} : {path}")
    print()

    print("Example 10: Verify toolchain before build")
    required_tools = ["arm-none-eabi-gcc", "arm-none-eabi-objcopy", "make"]
    print("  Pre-build toolchain verification:")
    all_found = True
    for tool in required_tools:
        found = ExecutableFile.can_run_executable(tool)
        status = "✓" if found else "✗"
        print(f"    {status} {tool}")
        if not found:
            all_found = False

    if all_found:
        print("\n  ✓ All required tools are available. Ready to build!")
    else:
        print(
            "\n  ✗ Some tools are missing. Please install missing toolchain components."
        )


if __name__ == "__main__":
    # r = my_test()
    # print(r)
    # main()

    dir = r"D:\00_test"
    dir = "D://00_test"
    exe_name = "test2.exe"
    found = ExecutableFile.is_executable_in_directory(dir, exe_name)
    print(f"  Found: {found}")

    found = ExecutableFile.is_executable_in_path(exe_name)
    print(f"  Found in PATH: {found}")
