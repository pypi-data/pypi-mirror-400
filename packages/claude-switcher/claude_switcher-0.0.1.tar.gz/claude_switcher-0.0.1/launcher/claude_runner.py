import os
import sys
import subprocess
from launcher.config_handler import Colors

# 目标命令 (确保你已经安装了 claude code 并且在 PATH 中)
TARGET_COMMAND = "claude"

def run_claude(model_key, config):
    """设置环境变量并运行 Claude"""
    if model_key not in config['models']:
        print(f"{Colors.FAIL}错误: 找不到模型配置 '{model_key}'{Colors.ENDC}")
        return

    model_conf = config['models'][model_key]
    env_vars = model_conf.get('env', {})
    
    # 获取当前系统环境变量
    current_env = os.environ.copy()
    
    # 覆盖/添加配置中的环境变量
    # 注意：确保所有值都是字符串
    for k, v in env_vars.items():
        current_env[k] = str(v)
    
    print(f"{Colors.GREEN}正在启动 Claude Code...{Colors.ENDC}")
    print(f"配置: {Colors.BOLD}{model_key}{Colors.ENDC} ({model_conf.get('description', '')})")
    print(f"模型: {env_vars.get('ANTHROPIC_MODEL', 'Unknown')}")
    print("-" * 30)

    # 检查 API Key 是否被替换
    if "YOUR_" in env_vars.get("ANTHROPIC_AUTH_TOKEN", ""):
        print(f"{Colors.FAIL}警告: 检测到 API KEY 可能是默认占位符，请检查配置文件。{Colors.ENDC}")
        input("按 Enter 继续，或 Ctrl+C 退出...")

    try:
        # 在 Windows 上，execvp 行为略有不同，subprocess 更稳定
        # 在 Linux/Mac 上，execvp 可以替换当前进程
        if sys.platform == 'win32':
            subprocess.run([TARGET_COMMAND], env=current_env, shell=True)
        else:
            os.execvpe(TARGET_COMMAND, [TARGET_COMMAND], current_env)
            
    except FileNotFoundError:
        print(f"{Colors.FAIL}错误: 无法执行命令 '{TARGET_COMMAND}'。请确保已安装 claude-code (npm install -g @anthropic-ai/claude-code){Colors.ENDC}")
    except KeyboardInterrupt:
        print("\n已取消。")