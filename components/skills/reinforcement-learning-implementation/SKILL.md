---
name: reinforcement-learning-implementation
description: "强化学习算法实现与训练策略专家，精通核心算法实现、环境设计和训练优化。构建强化学习系统、多智能体训练和策略优化，处理RL算法实现、策略网络训练和环境模拟。使用PROACTIVELY进行强化学习、策略优化或智能决策系统。"
---

# 强化学习实现技能

## When to Use
Use this skill when implementing reinforcement learning algorithms, building RL environments and agents, training RL models for decision-making problems, developing multi-agent RL systems, or creating RL applications for robotics, gaming, and optimization. Essential for sequential decision-making problems, autonomous systems, resource allocation, and adaptive control systems.

## Core Concepts

### 1. 核心算法实现
- **Q-Learning**: 基于价值函数的强化学习算法
- **Policy Gradient**: 直接优化策略的方法
- **Actor-Critic**: 结合价值函数和策略的混合方法
- **Deep Q-Network (DQN)**: 深度强化学习基础算法

### 2. 环境设计模式
- **Gym环境**: 标准化的RL环境接口
- **自定义环境**: 针对特定问题的环境设计
- **多智能体环境**: 协作和竞争的RL环境
- **连续环境**: 连续状态和动作空间的环境

### 3. 训练策略技术
- **经验回放**: 存储和重用经验的机制
- **目标网络**: 稳定训练的目标网络技术
- **探索策略**: 平衡探索和利用的策略
- **课程学习**: 渐进式难度提升的训练方法

### 4. 高级RL技术
- **分布式训练**: 大规模分布式RL训练
- **元强化学习**: 快速适应新任务的RL方法
- **层级强化学习**: 分层决策的RL架构
- **逆向强化学习**: 从专家行为中学习的RL方法

## Code Examples

