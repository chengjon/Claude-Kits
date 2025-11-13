---
name: model-versioning-deployment
description: "模型版本管理与部署自动化专家，精通模型版本控制、自动化部署和蓝绿发布。构建模型生命周期管理、部署流水线和服务编排，处理模型版本管理、CI/CD集成和服务发布。使用PROACTIVELY进行模型部署、版本控制或MLOps流水线。"
---

# 模型版本部署技能

## When to Use
Use this skill when building model versioning systems, implementing automated deployment pipelines, managing model lifecycle from development to production, creating model registry systems, or establishing MLOps deployment workflows. Essential for production ML systems, model governance, deployment automation, and ensuring reliable ML operations.

## Core Concepts

### 1. 模型版本管理
- **语义化版本**: 使用语义化版本号管理模型迭代
- **模型谱系**: 跟踪模型的训练历史和依赖关系
- **版本比较**: 比较不同版本模型性能和特性
- **回滚机制**: 支持快速回滚到之前的版本

### 2. 自动化部署流程
- **CI/CD集成**: 将模型部署集成到持续集成/部署管道
- **A/B测试**: 渐进式部署和性能对比测试
- **灰度发布**: 逐步推广新版本模型
- **自动化验证**: 部署前后自动验证模型性能

### 3. 部署策略模式
- **蓝绿部署**: 并行维护新旧版本的部署策略
- **金丝雀发布**: 小规模测试后逐步推广
- **特性开关**: 控制模型功能的动态开关
- **多版本共存**: 多个版本模型同时在线服务

### 4. 模型治理系统
- **模型注册**: 中央化的模型注册和管理
- **审批工作流**: 模型上线前的审批和验证流程
- **监控告警**: 实时监控模型性能和异常
- **合规审计**: 满足法规要求的审计追踪

## Code Examples

