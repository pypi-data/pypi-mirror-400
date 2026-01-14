import sys
from typing import List, Optional
from launcher.config_handler import load_config
from launcher.claude_runner import run_claude, TARGET_COMMAND
from launcher.menu_handler import show_menu_and_handle_selection
from launcher.config_handler import Colors
import shutil

class Launcher:
    def __init__(self, args: Optional[List[str]] = None):
        self.args = args
        self.config = load_config()
        self.models = self.config.get('models', {})
        self.model_keys = list(self.models.keys())

    def _check_command_exists(self):
        """检查系统是否安装了 claude 命令"""
        return shutil.which(TARGET_COMMAND) is not None

    def run(self):
        if not self._check_command_exists():
             print(f"{Colors.FAIL}错误: 系统中未找到 '{TARGET_COMMAND}' 命令。{Colors.ENDC}")
             print(f"请先运行: {Colors.BOLD}npm install -g @anthropic-ai/claude-code{Colors.ENDC}")
             # 允许继续运行用于测试配置生成，但实际运行会失败

        # 1. 如果命令行带了参数 (例如: python cc.py kimi)
        if len(self.args) > 1:
            chosen_model = self.args[1]
            run_claude(chosen_model, self.config)
            return

        # 2. 如果没带参数，显示交互式菜单
        show_menu_and_handle_selection(self.config)