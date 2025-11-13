---
name: model-experiment-tracking
description: "模型实验管理与版本控制专家，精通MLflow、模型注册和实验对比分析。构建实验管理系统、模型版本追踪和实验协作平台，处理实验记录、模型管理和团队协作。使用PROACTIVELY进行ML实验管理、模型版本控制或实验协作。"
---

# 模型实验追踪技能

## When to Use
Use this skill when building ML experiment management systems, implementing model versioning, tracking hyperparameter optimization, comparing model performance across experiments, or building reproducible ML workflows. Essential for research teams, MLOps pipelines, model development lifecycle management, and ensuring reproducible ML experiments.

## Core Concepts

### 1. 实验管理系统
- **实验记录**: 自动记录实验配置、代码版本、数据版本
- **参数追踪**: 完整记录超参数、训练参数、实验设置
- **结果追踪**: 准确记录模型性能、训练损失、验证指标
- **元数据管理**: 存储实验的完整元数据和上下文

### 2. 模型版本控制
- **模型注册**: 自动注册和版本管理训练好的模型
- **版本标签**: 为模型版本添加有意义的标签和描述
- **模型谱系**: 记录模型的训练历史和依赖关系
- **回滚机制**: 支持模型版本的快速回滚和恢复

### 3. 实验对比分析
- **性能对比**: 自动比较多个实验的性能指标
- **可视化分析**: 生成实验结果的图表和报告
- **统计显著性**: 计算实验结果间的统计显著性
- **最优模型选择**: 基于多指标自动选择最优模型

### 4. 实验重现性
- **环境快照**: 记录完整的训练环境信息
- **代码版本**: 自动记录实验使用的代码版本
- **数据版本**: 记录训练数据的版本和哈希值
- **配置保存**: 保存完整的实验配置文件

## Code Examples

