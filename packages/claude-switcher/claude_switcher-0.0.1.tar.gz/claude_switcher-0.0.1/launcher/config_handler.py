import json
import os
import sys
from pathlib import Path

# 配置文件名
CONFIG_FILE = Path.home() / ".claude_switcher" / "claude_models.json"

# 默认配置模板
DEFAULT_CONFIG = {
  "models": {
    "kimi": {
      "description": "Kimi AI (Moonshot)",
      "env": {
        "ANTHROPIC_BASE_URL": "https://api.moonshot.cn/anthropic/",
        "ANTHROPIC_AUTH_TOKEN": "YOUR_KIMI_API_KEY_HERE",
        "API_TIMEOUT_MS": "600000",
        "ANTHROPIC_MODEL": "kimi-k2-0711-preview",
        "ANTHROPIC_SMALL_FAST_MODEL": "kimi-k2-0711-preview"
      }
    },
    "deepseek": {
      "description": "DeepSeek V3",
      "env": {
        "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
        "ANTHROPIC_AUTH_TOKEN": "YOUR_DEEPSEEK_API_KEY_HERE",
        "API_TIMEOUT_MS": "600000",
        "ANTHROPIC_MODEL": "deepseek-chat",
        "ANTHROPIC_SMALL_FAST_MODEL": "deepseek-chat"
      }
    }
  }
}

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def load_config():
    """加载配置，如果不存在则创建默认配置"""
    
    # 确保配置目录存在
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    if not os.path.exists(CONFIG_FILE):
        print(f"{Colors.WARNING}配置文件不存在，正在创建默认模板: {CONFIG_FILE}{Colors.ENDC}")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        print(f"{Colors.WARNING}请编辑 {CONFIG_FILE} 填入你的 API Key 后再次运行。{Colors.ENDC}")
        sys.exit(0)
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"{Colors.FAIL}错误: 配置文件格式不正确。{Colors.ENDC}")
        sys.exit(1)