### 模型版本控制系统
```python
import os
import json
import hashlib
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import sqlite3
import yaml
from pathlib import Path
import logging

class ModelStatus(Enum):
    """模型状态枚举"""
    DRAFT = "draft"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"
    FAILED = "failed"

@dataclass
class ModelVersion:
    """模型版本信息"""
    version_id: str
    model_name: str
    version: str
    status: ModelStatus
    created_at: datetime
    created_by: str
    model_path: str
    metadata: Dict[str, Any]
    metrics: Dict[str, float]
    dependencies: List[str]
    parent_version: Optional[str]
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class DeploymentConfig:
    """部署配置"""
    deployment_id: str
    model_version: str
    target_environment: str
    resources: Dict[str, Any]
    scaling_config: Dict[str, Any]
    health_check_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    rollback_config: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ModelVersioningSystem:
    """模型版本管理系统"""
    
    def __init__(self, 
                 registry_path: str = "./model_registry",
                 database_path: str = "./model_registry/versions.db"):
        
        self.registry_path = Path(registry_path)
        self.database_path = Path(database_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
        
        # 设置日志
        self.logger = self._setup_logging()
    
    def _init_database(self):
        """初始化版本数据库"""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_versions (
                    version_id TEXT PRIMARY KEY,
                    model_name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    model_path TEXT NOT NULL,
                    metadata TEXT,
                    metrics TEXT,
                    dependencies TEXT,
                    parent_version TEXT,
                    tags TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deployments (
                    deployment_id TEXT PRIMARY KEY,
                    model_version TEXT NOT NULL,
                    target_environment TEXT NOT NULL,
                    config TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    deployed_at TEXT,
                    FOREIGN KEY (model_version) REFERENCES model_versions (version_id)
                )
            """)
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志系统"""
        logger = logging.getLogger('model_versioning')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.registry_path / 'versioning.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def register_model(self,
                      model_name: str,
                      model_path: str,
                      version: str,
                      created_by: str,
                      metadata: Dict[str, Any] = None,
                      metrics: Dict[str, float] = None,
                      dependencies: List[str] = None,
                      parent_version: Optional[str] = None,
                      tags: List[str] = None) -> str:
        """注册新模型版本"""
        
        # 生成版本ID
        version_id = self._generate_version_id(model_name, version)
        
        # 检查是否已存在
        if self._version_exists(version_id):
            raise ValueError(f"版本 {version_id} 已存在")
        
        # 复制模型文件到注册表
        registry_model_path = self._copy_model_to_registry(model_path, version_id)
        
        # 创建模型版本对象
        model_version = ModelVersion(
            version_id=version_id,
            model_name=model_name,
            version=version,
            status=ModelStatus.DRAFT,
            created_at=datetime.now(),
            created_by=created_by,
            model_path=str(registry_model_path),
            metadata=metadata or {},
            metrics=metrics or {},
            dependencies=dependencies or [],
            parent_version=parent_version,
            tags=tags or []
        )
        
        # 保存到数据库
        self._save_model_version(model_version)
        
        # 记录日志
        self.logger.info(f"注册模型版本: {version_id}")
        
        return version_id
    
    def _generate_version_id(self, model_name: str, version: str) -> str:
        """生成版本ID"""
        content = f"{model_name}:{version}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _copy_model_to_registry(self, model_path: str, version_id: str) -> Path:
        """复制模型到注册表"""
        source_path = Path(model_path)
        target_path = self.registry_path / version_id
        
        if source_path.is_dir():
            shutil.copytree(source_path, target_path)
        else:
            target_path.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_path / source_path.name)
        
        return target_path
    
    def _version_exists(self, version_id: str) -> bool:
        """检查版本是否存在"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM model_versions WHERE version_id = ?",
                (version_id,)
            )
            return cursor.fetchone()[0] > 0
    
    def _save_model_version(self, model_version: ModelVersion):
        """保存模型版本到数据库"""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                INSERT INTO model_versions (
                    version_id, model_name, version, status, created_at,
                    created_by, model_path, metadata, metrics, dependencies,
                    parent_version, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                model_version.version_id,
                model_version.model_name,
                model_version.version,
                model_version.status.value,
                model_version.created_at.isoformat(),
                model_version.created_by,
                model_version.model_path,
                json.dumps(model_version.metadata),
                json.dumps(model_version.metrics),
                json.dumps(model_version.dependencies),
                model_version.parent_version,
                json.dumps(model_version.tags)
            ))
    
    def get_model_versions(self, 
                          model_name: str = None,
                          status: ModelStatus = None,
                          limit: int = 100) -> List[ModelVersion]:
        """获取模型版本列表"""
        
        query = "SELECT * FROM model_versions WHERE 1=1"
        params = []
        
        if model_name:
            query += " AND model_name = ?"
            params.append(model_name)
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.database_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        
        model_versions = []
        for row in rows:
            model_version = ModelVersion(
                version_id=row['version_id'],
                model_name=row['model_name'],
                version=row['version'],
                status=ModelStatus(row['status']),
                created_at=datetime.fromisoformat(row['created_at']),
                created_by=row['created_by'],
                model_path=row['model_path'],
                metadata=json.loads(row['metadata'] or '{}'),
                metrics=json.loads(row['metrics'] or '{}'),
                dependencies=json.loads(row['dependencies'] or '[]'),
                parent_version=row['parent_version'],
                tags=json.loads(row['tags'] or '[]')
            )
            model_versions.append(model_version)
        
        return model_versions
    
    def update_model_status(self, 
                           version_id: str,
                           new_status: ModelStatus,
                           updated_by: str) -> bool:
        """更新模型状态"""
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    UPDATE model_versions 
                    SET status = ? 
                    WHERE version_id = ?
                """, (new_status.value, version_id))
            
            self.logger.info(f"更新模型状态: {version_id} -> {new_status.value}")
            return True
        
        except Exception as e:
            self.logger.error(f"更新模型状态失败: {e}")
            return False
    
    def promote_model(self, 
                     version_id: str,
                     target_status: ModelStatus,
                     approved_by: str,
                     approval_notes: str = None) -> bool:
        """提升模型状态（带审批）"""
        
        # 更新状态
        success = self.update_model_status(version_id, target_status, approved_by)
        
        if success:
            # 记录审批日志
            self.logger.info(f"模型提升: {version_id} -> {target_status.value} by {approved_by}")
            if approval_notes:
                self.logger.info(f"审批备注: {approval_notes}")
        
        return success
    
    def compare_versions(self, 
                        version_id1: str, 
                        version_id2: str) -> Dict[str, Any]:
        """比较两个模型版本"""
        
        version1 = self.get_model_versions_by_id(version_id1)
        version2 = self.get_model_versions_by_id(version_id2)
        
        if not version1 or not version2:
            raise ValueError("版本不存在")
        
        return {
            'version1': {
                'version_id': version1.version_id,
                'model_name': version1.model_name,
                'version': version1.version,
                'status': version1.status.value,
                'created_at': version1.created_at.isoformat(),
                'metrics': version1.metrics,
                'metadata': version1.metadata
            },
            'version2': {
                'version_id': version2.version_id,
                'model_name': version2.model_name,
                'version': version2.version,
                'status': version2.status.value,
                'created_at': version2.created_at.isoformat(),
                'metrics': version2.metrics,
                'metadata': version2.metadata
            },
            'comparison': self._compute_version_comparison(version1, version2)
        }
    
    def get_model_versions_by_id(self, version_id: str) -> Optional[ModelVersion]:
        """根据版本ID获取模型版本"""
        versions = self.get_model_versions()
        for version in versions:
            if version.version_id == version_id:
                return version
        return None
    
    def _compute_version_comparison(self, 
                                  version1: ModelVersion, 
                                  version2: ModelVersion) -> Dict[str, Any]:
        """计算版本比较结果"""
        
        comparison = {
            'metrics_diff': {},
            'metadata_diff': {},
            'dependency_changes': {
                'added': [],
                'removed': [],
                'common': []
            }
        }
        
        # 比较指标
        for metric in set(version1.metrics.keys()) | set(version2.metrics.keys()):
            val1 = version1.metrics.get(metric, 0)
            val2 = version2.metrics.get(metric, 0)
            comparison['metrics_diff'][metric] = {
                'version1': val1,
                'version2': val2,
                'difference': val2 - val1,
                'percentage_change': ((val2 - val1) / val1 * 100) if val1 != 0 else 0
            }
        
        # 比较依赖
        deps1 = set(version1.dependencies)
        deps2 = set(version2.dependencies)
        comparison['dependency_changes']['added'] = list(deps2 - deps1)
        comparison['dependency_changes']['removed'] = list(deps1 - deps2)
        comparison['dependency_changes']['common'] = list(deps1 & deps2)
        
        return comparison

class ModelDeploymentSystem:
    """模型部署系统"""
    
    def __init__(self, versioning_system: ModelVersioningSystem):
        self.versioning_system = versioning_system
        self.deployment_configs = {}
        self.active_deployments = {}
    
    def create_deployment_config(self, 
                                model_version: str,
                                target_environment: str,
                                resources: Dict[str, Any],
                                scaling_config: Dict[str, Any] = None,
                                health_check_config: Dict[str, Any] = None,
                                monitoring_config: Dict[str, Any] = None,
                                rollback_config: Dict[str, Any] = None) -> str:
        """创建部署配置"""
        
        deployment_id = f"{model_version}:{target_environment}"
        
        config = DeploymentConfig(
            deployment_id=deployment_id,
            model_version=model_version,
            target_environment=target_environment,
            resources=resources,
            scaling_config=scaling_config or {
                'min_replicas': 1,
                'max_replicas': 10,
                'target_cpu_utilization': 70
            },
            health_check_config=health_check_config or {
                'path': '/health',
                'port': 8080,
                'initial_delay': 30,
                'period': 10
            },
            monitoring_config=monitoring_config or {
                'metrics_endpoint': '/metrics',
                'log_level': 'INFO',
                'alert_thresholds': {
                    'accuracy_drop': 0.05,
                    'latency_ms': 1000
                }
            },
            rollback_config=rollback_config or {
                'auto_rollback': True,
                'rollback_threshold': 0.1,
                'health_check_failures': 3
            }
        )
        
        self.deployment_configs[deployment_id] = config
        return deployment_id
    
    def deploy_model(self, 
                    deployment_id: str,
                    deployment_strategy: str = 'rolling') -> Dict[str, Any]:
        """部署模型"""
        
        if deployment_id not in self.deployment_configs:
            raise ValueError(f"部署配置不存在: {deployment_id}")
        
        config = self.deployment_configs[deployment_id]
        
        # 获取模型版本
        model_version = self.versioning_system.get_model_versions_by_id(
            config.model_version
        )
        
        if not model_version:
            raise ValueError(f"模型版本不存在: {config.model_version}")
        
        # 执行部署策略
        deployment_result = self._execute_deployment_strategy(
            deployment_strategy, model_version, config
        )
        
        # 记录部署
        self.active_deployments[deployment_id] = deployment_result
        
        return deployment_result
    
    def _execute_deployment_strategy(self, 
                                   strategy: str,
                                   model_version: ModelVersion,
                                   config: DeploymentConfig) -> Dict[str, Any]:
        """执行部署策略"""
        
        if strategy == 'blue_green':
            return self._blue_green_deployment(model_version, config)
        elif strategy == 'canary':
            return self._canary_deployment(model_version, config)
        elif strategy == 'rolling':
            return self._rolling_deployment(model_version, config)
        else:
            raise ValueError(f"不支持的部署策略: {strategy}")
    
    def _blue_green_deployment(self, 
                             model_version: ModelVersion, 
                             config: DeploymentConfig) -> Dict[str, Any]:
        """蓝绿部署"""
        
        deployment_result = {
            'deployment_id': config.deployment_id,
            'strategy': 'blue_green',
            'model_version': config.model_version,
            'environment': config.target_environment,
            'status': 'deploying',
            'started_at': datetime.now().isoformat(),
            'green_deployment': {
                'deployment_id': f"{config.deployment_id}:green",
                'status': 'active',
                'instances': self._deploy_instances(model_version, config, 'green')
            },
            'blue_deployment': self._get_existing_blue_deployment(config.deployment_id)
        }
        
        # 执行切换（简化实现）
        deployment_result['status'] = 'completed'
        deployment_result['completed_at'] = datetime.now().isoformat()
        
        return deployment_result
    
    def _canary_deployment(self, 
                          model_version: ModelVersion, 
                          config: DeploymentConfig) -> Dict[str, Any]:
        """金丝雀部署"""
        
        deployment_result = {
            'deployment_id': config.deployment_id,
            'strategy': 'canary',
            'model_version': config.model_version,
            'environment': config.target_environment,
            'status': 'deploying',
            'started_at': datetime.now().isoformat(),
            'canary_deployment': {
                'deployment_id': f"{config.deployment_id}:canary",
                'traffic_percentage': 10,
                'status': 'active',
                'instances': self._deploy_instances(model_version, config, 'canary')
            },
            'stable_deployment': self._get_stable_deployment(config.deployment_id)
        }
        
        deployment_result['status'] = 'canary_active'
        
        return deployment_result
    
    def _rolling_deployment(self, 
                          model_version: ModelVersion, 
                          config: DeploymentConfig) -> Dict[str, Any]:
        """滚动部署"""
        
        max_unavailable = config.scaling_config.get('max_unavailable', 1)
        max_surge = config.scaling_config.get('max_surge', 1)
        
        deployment_result = {
            'deployment_id': config.deployment_id,
            'strategy': 'rolling',
            'model_version': config.model_version,
            'environment': config.target_environment,
            'status': 'deploying',
            'started_at': datetime.now().isoformat(),
            'rolling_update': {
                'max_unavailable': max_unavailable,
                'max_surge': max_surge,
                'current_batch': 0,
                'total_batches': 3
            }
        }
        
        # 模拟滚动更新
        deployment_result['status'] = 'completed'
        deployment_result['completed_at'] = datetime.now().isoformat()
        
        return deployment_result
    
    def _deploy_instances(self, 
                         model_version: ModelVersion, 
                         config: DeploymentConfig,
                         deployment_type: str) -> List[Dict[str, Any]]:
        """部署实例"""
        
        replicas = config.resources.get('replicas', 1)
        instances = []
        
        for i in range(replicas):
            instance = {
                'instance_id': f"{config.deployment_id}:{deployment_type}:{i}",
                'pod_id': f"pod-{deployment_type}-{i}",
                'node': f"node-{i % 3}",
                'status': 'running',
                'start_time': datetime.now().isoformat(),
                'resource_usage': {
                    'cpu': '500m',
                    'memory': '1Gi'
                }
            }
            instances.append(instance)
        
        return instances
    
    def _get_existing_blue_deployment(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """获取现有的蓝版本部署"""
        blue_deployment_id = f"{deployment_id}:blue"
        return self.active_deployments.get(blue_deployment_id)
    
    def _get_stable_deployment(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """获取稳定的生产部署"""
        return self.active_deployments.get(deployment_id)
    
    def rollback_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """回滚部署"""
        
        if deployment_id not in self.active_deployments:
            raise ValueError(f"部署不存在: {deployment_id}")
        
        deployment = self.active_deployments[deployment_id]
        config = self.deployment_configs[deployment_id]
        
        # 执行回滚
        rollback_result = {
            'deployment_id': deployment_id,
            'rollback_reason': 'manual_rollback',
            'rollback_at': datetime.now().isoformat(),
            'original_deployment': deployment,
            'rollback_status': 'completed'
        }
        
        # 更新部署状态
        self.active_deployments[deployment_id]['status'] = 'rolled_back'
        self.active_deployments[deployment_id]['rollback_info'] = rollback_result
        
        return rollback_result
    
    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """获取部署状态"""
        
        if deployment_id not in self.active_deployments:
            return {
                'deployment_id': deployment_id,
                'status': 'not_found'
            }
        
        deployment = self.active_deployments[deployment_id]
        
        # 模拟实时状态更新
        status = {
            'deployment_id': deployment_id,
            'status': deployment['status'],
            'model_version': deployment['model_version'],
            'environment': deployment['environment'],
            'deployed_at': deployment.get('completed_at', deployment['started_at']),
            'instances': self._get_instance_status(deployment),
            'health_metrics': self._get_health_metrics(deployment_id)
        }
        
        return status
    
    def _get_instance_status(self, deployment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取实例状态"""
        
        if 'green_deployment' in deployment:
            return deployment['green_deployment']['instances']
        elif 'canary_deployment' in deployment:
            return deployment['canary_deployment']['instances']
        else:
            return []
    
    def _get_health_metrics(self, deployment_id: str) -> Dict[str, Any]:
        """获取健康指标"""
        
        # 模拟健康指标
        import random
        
        return {
            'cpu_utilization': random.uniform(30, 80),
            'memory_utilization': random.uniform(40, 90),
            'request_rate': random.uniform(100, 1000),
            'error_rate': random.uniform(0, 0.05),
            'latency_p95': random.uniform(50, 500),
            'availability': random.uniform(99.5, 99.9)
        }

# 高级部署特性
class AdvancedDeploymentFeatures:
    """高级部署功能"""
    
    def __init__(self, deployment_system: ModelDeploymentSystem):
        self.deployment_system = deployment_system
        self.feature_flags = {}
        self.ab_tests = {}
        self.performance_monitoring = PerformanceMonitor()
    
    def setup_feature_flags(self, 
                           model_version: str, 
                           flags: Dict[str, Any]) -> None:
        """设置特性开关"""
        
        self.feature_flags[model_version] = flags
        print(f"为模型版本 {model_version} 设置特性开关: {flags}")
    
    def toggle_feature_flag(self, 
                           model_version: str, 
                           flag_name: str, 
                           enabled: bool) -> bool:
        """切换特性开关"""
        
        if model_version in self.feature_flags:
            self.feature_flags[model_version][flag_name] = enabled
            print(f"特性开关 {flag_name} {'启用' if enabled else '禁用'} for {model_version}")
            return True
        
        return False
    
    def create_ab_test(self, 
                      test_name: str,
                      model_version_a: str,
                      model_version_b: str,
                      traffic_split: float = 0.5) -> str:
        """创建A/B测试"""
        
        ab_test_id = f"ab_test_{test_name}"
        
        self.ab_tests[ab_test_id] = {
            'test_id': ab_test_id,
            'model_a': model_version_a,
            'model_b': model_version_b,
            'traffic_split': traffic_split,
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'results': {
                'model_a_metrics': {},
                'model_b_metrics': {},
                'winner': None
            }
        }
        
        print(f"创建A/B测试: {ab_test_id}")
        return ab_test_id
    
    def get_ab_test_results(self, ab_test_id: str) -> Dict[str, Any]:
        """获取A/B测试结果"""
        
        if ab_test_id not in self.ab_tests:
            return {'error': 'A/B测试不存在'}
        
        ab_test = self.ab_tests[ab_test_id]
        
        # 模拟结果收集和分析
        # 实际实现中需要从监控系统收集真实数据
        
        return {
            'test_id': ab_test['test_id'],
            'status': ab_test['status'],
            'traffic_split': ab_test['traffic_split'],
            'results': ab_test['results'],
            'recommendation': self._analyze_ab_test_results(ab_test['results'])
        }
    
    def _analyze_ab_test_results(self, results: Dict[str, Any]) -> str:
        """分析A/B测试结果"""
        
        model_a_metrics = results.get('model_a_metrics', {})
        model_b_metrics = results.get('model_b_metrics', {})
        
        # 简化分析：比较准确率
        accuracy_a = model_a_metrics.get('accuracy', 0)
        accuracy_b = model_b_metrics.get('accuracy', 0)
        
        if accuracy_b > accuracy_a * 1.02:  # 2%提升阈值
            return "model_b"
        elif accuracy_a > accuracy_b * 1.02:
            return "model_a"
        else:
            return "inconclusive"

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics_history = {}
        self.alerts = []
    
    def record_metrics(self, 
                      deployment_id: str, 
                      metrics: Dict[str, float]) -> None:
        """记录性能指标"""
        
        if deployment_id not in self.metrics_history:
            self.metrics_history[deployment_id] = []
        
        self.metrics_history[deployment_id].append({
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        })
        
        # 检查告警
        self._check_alerts(deployment_id, metrics)
    
    def _check_alerts(self, deployment_id: str, metrics: Dict[str, float]) -> None:
        """检查告警条件"""
        
        # 检查准确率下降
        accuracy = metrics.get('accuracy')
        if accuracy and accuracy < 0.8:  # 告警阈值
            self.alerts.append({
                'alert_id': f"accuracy_low_{deployment_id}",
                'deployment_id': deployment_id,
                'alert_type': 'accuracy_degradation',
                'message': f"模型准确率降至 {accuracy:.3f}",
                'timestamp': datetime.now().isoformat(),
                'severity': 'high'
            })
        
        # 检查延迟过高
        latency = metrics.get('latency_ms')
        if latency and latency > 1000:  # 1秒阈值
            self.alerts.append({
                'alert_id': f"latency_high_{deployment_id}",
                'deployment_id': deployment_id,
                'alert_type': 'high_latency',
                'message': f"模型延迟升至 {latency:.0f}ms",
                'timestamp': datetime.now().isoformat(),
                'severity': 'medium'
            })
    
    def get_alerts(self, deployment_id: str = None) -> List[Dict[str, Any]]:
        """获取告警"""
        
        if deployment_id:
            return [alert for alert in self.alerts 
                   if alert['deployment_id'] == deployment_id]
        
        return self.alerts

# 使用示例
async def main():
    # 创建模型版本管理系统
    versioning_system = ModelVersioningSystem("./model_registry_demo")
    
    # 注册多个模型版本
    print("=== 模型版本管理演示 ===")
    
    # 版本1：初始模型
    version1_id = versioning_system.register_model(
        model_name="sentiment_classifier",
        model_path="./dummy_model_v1.pkl",  # 模拟路径
        version="1.0.0",
        created_by="alice",
        metadata={
            "training_data": "senticorp_v1",
            "algorithm": "random_forest",
            "training_time_hours": 2.5
        },
        metrics={
            "accuracy": 0.85,
            "precision": 0.83,
            "recall": 0.87,
            "f1_score": 0.85
        },
        tags=["baseline", "production"]
    )
    
    print(f"注册模型版本: {version1_id}")
    
    # 版本2：优化版本
    version2_id = versioning_system.register_model(
        model_name="sentiment_classifier",
        model_path="./dummy_model_v2.pkl",
        version="1.1.0",
        created_by="bob",
        parent_version=version1_id,
        metadata={
            "training_data": "senticorp_v2",
            "algorithm": "random_forest",
            "training_time_hours": 3.2,
            "hyperparameters": {"n_estimators": 200, "max_depth": 15}
        },
        metrics={
            "accuracy": 0.89,
            "precision": 0.87,
            "recall": 0.91,
            "f1_score": 0.89
        },
        tags=["improved", "production"]
    )
    
    print(f"注册模型版本: {version2_id}")
    
    # 获取版本列表
    versions = versioning_system.get_model_versions("sentiment_classifier")
    print(f"\n当前版本数量: {len(versions)}")
    
    for version in versions:
        print(f"  - {version.version} ({version.status.value})")
    
    # 比较版本
    print("\n=== 版本比较 ===")
    comparison = versioning_system.compare_versions(version1_id, version2_id)
    print(f"准确率提升: {comparison['comparison']['metrics_diff']['accuracy']['difference']:.3f}")
    
    # 部署系统
    print("\n=== 模型部署演示 ===")
    
    deployment_system = ModelDeploymentSystem(versioning_system)
    
    # 创建部署配置
    deployment_config_id = deployment_system.create_deployment_config(
        model_version=version2_id,
        target_environment="production",
        resources={
            "replicas": 3,
            "cpu": "1",
            "memory": "2Gi",
            "gpu": False
        },
        scaling_config={
            "min_replicas": 2,
            "max_replicas": 10,
            "target_cpu_utilization": 70
        }
    )
    
    print(f"创建部署配置: {deployment_config_id}")
    
    # 执行部署
    deployment_result = deployment_system.deploy_model(
        deployment_config_id,
        deployment_strategy="canary"
    )
    
    print(f"部署状态: {deployment_result['status']}")
    print(f"部署策略: {deployment_result['strategy']}")
    
    # 监控部署状态
    status = deployment_system.get_deployment_status(deployment_config_id)
    print(f"\n部署监控状态:")
    print(f"  - 状态: {status['status']}")
    print(f"  - 实例数量: {len(status['instances'])}")
    print(f"  - CPU使用率: {status['health_metrics']['cpu_utilization']:.1f}%")
    
    # 高级功能演示
    print("\n=== 高级部署功能 ===")
    
    advanced_features = AdvancedDeploymentFeatures(deployment_system)
    
    # 设置特性开关
    advanced_features.setup_feature_flags(
        version2_id,
        {
            "enable_sentiment_fallback": True,
            "enable_confidence_threshold": True,
            "confidence_threshold": 0.7
        }
    )
    
    # 创建A/B测试
    ab_test_id = advanced_features.create_ab_test(
        test_name="model_optimization",
        model_version_a=version1_id,
        model_version_b=version2_id,
        traffic_split=0.3
    )
    
    print(f"创建A/B测试: {ab_test_id}")
    
    # 模拟性能指标收集
    monitor = advanced_features.performance_monitor
    monitor.record_metrics(deployment_config_id, {
        "accuracy": 0.89,
        "latency_ms": 150,
        "throughput": 500,
        "error_rate": 0.01
    })
    
    # 获取告警
    alerts = monitor.get_alerts(deployment_config_id)
    if alerts:
        print(f"\n当前告警数量: {len(alerts)}")
        for alert in alerts:
            print(f"  - {alert['alert_type']}: {alert['message']}")
    
    # 提升模型状态
    print("\n=== 模型状态管理 ===")
    versioning_system.promote_model(
        version2_id,
        ModelStatus.PRODUCTION,
        approved_by="admin",
        approval_notes="性能验证通过，可投入生产"
    )
    
    print("模型状态更新成功")
    
    # 获取最终统计
    print("\n=== 系统统计 ===")
    final_versions = versioning_system.get_model_versions("sentiment_classifier")
    production_versions = [v for v in final_versions if v.status == ModelStatus.PRODUCTION]
    
    print(f"总版本数: {len(final_versions)}")
    print(f"生产版本数: {len(production_versions)}")
    print(f"最新生产版本: {production_versions[0].version if production_versions else 'N/A'}")
    
    return {
        'versioning_system': versioning_system,
        'deployment_system': deployment_system,
        'advanced_features': advanced_features,
        'final_versions': final_versions
    }

# 运行示例
if __name__ == "__main__":
    result = asyncio.run(main())
```

