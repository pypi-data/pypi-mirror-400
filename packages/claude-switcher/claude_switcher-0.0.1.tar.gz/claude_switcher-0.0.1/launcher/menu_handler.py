import sys
from launcher.config_handler import Colors
from launcher.claude_runner import run_claude

def show_menu_and_handle_selection(config):
    """显示交互式菜单并处理用户选择"""
    models = config.get('models', {})
    model_keys = list(models.keys())

    print(f"{Colors.HEADER}=== Claude Code 模型启动器 ==={Colors.ENDC}")
    print("请选择要使用的模型配置:")
    
    for idx, key in enumerate(model_keys):
        desc = models[key].get('description', '')
        print(f"{Colors.BLUE}[{idx + 1}]{Colors.ENDC} {key.ljust(15)} {Colors.BOLD}{desc}{Colors.ENDC}")
    
    print(f"{Colors.BLUE}[q]{Colors.ENDC} 退出")

    try:
        choice = input(f"\n{Colors.GREEN}请输入序号或名称 > {Colors.ENDC}").strip()
        
        if choice.lower() == 'q':
            sys.exit(0)

        selected_key = None
        
        # 尝试通过序号匹配
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(model_keys):
                selected_key = model_keys[idx]
        
        # 尝试通过名称匹配
        if not selected_key:
            if choice in model_keys:
                selected_key = choice
        
        if selected_key:
            run_claude(selected_key, config)
        else:
            print(f"{Colors.FAIL}无效的选择。{Colors.ENDC}")
            
    except KeyboardInterrupt:
        sys.exit(0)