### 强化学习核心系统
```python
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from typing import Dict, List, Optional, Any, Tuple, Union
from abc import ABC, abstractmethod
import gym
import random
from collections import deque, namedtuple
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from enum import Enum
import time
import logging

# 经验回放缓冲区
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])

class ReplayBuffer:
    """经验回放缓冲区"""
    
    def __init__(self, capacity: int):
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity
    
    def push(self, state, action, reward, next_state, done):
        """添加经验"""
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """采样批量经验"""
        return random.sample(self.buffer, batch_size)
    
    def __len__(self):
        return len(self.buffer)

# 神经网络模型
class DQNNetwork(nn.Module):
    """深度Q网络"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [256, 256]):
        super(DQNNetwork, self).__init__()
        
        layers = []
        input_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            input_dim = hidden_dim
        
        layers.append(nn.Linear(input_dim, action_dim))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, state):
        return self.network(state)

class PolicyNetwork(nn.Module):
    """策略网络（Actor）"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [256, 256]):
        super(PolicyNetwork, self).__init__()
        
        layers = []
        input_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            input_dim = hidden_dim
        
        # 策略输出
        self.policy_head = nn.Linear(input_dim, action_dim)
        # 价值输出
        self.value_head = nn.Linear(input_dim, 1)
    
    def forward(self, state):
        x = F.relu(self.network(state))
        policy_logits = self.policy_head(x)
        value = self.value_head(x)
        return policy_logits, value
    
    def network(self, state):
        x = state
        input_dim = state.shape[-1]
        
        hidden_dims = [256, 256]
        for hidden_dim in hidden_dims:
            x = F.relu(nn.Linear(input_dim, hidden_dim)(x))
            input_dim = hidden_dim
        
        return x

class ValueNetwork(nn.Module):
    """价值网络（Critic）"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [256, 256]):
        super(ValueNetwork, self).__init__()
        
        # Q值网络
        layers = []
        input_dim = state_dim + action_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            input_dim = hidden_dim
        
        layers.append(nn.Linear(input_dim, 1))
        self.q_network = nn.Sequential(*layers)
    
    def forward(self, state, action):
        x = torch.cat([state, action], dim=-1)
        return self.q_network(x)

# DQN智能体
class DQNAgent:
    """深度Q网络智能体"""
    
    def __init__(self,
                 state_dim: int,
                 action_dim: int,
                 learning_rate: float = 1e-3,
                 gamma: float = 0.99,
                 epsilon: float = 1.0,
                 epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01,
                 target_update_freq: int = 1000,
                 replay_buffer_size: int = 10000,
                 batch_size: int = 32):
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.target_update_freq = target_update_freq
        self.batch_size = batch_size
        self.step_count = 0
        
        # 神经网络
        self.q_network = DQNNetwork(state_dim, action_dim)
        self.target_network = DQNNetwork(state_dim, action_dim)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # 复制参数到目标网络
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        # 经验回放
        self.replay_buffer = ReplayBuffer(replay_buffer_size)
        
        # 训练历史
        self.training_history = []
        self.loss_history = []
    
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """选择动作"""
        
        if training and random.random() < self.epsilon:
            # 探索：随机选择动作
            return random.randint(0, self.action_dim - 1)
        else:
            # 利用：选择最优动作
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
            return q_values.argmax().item()
    
    def update(self) -> float:
        """更新网络"""
        
        if len(self.replay_buffer) < self.batch_size:
            return 0.0
        
        # 采样经验
        experiences = self.replay_buffer.sample(self.batch_size)
        batch = Experience(*zip(*experiences))
        
        # 转换为张量
        state_batch = torch.FloatTensor(batch.state)
        action_batch = torch.LongTensor(batch.action)
        reward_batch = torch.FloatTensor(batch.reward)
        next_state_batch = torch.FloatTensor(batch.next_state)
        done_batch = torch.FloatTensor(batch.done)
        
        # 当前Q值
        current_q_values = self.q_network(state_batch).gather(1, action_batch.unsqueeze(1))
        
        # 目标Q值
        with torch.no_grad():
            next_q_values = self.target_network(next_state_batch).max(1)[0]
            target_q_values = reward_batch + (1 - done_batch) * self.gamma * next_q_values
        
        # 计算损失
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        # 反向传播
        self.optimizer.zero_grad()
        loss.backward()
        
        # 梯度裁剪
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=1.0)
        
        self.optimizer.step()
        
        # 更新目标网络
        if self.step_count % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        self.step_count += 1
        return loss.item()
    
    def update_epsilon(self):
        """更新探索率"""
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def save_model(self, filepath: str):
        """保存模型"""
        torch.save({
            'q_network': self.q_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'step_count': self.step_count
        }, filepath)
    
    def load_model(self, filepath: str):
        """加载模型"""
        checkpoint = torch.load(filepath)
        self.q_network.load_state_dict(checkpoint['q_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint['epsilon']
        self.step_count = checkpoint['step_count']

# Actor-Critic智能体
class ActorCriticAgent:
    """Actor-Critic智能体"""
    
    def __init__(self,
                 state_dim: int,
                 action_dim: int,
                 learning_rate: float = 1e-3,
                 gamma: float = 0.99,
                 actor_hidden_dims: List[int] = [256, 256],
                 critic_hidden_dims: List[int] = [256, 256]):
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate
        self.gamma = gamma
        
        # 网络
        self.policy_network = PolicyNetwork(state_dim, action_dim, actor_hidden_dims)
        self.value_network = ValueNetwork(state_dim, action_dim, critic_hidden_dims)
        
        # 优化器
        self.policy_optimizer = optim.Adam(self.policy_network.parameters(), lr=learning_rate)
        self.value_optimizer = optim.Adam(self.value_network.parameters(), lr=learning_rate)
        
        # 训练历史
        self.training_history = []
    
    def select_action(self, state: np.ndarray, training: bool = True) -> Tuple[int, float]:
        """选择动作和动作概率"""
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        # 前向传播
        policy_logits, value = self.policy_network(state_tensor)
        
        # Softmax动作概率
        action_probs = F.softmax(policy_logits, dim=-1)
        
        if training:
            # 训练时：采样动作
            action_dist = torch.distributions.Categorical(action_probs)
            action = action_dist.sample()
            log_prob = action_dist.log_prob(action)
        else:
            # 推理时：选择最优动作
            action = action_probs.argmax()
            log_prob = torch.log(action_probs[0, action])
        
        return action.item(), log_prob.item()
    
    def update(self, states: List, actions: List, rewards: List, next_states: List, dones: List) -> Dict[str, float]:
        """更新网络"""
        
        # 转换为张量
        states_tensor = torch.FloatTensor(states)
        actions_tensor = torch.LongTensor(actions)
        rewards_tensor = torch.FloatTensor(rewards)
        next_states_tensor = torch.FloatTensor(next_states)
        dones_tensor = torch.FloatTensor(dones)
        
        # 当前策略和价值
        policy_logits, values = self.policy_network(states_tensor)
        values = values.squeeze()
        
        # 下一步价值
        with torch.no_grad():
            next_policy_logits, next_values = self.policy_network(next_states_tensor)
            next_values = next_values.squeeze()
        
        # 计算TD目标
        td_targets = rewards_tensor + self.gamma * next_values * (1 - dones_tensor)
        td_errors = td_targets - values
        
        # 策略损失
        action_probs = F.softmax(policy_logits, dim=-1)
        action_dist = torch.distributions.Categorical(action_probs)
        log_probs = action_dist.log_prob(actions_tensor)
        
        policy_loss = -(log_probs * td_errors.detach()).mean()
        
        # 价值损失
        value_loss = F.mse_loss(values, td_targets.detach())
        
        # 更新网络
        self.policy_optimizer.zero_grad()
        policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_network.parameters(), max_norm=1.0)
        self.policy_optimizer.step()
        
        self.value_optimizer.zero_grad()
        value_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.value_network.parameters(), max_norm=1.0)
        self.value_optimizer.step()
        
        return {
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
            'total_loss': policy_loss.item() + value_loss.item()
        }

# 自定义RL环境
class CustomTradingEnvironment(gym.Env):
    """自定义交易RL环境"""
    
    def __init__(self, data: np.ndarray, initial_balance: float = 10000, 
                 transaction_cost: float = 0.001, window_size: int = 10):
        super(CustomTradingEnvironment, self).__init__()
        
        self.data = data
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.window_size = window_size
        
        # 动作空间：0=持有, 1=买入, 2=卖出
        self.action_space = gym.spaces.Discrete(3)
        
        # 状态空间：价格数据、技术指标等
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(window_size * 4,), dtype=np.float32
        )
        
        # 环境状态
        self.reset()
    
    def reset(self) -> np.ndarray:
        """重置环境"""
        self.current_step = self.window_size
        self.balance = self.initial_balance
        self.position = 0  # 持仓数量
        self.total_value = self.initial_balance
        self.price_history = []
        self.action_history = []
        self.reward_history = []
        
        return self._get_state()
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """执行动作"""
        
        current_price = self.data[self.current_step]
        self.price_history.append(current_price)
        
        # 执行动作
        reward = 0
        
        if action == 1:  # 买入
            if self.balance > current_price:
                shares_to_buy = self.balance // current_price
                cost = shares_to_buy * current_price * (1 + self.transaction_cost)
                if cost <= self.balance:
                    self.balance -= cost
                    self.position += shares_to_buy
        
        elif action == 2:  # 卖出
            if self.position > 0:
                revenue = self.position * current_price * (1 - self.transaction_cost)
                self.balance += revenue
                self.position = 0
        
        # 计算总价值
        self.total_value = self.balance + self.position * current_price
        
        # 计算奖励（价值变化）
        if len(self.price_history) > 1:
            prev_total_value = self.price_history[-2] * (self.position + self.balance / current_price)
            reward = (self.total_value - prev_total_value) / prev_total_value
        
        self.action_history.append(action)
        self.reward_history.append(reward)
        
        # 更新步骤
        self.current_step += 1
        done = self.current_step >= len(self.data) - 1
        
        info = {
            'balance': self.balance,
            'position': self.position,
            'total_value': self.total_value,
            'current_price': current_price
        }
        
        return self._get_state(), reward, done, info
    
    def _get_state(self) -> np.ndarray:
        """获取状态"""
        
        if self.current_step < self.window_size:
            # 初期填充
            return np.zeros(self.window_size * 4)
        
        # 获取价格窗口
        price_window = self.data[self.current_step - self.window_size:self.current_step]
        
        # 技术指标
        sma = np.mean(price_window)  # 简单移动平均
        rsi = self._calculate_rsi(price_window)  # RSI指标
        momentum = price_window[-1] - price_window[0]  # 动量
        
        # 状态特征
        state = np.concatenate([
            price_window / np.max(price_window),  # 归一化价格
            [sma / np.max(price_window)],         # 归一化移动平均
            [rsi],                                # RSI
            [momentum / np.max(price_window)]     # 归一化动量
        ])
        
        return state
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """计算RSI指标"""
        
        if len(prices) < period + 1:
            return 50.0  # 默认值
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

# 分布式RL训练
class DistributedRLTrainer:
    """分布式强化学习训练器"""
    
    def __init__(self, agent_class, env_class, config: Dict[str, Any]):
        self.agent_class = agent_class
        self.env_class = env_class
        self.config = config
        
        # 创建环境
        self.env = env_class(**config.get('env_config', {}))
        
        # 创建智能体
        self.agent = agent_class(**config.get('agent_config', {}))
        
        # 训练统计
        self.episode_rewards = []
        self.episode_lengths = []
        self.episode_count = 0
    
    def train(self, num_episodes: int = 1000, eval_freq: int = 100) -> Dict[str, List]:
        """训练智能体"""
        
        training_logs = {
            'episode_rewards': [],
            'episode_lengths': [],
            'eval_rewards': [],
            'eval_lengths': []
        }
        
        print(f"开始训练，共 {num_episodes} 回合")
        
        for episode in range(num_episodes):
            # 训练一个回合
            episode_reward, episode_length = self._train_episode()
            
            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(episode_length)
            training_logs['episode_rewards'].append(episode_reward)
            training_logs['episode_lengths'].append(episode_length)
            
            # 评估
            if episode % eval_freq == 0:
                eval_reward, eval_length = self._evaluate_episode()
                training_logs['eval_rewards'].append(eval_reward)
                training_logs['eval_lengths'].append(eval_length)
                
                print(f"回合 {episode}: 训练奖励={episode_reward:.2f}, 评估奖励={eval_reward:.2f}")
            
            # 输出进度
            if episode % 100 == 0:
                avg_reward = np.mean(self.episode_rewards[-100:])
                print(f"回合 {episode}: 平均奖励={avg_reward:.2f}")
        
        print("训练完成")
        return training_logs
    
    def _train_episode(self) -> Tuple[float, int]:
        """训练单个回合"""
        
        state = self.env.reset()
        total_reward = 0
        steps = 0
        
        while True:
            # 选择动作
            if hasattr(self.agent, 'select_action'):
                action = self.agent.select_action(state, training=True)
            else:
                action = self.agent.select_action(state)
            
            # 执行动作
            next_state, reward, done, _ = self.env.step(action)
            
            # 存储经验（如果智能体有经验回放）
            if hasattr(self.agent, 'replay_buffer'):
                self.agent.replay_buffer.push(state, action, reward, next_state, done)
                
                # 更新智能体
                loss = self.agent.update()
            
            state = next_state
            total_reward += reward
            steps += 1
            
            if done:
                break
        
        # 更新探索率
        if hasattr(self.agent, 'update_epsilon'):
            self.agent.update_epsilon()
        
        return total_reward, steps
    
    def _evaluate_episode(self) -> Tuple[float, int]:
        """评估智能体性能"""
        
        state = self.env.reset()
        total_reward = 0
        steps = 0
        
        while True:
            # 选择动作（不探索）
            if hasattr(self.agent, 'select_action'):
                action = self.agent.select_action(state, training=False)
            else:
                action = self.agent.select_action(state)
            
            # 执行动作
            next_state, reward, done, _ = self.env.step(action)
            
            state = next_state
            total_reward += reward
            steps += 1
            
            if done:
                break
        
        return total_reward, steps

# 多智能体RL系统
class MultiAgentEnvironment:
    """多智能体环境"""
    
    def __init__(self, agents: List, shared_state: Dict[str, Any]):
        self.agents = agents
        self.shared_state = shared_state
        self.num_agents = len(agents)
    
    def train_multi_agent(self, num_episodes: int = 1000) -> Dict[str, List]:
        """多智能体训练"""
        
        training_logs = {
            'agent_rewards': [[] for _ in self.agents],
            'cooperation_scores': [],
            'competition_scores': []
        }
        
        for episode in range(num_episodes):
            episode_rewards = []
            
            # 每个智能体执行动作
            actions = []
            for i, agent in enumerate(self.agents):
                # 获取智能体的局部观察
                observation = self._get_observation(i)
                
                # 选择动作
                action = agent.select_action(observation)
                actions.append(action)
                
                episode_rewards.append(0)  # 初始化奖励
            
            # 环境响应
            observations, rewards, dones, info = self._step(actions)
            
            # 更新智能体
            for i, agent in enumerate(self.agents):
                if hasattr(agent, 'update'):
                    agent.update(
                        observations[i], actions[i], rewards[i], 
                        observations[i], dones[i]
                    )
                
                episode_rewards[i] = rewards[i]
            
            # 记录训练日志
            for i, reward in enumerate(episode_rewards):
                training_logs['agent_rewards'][i].append(reward)
            
            # 计算合作/竞争分数
            cooperation_score = np.mean(episode_rewards)  # 简化的合作分数
            training_logs['cooperation_scores'].append(cooperation_score)
            
            if episode % 100 == 0:
                avg_rewards = [np.mean(rewards[-100:]) for rewards in training_logs['agent_rewards']]
                print(f"回合 {episode}: 智能体奖励 {avg_rewards}")
        
        return training_logs
    
    def _get_observation(self, agent_id: int) -> np.ndarray:
        """获取智能体的观察"""
        # 简化的观察获取
        return np.random.randn(10)  # 随机观察
    
    def _step(self, actions: List) -> Tuple[List, List, List, Dict]:
        """环境步进"""
        # 简化的环境响应
        observations = [np.random.randn(10) for _ in self.num_agents]
        rewards = [np.random.randn() for _ in self.num_agents]
        dones = [False for _ in self.num_agents]
        info = {}
        
        return observations, rewards, dones, info

# 高级RL技术
class AdvancedRLTechniques:
    """高级RL技术集合"""
    
    def __init__(self):
        self.techniques = {
            'curriculum_learning': self._curriculum_learning,
            'her': self._her_decomposition,
            'maml': self._maml_few_shot,
            'hierarchical_rl': self._hierarchical_rl
        }
    
    def apply_curriculum_learning(self, agent, env, difficulty_progression: List[str]):
        """课程学习应用"""
        
        for difficulty in difficulty_progression:
            print(f"训练难度级别: {difficulty}")
            
            # 根据难度调整环境
            if difficulty == 'easy':
                env_config = {'max_steps': 100, 'noise_level': 0.1}
            elif difficulty == 'medium':
                env_config = {'max_steps': 200, 'noise_level': 0.2}
            elif difficulty == 'hard':
                env_config = {'max_steps': 300, 'noise_level': 0.3}
            
            # 创建相应难度的环境
            difficulty_env = env(**env_config)
            
            # 训练
            trainer = DistributedRLTrainer(type(agent), type(difficulty_env), {})
            training_logs = trainer.train(num_episodes=500)
            
            # 渐进到下一难度
            print(f"难度 {difficulty} 训练完成")
    
    def apply_her(self, agent, env, goal_environment=True):
        """Hindsight Experience Replay应用"""
        
        # 简化实现
        # 实际应用中需要复杂的经验重放机制
        
        replay_buffer = ReplayBuffer(10000)
        her_replay_buffer = ReplayBuffer(10000)
        
        # 标准HER训练循环
        for episode in range(1000):
            state = env.reset()
            goal = env.get_goal() if goal_environment else None
            
            episode_experiences = []
            
            while True:
                # 添加目标到状态（如果使用HER）
                if goal_environment:
                    extended_state = np.concatenate([state, goal])
                    action = agent.select_action(extended_state)
                else:
                    action = agent.select_action(state)
                
                next_state, reward, done, _ = env.step(action)
                
                # 存储原始经验
                experience = Experience(state, action, reward, next_state, done)
                episode_experiences.append(experience)
                
                # HER：生成替代目标
                if goal_environment and done:
                    achieved_goal = env.get_achieved_goal()
                    
                    for exp in episode_experiences:
                        # 使用新的目标重放经验
                        new_goal = achieved_goal
                        new_extended_state = np.concatenate([exp.state, new_goal])
                        new_next_extended_state = np.concatenate([exp.next_state, new_goal])
                        
                        # 重新计算奖励
                        new_reward = env.compute_reward(achieved_goal, new_goal)
                        
                        # 存储HER经验
                        her_experience = Experience(
                            new_extended_state, exp.action, new_reward, 
                            new_next_extended_state, exp.done
                        )
                        her_replay_buffer.push(*her_experience)
                
                state = next_state
                
                if done:
                    break
            
            # 使用HER经验训练
            if len(her_replay_buffer) > agent.batch_size:
                for _ in range(10):  # 多次更新
                    agent.update()
    
    def _curriculum_learning(self, agent, env, progression):
        """课程学习实现"""
        pass
    
    def _her_decomposition(self, agent, env):
        """HER实现"""
        pass
    
    def _maml_few_shot(self, agent, env):
        """MAML实现"""
        pass
    
    def _hierarchical_rl(self, agent, env):
        """分层RL实现"""
        pass

# 使用示例
async def main():
    print("=== 强化学习实现演示 ===")
    
    # 1. 使用内置Gym环境演示DQN
    print("\n1. 使用CartPole环境演示DQN")
    
    try:
        # 创建CartPole环境
        env = gym.make('CartPole-v1')
        
        # 创建DQN智能体
        agent = DQNAgent(
            state_dim=env.observation_space.shape[0],
            action_dim=env.action_space.n,
            learning_rate=1e-3
        )
        
        # 训练
        trainer = DistributedRLTrainer(
            agent.__class__, 
            lambda: env,
            {'agent_config': {'learning_rate': 1e-3}}
        )
        
        training_logs = trainer.train(num_episodes=200)  # 减少训练回合数
        print("CartPole训练完成")
        
        # 保存模型
        agent.save_model('dqn_cartpole.pth')
        print("模型已保存")
        
    except Exception as e:
        print(f"CartPole环境演示失败: {e}")
    
    # 2. 自定义交易环境演示
    print("\n2. 自定义交易环境演示")
    
    # 生成模拟交易数据
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=1000, freq='D')
    price_changes = np.random.normal(0.001, 0.02, len(dates))
    prices = 100 * np.cumprod(1 + price_changes)
    
    # 创建交易环境
    trading_env = CustomTradingEnvironment(
        data=prices.values,
        initial_balance=10000,
        window_size=20
    )
    
    # 创建交易智能体
    trading_agent = DQNAgent(
        state_dim=trading_env.observation_space.shape[0],
        action_dim=trading_env.action_space.n,
        learning_rate=1e-4,
        epsilon=0.9,  # 保守的探索策略
        epsilon_decay=0.999
    )
    
    # 训练交易智能体
    trading_trainer = DistributedRLTrainer(
        trading_agent.__class__,
        lambda: trading_env,
        {'agent_config': {'learning_rate': 1e-4}}
    )
    
    trading_logs = trading_trainer.train(num_episodes=100)
    print("交易环境训练完成")
    
    # 3. Actor-Critic演示
    print("\n3. Actor-Critic演示")
    
    actor_critic_agent = ActorCriticAgent(
        state_dim=4,
        action_dim=2,
        learning_rate=1e-3
    )
    
    # 模拟训练数据
    states = [np.random.randn(4) for _ in range(100)]
    actions = [np.random.randint(0, 2) for _ in range(100)]
    rewards = [np.random.randn() for _ in range(100)]
    next_states = [np.random.randn(4) for _ in range(100)]
    dones = [False for _ in range(100)]
    
    # 更新智能体
    losses = []
    for _ in range(10):
        loss_info = actor_critic_agent.update(states, actions, rewards, next_states, dones)
        losses.append(loss_info)
    
    print("Actor-Critic更新完成")
    
    # 4. 多智能体演示
    print("\n4. 多智能体系统演示")
    
    # 创建多个智能体
    multi_agents = [ActorCriticAgent(10, 3) for _ in range(3)]
    shared_state = {'world_state': np.random.randn(20)}
    
    multi_agent_env = MultiAgentEnvironment(multi_agents, shared_state)
    multi_agent_logs = multi_agent_env.train_multi_agent(num_episodes=50)
    
    print("多智能体训练完成")
    
    # 5. 高级技术演示
    print("\n5. 高级RL技术演示")
    
    advanced_techniques = AdvancedRLTechniques()
    
    # 课程学习
    difficulty_progression = ['easy', 'medium', 'hard']
    print("开始课程学习演示...")
    advanced_techniques.apply_curriculum_learning(
        trading_agent, CustomTradingEnvironment, difficulty_progression
    )
    
    # 6. 性能分析
    print("\n=== 性能分析 ===")
    
    # 绘制训练曲线
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # DQN训练曲线
    if 'episode_rewards' in trading_logs:
        axes[0, 0].plot(trading_logs['episode_rewards'])
        axes[0, 0].set_title('DQN 训练奖励曲线')
        axes[0, 0].set_xlabel('回合')
        axes[0, 0].set_ylabel('奖励')
    
    # Actor-Critic损失
    if losses:
        policy_losses = [loss['policy_loss'] for loss in losses]
        value_losses = [loss['value_loss'] for loss in losses]
        axes[0, 1].plot(policy_losses, label='Policy Loss')
        axes[0, 1].plot(value_losses, label='Value Loss')
        axes[0, 1].set_title('Actor-Critic 损失')
        axes[0, 1].legend()
    
    # 多智能体奖励
    if 'agent_rewards' in multi_agent_logs:
        for i, rewards in enumerate(multi_agent_logs['agent_rewards'][:3]):
            axes[1, 0].plot(rewards, label=f'Agent {i+1}')
        axes[1, 0].set_title('多智能体奖励')
        axes[1, 0].legend()
    
    # 合作分数
    if 'cooperation_scores' in multi_agent_logs:
        axes[1, 1].plot(multi_agent_logs['cooperation_scores'])
        axes[1, 1].set_title('合作分数')
        axes[1, 1].set_xlabel('回合')
        axes[1, 1].set_ylabel('合作分数')
    
    plt.tight_layout()
    plt.savefig('rl_performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("性能分析图表已保存")
    
    # 7. 模型评估
    print("\n=== 模型评估 ===")
    
    # 评估交易智能体
    eval_reward, eval_steps = trading_trainer._evaluate_episode()
    print(f"交易智能体评估: 奖励={eval_reward:.2f}, 步数={eval_steps}")
    
    # 评估CartPole智能体
    try:
        eval_reward_cartpole, eval_steps_cartpole = trainer._evaluate_episode()
        print(f"CartPole智能体评估: 奖励={eval_reward_cartpole:.2f}, 步数={eval_steps_cartpole}")
    except:
        print("CartPole评估失败")
    
    return {
        'dqn_cartpole': training_logs,
        'trading_agent': trading_logs,
        'actor_critic': losses,
        'multi_agent': multi_agent_logs,
        'performance_fig': fig
    }

# 运行示例
if __name__ == "__main__":
    result = asyncio.run(main())
```

