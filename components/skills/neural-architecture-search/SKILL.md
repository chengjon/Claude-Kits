---
name: neural-architecture-search
description: "神经架构搜索与自动设计专家，精通搜索空间设计、强化学习搜索和进化算法。构建自动化设计系统、性能评估框架和架构生成工具，处理NAS算法、神经网络自动设计和架构优化。使用PROACTIVELY进行神经网络设计、NAS实施或模型架构优化。"
---

# 神经架构搜索技能

## When to Use
Use this skill when designing and optimizing neural network architectures automatically, implementing efficient neural architecture search (NAS) algorithms, creating domain-specific architectures, optimizing model performance for specific tasks, or building automated deep learning design systems. Essential for computer vision, NLP, and specialized ML applications requiring custom architectures.

## Core Concepts

### 1. 搜索空间设计
- **细胞架构**: 搜索可重复使用的网络细胞单元
- **层连接模式**: 自动发现最优的层间连接方式
- **超参数空间**: 动态调整网络深度、宽度、激活函数
- **搜索约束**: 基于资源限制的架构约束设计

### 2. 搜索策略算法
- **强化学习NAS**: 使用RL代理搜索最优架构
- **进化算法**: 基于进化的架构优化策略
- **贝叶斯优化**: 概率模型指导的架构搜索
- **梯度可微搜索**: 可微分的架构搜索方法

### 3. 性能评估技术
- **代理训练**: 使用小模型快速评估架构性能
- **早停机制**: 基于早期性能的架构筛选
- **权重共享**: 减少架构评估的计算成本
- **渐进搜索**: 分阶段逐步细化搜索空间

### 4. 多目标优化
- **准确率优化**: 最大化模型预测准确率
- **计算效率**: 平衡性能与计算资源消耗
- **模型大小**: 约束模型参数数量和存储空间
- **推理速度**: 优化模型的实时推理性能

## Code Examples