### MLflow集成实验追踪系统
```python
import mlflow
import mlflow.sklearn
from datetime import datetime
import hashlib
import json
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

class MLExperimentTracker:
    def __init__(self, experiment_name: str, tracking_uri: str = None):
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri
        self.mlflow_client = None
        
        # 初始化MLflow
        self._setup_mlflow()
        
        # 实验管理
        self.active_experiments = {}
        self.model_registry = {}
        self.experiment_history = []
    
    def _setup_mlflow(self):
        """设置MLflow实验追踪"""
        if self.tracking_uri:
            mlflow.set_tracking_uri(self.tracking_uri)
        
        # 创建或获取实验
        try:
            experiment_id = mlflow.create_experiment(self.experiment_name)
        except mlflow.exceptions.MlflowException:
            experiment_id = mlflow.get_experiment_by_name(self.experiment_name).experiment_id
        
        mlflow.set_experiment(experiment_name=self.experiment_name)
        self.mlflow_client = mlflow.MlflowClient()
    
    def start_experiment(self, 
                        experiment_config: Dict[str, Any],
                        tags: Dict[str, str] = None) -> str:
        """开始新的实验"""
        experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(experiment_config).encode()).hexdigest()[:8]}"
        
        # 设置实验标签
        mlflow.set_tags(tags or {})
        
        # 记录实验配置
        for key, value in experiment_config.items():
            mlflow.log_param(key, value)
        
        # 记录实验元数据
        experiment_metadata = {
            'experiment_id': experiment_id,
            'start_time': datetime.now().isoformat(),
            'config': experiment_config,
            'tags': tags,
            'git_commit': self._get_git_commit(),
            'python_version': self._get_python_version(),
            'mlflow_version': mlflow.__version__
        }
        
        self.active_experiments[experiment_id] = experiment_metadata
        
        # 开始MLflow运行
        with mlflow.start_run() as run:
            self.current_run_id = run.info.run_id
            mlflow.set_tag("experiment_id", experiment_id)
            
            # 记录运行环境信息
            self._log_environment_info()
        
        return experiment_id
    
    def log_metrics(self, metrics: Dict[str, float], step: int = None):
        """记录实验指标"""
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, (int, float, np.number)):
                mlflow.log_metric(metric_name, metric_value, step=step)
    
    def log_parameters(self, params: Dict[str, Any]):
        """记录超参数"""
        for param_name, param_value in params.items():
            if isinstance(param_value, (int, float, str, bool)):
                mlflow.log_param(param_name, param_value)
    
    def log_artifacts(self, artifacts: List[str]):
        """记录实验文件"""
        for artifact_path in artifacts:
            mlflow.log_artifact(artifact_path)
    
    def log_model(self, 
                 model, 
                 artifact_path: str,
                 registered_model_name: str = None):
        """记录训练好的模型"""
        if hasattr(model, 'save') or hasattr(model, 'to_json'):
            # Sklearn模型
            mlflow.sklearn.log_model(
                model, 
                artifact_path=artifact_path,
                registered_model_name=registered_model_name
            )
        else:
            # 其他类型模型
            mlflow.pyfunc.log_model(
                python_model=model,
                artifact_path=artifact_path,
                registered_model_name=registered_model_name
            )
    
    def end_experiment(self, 
                      experiment_id: str = None,
                      status: str = "FINISHED"):
        """结束实验"""
        if not experiment_id:
            experiment_id = self.current_run_id
        
        if experiment_id in self.active_experiments:
            self.active_experiments[experiment_id]['end_time'] = datetime.now().isoformat()
            self.active_experiments[experiment_id]['status'] = status
            
            # 移动到历史记录
            self.experiment_history.append(self.active_experiments[experiment_id])
            del self.active_experiments[experiment_id]
        
        # 结束MLflow运行
        mlflow.end_run(status=status)
    
    def compare_experiments(self, 
                           experiment_ids: List[str],
                           metrics: List[str] = None) -> pd.DataFrame:
        """比较多个实验的结果"""
        comparison_data = []
        
        for exp_id in experiment_ids:
            # 获取实验运行信息
            runs = self.mlflow_client.search_runs(
                experiment_ids=[mlflow.get_experiment_by_name(self.experiment_name).experiment_id],
                filter_string=f"tags.experiment_id = '{exp_id}'"
            )
            
            if runs:
                run = runs[0]
                exp_data = {
                    'experiment_id': exp_id,
                    'run_id': run.info.run_id,
                    'status': run.info.status,
                    'start_time': run.info.start_time,
                    'end_time': run.info.end_time
                }
                
                # 记录参数
                for param_name, param_value in run.data.params.items():
                    exp_data[f"param_{param_name}"] = param_value
                
                # 记录指标
                for metric_name, metric_value in run.data.metrics.items():
                    exp_data[f"metric_{metric_name}"] = metric_value
                
                comparison_data.append(exp_data)
        
        return pd.DataFrame(comparison_data)
    
    def get_best_model(self, 
                      experiment_ids: List[str],
                      metric_name: str,
                      ascending: bool = False) -> Dict[str, Any]:
        """获取最优模型"""
        best_run = None
        best_score = None
        
        for exp_id in experiment_ids:
            runs = self.mlflow_client.search_runs(
                experiment_ids=[mlflow.get_experiment_by_name(self.experiment_name).experiment_id],
                filter_string=f"tags.experiment_id = '{exp_id}'",
                max_results=1,
                order_by=[f"metrics.{metric_name} {'asc' if ascending else 'desc'}"]
            )
            
            if runs:
                run = runs[0]
                if metric_name in run.data.metrics:
                    score = run.data.metrics[metric_name]
                    
                    if best_score is None or (ascending and score < best_score) or (not ascending and score > best_score):
                        best_score = score
                        best_run = {
                            'run_id': run.info.run_id,
                            'experiment_id': exp_id,
                            'score': score,
                            'run_data': run
                        }
        
        return best_run
    
    def generate_experiment_report(self, 
                                  experiment_id: str,
                                  output_path: str = None) -> str:
        """生成实验报告"""
        runs = self.mlflow_client.search_runs(
            experiment_ids=[mlflow.get_experiment_by_name(self.experiment_name).experiment_id],
            filter_string=f"tags.experiment_id = '{experiment_id}'"
        )
        
        if not runs:
            return "No runs found for experiment"
        
        run = runs[0]
        
        report = f"""
# 实验报告 - {experiment_id}

## 实验概况
- 实验ID: {experiment_id}
- 运行ID: {run.info.run_id}
- 状态: {run.info.status}
- 开始时间: {run.info.start_time}
- 结束时间: {run.info.end_time}

## 超参数配置
"""
        
        for param_name, param_value in run.data.params.items():
            report += f"- {param_name}: {param_value}\n"
        
        report += "\n## 性能指标\n"
        for metric_name, metric_value in run.data.metrics.items():
            report += f"- {metric_name}: {metric_value}\n"
        
        # 保存报告
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
        
        return report
    
    def _get_git_commit(self) -> str:
        """获取当前Git提交信息"""
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_python_version(self) -> str:
        """获取Python版本"""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _log_environment_info(self):
        """记录环境信息"""
        import platform
        import pkg_resources
        
        # 记录包版本
        installed_packages = [d for d in pkg_resources.working_set]
        package_versions = {pkg.project_name: pkg.version for pkg in installed_packages}
        
        # 记录到文件
        env_info = {
            'python_version': self._get_python_version(),
            'platform': platform.platform(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'packages': package_versions
        }
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(env_info, f, indent=2)
            mlflow.log_artifact(f.name, "environment_info.json")

class ModelRegistry:
    def __init__(self, tracker: MLExperimentTracker):
        self.tracker = tracker
        self.registered_models = {}
    
    def register_model(self, 
                      model_name: str,
                      run_id: str,
                      model_stage: str = "Staging",
                      description: str = None):
        """注册模型到模型注册表"""
        try:
            # 获取模型工件路径
            model_uri = f"runs:/{run_id}/model"
            
            # 注册模型
            model_version = mlflow.register_model(
                model_uri, 
                model_name
            )
            
            # 设置模型标签和描述
            self.tracker.mlflow_client.update_model_version(
                name=model_name,
                version=model_version.version,
                description=description
            )
            
            # 设置模型阶段
            self.tracker.mlflow_client.transition_model_version_stage(
                name=model_name,
                version=model_version.version,
                stage=model_stage
            )
            
            self.registered_models[model_name] = {
                'latest_version': model_version.version,
                'current_stage': model_stage,
                'run_id': run_id,
                'registered_at': datetime.now().isoformat()
            }
            
            return model_version
            
        except Exception as e:
            print(f"模型注册失败: {e}")
            return None
    
    def promote_model(self, 
                     model_name: str,
                     target_stage: str,
                     version: str = None):
        """提升模型到下一阶段"""
        if version is None:
            version = self.registered_models.get(model_name, {}).get('latest_version')
        
        try:
            self.tracker.mlflow_client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=target_stage
            )
            
            if model_name in self.registered_models:
                self.registered_models[model_name]['current_stage'] = target_stage
                self.registered_models[model_name]['promoted_at'] = datetime.now().isoformat()
            
            print(f"模型 {model_name} 已提升到 {target_stage} 阶段")
            
        except Exception as e:
            print(f"模型提升失败: {e}")
    
    def get_production_models(self) -> List[Dict]:
        """获取生产阶段的所有模型"""
        production_models = []
        
        for model_name, model_info in self.registered_models.items():
            if model_info['current_stage'] == 'Production':
                production_models.append({
                    'model_name': model_name,
                    'version': model_info['latest_version'],
                    'run_id': model_info['run_id']
                })
        
        return production_models

# 高级实验对比和分析
class ExperimentAnalyzer:
    def __init__(self, tracker: MLExperimentTracker):
        self.tracker = tracker
    
    def statistical_significance_test(self,
                                    experiment_ids: List[str],
                                    metric_name: str) -> Dict[str, Any]:
        """执行统计显著性检验"""
        from scipy import stats
        
        # 收集指标数据
        metric_data = []
        for exp_id in experiment_ids:
            runs = self.tracker.mlflow_client.search_runs(
                experiment_ids=[mlflow.get_experiment_by_name(self.tracker.experiment_name).experiment_id],
                filter_string=f"tags.experiment_id = '{exp_id}'"
            )
            
            for run in runs:
                if metric_name in run.data.metrics:
                    metric_data.append(run.data.metrics[metric_name])
        
        if len(metric_data) < 2:
            return {"error": "Insufficient data for statistical test"}
        
        # 执行t检验
        if len(experiment_ids) == 2:
            # 双样本t检验
            group1 = [runs.data.metrics[metric_name] for runs in 
                     self.tracker.mlflow_client.search_runs(
                         experiment_ids=[mlflow.get_experiment_by_name(self.tracker.experiment_name).experiment_id],
                         filter_string=f"tags.experiment_id = '{experiment_ids[0]}'"
                     ) if metric_name in runs.data.metrics]
            
            group2 = [runs.data.metrics[metric_name] for runs in 
                     self.tracker.mlflow_client.search_runs(
                         experiment_ids=[mlflow.get_experiment_by_name(self.tracker.experiment_name).experiment_id],
                         filter_string=f"tags.experiment_id = '{experiment_ids[1]}'"
                     ) if metric_name in runs.data.metrics]
            
            if len(group1) > 0 and len(group2) > 0:
                t_stat, p_value = stats.ttest_ind(group1, group2)
                return {
                    'test_type': 'independent_t_test',
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05,
                    'group1_mean': np.mean(group1),
                    'group2_mean': np.mean(group2)
                }
        
        return {"error": "Statistical test not applicable"}
    
    def hyperparameter_importance_analysis(self, 
                                         experiment_ids: List[str],
                                         target_metric: str) -> pd.DataFrame:
        """分析超参数重要性"""
        # 收集所有实验的超参数和目标指标
        experiment_data = []
        
        for exp_id in experiment_ids:
            runs = self.tracker.mlflow_client.search_runs(
                experiment_ids=[mlflow.get_experiment_by_name(self.tracker.experiment_name).experiment_id],
                filter_string=f"tags.experiment_id = '{exp_id}'"
            )
            
            for run in runs:
                if target_metric in run.data.metrics:
                    row = {'experiment_id': exp_id}
                    
                    # 添加超参数
                    row.update(run.data.params)
                    
                    # 添加目标指标
                    row[target_metric] = run.data.metrics[target_metric]
                    
                    experiment_data.append(row)
        
        df = pd.DataFrame(experiment_data)
        
        if df.empty:
            return pd.DataFrame()
        
        # 计算相关系数
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        correlation_with_target = []
        
        for col in numeric_columns:
            if col != target_metric:
                correlation = df[col].corr(df[target_metric])
                correlation_with_target.append({
                    'hyperparameter': col,
                    'correlation': correlation,
                    'abs_correlation': abs(correlation)
                })
        
        return pd.DataFrame(correlation_with_target).sort_values('abs_correlation', ascending=False)

# 使用示例
async def main():
    # 初始化实验追踪器
    tracker = MLExperimentTracker(
        experiment_name="sentiment_classification",
        tracking_uri="http://localhost:5000"  # MLflow tracking server
    )
    
    # 初始化模型注册表
    model_registry = ModelRegistry(tracker)
    
    # 初始化分析器
    analyzer = ExperimentAnalyzer(tracker)
    
    # 实验1: 基础模型
    experiment_config_1 = {
        'model_type': 'logistic_regression',
        'learning_rate': 0.01,
        'max_iter': 1000,
        'regularization': 'l2'
    }
    
    exp_id_1 = tracker.start_experiment(
        experiment_config_1, 
        tags={'experiment_type': 'baseline', 'dataset': 'sentiment_v1'}
    )
    
    # 模拟训练过程
    for epoch in range(10):
        # 记录训练指标
        tracker.log_metrics({
            'train_loss': 0.8 - epoch * 0.05,
            'val_accuracy': 0.6 + epoch * 0.03,
            'val_precision': 0.55 + epoch * 0.025,
            'val_recall': 0.5 + epoch * 0.03
        }, step=epoch)
    
    # 结束实验
    tracker.end_experiment(exp_id_1)
    
    # 实验2: 优化模型
    experiment_config_2 = {
        'model_type': 'random_forest',
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 5,
        'random_state': 42
    }
    
    exp_id_2 = tracker.start_experiment(
        experiment_config_2,
        tags={'experiment_type': 'optimized', 'dataset': 'sentiment_v1'}
    )
    
    # 模拟训练过程
    for epoch in range(10):
        tracker.log_metrics({
            'train_loss': 0.6 - epoch * 0.04,
            'val_accuracy': 0.75 + epoch * 0.02,
            'val_precision': 0.7 + epoch * 0.025,
            'val_recall': 0.68 + epoch * 0.02
        }, step=epoch)
    
    # 结束实验
    tracker.end_experiment(exp_id_2)
    
    # 比较实验结果
    comparison_df = tracker.compare_experiments([exp_id_1, exp_id_2])
    print("实验对比:")
    print(comparison_df)
    
    # 获取最佳模型
    best_model = tracker.get_best_model([exp_id_1, exp_id_2], 'val_accuracy')
    print(f"最佳模型: {best_model}")
    
    # 生成实验报告
    report = tracker.generate_experiment_report(exp_id_1, "experiment_report_1.md")
    print("实验报告已生成")
    
    # 注册最佳模型
    if best_model:
        model_version = model_registry.register_model(
            model_name="sentiment_classifier",
            run_id=best_model['run_id'],
            model_stage="Production",
            description="最佳情感分类模型"
        )
        print(f"模型已注册，版本: {model_version.version if model_version else 'N/A'}")
    
    # 统计显著性检验
    significance_result = analyzer.statistical_significance_test(
        [exp_id_1, exp_id_2], 'val_accuracy'
    )
    print(f"统计显著性: {significance_result}")
    
    return {
        'comparison_df': comparison_df,
        'best_model': best_model,
        'significance_result': significance_result
    }

# 运行示例
if __name__ == "__main__":
    result = asyncio.run(main())
```