## Best Practices

### 1. 环境设计原则
- **标准化接口**: 遵循Gym环境标准
- **奖励设计**: 设计有意义的奖励函数
- **状态空间**: 确保状态信息充分且有效
- **动作空间**: 平衡动作的复杂性和有效性

### 2. 算法选择策略
- **问题匹配**: 根据问题特性选择合适的RL算法
- **样本效率**: 考虑算法的样本效率
- **稳定性**: 选择训练稳定的算法
- **扩展性**: 考虑算法的可扩展性

### 3. 训练优化技巧
- **超参数调优**: 仔细调整学习率、探索率等超参数
- **经验回放**: 合理设置经验回放缓冲区大小
- **网络架构**: 选择合适的神经网络架构
- **正则化**: 使用适当的正则化技术

### 4. 部署和监控
- **模型验证**: 部署前充分验证模型性能
- **在线学习**: 考虑在线学习和适应能力
- **安全约束**: 确保RL代理的安全行为
- **性能监控**: 持续监控代理性能变化

## Integration Patterns

### 1. 实时控制系统
```python
# 实时RL控制系统
class RealTimeRLController:
    def __init__(self, trained_agent, control_config):
        self.agent = trained_agent
        self.config = control_config
        self.state_buffer = deque(maxlen=10)
        self.performance_monitor = PerformanceMonitor()
    
    def control_step(self, current_state):
        """实时控制步骤"""
        self.state_buffer.append(current_state)
        
        # 使用模型预测控制动作
        if hasattr(self.agent, 'select_action'):
            action = self.agent.select_action(current_state, training=False)
        else:
            action = self.agent.select_action(current_state)
        
        # 监控性能
        self.performance_monitor.log_state_action(current_state, action)
        
        # 验证动作安全性
        if not self._validate_action_safety(action, current_state):
            action = self._get_safe_action(current_state)
        
        return action
    
    def _validate_action_safety(self, action, state):
        """验证动作安全性"""
        # 实现安全检查逻辑
        return True
    
    def _get_safe_action(self, state):
        """获取安全动作"""
        return 0  # 默认安全动作
```