## Best Practices

### 1. 版本管理策略
- **语义化版本**: 遵循语义化版本控制规范
- **模型谱系**: 维护完整的模型训练历史
- **标签系统**: 使用标签组织和管理模型版本
- **自动化流程**: 自动化版本注册和状态转换

### 2. 部署安全策略
- **安全扫描**: 部署前进行安全扫描和验证
- **访问控制**: 严格的部署权限管理
- **审计日志**: 完整的部署操作审计
- **加密传输**: 模型文件和配置的安全传输

### 3. 监控和告警
- **实时监控**: 关键性能指标的实时监控
- **智能告警**: 基于阈值的智能告警系统
- **自动回滚**: 基于性能下降的自动回滚机制
- **容量规划**: 基于使用情况的容量规划

### 4. 文档和治理
- **模型文档**: 完整的模型文档和元数据
- **审批流程**: 标准化的模型上线审批流程
- **合规报告**: 自动化的合规性报告生成
- **知识管理**: 模型经验和最佳实践的积累

## Integration Patterns

### 1. CI/CD集成
```yaml
# GitHub Actions工作流
name: Model Deployment Pipeline
on:
  push:
    branches: [main]
    paths: ['models/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Register Model Version
      run: |
        python scripts/register_model.py \
          --model-name=${{ matrix.model }} \
          --version=${{ github.sha }} \
          --metadata-file=metadata.json
    - name: Run Deployment
      run: |
        python scripts/deploy_model.py \
          --deployment-config=production_config.yaml \
          --strategy=canary
    - name: Validate Deployment
      run: |
        python scripts/validate_deployment.py \
          --deployment-id=${{ steps.register.outputs.deployment_id }}
```

