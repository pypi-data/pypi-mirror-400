"""
项目唯一的启动入口。
此脚本使用 subprocess 来执行 streamlit run 命令，避免将复杂的路径暴露给用户。
"""
import subprocess
import sys
from pathlib import Path

def main():
    """查找并运行 Streamlit 应用。"""
    project_root = Path(__file__).parent
    app_entry_point = project_root / "src" / "doc_gen" / "app" / "main.py"

    if not app_entry_point.exists():
        print(f"错误: Streamlit 入口文件未找到: {app_entry_point}", file=sys.stderr)
        sys.exit(1)

    command = [sys.executable, "-m", "streamlit", "run", str(app_entry_point), "--server.port", "8080"]
    
    print(f"🚀 正在启动应用: {' '.join(command)}")
    
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError:
        print("错误: 无法找到 Python 解释器。", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"应用启动失败，错误码: {e.returncode}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
        sys.exit(0)

def cli_main():
    """命令行入口点函数"""
    main()

if __name__ == "__main__":
    main()