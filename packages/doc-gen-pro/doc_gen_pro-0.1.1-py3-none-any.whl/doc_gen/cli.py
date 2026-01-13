"""
命令行启动脚本
"""
import subprocess
import sys
from pathlib import Path

def main():
    """启动Streamlit应用"""
    project_root = Path(__file__).parent.parent.parent
    app_entry_point = project_root / "src" / "doc_gen" / "app" / "main.py"
    
    if not app_entry_point.exists():
        print(f"错误: Streamlit入口文件未找到: {app_entry_point}", file=sys.stderr)
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

if __name__ == "__main__":
    main()