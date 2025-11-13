---
name: federated-learning-implementation
description: "联邦学习与隐私保护专家，精通联邦学习架构、差分隐私和同态加密。构建分布式训练系统、隐私保护机制和联邦聚合算法，处理多方协作学习、数据隐私和安全计算。使用PROACTIVELY进行联邦学习、隐私计算或分布式ML协作。"
---

# 联邦学习实现技能

## When to Use
Use this skill when implementing privacy-preserving distributed machine learning, building federated learning systems across multiple devices or organizations, training models on sensitive data without centralizing it, or developing decentralized AI systems. Essential for healthcare, finance, IoT, and any scenario requiring collaborative learning while maintaining data privacy.

## Core Concepts

### 1. 联邦学习架构
- **客户端-服务器模式**: 中心服务器协调多个客户端的训练过程
- **点对点模式**: 设备间直接通信进行模型聚合
- **混合模式**: 结合中心化和去中心化的优势
- **层次化架构**: 多级聚合的联邦学习系统

### 2. 隐私保护技术
- **差分隐私**: 在模型更新中添加噪声保护隐私
- **同态加密**: 加密状态下的模型训练和推理
- **安全多方计算**: 多方协作计算而不泄露数据
- **梯度压缩**: 减少通信开销的同时保护梯度信息

### 3. 联邦优化算法
- **FedAvg**: 联邦平均算法的经典实现
- **FedProx**: 处理数据异构性的联邦优化
- **FedNova**: 归一化聚合算法
- **SCAFFOLD**: 方差减少的联邦优化方法

### 4. 异构数据处理
- **非IID数据**: 处理非独立同分布的数据分布
- **数据漂移**: 适应数据分布的变化
- **系统异构**: 处理不同设备的计算能力差异
- **网络约束**: 在网络限制下的有效训练

## Code Examples

