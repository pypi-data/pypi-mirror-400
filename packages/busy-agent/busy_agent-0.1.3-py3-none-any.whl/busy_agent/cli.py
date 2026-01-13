#!/usr/bin/env python3
"""
Busy Agent CLI - 命令行入口
"""

import time
from .agent import BusyAgent, Colors


def main():
    """主程序入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Busy Agent - 模拟 ReAct Agent 工作过程"
    )
    parser.add_argument(
        "--index",
        type=int,
        default=None,
        help="指定要显示的 trajectory 索引（自动进入单次模式）",
    )
    parser.add_argument(
        "--once", action="store_true", help="单次运行模式（默认为循环模式）"
    )
    parser.add_argument("--fast", action="store_true", help="快速模式（跳过动画）")
    parser.add_argument(
        "--delay", type=float, default=3.0, help="循环模式下每次之间的延迟（秒）"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        choices=["qwen-flash", "qwen-plus", "qwen-max"],
        help="选择模型：qwen-flash（快速）、qwen-plus（平衡）、qwen-max（最强）",
    )
    parser.add_argument(
        "--language",
        "--lang",
        type=str,
        default=None,
        choices=["zh", "en"],
        help="选择语言：zh (中文) 或 en (English)",
    )

    args = parser.parse_args()

    # 创建 Agent
    agent = BusyAgent(model=args.model, language=args.language)

    # 如果指定了 index 或 once，进入单次模式；否则默认循环模式
    if args.once or args.index is not None:
        # 单次运行
        agent.run(index=args.index, fast_mode=args.fast)
    else:
        try:
            while True:
                agent.run(fast_mode=args.fast)
                time.sleep(args.delay)
        except KeyboardInterrupt:
            print(f"\n{Colors.BRIGHT_YELLOW}{agent._t('exited')}{Colors.RESET}")


if __name__ == "__main__":
    main()
