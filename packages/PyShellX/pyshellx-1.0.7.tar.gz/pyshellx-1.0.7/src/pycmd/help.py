helpinfo = """
1. 如何添加一个新的自带命令行
  参考 cli.py中的main  execute_file 函数
  execute 函数通过return 截断，就可以不解释文件了

2. 如何将命令行参数传到environ.py
  在 environ.py 中
  ARGS = globals().get('ARGS', {})
  print(ARGS)  # 获取所有命令行参数
  
3. 如何执行自己目录中的文件
    添加 -e 或 --example 参数
    # 修改 cli.py，添加参数：
    parser.add_argument(
        '-e', '--example',
        help='Execute example file from Example directory (e.g., -e 01 or -e 01.py)'
    )

    # 在 main() 函数中处理：
    if args.example:
        example_name = args.example if args.example.endswith('.py') else f"{args.example}.py"
        args.file = os.path.join('Example', example_name)

    使用方式：

    python cli.py -e 01
    python cli.py -e 02.py --install_dir=D:\Python
"""
