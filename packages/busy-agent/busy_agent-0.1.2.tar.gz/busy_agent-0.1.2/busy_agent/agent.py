#!/usr/bin/env python3
"""
Busy Agent - 模拟 ReAct Agent 工作过程
从 react-llama 数据集读取 trajectory 并以真实的方式打印
"""

import pandas as pd
import re
import time
import sys
import random
import json
import os
from typing import List, Dict


# ANSI 颜色代码
class Colors:
    """终端颜色代码"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # 亮色
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


# 语言字典
LANGUAGES = {
    'zh': {
        'loaded_data': '✓ 加载了 {count} 条 trajectory 数据',
        'loaded_config': '✓ 加载配置文件: {path}',
        'config_load_failed': '⚠️  配置文件加载失败，使用默认配置: {error}',
        'config_not_found': '⚠️  配置文件不存在，使用默认配置',
        'thinking': '思考中...',
        'executing': '执行中...',
        'model_disconnect': '⚠️  模型断连: {model} 连接失败',
        'retrying': '🔄 重试中... (尝试 {current}/{max})',
        'reconnect_success': '✓ 重新连接成功',
        'connect_failed': '✗ 连接失败，跳过此步骤',
        'action_timeout': '⏱️  动作超时: 执行时间过长',
        'execution_success': '✓ 执行成功',
        'execution_failed': '✗ 执行失败，跳过此动作',
        'agent_working': '🤖 ReAct Agent 工作中...',
        'question': '❓ 问题:',
        'start_reasoning': '🔄 开始推理过程...',
        'final_answer': '✅ 最终答案: {answer}',
        'loop_mode_started': '🔄 循环模式已启动，按 Ctrl+C 退出',
        'exited': '👋 已退出',
        'observable_metrics': '📊 可观测指标:',
        'llm_judge_score': '🤖 LLM 评分:',
        'overall_success_rate': '✅ 总体成功率:',
        'time_spent': '⏱️  耗时:',
        'total_steps': '📝 总步骤数:',
        'incidents': '⚠️  意外事件:',
        'retry_count': '🔄 重试次数:',
    },
    'en': {
        'loaded_data': '✓ Loaded {count} trajectory data',
        'loaded_config': '✓ Loaded config file: {path}',
        'config_load_failed': '⚠️  Failed to load config, using defaults: {error}',
        'config_not_found': '⚠️  Config file not found, using defaults',
        'thinking': 'Thinking...',
        'executing': 'Executing...',
        'model_disconnect': '⚠️  Model disconnected: {model} connection failed',
        'retrying': '🔄 Retrying... (attempt {current}/{max})',
        'reconnect_success': '✓ Reconnected successfully',
        'connect_failed': '✗ Connection failed, skipping this step',
        'action_timeout': '⏱️  Action timeout: execution took too long',
        'execution_success': '✓ Execution successful',
        'execution_failed': '✗ Execution failed, skipping this action',
        'agent_working': '🤖 ReAct Agent Working...',
        'question': '❓ Question:',
        'start_reasoning': '🔄 Starting reasoning process...',
        'final_answer': '✅ Final Answer: {answer}',
        'loop_mode_started': '🔄 Loop mode started, press Ctrl+C to exit',
        'exited': '👋 Exited',
        'observable_metrics': '📊 Observable Metrics:',
        'llm_judge_score': '🤖 LLM as Judge Score:',
        'overall_success_rate': '✅ Overall Success Rate:',
        'time_spent': '⏱️  Time Spent:',
        'total_steps': '📝 Total Steps:',
        'incidents': '⚠️  Incidents:',
        'retry_count': '🔄 Retry Count:',
    }
}


class BusyAgent:
    """模拟忙碌的 ReAct Agent"""

    def __init__(self, dataset_path: str = None, config_path: str = None, model: str = None, language: str = None):
        """初始化 Agent"""
        # 获取包数据目录路径
        if dataset_path is None:
            package_dir = os.path.dirname(os.path.abspath(__file__))
            dataset_path = os.path.join(package_dir, 'data', 'datasets', 'react-llama.parquet')

        if config_path is None:
            package_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(package_dir, 'data', 'config.json')

        self.df = pd.read_parquet(dataset_path)

        # 加载配置文件
        self.config = self._load_config(config_path)

        # 设置语言
        self.language = language or self.config.get('language', {}).get('default', 'zh')

        # 输出加载信息
        print(self._t('loaded_data', count=len(self.df)))
        print(self._t('loaded_config', path=config_path))

        # 设置模型（保留用于未来扩展）
        self.model = model or self.config.get('model', {}).get('default', 'qwen-plus')

        # 初始化打印模式相关变量
        self.step_counter = 0
        self.current_print_mode = self._select_random_print_mode()

        # 初始化统计信息
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0

        # 当前运行的统计信息
        self.current_run_stats = {
            'start_time': None,
            'end_time': None,
            'total_steps': 0,
            'incidents_occurred': [],
            'retry_count': 0,
            'is_correct': False
        }

    def _select_random_print_mode(self) -> str:
        """随机选择一个打印模式"""
        modes = ['smooth', 'chunky', 'slow', 'instant']
        return random.choice(modes)

    def _should_answer_correctly(self) -> bool:
        """
        根据成功率和意外情况判断是否应该输出正确答案

        Returns:
            True 表示输出正确答案，False 表示输出错误答案
        """
        success_config = self.config.get('success_rate', {})
        target_rate = success_config.get('target_rate', 0.75)
        incident_penalty = success_config.get('incident_penalty', 0.3)

        # 计算基础失败概率
        base_failure_prob = 1.0 - target_rate

        # 如果有意外发生，增加失败概率
        if len(self.current_run_stats['incidents_occurred']) > 0:
            failure_prob = base_failure_prob + incident_penalty
            failure_prob = min(failure_prob, 0.95)  # 最多95%失败率
        else:
            failure_prob = base_failure_prob

        # 随机判断
        return random.random() > failure_prob

    def _generate_fake_answer(self, correct_answer: str) -> str:
        """
        生成一个错误答案

        Args:
            correct_answer: 正确答案

        Returns:
            错误答案
        """
        success_config = self.config.get('success_rate', {})
        strategies = success_config.get('wrong_answer_strategies', {})

        # 根据权重选择策略
        strategy_choices = []
        weights = []

        for strategy_name, strategy_config in strategies.items():
            strategy_choices.append(strategy_name)
            weights.append(strategy_config.get('weight', 0.33))

        # 归一化权重
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]

        chosen_strategy = random.choices(strategy_choices, weights=weights)[0]

        # 根据策略生成答案
        if chosen_strategy == 'unable_to_determine':
            templates = strategies['unable_to_determine'].get('templates', ['Unable to determine'])
            return random.choice(templates)
        elif chosen_strategy == 'reasoning_failed':
            templates = strategies['reasoning_failed'].get('templates', ['Reasoning process incomplete'])
            return random.choice(templates)
        elif chosen_strategy == 'wrong_guess':
            # 随机选择数据集中其他问题的答案
            random_idx = random.randint(0, len(self.df) - 1)
            random_answer = self.df.iloc[random_idx]['correct_answer']
            # 确保不是同一个答案
            max_attempts = 10
            attempts = 0
            while random_answer == correct_answer and attempts < max_attempts:
                random_idx = random.randint(0, len(self.df) - 1)
                random_answer = self.df.iloc[random_idx]['correct_answer']
                attempts += 1
            return random_answer
        else:
            return "Unable to determine"

    def _calculate_llm_judge_score(self, is_correct: bool) -> float:
        """
        计算 LLM as judge 评分

        Args:
            is_correct: 答案是否正确

        Returns:
            评分（0-10）
        """
        judge_config = self.config.get('llm_judge', {})

        if not judge_config.get('enabled', True):
            return 0.0

        if is_correct:
            score_min = judge_config.get('correct_answer_score', {}).get('min', 8.5)
            score_max = judge_config.get('correct_answer_score', {}).get('max', 10.0)
        else:
            score_min = judge_config.get('wrong_answer_score', {}).get('min', 2.0)
            score_max = judge_config.get('wrong_answer_score', {}).get('max', 6.0)

        return random.uniform(score_min, score_max)

    def _t(self, key: str, **kwargs) -> str:
        """
        获取翻译文本

        Args:
            key: 文本键
            **kwargs: 格式化参数

        Returns:
            翻译后的文本
        """
        text = LANGUAGES.get(self.language, LANGUAGES['zh']).get(key, key)
        return text.format(**kwargs) if kwargs else text

    def _load_config(self, config_path: str) -> dict:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            配置字典
        """
        # 默认配置
        default_config = {
            "model": {
                "default": "qwen-plus",
                "available_models": {
                    "qwen-flash": {"display_name": "Qwen-Flash", "tier": "flash"},
                    "qwen-plus": {"display_name": "Qwen-Plus", "tier": "plus"},
                    "qwen-max": {"display_name": "Qwen-Max", "tier": "max"}
                }
            },
            "delays": {
                "thinking": {"min": 2.0, "max": 5.0},
                "executing": {"min": 3.0, "max": 6.0}
            },
            "typewriter": {
                "thought_speed": 0.02,
                "action_speed": 0.015,
                "observation_speed": 0.005
            },
            "display": {
                "observation_max_length": 500
            }
        }

        # 尝试加载配置文件
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config
            except Exception as e:
                print(f"⚠️  配置文件加载失败，使用默认配置: {e}")
                return default_config
        else:
            print(f"⚠️  配置文件不存在，使用默认配置")
            return default_config

    def _display_model_info(self):
        """显示当前使用的模型信息"""
        models = self.config.get('model', {}).get('available_models', {})
        model_info = models.get(self.model, {})

        if model_info:
            display_name = model_info.get('display_name', self.model)
            tier = model_info.get('tier', 'unknown')

            # 根据模型档位选择颜色
            if tier == 'flash':
                color = Colors.BRIGHT_CYAN
            elif tier == 'plus':
                color = Colors.BRIGHT_GREEN
            elif tier == 'max':
                color = Colors.BRIGHT_MAGENTA
            else:
                color = Colors.WHITE

            print(f"{color}🤖 使用模型: {display_name}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}🤖 使用模型: {self.model}{Colors.RESET}")

    def parse_trajectory(self, trajectory: str) -> List[Dict[str, str]]:
        """
        解析 trajectory 文本，提取 Thought、Action、Observation

        返回格式：[
            {'type': 'thought', 'number': 1, 'content': '...'},
            {'type': 'action', 'number': 1, 'content': '...'},
            {'type': 'observation', 'number': 1, 'content': '...'},
            ...
        ]
        """
        steps = []

        # 使用正则表达式匹配 Thought、Action、Observation
        pattern = r'(Thought|Action|Observation)\s+(\d+):\s*([^\n]+(?:\n(?!(?:Thought|Action|Observation)\s+\d+:)[^\n]+)*)'

        matches = re.finditer(pattern, trajectory, re.MULTILINE)

        for match in matches:
            step_type = match.group(1).lower()
            step_number = int(match.group(2))
            content = match.group(3).strip()

            steps.append({
                'type': step_type,
                'number': step_number,
                'content': content
            })

        return steps

    def typewriter_print(self, text: str, delay: float = 0.03, end: str = '\n'):
        """
        打字机效果打印文本，支持多种打印模式

        Args:
            text: 要打印的文本
            delay: 每个字符的延迟时间（秒）
            end: 结束字符
        """
        mode = self.current_print_mode

        if mode == 'instant':
            # 模式4：即时打印，直接输出全部
            sys.stdout.write(text)
            sys.stdout.write(end)
            sys.stdout.flush()
        elif mode == 'smooth':
            # 模式1：流畅打印（当前的打字机效果）
            for char in text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(delay)
            sys.stdout.write(end)
            sys.stdout.flush()
        elif mode == 'slow':
            # 模式3：慢速打印
            slow_delay = delay * self.config.get('print_modes', {}).get('modes', {}).get('slow', {}).get('speed_multiplier', 3.0)
            for char in text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(slow_delay)
            sys.stdout.write(end)
            sys.stdout.flush()
        elif mode == 'chunky':
            # 模式2：分片打印
            chunk_size = self.config.get('print_modes', {}).get('modes', {}).get('chunky', {}).get('chunk_size', 15)
            chunk_delay = self.config.get('print_modes', {}).get('modes', {}).get('chunky', {}).get('chunk_delay', 0.3)

            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                sys.stdout.write(chunk)
                sys.stdout.flush()
                if i + chunk_size < len(text):
                    time.sleep(chunk_delay)
            sys.stdout.write(end)
            sys.stdout.flush()

    def loading_animation(self, message: str, duration: float = 2.0):
        """
        显示加载动画

        Args:
            message: 加载消息
            duration: 动画持续时间（秒）
        """
        frames = ['|', '/', '-', '\\', '|', '/', '-', '\\']
        end_time = time.time() + duration

        while time.time() < end_time:
            for frame in frames:
                sys.stdout.write(f'\r{frame} {message}')
                sys.stdout.flush()
                time.sleep(0.1)
                if time.time() >= end_time:
                    break

        sys.stdout.write('\r' + ' ' * (len(message) + 3) + '\r')
        sys.stdout.flush()

    def simulate_model_disconnect(self, model_name: str, fast_mode: bool = False) -> bool:
        """
        模拟模型断连和重试

        Args:
            model_name: 模型名称
            fast_mode: 是否快速模式

        Returns:
            是否最终成功
        """
        incidents_config = self.config.get('incidents', {})
        disconnect_config = incidents_config.get('model_disconnect', {})

        if not disconnect_config.get('enabled', False):
            return True

        # 根据概率决定是否触发断连
        if random.random() > disconnect_config.get('probability', 0):
            return True

        # 触发断连 - 记录意外
        self.current_run_stats['incidents_occurred'].append('model_disconnect')
        max_retries = disconnect_config.get('max_retries', 2)

        for retry in range(max_retries):
            self.current_run_stats['retry_count'] += 1
            print(f"\n{Colors.RED}{self._t('model_disconnect', model=model_name)}{Colors.RESET}")

            if not fast_mode:
                time.sleep(random.uniform(0.5, 1.0))

            print(f"{Colors.YELLOW}{self._t('retrying', current=retry + 1, max=max_retries)}{Colors.RESET}")

            if not fast_mode:
                time.sleep(random.uniform(1.0, 2.0))

            # 重试成功（80%概率）
            if random.random() < 0.8:
                print(f"{Colors.GREEN}{self._t('reconnect_success')}{Colors.RESET}\n")
                return True

        # 所有重试都失败
        print(f"{Colors.RED}{self._t('connect_failed')}{Colors.RESET}\n")
        return False

    def simulate_action_timeout(self, action_content: str, fast_mode: bool = False) -> bool:
        """
        模拟动作超时和重试

        Args:
            action_content: 动作内容
            fast_mode: 是否快速模式

        Returns:
            是否最终成功
        """
        incidents_config = self.config.get('incidents', {})
        timeout_config = incidents_config.get('action_timeout', {})

        if not timeout_config.get('enabled', False):
            return True

        # 根据概率决定是否触发超时
        if random.random() > timeout_config.get('probability', 0):
            return True

        # 触发超时 - 记录意外
        self.current_run_stats['incidents_occurred'].append('action_timeout')
        max_retries = timeout_config.get('max_retries', 3)

        for retry in range(max_retries):
            self.current_run_stats['retry_count'] += 1
            print(f"\n{Colors.RED}{self._t('action_timeout')}{Colors.RESET}")

            if not fast_mode:
                time.sleep(random.uniform(0.5, 1.0))

            print(f"{Colors.YELLOW}{self._t('retrying', current=retry + 1, max=max_retries)}{Colors.RESET}")

            if not fast_mode:
                time.sleep(random.uniform(1.5, 3.0))

            # 重试成功（70%概率）
            if random.random() < 0.7:
                print(f"{Colors.GREEN}{self._t('execution_success')}{Colors.RESET}\n")
                return True

        # 所有重试都失败
        print(f"{Colors.RED}{self._t('execution_failed')}{Colors.RESET}\n")
        return False

    def print_step(self, step: Dict[str, str], fast_mode: bool = False):
        """
        打印单个步骤

        Args:
            step: 步骤字典 {'type': 'thought/action/observation', 'number': 1, 'content': '...'}
            fast_mode: 是否快速模式（跳过动画）
        """
        # 增加步骤计数器并检查是否需要切换打印模式
        self.step_counter += 1
        switch_interval = self.config.get('print_modes', {}).get('switch_interval', 10)
        if self.step_counter % switch_interval == 0:
            self.current_print_mode = self._select_random_print_mode()

        step_type = step['type']
        step_number = step['number']
        content = step['content']

        if step_type == 'thought':
            # 思考步骤 - 使用 Plus 模型
            if not fast_mode:
                thinking_min = self.config['delays']['thinking']['min']
                thinking_max = self.config['delays']['thinking']['max']
                self.loading_animation(self._t('thinking'), duration=random.uniform(thinking_min, thinking_max))

            # 模拟模型断连
            if not self.simulate_model_disconnect('Qwen-Plus', fast_mode):
                return

            # 显示模型标签和步骤
            model_tag = f"{Colors.BRIGHT_GREEN}(Qwen-Plus){Colors.RESET} "
            prefix = f"{model_tag}{Colors.BOLD}{Colors.BRIGHT_YELLOW}💭 Thought {step_number}:{Colors.RESET} "
            print(prefix, end='')

            if not fast_mode:
                thought_speed = self.config['typewriter']['thought_speed']
                self.typewriter_print(content, delay=thought_speed)
            else:
                print(content)

        elif step_type == 'action':
            # 动作步骤 - 系统执行
            # 显示系统标签和步骤
            system_tag = f"{Colors.BRIGHT_BLUE}(System){Colors.RESET} "
            prefix = f"{system_tag}{Colors.BOLD}{Colors.BRIGHT_GREEN}⚡ Action {step_number}:{Colors.RESET} "
            print(prefix, end='')

            if not fast_mode:
                action_speed = self.config['typewriter']['action_speed']
                self.typewriter_print(content, delay=action_speed)
            else:
                print(content)

            # 模拟动作超时
            if not self.simulate_action_timeout(content, fast_mode):
                return

            # 执行动作后的延迟
            if not fast_mode:
                executing_min = self.config['delays']['executing']['min']
                executing_max = self.config['delays']['executing']['max']
                self.loading_animation(self._t('executing'), duration=random.uniform(executing_min, executing_max))

        elif step_type == 'observation':
            # 观察步骤 - 根据内容长度选择模型
            # 短内容用 Flash，长内容用 Plus
            content_length_threshold = 200
            if len(content) < content_length_threshold:
                model_name = 'Qwen-Flash'
                model_tag = f"{Colors.BRIGHT_CYAN}(Qwen-Flash){Colors.RESET} "
            else:
                model_name = 'Qwen-Plus'
                model_tag = f"{Colors.BRIGHT_GREEN}(Qwen-Plus){Colors.RESET} "

            # 模拟模型断连
            if not self.simulate_model_disconnect(model_name, fast_mode):
                return

            prefix = f"{model_tag}{Colors.BRIGHT_CYAN}📊 Observation {step_number}:{Colors.RESET} "
            print(prefix, end='')

            # Observation 通常很长，截断显示
            max_length = self.config['display']['observation_max_length']
            if len(content) > max_length and not fast_mode:
                display_content = content[:max_length] + '...'
            else:
                display_content = content

            if not fast_mode:
                observation_speed = self.config['typewriter']['observation_speed']
                self.typewriter_print(display_content, delay=observation_speed)
            else:
                print(display_content)

            print()  # 空行分隔

    def run(self, index: int = None, fast_mode: bool = False):
        """
        运行 Agent，显示一个 trajectory

        Args:
            index: 指定要显示的 trajectory 索引，None 表示随机选择
            fast_mode: 是否快速模式（跳过动画）
        """
        # 初始化当前运行统计信息
        self.current_run_stats = {
            'start_time': time.time(),
            'end_time': None,
            'total_steps': 0,
            'incidents_occurred': [],
            'retry_count': 0,
            'is_correct': False
        }

        # 选择一个 trajectory
        if index is None:
            index = random.randint(0, len(self.df) - 1)

        row = self.df.iloc[index]
        question = row['question']
        correct_answer = row['correct_answer']
        trajectory = row['trajectory']

        # 显示标题
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_MAGENTA}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}{self._t('agent_working')}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}{'=' * 80}{Colors.RESET}\n")

        # 显示问题
        print(f"{Colors.BOLD}{Colors.BRIGHT_WHITE}{self._t('question')}{Colors.RESET}")
        print(f"{Colors.WHITE}{question}{Colors.RESET}\n")

        # 解析 trajectory
        steps = self.parse_trajectory(trajectory)

        if not steps:
            print(f"{Colors.RED}错误: 无法解析 trajectory{Colors.RESET}")
            return

        # 统计步骤数
        self.current_run_stats['total_steps'] = len(steps)

        # 找到最后一个 Action 步骤（包含 Finish[...]）
        last_action_index = -1
        for i, step in enumerate(steps):
            if step['type'] == 'action' and 'Finish[' in step['content']:
                last_action_index = i

        # 逐步打印
        print(f"{Colors.BOLD}{Colors.BRIGHT_WHITE}{self._t('start_reasoning')}{Colors.RESET}\n")

        for step in steps:
            self.print_step(step, fast_mode=fast_mode)

        # 判断答案是否正确
        is_correct = self._should_answer_correctly()
        self.current_run_stats['is_correct'] = is_correct

        # 确定最终显示的答案
        if is_correct:
            final_answer = correct_answer
        else:
            final_answer = self._generate_fake_answer(correct_answer)

        # 记录统计信息
        self.current_run_stats['end_time'] = time.time()
        self.total_runs += 1
        if is_correct:
            self.successful_runs += 1
        else:
            self.failed_runs += 1

        # 计算 LLM judge 评分
        llm_judge_score = self._calculate_llm_judge_score(is_correct)

        # 显示最终答案和指标
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_GREEN}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_GREEN}{self._t('final_answer', answer=final_answer)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_GREEN}{'=' * 80}{Colors.RESET}\n")

        # 显示可观测指标
        metrics_config = self.config.get('metrics', {})

        print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{self._t('observable_metrics')}{Colors.RESET}\n")

        # LLM as Judge 评分
        if metrics_config.get('track_success_rate', True):
            print(f"{Colors.CYAN}{self._t('llm_judge_score')} {Colors.BRIGHT_WHITE}{llm_judge_score:.2f}/10.0{Colors.RESET}")

        # 成功率
        if metrics_config.get('track_success_rate', True) and self.total_runs > 0:
            success_rate = (self.successful_runs / self.total_runs) * 100
            print(f"{Colors.CYAN}{self._t('overall_success_rate')} {Colors.BRIGHT_WHITE}{success_rate:.1f}% ({self.successful_runs}/{self.total_runs}){Colors.RESET}")

        # 时间统计
        if metrics_config.get('track_time', True):
            elapsed_time = self.current_run_stats['end_time'] - self.current_run_stats['start_time']
            print(f"{Colors.CYAN}{self._t('time_spent')} {Colors.BRIGHT_WHITE}{elapsed_time:.2f}s{Colors.RESET}")

        # 步骤数
        if metrics_config.get('track_steps', True):
            print(f"{Colors.CYAN}{self._t('total_steps')} {Colors.BRIGHT_WHITE}{self.current_run_stats['total_steps']}{Colors.RESET}")

        # 意外事件
        if metrics_config.get('track_incidents', True) and len(self.current_run_stats['incidents_occurred']) > 0:
            incidents_str = ', '.join(self.current_run_stats['incidents_occurred'])
            print(f"{Colors.CYAN}{self._t('incidents')} {Colors.BRIGHT_WHITE}{incidents_str}{Colors.RESET}")

        # 重试次数
        if metrics_config.get('track_retries', True) and self.current_run_stats['retry_count'] > 0:
            print(f"{Colors.CYAN}{self._t('retry_count')} {Colors.BRIGHT_WHITE}{self.current_run_stats['retry_count']}{Colors.RESET}")

        print()  # 空行


