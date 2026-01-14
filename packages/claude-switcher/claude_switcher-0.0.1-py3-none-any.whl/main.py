import sys
from launcher.launcher import Launcher


def main():
    """
    主函数，启动Claude模型切换器
    """
    launcher = Launcher(sys.argv[1:])
    launcher.run()


if __name__ == "__main__":
    main()