### NAS基础架构搜索系统
```python
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from typing import Dict, List, Optional, Any, Tuple
from abc import ABC, abstractmethod
import copy
import itertools
from collections import deque

class NASSearchSpace:
    """神经架构搜索空间定义"""
    
    def __init__(self):
        # 定义搜索空间配置
        self.search_space_config = {
            'num_blocks': {'min': 5, 'max': 20},
            'channels': [16, 32, 64, 128, 256, 512],
            'kernel_sizes': [1, 3, 5, 7],
            'activation_functions': ['relu', 'gelu', 'swish', 'mish'],
            'normalization_layers': ['batch_norm', 'group_norm', 'layer_norm'],
            'skip_connections': [True, False],
            'attention_mechanisms': ['none', 'se_block', 'cbam', 'eca'],
            'block_types': ['basic', 'bottleneck', 'depthwise', 'shufflenet']
        }
    
    def sample_architecture(self) -> Dict[str, Any]:
        """随机采样一个网络架构"""
        architecture = {}
        
        # 采样基础配置
        architecture['num_blocks'] = random.randint(
            self.search_space_config['num_blocks']['min'],
            self.search_space_config['num_blocks']['max']
        )
        
        # 采样每层的配置
        architecture['layer_configs'] = []
        input_channels = self.search_space_config['channels'][0]
        
        for i in range(architecture['num_blocks']):
            layer_config = {
                'out_channels': random.choice(self.search_space_config['channels']),
                'kernel_size': random.choice(self.search_space_config['kernel_sizes']),
                'activation': random.choice(self.search_space_config['activation_functions']),
                'normalization': random.choice(self.search_space_config['normalization_layers']),
                'skip_connection': random.choice(self.search_space_config['skip_connections']),
                'attention': random.choice(self.search_space_config['attention_mechanisms']),
                'block_type': random.choice(self.search_space_config['block_types'])
            }
            architecture['layer_configs'].append(layer_config)
            input_channels = layer_config['out_channels']
        
        return architecture

class NeuralArchitectureGenerator:
    """神经架构生成器"""
    
    def __init__(self, input_shape: Tuple[int, ...], num_classes: int):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.search_space = NASSearchSpace()
    
    def generate_model(self, architecture: Dict[str, Any]) -> nn.Module:
        """根据架构配置生成PyTorch模型"""
        
        class NASModel(nn.Module):
            def __init__(self, config, input_shape, num_classes):
                super(NASModel, self).__init__()
                self.config = config
                self.input_shape = input_shape
                
                # 构建模型层
                self.layers = self._build_layers(config)
                self.classifier = self._build_classifier(config)
            
            def _build_layers(self, config):
                layers = []
                current_channels = config['layer_configs'][0]['out_channels']
                
                # 初始卷积层
                layers.append(nn.Conv2d(
                    self.input_shape[0], current_channels, 
                    kernel_size=3, padding=1
                ))
                layers.append(self._get_activation_layer(config['layer_configs'][0]['activation']))
                
                # 构建搜索到的块
                for i, layer_config in enumerate(config['layer_configs']):
                    block = self._build_block(
                        current_channels, layer_config
                    )
                    layers.append(block)
                    current_channels = layer_config['out_channels']
                
                return nn.Sequential(*layers)
            
            def _build_block(self, in_channels: int, config: Dict) -> nn.Module:
                """构建单个网络块"""
                
                if config['block_type'] == 'basic':
                    block = self._build_basic_block(in_channels, config)
                elif config['block_type'] == 'bottleneck':
                    block = self._build_bottleneck_block(in_channels, config)
                elif config['block_type'] == 'depthwise':
                    block = self._build_depthwise_block(in_channels, config)
                else:
                    block = self._build_basic_block(in_channels, config)
                
                # 添加注意力机制
                if config['attention'] != 'none':
                    attention_layer = self._build_attention_block(
                        config['out_channels'], config['attention']
                    )
                    block = nn.Sequential(block, attention_layer)
                
                return block
            
            def _build_basic_block(self, in_channels: int, config: Dict) -> nn.Module:
                """构建基本残差块"""
                out_channels = config['out_channels']
                kernel_size = config['kernel_size']
                activation = self._get_activation_layer(config['activation'])
                
                block = [nn.Conv2d(in_channels, out_channels, kernel_size, padding=1)]
                
                if config['normalization'] == 'batch_norm':
                    block.append(nn.BatchNorm2d(out_channels))
                elif config['normalization'] == 'group_norm':
                    block.append(nn.GroupNorm(8, out_channels))
                
                block.append(activation)
                
                # 第二个卷积层
                block.append(nn.Conv2d(out_channels, out_channels, kernel_size, padding=1))
                
                if config['normalization'] == 'batch_norm':
                    block.append(nn.BatchNorm2d(out_channels))
                
                # 残差连接
                if config['skip_connection'] and in_channels == out_channels:
                    layers = [nn.Sequential(*block)]
                    layers.append(nn.Identity() if in_channels == out_channels else nn.Conv2d(in_channels, out_channels, 1))
                    return ResidualBlock(nn.Sequential(*block), nn.Identity() if in_channels == out_channels else nn.Conv2d(in_channels, out_channels, 1))
                else:
                    return nn.Sequential(*block)
            
            def _build_bottleneck_block(self, in_channels: int, config: Dict) -> nn.Module:
                """构建瓶颈块"""
                out_channels = config['out_channels']
                bottleneck_channels = out_channels // 4
                
                layers = [
                    nn.Conv2d(in_channels, bottleneck_channels, 1),
                    self._get_activation_layer(config['activation'])
                ]
                
                if config['normalization'] == 'batch_norm':
                    layers.append(nn.BatchNorm2d(bottleneck_channels))
                
                layers.extend([
                    nn.Conv2d(bottleneck_channels, bottleneck_channels, config['kernel_size'], padding=1),
                    self._get_activation_layer(config['activation'])
                ])
                
                if config['normalization'] == 'batch_norm':
                    layers.append(nn.BatchNorm2d(bottleneck_channels))
                
                layers.extend([
                    nn.Conv2d(bottleneck_channels, out_channels, 1),
                ])
                
                if config['normalization'] == 'batch_norm':
                    layers.append(nn.BatchNorm2d(out_channels))
                
                if config['skip_connection'] and in_channels == out_channels:
                    return ResidualBlock(nn.Sequential(*layers), nn.Identity())
                else:
                    return nn.Sequential(*layers)
            
            def _build_depthwise_block(self, in_channels: int, config: Dict) -> nn.Module:
                """构建深度可分离卷积块"""
                out_channels = config['out_channels']
                
                layers = [
                    nn.Conv2d(in_channels, in_channels, config['kernel_size'], 
                             padding=1, groups=in_channels),
                    self._get_activation_layer(config['activation'])
                ]
                
                if config['normalization'] == 'batch_norm':
                    layers.append(nn.BatchNorm2d(in_channels))
                
                layers.extend([
                    nn.Conv2d(in_channels, out_channels, 1),
                    self._get_activation_layer(config['activation'])
                ])
                
                if config['normalization'] == 'batch_norm':
                    layers.append(nn.BatchNorm2d(out_channels))
                
                if config['skip_connection'] and in_channels == out_channels:
                    return ResidualBlock(nn.Sequential(*layers), nn.Identity())
                else:
                    return nn.Sequential(*layers)
            
            def _build_attention_block(self, channels: int, attention_type: str) -> nn.Module:
                """构建注意力机制"""
                if attention_type == 'se_block':
                    return SEBlock(channels)
                elif attention_type == 'cbam':
                    return CBAMBlock(channels)
                elif attention_type == 'eca':
                    return ECABlock(channels)
                else:
                    return nn.Identity()
            
            def _get_activation_layer(self, activation_name: str) -> nn.Module:
                """获取激活函数层"""
                if activation_name == 'relu':
                    return nn.ReLU(inplace=True)
                elif activation_name == 'gelu':
                    return nn.GELU()
                elif activation_name == 'swish':
                    return Swish()
                elif activation_name == 'mish':
                    return nn.Mish()
                else:
                    return nn.ReLU(inplace=True)
            
            def _build_classifier(self, config):
                """构建分类器"""
                return nn.Sequential(
                    nn.AdaptiveAvgPool2d((1, 1)),
                    nn.Flatten(),
                    nn.Linear(config['layer_configs'][-1]['out_channels'], self.num_classes)
                )
            
            def forward(self, x):
                x = self.layers(x)
                x = self.classifier(x)
                return x
        
        return NASModel(architecture, self.input_shape, self.num_classes)

# 注意力机制模块
class SEBlock(nn.Module):
    """Squeeze-and-Excitation块"""
    def __init__(self, channels, reduction=16):
        super(SEBlock, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channels, channels // reduction),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y.expand_as(x)

class CBAMBlock(nn.Module):
    """Convolutional Block Attention Module"""
    def __init__(self, channels, reduction=16, kernel_size=7):
        super(CBAMBlock, self).__init__()
        self.channel_attention = ChannelAttention(channels, reduction)
        self.spatial_attention = SpatialAttention(kernel_size)
    
    def forward(self, x):
        x = self.channel_attention(x)
        x = self.spatial_attention(x)
        return x

class ChannelAttention(nn.Module):
    def __init__(self, channels, reduction=16):
        super(ChannelAttention, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.mlp = nn.Sequential(
            nn.Linear(channels, channels // reduction),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels)
        )
    
    def forward(self, x):
        avg_out = self.mlp(self.avg_pool(x).view(x.size(0), -1)).view(x.size(0), x.size(1), 1, 1)
        max_out = self.mlp(self.max_pool(x).view(x.size(0), -1)).view(x.size(0), x.size(1), 1, 1)
        attention = torch.sigmoid(avg_out + max_out)
        return x * attention

class SpatialAttention(nn.Module):
    def __init__(self, kernel_size=7):
        super(SpatialAttention, self).__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size, padding=kernel_size // 2, bias=False)
    
    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        attention = torch.cat([avg_out, max_out], dim=1)
        attention = self.conv(attention)
        attention = torch.sigmoid(attention)
        return x * attention

class ECABlock(nn.Module):
    """Efficient Channel Attention"""
    def __init__(self, channels, gamma=2, b=1):
        super(ECABlock, self).__init__()
        t = int(abs((np.log(channels, 2) + b) / gamma))
        k = t if t % 2 else t + 1
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.conv = nn.Conv1d(1, 1, kernel_size=k, padding=k // 2, bias=False)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        y = self.avg_pool(x)
        y = self.conv(y.squeeze(-1).transpose(-1, -2)).transpose(-1, -2).unsqueeze(-1)
        y = self.sigmoid(y)
        return x * y.expand_as(x)

class ResidualBlock(nn.Module):
    """残差块"""
    def __init__(self, main_branch, skip_branch):
        super(ResidualBlock, self).__init__()
        self.main_branch = main_branch
        self.skip_branch = skip_branch
    
    def forward(self, x):
        return self.main_branch(x) + self.skip_branch(x)

class Swish(nn.Module):
    """Swish激活函数"""
    def forward(self, x):
        return x * torch.sigmoid(x)

# 神经架构搜索算法
class NeuralArchitectureSearch:
    """神经架构搜索主算法"""
    
    def __init__(self, 
                 input_shape: Tuple[int, ...],
                 num_classes: int,
                 search_strategy: str = 'evolutionary',
                 max_evaluations: int = 100,
                 population_size: int = 50,
                 regularization: float = 0.001):
        
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.search_strategy = search_strategy
        self.max_evaluations = max_evaluations
        self.population_size = population_size
        self.regularization = regularization
        
        self.generator = NeuralArchitectureGenerator(input_shape, num_classes)
        self.evaluator = ArchitectureEvaluator()
        self.search_history = []
        self.best_architecture = None
        self.best_score = -np.inf
    
    def search(self, 
               train_loader,
               val_loader,
               device: str = 'cuda') -> Dict[str, Any]:
        """执行神经架构搜索"""
        
        if self.search_strategy == 'evolutionary':
            return self._evolutionary_search(train_loader, val_loader, device)
        elif self.search_strategy == 'random':
            return self._random_search(train_loader, val_loader, device)
        elif self.search_strategy == 'bayesian':
            return self._bayesian_search(train_loader, val_loader, device)
        else:
            raise ValueError(f"不支持的搜索策略: {self.search_strategy}")
    
    def _evolutionary_search(self, 
                           train_loader,
                           val_loader,
                           device: str) -> Dict[str, Any]:
        """进化算法搜索"""
        
        # 初始化种群
        population = []
        for _ in range(self.population_size):
            architecture = self.generator.search_space.sample_architecture()
            population.append(architecture)
        
        print(f"初始化种群大小: {len(population)}")
        
        for generation in range(self.max_evaluations // self.population_size):
            print(f"第 {generation + 1} 代搜索...")
            
            # 评估种群
            population_scores = []
            for arch in population:
                score = self.evaluator.evaluate_architecture(
                    arch, train_loader, val_loader, device
                )
                population_scores.append(score)
                
                # 更新最佳架构
                if score > self.best_score:
                    self.best_score = score
                    self.best_architecture = arch
            
            # 记录搜索历史
            generation_info = {
                'generation': generation,
                'population_size': len(population),
                'best_score': max(population_scores),
                'avg_score': np.mean(population_scores),
                'best_architecture': self.best_architecture.copy()
            }
            self.search_history.append(generation_info)
            
            print(f"最佳得分: {generation_info['best_score']:.4f}")
            
            # 选择、交叉、变异生成下一代
            population = self._evolve_population(population, population_scores)
        
        return {
            'best_architecture': self.best_architecture,
            'best_score': self.best_score,
            'search_history': self.search_history,
            'final_population': population
        }
    
    def _evolve_population(self, 
                          population: List[Dict],
                          scores: List[float]) -> List[Dict]:
        """进化操作：选择、交叉、变异"""
        
        # 按分数排序
        sorted_indices = np.argsort(scores)[::-1]
        sorted_population = [population[i] for i in sorted_indices]
        
        # 精英保留
        elite_size = max(1, len(population) // 4)
        new_population = sorted_population[:elite_size].copy()
        
        # 交叉和变异
        while len(new_population) < len(population):
            # 选择父代
            parent1 = self._tournament_selection(sorted_population, scores, tournament_size=3)
            parent2 = self._tournament_selection(sorted_population, scores, tournament_size=3)
            
            # 交叉
            child1, child2 = self._crossover(parent1, parent2)
            
            # 变异
            child1 = self._mutate(child1)
            child2 = self._mutate(child2)
            
            new_population.extend([child1, child2])
        
        return new_population[:len(population)]
    
    def _tournament_selection(self, 
                             population: List[Dict],
                             scores: List[float],
                             tournament_size: int = 3) -> Dict:
        """锦标赛选择"""
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_scores = [scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_scores)]
        return population[winner_idx]
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
        """交叉操作"""
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        # 随机选择交叉点
        num_blocks = min(len(parent1['layer_configs']), len(parent2['layer_configs']))
        if num_blocks > 1:
            crossover_point = random.randint(1, num_blocks - 1)
            
            # 交换层配置
            child1['layer_configs'] = (
                parent1['layer_configs'][:crossover_point] + 
                parent2['layer_configs'][crossover_point:]
            )
            child2['layer_configs'] = (
                parent2['layer_configs'][:crossover_point] + 
                parent1['layer_configs'][crossover_point:]
            )
        
        return child1, child2
    
    def _mutate(self, architecture: Dict) -> Dict:
        """变异操作"""
        mutated = copy.deepcopy(architecture)
        
        # 随机变异层配置
        if mutated['layer_configs']:
            layer_idx = random.randint(0, len(mutated['layer_configs']) - 1)
            layer_config = mutated['layer_configs'][layer_idx]
            
            # 随机选择一个属性进行变异
            attributes = ['out_channels', 'kernel_size', 'activation', 'normalization', 
                         'skip_connection', 'attention', 'block_type']
            attr_to_mutate = random.choice(attributes)
            
            if attr_to_mutate in layer_config:
                if attr_to_mutate == 'out_channels':
                    layer_config[attr_to_mutate] = random.choice(
                        self.generator.search_space.search_space_config['channels']
                    )
                elif attr_to_mutate == 'kernel_size':
                    layer_config[attr_to_mutate] = random.choice(
                        self.generator.search_space.search_space_config['kernel_sizes']
                    )
                elif attr_to_mutate == 'activation':
                    layer_config[attr_to_mutate] = random.choice(
                        self.generator.search_space.search_space_config['activation_functions']
                    )
                elif attr_to_mutate == 'normalization':
                    layer_config[attr_to_mutate] = random.choice(
                        self.generator.search_space.search_space_config['normalization_layers']
                    )
                elif attr_to_mutate == 'skip_connection':
                    layer_config[attr_to_mutate] = random.choice(
                        self.generator.search_space.search_space_config['skip_connections']
                    )
                elif attr_to_mutate == 'attention':
                    layer_config[attr_to_mutate] = random.choice(
                        self.generator.search_space.search_space_config['attention_mechanisms']
                    )
                elif attr_to_mutate == 'block_type':
                    layer_config[attr_to_mutate] = random.choice(
                        self.generator.search_space.search_space_config['block_types']
                    )
        
        return mutated
    
    def _random_search(self, 
                      train_loader,
                      val_loader,
                      device: str) -> Dict[str, Any]:
        """随机搜索"""
        
        for evaluation in range(self.max_evaluations):
            # 随机采样架构
            architecture = self.generator.search_space.sample_architecture()
            
            # 评估架构
            score = self.evaluator.evaluate_architecture(
                architecture, train_loader, val_loader, device
            )
            
            # 更新最佳架构
            if score > self.best_score:
                self.best_score = score
                self.best_architecture = architecture
            
            # 记录搜索历史
            search_info = {
                'evaluation': evaluation,
                'architecture': architecture,
                'score': score,
                'best_score': self.best_score
            }
            self.search_history.append(search_info)
            
            if (evaluation + 1) % 10 == 0:
                print(f"随机搜索进度: {evaluation + 1}/{self.max_evaluations}, 最佳得分: {self.best_score:.4f}")
        
        return {
            'best_architecture': self.best_architecture,
            'best_score': self.best_score,
            'search_history': self.search_history
        }

class ArchitectureEvaluator:
    """架构评估器"""
    
    def __init__(self, 
                 epochs: int = 20,
                 learning_rate: float = 0.001,
                 batch_size: int = 64,
                 regularization: float = 0.001):
        
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.regularization = regularization
        self.early_stopping_patience = 5
    
    def evaluate_architecture(self, 
                            architecture: Dict,
                            train_loader,
                            val_loader,
                            device: str = 'cuda') -> float:
        """评估单个架构"""
        
        # 生成模型
        input_shape = next(iter(train_loader))[0].shape
        num_classes = len(train_loader.dataset.classes)
        generator = NeuralArchitectureGenerator(input_shape, num_classes)
        model = generator.generate_model(architecture)
        
        # 计算模型复杂度指标
        complexity_score = self._calculate_complexity_score(model)
        
        # 快速训练评估
        performance_score = self._quick_training_evaluation(
            model, train_loader, val_loader, device
        )
        
        # 多目标优化得分
        final_score = self._calculate_final_score(
            performance_score, complexity_score
        )
        
        return final_score
    
    def _calculate_complexity_score(self, model: nn.Module) -> float:
        """计算模型复杂度得分"""
        
        # 计算参数数量
        total_params = sum(p.numel() for p in model.parameters())
        
        # 计算FLOPs
        from torchsummary import summary
        try:
            sample_input = torch.randn(1, *model.input_shape)
            flops = self._calculate_flops(model, sample_input)
        except:
            flops = total_params  # 简化计算
        
        # 复杂度得分：参数数量和FLOPs的组合
        complexity_score = np.log(total_params) + np.log(flops)
        
        return complexity_score
    
    def _calculate_flops(self, model: nn.Module, input_tensor: torch.Tensor) -> int:
        """计算模型的FLOPs"""
        # 简化的FLOPs计算
        # 实际应用中可以使用更精确的工具如fvcore
        with torch.no_grad():
            flops = 0
            for module in model.modules():
                if isinstance(module, nn.Conv2d):
                    output_size = ((input_tensor.shape[2] - module.kernel_size[0] + 2 * module.padding[0]) // module.stride[0] + 1)
                    output_size = ((output_size - module.kernel_size[0] + 2 * module.padding[0]) // module.stride[0] + 1)
                    flops += module.in_channels * module.out_channels * module.kernel_size[0] * module.kernel_size[1] * output_size * output_size
                elif isinstance(module, nn.Linear):
                    flops += module.in_features * module.out_features
                input_tensor = module(input_tensor)
        
        return flops
    
    def _quick_training_evaluation(self, 
                                  model: nn.Module,
                                  train_loader,
                                  val_loader,
                                  device: str) -> float:
        """快速训练评估"""
        
        model = model.to(device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=self.learning_rate, weight_decay=self.regularization)
        
        # 短期训练
        best_val_acc = 0
        no_improvement_count = 0
        
        for epoch in range(self.epochs):
            # 训练
            model.train()
            for batch_idx, (data, target) in enumerate(train_loader):
                if batch_idx >= 10:  # 限制训练步数
                    break
                    
                data, target = data.to(device), target.to(device)
                optimizer.zero_grad()
                output = model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
            
            # 验证
            val_acc = self._validate_model(model, val_loader, device)
            
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                no_improvement_count = 0
            else:
                no_improvement_count += 1
            
            # 早停
            if no_improvement_count >= self.early_stopping_patience:
                break
        
        return best_val_acc
    
    def _validate_model(self, model: nn.Module, val_loader, device: str) -> float:
        """验证模型"""
        
        model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(device), target.to(device)
                outputs = model(data)
                _, predicted = torch.max(outputs.data, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()
        
        return correct / total
    
    def _calculate_final_score(self, 
                              performance_score: float,
                              complexity_score: float) -> float:
        """计算最终得分"""
        
        # 性能得分权重：0.8，复杂度得分权重：0.2
        performance_weight = 0.8
        complexity_weight = 0.2
        
        # 复杂度得分转换为惩罚项（复杂度越高惩罚越大）
        complexity_penalty = np.exp(-complexity_score / 1000)
        
        final_score = (performance_weight * performance_score + 
                      complexity_weight * complexity_penalty)
        
        return final_score

# 高级NAS技术
class ProgressiveNeuralArchitectureSearch:
    """渐进式神经架构搜索"""
    
    def __init__(self, base_nas: NeuralArchitectureSearch):
        self.base_nas = base_nas
        self.search_phases = {
            'coarse': {'population_size': 100, 'evaluations': 200, 'epochs': 10},
            'medium': {'population_size': 50, 'evaluations': 300, 'epochs': 20},
            'fine': {'population_size': 20, 'evaluations': 500, 'epochs': 50}
        }
    
    def progressive_search(self, train_loader, val_loader, device: str = 'cuda') -> Dict[str, Any]:
        """渐进式搜索"""
        
        all_results = {}
        current_population = []
        
        for phase_name, phase_config in self.search_phases.items():
            print(f"开始{phase_name}搜索阶段...")
            
            # 更新NAS配置
            self.base_nas.population_size = phase_config['population_size']
            self.base_nas.max_evaluations = phase_config['evaluations']
            self.base_nas.evaluator.epochs = phase_config['epochs']
            
            # 如果不是第一阶段，使用上一阶段的种群
            if current_population:
                self.base_nas.search_history = all_results.get('coarse', {}).get('search_history', [])
            
            # 执行搜索
            phase_result = self.base_nas.search(train_loader, val_loader, device)
            all_results[phase_name] = phase_result
            
            # 更新当前种群
            current_population = phase_result.get('final_population', [])
            
            print(f"{phase_name}阶段完成，最佳得分: {phase_result['best_score']:.4f}")
        
        return {
            'progressive_results': all_results,
            'final_architecture': all_results['fine']['best_architecture'],
            'final_score': all_results['fine']['best_score']
        }

# 多目标NAS
class MultiObjectiveNAS:
    """多目标神经架构搜索"""
    
    def __init__(self, base_nas: NeuralArchitectureSearch):
        self.base_nas = base_nas
        self.objective_weights = {
            'accuracy': 0.5,
            'latency': 0.3,
            'memory': 0.2
        }
    
    def search(self, 
               train_loader,
               val_loader,
               device: str = 'cuda',
               target_constraints: Dict[str, float] = None) -> Dict[str, Any]:
        """多目标搜索"""
        
        # 执行基础搜索
        base_result = self.base_nas.search(train_loader, val_loader, device)
        
        # 评估多目标
        multi_objective_scores = []
        for arch_info in base_result['search_history']:
            architecture = arch_info.get('best_architecture', {})
            if architecture:
                scores = self._evaluate_multi_objectives(
                    architecture, train_loader, val_loader, device
                )
                multi_objective_scores.append(scores)
        
        # Pareto前沿分析
        pareto_front = self._find_pareto_front(multi_objective_scores)
        
        return {
            'base_result': base_result,
            'multi_objective_scores': multi_objective_scores,
            'pareto_front': pareto_front,
            'objective_weights': self.objective_weights
        }
    
    def _evaluate_multi_objectives(self, 
                                 architecture: Dict,
                                 train_loader,
                                 val_loader,
                                 device: str) -> Dict[str, float]:
        """评估多目标"""
        
        # 生成模型
        generator = NeuralArchitectureGenerator(
            next(iter(train_loader))[0].shape, 
            len(train_loader.dataset.classes)
        )
        model = generator.generate_model(architecture)
        
        # 评估准确率
        accuracy_score = self.base_nas.evaluator._quick_training_evaluation(
            model, train_loader, val_loader, device
        )
        
        # 评估延迟
        latency_score = self._measure_latency(model, device)
        
        # 评估内存
        memory_score = self._measure_memory(model)
        
        return {
            'accuracy': accuracy_score,
            'latency': latency_score,
            'memory': memory_score
        }
    
    def _measure_latency(self, model: nn.Module, device: str) -> float:
        """测量推理延迟"""
        model.eval()
        
        # 使用小批量测量
        dummy_input = torch.randn(1, *model.input_shape).to(device)
        
        with torch.no_grad():
            start_time = time.time()
            for _ in range(100):
                _ = model(dummy_input)
            end_time = time.time()
        
        avg_latency = (end_time - start_time) / 100
        return avg_latency
    
    def _measure_memory(self, model: nn.Module) -> float:
        """测量模型内存使用"""
        param_size = sum(p.numel() * p.element_size() for p in model.parameters())
        buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
        total_size = param_size + buffer_size
        
        return total_size / (1024 * 1024)  # MB
    
    def _find_pareto_front(self, scores_list: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """找到Pareto前沿"""
        
        pareto_front = []
        
        for i, scores_i in enumerate(scores_list):
            is_pareto = True
            
            for j, scores_j in enumerate(scores_list):
                if i != j:
                    # 检查是否被另一个解支配
                    if (scores_j['accuracy'] >= scores_i['accuracy'] and 
                        scores_j['latency'] <= scores_i['latency'] and
                        scores_j['memory'] <= scores_i['memory'] and
                        (scores_j['accuracy'] > scores_i['accuracy'] or
                         scores_j['latency'] < scores_i['latency'] or
                         scores_j['memory'] < scores_i['memory'])):
                        is_pareto = False
                        break
            
            if is_pareto:
                pareto_front.append({
                    'index': i,
                    'scores': scores_i,
                    'dominated_objectives': []
                })
        
        return pareto_front

# 使用示例
async def main():
    # 导入必要的库
    import torch
    from torch.utils.data import DataLoader
    from torchvision import datasets, transforms
    
    # 准备数据
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    # 使用CIFAR-10作为示例
    train_dataset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
    val_dataset = datasets.CIFAR10(root='./data', train=False, transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
    
    print("数据准备完成")
    
    # 初始化NAS搜索器
    nas_searcher = NeuralArchitectureSearch(
        input_shape=(3, 32, 32),
        num_classes=10,
        search_strategy='evolutionary',
        max_evaluations=50,  # 减少评估次数以加快示例
        population_size=10
    )
    
    print("开始神经架构搜索...")
    
    # 执行搜索
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    search_results = nas_searcher.search(train_loader, val_loader, device)
    
    print(f"\n搜索完成!")
    print(f"最佳得分: {search_results['best_score']:.4f}")
    print(f"最佳架构: {search_results['best_architecture']}")
    
    # 生成最佳模型
    generator = NeuralArchitectureGenerator((3, 32, 32), 10)
    best_model = generator.generate_model(search_results['best_architecture'])
    
    print(f"\n最佳模型参数数量: {sum(p.numel() for p in best_model.parameters())}")
    
    # 使用渐进式搜索
    print("\n开始渐进式神经架构搜索...")
    progressive_nas = ProgressiveNeuralArchitectureSearch(nas_searcher)
    progressive_results = progressive_nas.progressive_search(train_loader, val_loader, device)
    
    print(f"渐进式搜索完成，最佳得分: {progressive_results['final_score']:.4f}")
    
    return {
        'search_results': search_results,
        'progressive_results': progressive_results,
        'best_model': best_model
    }

# 运行示例
if __name__ == "__main__":
    result = asyncio.run(main())
```