## Best Practices

### 1. 实验组织策略
- **实验命名规范**: 使用一致的命名规范便于管理
- **标签系统**: 为实验添加有意义的标签和分类
- **版本控制**: 明确区分不同版本的实验
- **团队协作**: 建立团队协作的实验共享机制

### 2. 数据管理
- **数据版本**: 记录训练数据的版本和完整性
- **数据分割**: 记录训练/验证/测试集的分割策略
- **特征工程**: 记录特征工程的步骤和版本
- **数据质量**: 监控数据质量的变化

### 3. 模型管理
- **模型生命周期**: 管理模型的完整生命周期
- **性能监控**: 持续监控生产模型的性能
- **模型回滚**: 支持快速回滚到之前的版本
- **A/B测试**: 自动化A/B测试流程

### 4. 可重现性保证
- **环境锁定**: 锁定训练环境的依赖版本
- **随机种子**: 记录和设置随机种子
- **配置保存**: 保存完整的实验配置
- **日志记录**: 详细的训练日志记录

## Integration Patterns

### 1. CI/CD集成
```yaml
# .github/workflows/ml-experiment.yml
name: ML Experiment Tracking
on:
  push:
    branches: [main]

jobs:
  experiment:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run ML Experiment
      run: |
        python train_model.py --experiment-name="ci_experiment_${{ github.sha }}"
    - name: Upload to MLflow
      run: |
        mlflow experiments create --experiment-name="ci_${{ github.sha }}"
```