### 2. Kubernetes部署
```yaml
# 模型部署的Kubernetes配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentiment-classifier
  labels:
    app: sentiment-classifier
    version: v1.1.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sentiment-classifier
  template:
    metadata:
      labels:
        app: sentiment-classifier
        version: v1.1.0
    spec:
      containers:
      - name: model-server
        image: sentiment-classifier:v1.1.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 3. 云原生集成
```python
# AWS SageMaker集成
import boto3
import sagemaker

class CloudModelDeployment:
    def __init__(self):
        self.sagemaker_client = boto3.client('sagemaker')
        self.endpoint_name = None
    
    def deploy_to_sagemaker(self, 
                           model_s3_uri: str,
                           endpoint_config_name: str,
                           instance_type: str = 'ml.t2.medium') -> str:
        """部署模型到SageMaker"""
        
        # 创建SageMaker模型
        model_name = f"model-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        response = self.sagemaker_client.create_model(
            ModelName=model_name,
            PrimaryContainer={
                'Image': '683313688378.dkr.ecr.us-west-2.amazonaws.com/sagemaker-scikit-learn:0.23-1-cpu-py3',
                'ModelDataUrl': model_s3_uri,
                'Environment': {
                    'SAGEMAKER_PROGRAM': 'inference.py',
                    'SAGEMAKER_SUBMIT_DIRECTORY': '/opt/ml/code'
                }
            },
            ExecutionRoleArn='arn:aws:iam::account:role/SageMakerExecutionRole'
        )
        
        # 创建端点配置
        endpoint_config_name = f"endpoint-config-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.sagemaker_client.create_endpoint_config(
            EndpointConfigName=endpoint_config_name,
            ProductionVariants=[
                {
                    'VariantName': 'primary',
                    'ModelName': model_name,
                    'InitialInstanceCount': 1,
                    'InstanceType': instance_type,
                    'InitialVariantWeight': 1
                }
            ]
        )
        
        # 部署端点
        self.endpoint_name = f"endpoint-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.sagemaker_client.create_endpoint(
            EndpointConfigName=endpoint_config_name,
            EndpointName=self.endpoint_name,
            EndpointName=endpoint_name
        )
        
        return self.endpoint_name
```

## Success Metrics

### 1. 部署效率指标
- **部署时间**: 从模型注册到生产部署的总时间
- **自动化程度**: 自动完成的部署步骤比例
- **部署频率**: 单位时间内成功部署的次数
- **变更失败率**: 部署失败或回滚的比例

### 2. 运营效率指标
- **回滚时间**: 发现问题到完成回滚的时间
- **监控覆盖率**: 被监控的关键指标比例
- **告警响应时间**: 告警到响应的平均时间
- **MTTR**: 平均修复时间

### 3. 模型质量指标
- **版本稳定性**: 模型版本在不同环境的一致性
- **性能一致性**: 部署前后模型性能变化
- **A/B测试效果**: A/B测试的统计显著性
- **特性开关效果**: 特性开关对性能的影响

### 4. 治理和合规指标
- **审计完成率**: 审计任务的完成比例
- **合规检查通过率**: 合规检查的通过比例
- **文档完整性**: 模型文档的完整程度
- **知识传承**: 经验文档化和复用程度

---

*模型版本部署是现代MLOps的核心组件，通过系统化的版本管理、自动化部署流程、持续监控和智能回滚，确保模型从开发到生产的可靠交付和稳定运行。*