### 联邦学习核心系统
```python
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import copy
import asyncio
import json
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import hashlib
from cryptography.fernet import Fernet
import secrets

class FederatedClient:
    """联邦学习客户端"""
    
    def __init__(self, 
                 client_id: str,
                 local_data: torch.utils.data.DataLoader,
                 model: nn.Module,
                 local_epochs: int = 5,
                 learning_rate: float = 0.01,
                 device: str = 'cpu',
                 privacy_budget: float = 1.0):
        
        self.client_id = client_id
        self.local_data = local_data
        self.model = model
        self.local_epochs = local_epochs
        self.learning_rate = learning_rate
        self.device = device
        self.privacy_budget = privacy_budget
        
        # 隐私保护机制
        self.dp_mechanism = DifferentialPrivacyMechanism(privacy_budget)
        self.gradient_compression = GradientCompression()
        
        # 训练历史
        self.training_history = []
        
        # 加密机制
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def local_training(self, global_model_state: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """执行本地训练"""
        
        # 同步全局模型
        self.model.load_state_dict(global_model_state)
        self.model = self.model.to(self.device)
        
        # 本地训练
        optimizer = optim.SGD(self.model.parameters(), lr=self.learning_rate)
        local_weights = []
        total_loss = 0.0
        total_samples = 0
        
        self.model.train()
        
        for epoch in range(self.local_epochs):
            epoch_loss = 0.0
            epoch_samples = 0
            
            for batch_idx, (data, target) in enumerate(self.local_data):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                output = self.model(data)
                loss = F.cross_entropy(output, target)
                loss.backward()
                
                # 梯度裁剪
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                optimizer.step()
                
                epoch_loss += loss.item() * data.size(0)
                epoch_samples += data.size(0)
                
                if batch_idx % 10 == 0:
                    print(f'Client {self.client_id}, Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}')
            
            epoch_loss /= epoch_samples
            print(f'Client {self.client_id}, Epoch {epoch}, Average Loss: {epoch_loss:.4f}')
        
        # 收集模型权重
        for param in self.model.parameters():
            local_weights.append(param.data.clone())
        
        # 计算权重变化
        weight_updates = self._compute_weight_updates(global_model_state, local_weights)
        
        # 应用隐私保护
        private_updates = self.dp_mechanism.add_noise(weight_updates, self.privacy_budget)
        
        # 梯度压缩
        compressed_updates = self.gradient_compression.compress(private_updates)
        
        # 记录训练信息
        training_info = {
            'client_id': self.client_id,
            'local_epochs': self.local_epochs,
            'total_samples': epoch_samples,
            'final_loss': epoch_loss,
            'timestamp': time.time(),
            'data_distribution': self._analyze_data_distribution()
        }
        
        self.training_history.append(training_info)
        
        return {
            'client_id': self.client_id,
            'weight_updates': compressed_updates,
            'sample_size': epoch_samples,
            'training_loss': epoch_loss,
            'training_info': training_info,
            'encryption_key': self.encryption_key  # 在实际中应该通过安全通道传输
        }
    
    def _compute_weight_updates(self, 
                               global_weights: Dict[str, torch.Tensor],
                               local_weights: List[torch.Tensor]) -> List[torch.Tensor]:
        """计算权重更新"""
        weight_updates = []
        
        global_state_dict = global_weights
        param_names = list(global_state_dict.keys())
        
        for i, local_weight in enumerate(local_weights):
            if i < len(param_names):
                param_name = param_names[i]
                global_weight = global_state_dict[param_name]
                
                # 计算权重差异
                weight_update = local_weight - global_weight
                weight_updates.append(weight_update)
        
        return weight_updates
    
    def _analyze_data_distribution(self) -> Dict[str, float]:
        """分析数据分布"""
        if len(self.local_data.dataset) == 0:
            return {}
        
        # 统计各类别样本数量
        class_counts = defaultdict(int)
        
        for _, target in self.local_data:
            for label in target:
                class_counts[int(label)] += 1
        
        total_samples = sum(class_counts.values())
        
        # 计算分布
        distribution = {
            f'class_{cls}': count / total_samples 
            for cls, count in class_counts.items()
        }
        
        return distribution
    
    def evaluate_global_model(self, global_model_state: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """评估全局模型"""
        self.model.load_state_dict(global_model_state)
        self.model = self.model.to(self.device)
        self.model.eval()
        
        correct = 0
        total = 0
        total_loss = 0.0
        
        with torch.no_grad():
            for data, target in self.local_data:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                
                # 计算损失
                loss = F.cross_entropy(output, target)
                total_loss += loss.item()
                
                # 计算准确率
                _, predicted = torch.max(output.data, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()
        
        accuracy = correct / total if total > 0 else 0.0
        avg_loss = total_loss / len(self.local_data) if len(self.local_data) > 0 else 0.0
        
        return {
            'client_id': self.client_id,
            'accuracy': accuracy,
            'loss': avg_loss,
            'sample_size': total,
            'evaluation_timestamp': time.time()
        }

class FederatedServer:
    """联邦学习服务器"""
    
    def __init__(self, 
                 global_model: nn.Module,
                 aggregation_method: str = 'fedavg',
                 min_clients: int = 2,
                 privacy_budget: float = 10.0):
        
        self.global_model = global_model
        self.aggregation_method = aggregation_method
        self.min_clients = min_clients
        self.privacy_budget = privacy_budget
        
        # 客户端管理
        self.clients = {}
        self.client_weights = {}
        self.client_schedules = {}
        
        # 聚合器
        if aggregation_method == 'fedavg':
            self.aggregator = FedAvgAggregator()
        elif aggregation_method == 'fedprox':
            self.aggregator = FedProxAggregator()
        elif aggregation_method == 'fednova':
            self.aggregator = FedNovaAggregator()
        else:
            self.aggregator = FedAvgAggregator()
        
        # 隐私保护
        self.privacy_mechanism = DifferentialPrivacyMechanism(privacy_budget)
        
        # 训练统计
        self.training_rounds = 0
        self.global_history = []
    
    def register_client(self, client: FederatedClient) -> bool:
        """注册客户端"""
        self.clients[client.client_id] = client
        print(f"客户端 {client.client_id} 已注册")
        return True
    
    def federation_round(self, 
                        selected_clients: List[str] = None) -> Dict[str, Any]:
        """执行一轮联邦学习"""
        
        print(f"开始第 {self.training_rounds + 1} 轮联邦学习")
        
        # 选择客户端
        if selected_clients is None:
            selected_clients = self._select_clients()
        
        if len(selected_clients) < self.min_clients:
            print(f"可用客户端数量不足 ({len(selected_clients)} < {self.min_clients})")
            return None
        
        # 获取全局模型状态
        global_state = self.global_model.state_dict()
        
        # 收集客户端更新
        client_updates = []
        
        for client_id in selected_clients:
            if client_id in self.clients:
                client = self.clients[client_id]
                
                # 执行本地训练
                update = client.local_training(global_state)
                client_updates.append(update)
                
                print(f"客户端 {client_id} 完成本地训练，更新样本数: {update['sample_size']}")
        
        # 聚合模型
        aggregated_model = self.aggregator.aggregate(
            global_state, client_updates, self.aggregation_method
        )
        
        # 更新全局模型
        self.global_model.load_state_dict(aggregated_model)
        
        # 评估全局模型
        evaluation_results = self._evaluate_global_model(selected_clients)
        
        # 记录训练信息
        round_info = {
            'round': self.training_rounds + 1,
            'selected_clients': selected_clients,
            'num_participating_clients': len(client_updates),
            'aggregation_method': self.aggregation_method,
            'evaluation_results': evaluation_results,
            'timestamp': time.time(),
            'global_state_hash': self._compute_model_hash(aggregated_model)
        }
        
        self.global_history.append(round_info)
        self.training_rounds += 1
        
        # 打印结果
        print(f"第 {round_info['round']} 轮完成")
        print(f"参与客户端数: {round_info['num_participating_clients']}")
        
        avg_accuracy = np.mean([r['accuracy'] for r in evaluation_results])
        print(f"平均准确率: {avg_accuracy:.4f}")
        
        return round_info
    
    def _select_clients(self, 
                       fraction: float = 1.0,
                       min_num_clients: int = None) -> List[str]:
        """选择参与训练的客户端"""
        
        available_clients = list(self.clients.keys())
        
        if min_num_clients is None:
            min_num_clients = min(len(available_clients), int(len(available_clients) * fraction))
        
        # 随机选择客户端
        selected = np.random.choice(available_clients, min_num_clients, replace=False)
        return selected.tolist()
    
    def _evaluate_global_model(self, client_ids: List[str]) -> List[Dict[str, float]]:
        """评估全局模型在各个客户端上的性能"""
        
        global_state = self.global_model.state_dict()
        evaluation_results = []
        
        for client_id in client_ids:
            if client_id in self.clients:
                client = self.clients[client_id]
                result = client.evaluate_global_model(global_state)
                evaluation_results.append(result)
        
        return evaluation_results
    
    def _compute_model_hash(self, model_state: Dict[str, torch.Tensor]) -> str:
        """计算模型状态的哈希值"""
        
        # 序列化模型状态
        state_bytes = []
        for param in model_state.values():
            state_bytes.append(param.cpu().numpy().tobytes())
        
        combined_bytes = b''.join(state_bytes)
        model_hash = hashlib.sha256(combined_bytes).hexdigest()
        
        return model_hash
    
    def get_global_model(self) -> nn.Module:
        """获取全局模型"""
        return self.global_model
    
    def get_training_statistics(self) -> Dict[str, Any]:
        """获取训练统计信息"""
        
        if not self.global_history:
            return {}
        
        # 计算全局统计
        accuracies = []
        losses = []
        client_participation = []
        
        for round_info in self.global_history:
            eval_results = round_info['evaluation_results']
            accuracies.extend([r['accuracy'] for r in eval_results])
            losses.extend([r['loss'] for r in eval_results])
            client_participation.append(round_info['num_participating_clients'])
        
        return {
            'total_rounds': self.training_rounds,
            'avg_accuracy': np.mean(accuracies),
            'best_accuracy': np.max(accuracies),
            'avg_loss': np.mean(losses),
            'avg_participants': np.mean(client_participation),
            'participation_trend': client_participation,
            'accuracy_history': [np.mean(r['evaluation_results'])['accuracy'] for r in self.global_history]
        }

# 联邦聚合算法
class FedAvgAggregator:
    """联邦平均聚合器"""
    
    def aggregate(self, 
                  global_state: Dict[str, torch.Tensor],
                  client_updates: List[Dict[str, Any]],
                  method: str = 'fedavg') -> Dict[str, torch.Tensor]:
        """执行FedAvg聚合"""
        
        if not client_updates:
            return global_state
        
        # 计算每个客户端的权重
        total_samples = sum(update['sample_size'] for update in client_updates)
        client_weights = [update['sample_size'] / total_samples for update in client_updates]
        
        # 初始化聚合状态
        aggregated_state = copy.deepcopy(global_state)
        
        # 对每个参数进行加权平均
        for param_name in global_state.keys():
            # 收集所有客户端的权重更新
            param_updates = []
            for update in client_updates:
                # 找到对应的参数更新
                # 注意：实际实现中需要更精确的参数匹配
                for i, param in enumerate(global_state.keys()):
                    if param == param_name:
                        if i < len(update['weight_updates']):
                            param_updates.append(update['weight_updates'][i])
                        break
            
            if param_updates:
                # 加权平均聚合
                aggregated_update = self._weighted_average(param_updates, client_weights)
                aggregated_state[param_name] += aggregated_update
        
        return aggregated_state
    
    def _weighted_average(self, 
                         updates: List[torch.Tensor], 
                         weights: List[float]) -> torch.Tensor:
        """计算加权平均"""
        
        weighted_sum = torch.zeros_like(updates[0])
        
        for update, weight in zip(updates, weights):
            weighted_sum += weight * update
        
        return weighted_sum

class FedProxAggregator:
    """FedProx聚合器（处理异构数据）"""
    
    def __init__(self, mu: float = 0.01):
        self.mu = mu  # 近端项系数
    
    def aggregate(self, 
                  global_state: Dict[str, torch.Tensor],
                  client_updates: List[Dict[str, Any]],
                  method: str = 'fedprox') -> Dict[str, torch.Tensor]:
        
        # 使用FedAvg进行基础聚合
        fedavg_aggregator = FedAvgAggregator()
        aggregated_state = fedavg_aggregator.aggregate(global_state, client_updates, method)
        
        # 应用近端项修正
        for param_name in global_state.keys():
            proximal_correction = self._compute_proximal_correction(
                global_state[param_name], client_updates, param_name
            )
            aggregated_state[param_name] += self.mu * proximal_correction
        
        return aggregated_state
    
    def _compute_proximal_correction(self, 
                                   global_param: torch.Tensor,
                                   client_updates: List[Dict[str, Any]],
                                   param_name: str) -> torch.Tensor:
        """计算近端修正项"""
        
        corrections = []
        
        for update in client_updates:
            # 查找对应的参数更新
            for i, param in enumerate(global_state.keys()):
                if param == param_name:
                    if i < len(update['weight_updates']):
                        correction = -global_param + update['weight_updates'][i]
                        corrections.append(correction)
                    break
        
        if corrections:
            return torch.stack(corrections).mean(dim=0)
        else:
            return torch.zeros_like(global_param)

class FedNovaAggregator:
    """FedNova聚合器（归一化聚合）"""
    
    def aggregate(self, 
                  global_state: Dict[str, torch.Tensor],
                  client_updates: List[Dict[str, Any]],
                  method: str = 'fednova') -> Dict[str, torch.Tensor]:
        
        # 计算归一化权重
        client_weights = self._compute_nova_weights(client_updates)
        
        # 执行加权聚合
        fedavg_aggregator = FedAvgAggregator()
        return fedavg_aggregator.aggregate(global_state, client_updates, method)
    
    def _compute_nova_weights(self, client_updates: List[Dict[str, Any]]) -> List[float]:
        """计算FedNova权重"""
        
        # 基于客户端训练轮次和数据量计算权重
        weights = []
        
        for update in client_updates:
            # 考虑本地训练轮次的影响
            local_epochs = update['training_info']['local_epochs']
            sample_size = update['sample_size']
            
            # Nova权重计算
            weight = sample_size * local_epochs
            weights.append(weight)
        
        # 归一化权重
        total_weight = sum(weights)
        return [w / total_weight for w in weights]

# 隐私保护机制
class DifferentialPrivacyMechanism:
    """差分隐私机制"""
    
    def __init__(self, privacy_budget: float = 1.0):
        self.privacy_budget = privacy_budget
        self.noise_scale = 1.0 / privacy_budget
    
    def add_noise(self, weight_updates: List[torch.Tensor], budget: float) -> List[torch.Tensor]:
        """为权重更新添加高斯噪声"""
        
        noisy_updates = []
        
        for update in weight_updates:
            # 计算敏感度（这里简化为最大范数）
            sensitivity = torch.norm(update, p=2).item()
            
            # 生成高斯噪声
            noise = torch.normal(0, self.noise_scale * sensitivity, update.shape)
            
            # 添加噪声
            noisy_update = update + noise.to(update.device)
            noisy_updates.append(noisy_update)
        
        return noisy_updates

class GradientCompression:
    """梯度压缩机制"""
    
    def __init__(self, compression_ratio: float = 0.01):
        self.compression_ratio = compression_ratio
    
    def compress(self, weight_updates: List[torch.Tensor]) -> Dict[str, Any]:
        """压缩权重更新"""
        
        compressed_updates = []
        compression_stats = []
        
        for update in weight_updates:
            # Top-K稀疏化
            original_size = update.numel()
            k = max(1, int(original_size * self.compression_ratio))
            
            # 获取Top-K值
            flat_update = update.flatten()
            _, top_indices = torch.topk(torch.abs(flat_update), k)
            
            # 创建稀疏更新
            sparse_update = torch.zeros_like(flat_update)
            sparse_update[top_indices] = flat_update[top_indices]
            sparse_update = sparse_update.view_as(update)
            
            compressed_updates.append(sparse_update)
            
            # 记录压缩统计
            compression_stats.append({
                'original_size': original_size,
                'compressed_size': k,
                'compression_ratio': k / original_size,
                'sparsity': 1 - (k / original_size)
            })
        
        return {
            'weight_updates': compressed_updates,
            'compression_stats': compression_stats
        }

# 异步联邦学习
class AsynchronousFederatedClient(FederatedClient):
    """异步联邦学习客户端"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.staleness_threshold = 10
        self.local_update_buffer = deque(maxlen=5)
    
    def local_training_with_staleness(self, 
                                    global_model_state: Dict[str, torch.Tensor],
                                    global_round: int) -> Dict[str, Any]:
        """考虑陈旧性的本地训练"""
        
        # 计算陈旧性
        staleness = max(0, global_round - self.last_sync_round) if hasattr(self, 'last_sync_round') else 0
        
        if staleness > self.staleness_threshold:
            # 应用陈旧性补偿
            compensation_factor = 1.0 / (1.0 + staleness)
            global_model_state = self._apply_staleness_compensation(
                global_model_state, compensation_factor
            )
        
        # 执行本地训练
        update = self.local_training(global_model_state)
        
        # 记录陈旧性信息
        update['staleness'] = staleness
        update['staleness_compensation'] = compensation_factor if staleness > 0 else 1.0
        
        # 更新本地缓冲
        self.local_update_buffer.append(update)
        
        return update
    
    def _apply_staleness_compensation(self, 
                                    model_state: Dict[str, torch.Tensor],
                                    compensation_factor: float) -> Dict[str, torch.Tensor]:
        """应用陈旧性补偿"""
        
        compensated_state = copy.deepcopy(model_state)
        
        for param_name, param in model_state.items():
            # 简化补偿：缩放参数值
            compensated_state[param_name] = param * compensation_factor
        
        return compensated_state

# 异构数据处理
class HeterogeneousDataHandler:
    """异构数据处理器"""
    
    def __init__(self, federated_server: FederatedServer):
        self.server = federated_server
        self.client_heterogeneity_scores = {}
        self.adaptive_aggregation = AdaptiveAggregation()
    
    def analyze_data_heterogeneity(self) -> Dict[str, float]:
        """分析数据异构性"""
        
        heterogeneity_scores = {}
        
        for client_id, client in self.server.clients.items():
            if client.local_data and len(client.training_history) > 0:
                # 分析数据分布
                data_distribution = client._analyze_data_distribution()
                
                # 计算异构性分数（基于分布熵）
                entropy = self._calculate_distribution_entropy(data_distribution)
                heterogeneity_score = 1.0 - entropy  # 异构性 = 1 - 均匀性
                
                heterogeneity_scores[client_id] = heterogeneity_score
        
        self.client_heterogeneity_scores = heterogeneity_scores
        return heterogeneity_scores
    
    def _calculate_distribution_entropy(self, distribution: Dict[str, float]) -> float:
        """计算分布熵"""
        
        if not distribution:
            return 0.0
        
        probabilities = list(distribution.values())
        probabilities = [p for p in probabilities if p > 0]  # 移除零概率
        
        if not probabilities:
            return 0.0
        
        # 计算熵
        entropy = -sum(p * np.log2(p + 1e-10) for p in probabilities)
        
        # 归一化到[0, 1]
        max_entropy = np.log2(len(probabilities))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        return normalized_entropy
    
    def adaptive_federated_round(self) -> Dict[str, Any]:
        """执行自适应的联邦学习轮次"""
        
        # 分析异构性
        heterogeneity_scores = self.analyze_data_heterogeneity()
        
        # 根据异构性选择客户端
        selected_clients = self._heterogeneity_aware_client_selection(heterogeneity_scores)
        
        # 执行联邦轮次
        round_result = self.server.federation_round(selected_clients)
        
        # 更新自适应参数
        self.adaptive_aggregation.update_parameters(
            heterogeneity_scores, round_result
        )
        
        return round_result
    
    def _heterogeneity_aware_client_selection(self, 
                                            heterogeneity_scores: Dict[str, float]) -> List[str]:
        """异构性感知的客户端选择"""
        
        # 排序客户端异构性分数
        sorted_clients = sorted(
            heterogeneity_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # 选择策略：
        # - 包含高、中、低异构性的客户端
        # - 确保多样性
        
        selected_clients = []
        
        # 选择不同异构性水平的客户端
        if len(sorted_clients) >= 3:
            selected_clients.append(sorted_clients[0][0])  # 高异构性
            selected_clients.append(sorted_clients[len(sorted_clients)//2][0])  # 中等异构性
            selected_clients.append(sorted_clients[-1][0])  # 低异构性
        
        # 添加随机选择的其他客户端
        remaining_clients = [client_id for client_id, _ in sorted_clients[3:]]
        additional_clients = np.random.choice(
            remaining_clients, 
            min(len(remaining_clients), 5), 
            replace=False
        )
        selected_clients.extend(additional_clients)
        
        return selected_clients

class AdaptiveAggregation:
    """自适应聚合器"""
    
    def __init__(self):
        self.aggregation_weights = {}
        self.performance_history = []
    
    def update_parameters(self, 
                         heterogeneity_scores: Dict[str, float],
                         round_result: Dict[str, Any]):
        """更新聚合参数"""
        
        # 根据异构性和性能调整权重
        performance_scores = {
            client_id: result['accuracy'] 
            for client_id, result in zip(
                round_result['selected_clients'], 
                round_result['evaluation_results']
            )
        }
        
        # 动态调整聚合权重
        for client_id, heterogeneity in heterogeneity_scores.items():
            if client_id in performance_scores:
                # 异构性越高，权重越低
                # 性能越高，权重越高
                adaptive_weight = performance_scores[client_id] / (1 + heterogeneity)
                self.aggregation_weights[client_id] = adaptive_weight
        
        # 记录性能历史
        self.performance_history.append(round_result)

# 使用示例
async def main():
    # 导入必要的库
    import torch
    from torch.utils.data import DataLoader
    from torchvision import datasets, transforms
    
    # 定义简单模型
    class SimpleNet(nn.Module):
        def __init__(self):
            super(SimpleNet, self).__init__()
            self.conv1 = nn.Conv2d(1, 32, 3, 1)
            self.conv2 = nn.Conv2d(32, 64, 3, 1)
            self.dropout1 = nn.Dropout(0.25)
            self.dropout2 = nn.Dropout(0.5)
            self.fc1 = nn.Linear(9216, 128)
            self.fc2 = nn.Linear(128, 10)
        
        def forward(self, x):
            x = self.conv1(x)
            x = F.relu(x)
            x = self.conv2(x)
            x = F.relu(x)
            x = F.max_pool2d(x, 2)
            x = self.dropout1(x)
            x = torch.flatten(x, 1)
            x = self.fc1(x)
            x = F.relu(x)
            x = self.dropout2(x)
            x = self.fc2(x)
            return F.log_softmax(x, dim=1)
    
    # 准备数据
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # 模拟数据分布（非IID）
    np.random.seed(42)
    n_clients = 5
    
    clients_data = []
    for i in range(n_clients):
        # 为每个客户端创建数据子集
        client_data = torch.utils.data.Subset(
            datasets.MNIST('./data', train=True, download=True, transform=transform),
            indices=np.random.choice(range(60000), size=12000, replace=False)
        )
        client_loader = DataLoader(client_data, batch_size=32, shuffle=True)
        clients_data.append(client_loader)
    
    # 创建联邦学习系统
    global_model = SimpleNet()
    federated_server = FederatedServer(
        global_model=global_model,
        aggregation_method='fedavg',
        min_clients=2
    )
    
    # 创建客户端
    clients = []
    for i in range(n_clients):
        client_id = f"client_{i}"
        
        # 模拟每个客户端的独特模型（添加噪声）
        local_model = copy.deepcopy(global_model)
        
        # 为每个参数添加小量随机噪声
        for param in local_model.parameters():
            param.data += torch.randn_like(param.data) * 0.01
        
        client = FederatedClient(
            client_id=client_id,
            local_data=clients_data[i],
            model=local_model,
            local_epochs=3,
            learning_rate=0.01,
            device='cpu'
        )
        
        # 注册客户端
        federated_server.register_client(client)
        clients.append(client)
    
    print(f"初始化完成: {len(clients)} 个联邦客户端")
    
    # 执行联邦学习
    for round_num in range(5):
        print(f"\n=== 第 {round_num + 1} 轮联邦学习 ===")
        
        # 选择所有客户端参与
        round_result = federated_server.federation_round()
        
        if round_result:
            print(f"第 {round_num + 1} 轮完成!")
            print(f"参与客户端数: {round_result['num_participating_clients']}")
            
            avg_accuracy = np.mean([r['accuracy'] for r in round_result['evaluation_results']])
            print(f"平均准确率: {avg_accuracy:.4f}")
    
    # 获取训练统计
    stats = federated_server.get_training_statistics()
    print(f"\n=== 联邦学习总结 ===")
    print(f"总轮数: {stats['total_rounds']}")
    print(f"最佳准确率: {stats['best_accuracy']:.4f}")
    print(f"平均准确率: {stats['avg_accuracy']:.4f}")
    
    # 测试异构数据处理
    print("\n=== 异构数据处理测试 ===")
    hetero_handler = HeterogeneousDataHandler(federated_server)
    
    # 分析数据异构性
    heterogeneity_scores = hetero_handler.analyze_data_heterogeneity()
    print("客户端异构性分数:")
    for client_id, score in heterogeneity_scores.items():
        print(f"  {client_id}: {score:.4f}")
    
    return {
        'federated_server': federated_server,
        'clients': clients,
        'training_statistics': stats,
        'heterogeneity_analysis': heterogeneity_scores
    }

# 运行示例
if __name__ == "__main__":
    result = asyncio.run(main())
```