## Best Practices

### 1. 搜索空间设计
- **分层设计**: 使用分层搜索空间逐步细化架构
- **约束设置**: 基于资源限制设置合理的搜索约束
- **先验知识**: 利用领域知识减少不必要的搜索空间
- **模块化**: 设计可重复使用的网络模块

### 2. 搜索策略优化
- **混合策略**: 结合多种搜索策略提高效率
- **自适应调整**: 根据搜索进度动态调整策略
- **并行化**: 利用并行计算加速搜索过程
- **缓存机制**: 缓存评估结果避免重复计算

### 3. 评估方法改进
- **代理模型**: 使用小模型代理评估架构性能
- **早停机制**: 基于早期性能提前停止评估
- **权重共享**: 通过权重共享减少评估成本
- **渐进搜索**: 分阶段渐进细化搜索

### 4. 多目标平衡
- **Pareto前沿**: 分析多目标优化的Pareto前沿
- **权重调整**: 根据应用需求调整目标权重
- **约束处理**: 处理资源约束和性能要求
- **业务导向**: 平衡技术性能与业务需求

## Integration Patterns

### 1. 分布式NAS系统
```python
# 分布式架构搜索
class DistributedNAS:
    def __init__(self, nas_config, worker_nodes):
        self.nas_config = nas_config
        self.worker_nodes = worker_nodes
        self.task_queue = Queue()
        self.result_queue = Queue()
    
    def distribute_search(self, architectures):
        """分布式搜索执行"""
        # 分发架构评估任务
        for arch in architectures:
            self.task_queue.put(arch)
        
        # 启动工作节点
        workers = []
        for node in self.worker_nodes:
            worker = NASWorker(node, self.task_queue, self.result_queue)
            worker.start()
            workers.append(worker)
        
        # 收集结果
        results = []
        for _ in range(len(architectures)):
            result = self.result_queue.get()
            results.append(result)
        
        # 停止工作节点
        for worker in workers:
            worker.stop()
        
        return results
```

