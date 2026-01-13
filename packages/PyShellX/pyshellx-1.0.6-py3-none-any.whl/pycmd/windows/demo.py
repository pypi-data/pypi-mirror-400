from pycmd.environ import Environment

ARGS = globals().get("ARGS", {})
env = Environment()

print("=== Windows CMD 测试 ===\n")

if ARGS:
    print(f"命令行参数: {ARGS}\n")

print("=== CMD 命令 ===")
env.Run(
    [
        {"command": "echo Hello from CMD", "description": "输出 Hello"},
        {"command": "ver", "description": "Windows 版本"},
        {"command": "date /t", "description": "当前日期"},
        {"command": "time /t", "description": "当前时间"},
        {"command": "whoami", "description": "当前用户"},
    ]
)

# print("\n=== PowerShell 命令 ===")
# env.Run(
#     [
#         {"command": 'powershell -Command "Get-Date"', "description": "当前时间"},
#         {"command": 'powershell -Command "Get-Location"', "description": "当前位置"},
#         {
#             "command": 'powershell -Command "$PSVersionTable.PSVersion"',
#             "description": "PS 版本",
#         },
#     ]
# )

# print("\n=== 环境变量 ===")
# for var in ["COMPUTERNAME", "USERNAME", "OS"]:
#     print(f"{var}: {env.Execute(f'echo %{var}%').strip()}")

# print("\n=== 测试完成 ===")