## Best Practices

### 1. 隐私保护策略
- **多层次保护**: 结合差分隐私、加密和压缩技术
- **动态调整**: 根据隐私预算动态调整保护强度
- **本地化处理**: 敏感计算尽可能在本地完成
- **透明度**: 提供隐私保护的透明度报告

### 2. 通信优化
- **梯度压缩**: 使用稀疏化和量化技术减少通信量
- **异步更新**: 允许异步客户端更新减少等待时间
- **分层聚合**: 使用分层架构减少通信开销
- **缓存机制**: 缓存可重复使用的梯度信息

### 3. 系统鲁棒性
- **客户端容错**: 处理客户端故障和不稳定连接
- **拜占庭容错**: 防范恶意客户端的破坏性更新
- **网络自适应**: 适应不同网络条件的通信策略
- **动态客户端**: 支持客户端的动态加入和退出

### 4. 性能优化
- **本地预训练**: 利用本地数据进行预训练加速收敛
- **个性化模型**: 为不同客户端训练个性化模型
- **知识蒸馏**: 使用知识蒸馏技术提高学习效率
- **元学习**: 采用元学习方法快速适应新任务

## Integration Patterns

### 1. 移动设备集成
```python
# 移动端联邦学习客户端
class MobileFederatedClient(FederatedClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.battery_monitor = BatteryMonitor()
        self.network_monitor = NetworkMonitor()
    
    def should_participate(self) -> bool:
        """判断是否应该参与本轮训练"""
        # 检查电池电量
        if self.battery_monitor.get_battery_level() < 0.2:
            return False
        
        # 检查网络连接
        if not self.network_monitor.is_connected() or self.network_monitor.get_latency() > 1000:
            return False
        
        return True
    
    def adaptive_local_epochs(self, remaining_battery: float, network_quality: float) -> int:
        """自适应调整本地训练轮次"""
        base_epochs = self.local_epochs
        
        # 根据电池电量调整
        battery_factor = min(1.0, remaining_battery / 0.5)
        
        # 根据网络质量调整
        network_factor = max(0.5, network_quality)
        
        adaptive_epochs = int(base_epochs * battery_factor * network_factor)
        return max(1, adaptive_epochs)
```