### 2. 云原生部署
```yaml
# Kubernetes RL服务
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rl-agent-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rl-agent
  template:
    metadata:
      labels:
        app: rl-agent
    spec:
      containers:
      - name: rl-agent
        image: rl-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: MODEL_PATH
          value: "/models/rl_agent.pth"
        - name: ENVIRONMENT_TYPE
          value: "production"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        volumeMounts:
        - name: model-volume
          mountPath: /models
      volumes:
      - name: model-volume
        persistentVolumeClaim:
          claimName: rl-model-pvc
```

## Success Metrics

### 1. 学习效果指标
- **收敛性能**: 算法收敛到最优策略的速度
- **样本效率**: 达到目标性能所需的样本数量
- **最终性能**: 学习到的策略的最终性能水平
- **稳定性**: 训练过程的稳定性和一致性

### 2. 算法性能指标
- **计算效率**: 算法的时间复杂度和空间复杂度
- **并行化能力**: 算法支持并行训练的程度
- **内存使用**: 训练和推理的内存消耗
- **推理速度**: 实时决策的响应时间

### 3. 应用效果指标
- **任务完成率**: RL代理完成任务的比例
- **奖励最大化**: 累积奖励的优化程度
- **安全性**: 代理行为的安全性水平
- **适应性**: 对环境变化的适应能力

### 4. 工程指标
- **开发效率**: 开发RL应用的效率
- **部署复杂度**: 部署RL系统的复杂度
- **维护成本**: 长期维护的成本
- **可解释性**: RL决策的可解释程度

---

*强化学习是解决序列决策问题的强大工具，通过智能体与环境的交互学习最优策略，在机器人控制、游戏AI、推荐系统、资源优化等领域有着广泛的应用前景。*