### 2. 云原生NAS服务
```yaml
# Kubernetes NAS作业
apiVersion: batch/v1
kind: Job
metadata:
  name: neural-architecture-search
spec:
  template:
    spec:
      containers:
      - name: nas-searcher
        image: neural-nas:latest
        command: ["python", "run_nas.py"]
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        - name: SEARCH_SPACE_CONFIG
          valueFrom:
            configMapKeyRef:
              name: nas-config
              key: search_space
        resources:
          requests:
            nvidia.com/gpu: 1
            memory: 16Gi
            cpu: 8
          limits:
            nvidia.com/gpu: 1
            memory: 32Gi
            cpu: 16
      restartPolicy: Never
  backoffLimit: 3
```

## Success Metrics

### 1. 搜索效率指标
- **搜索时间**: 从开始到找到最优架构的时间
- **评估次数**: 达到目标性能所需的架构评估次数
- **并行效率**: 分布式搜索的并行化效率
- **资源利用**: 搜索过程的计算资源利用效率

### 2. 架构质量指标
- **性能提升**: 搜索到的架构相比基准的性能提升
- **效率改进**: 模型在准确率和资源消耗间的平衡
- **泛化能力**: 架构在未见数据上的泛化性能
- **稳定性**: 多次搜索结果的一致性

### 3. 自动化程度指标
- **人工干预**: 搜索过程需要的人工干预程度
- **自动化比例**: 完全自动化的搜索比例
- **知识传承**: 搜索经验和知识的积累程度
- **易用性**: 工具的易用性和可配置性

---

*神经架构搜索是现代深度学习自动化的核心，通过智能化的搜索算法和优化策略，能够自动发现针对特定任务的高效网络架构，大幅提升模型性能和开发效率。*