### 2. 分布式训练集成
```python
# 分布式训练实验追踪
class DistributedExperimentTracker:
    def __init__(self, base_tracker: MLExperimentTracker):
        self.base_tracker = base_tracker
        self.worker_trackers = {}
    
    def register_worker(self, worker_id: str):
        """注册分布式训练工作节点"""
        worker_tracker = MLExperimentTracker(
            experiment_name=f"{self.base_tracker.experiment_name}_worker_{worker_id}"
        )
        self.worker_trackers[worker_id] = worker_tracker
        return worker_tracker
    
    def sync_experiment_results(self):
        """同步分布式实验结果"""
        all_metrics = {}
        all_params = {}
        
        for worker_id, tracker in self.worker_trackers.items():
            # 聚合工作节点的指标和参数
            worker_runs = tracker.mlflow_client.search_runs(
                experiment_ids=[mlflow.get_experiment_by_name(tracker.experiment_name).experiment_id]
            )
            
            if worker_runs:
                run = worker_runs[0]
                all_metrics[worker_id] = run.data.metrics
                all_params[worker_id] = run.data.params
        
        # 在基础追踪器中记录聚合结果
        self.base_tracker.log_metrics({
            'avg_train_loss': np.mean([metrics.get('train_loss', 0) for metrics in all_metrics.values()]),
            'std_train_loss': np.std([metrics.get('train_loss', 0) for metrics in all_metrics.values()]),
            'num_workers': len(self.worker_trackers)
        })
```

## Success Metrics

### 1. 实验效率指标
- **实验时间**: 实验从开始到完成的时间
- **迭代速度**: 实验迭代和优化的速度
- **资源利用**: 计算资源的使用效率
- **实验成功率**: 成功完成的实验比例

### 2. 模型质量指标
- **性能改进**: 模型性能随时间的改进趋势
- **稳定性**: 模型性能的一致性和稳定性
- **泛化能力**: 模型在不同数据集上的表现
- **模型复杂度**: 模型复杂度与性能的平衡

### 3. 团队协作指标
- **实验共享**: 团队成员间的实验共享程度
- **知识传承**: 实验经验和知识的传承效果
- **复现率**: 实验结果的可复现性比例
- **代码质量**: 实验代码的质量和规范化程度

---

*模型实验追踪是现代ML开发的核心基础设施，通过系统化的实验管理、模型版本控制和性能分析，显著提升ML项目的开发效率和成功率。*