### 2. 边缘计算集成
```python
# 边缘计算联邦学习
class EdgeFederatedServer(FederatedServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edge_nodes = {}
        self.hierarchy_levels = 3
    
    def setup_hierarchy(self, edge_configs: List[Dict[str, Any]]):
        """设置层次化边缘节点"""
        for config in edge_configs:
            edge_node = EdgeNode(
                node_id=config['node_id'],
                level=config['level'],
                capacity=config['capacity'],
                clients=config['clients']
            )
            self.edge_nodes[config['node_id']] = edge_node
    
    def hierarchical_aggregation(self, round_result: Dict[str, Any]) -> Dict[str, Any]:
        """层次化聚合"""
        # 第一层：边缘节点聚合
        edge_aggregations = {}
        for node_id, edge_node in self.edge_nodes.items():
            if edge_node.level == 1:
                local_clients = [cid for cid in round_result['selected_clients'] 
                               if cid in edge_node.clients]
                if local_clients:
                    edge_aggregations[node_id] = self.edge_aggregation(
                        round_result, local_clients
                    )
        
        # 第二层：高层聚合
        high_level_aggregation = self.high_level_aggregation(edge_aggregations)
        
        return high_level_aggregation
```

## Success Metrics

### 1. 学习效果指标
- **全局准确率**: 联邦学习后模型的全局准确率
- **收敛速度**: 达到目标性能所需的轮次
- **个性化效果**: 不同客户端上的个性化性能
- **知识转移**: 跨客户端知识转移效果

### 2. 隐私保护指标
- **隐私预算**: 消耗的差分隐私预算
- **信息泄露**: 可量化的信息泄露风险
- **匿名化程度**: 数据匿名化的有效性
- **合规性**: 满足隐私法规的程度

### 3. 系统效率指标
- **通信成本**: 训练过程的通信开销
- **计算开销**: 客户端的计算资源消耗
- **时间效率**: 整体训练时间
- **扩展性**: 支持大规模客户端的能力

### 4. 鲁棒性指标
- **容错率**: 处理客户端故障的能力
- **网络适应**: 在网络不稳定环境下的表现
- **恶意检测**: 检测和防范恶意客户端的能力
- **稳定性**: 长期运行的系统稳定性

---

*联邦学习是隐私保护的分布式机器学习核心技术，通过在保护数据隐私的前提下实现多方协作训练，为医疗、金融、IoT等敏感数据场景提供了可行的AI解决方案。*
