---
name: hyperparameter-optimization
description: "超参数优化与自动调参专家，精通贝叶斯优化、网格搜索和进化算法。实现智能搜索策略、性能评估框架和并行调参，处理超参数搜索、模型调优和自动机器学习。使用PROACTIVELY进行模型调优、超参搜索或AutoML实施。"
---

# 超参数优化技能

## When to Use
Use this skill when optimizing ML model performance through systematic hyperparameter search, implementing Bayesian optimization, performing grid/random search, automating hyperparameter tuning, or building scalable hyperparameter optimization pipelines. Essential for maximizing model performance, reducing manual tuning effort, and implementing production-ready HPO systems.

## Core Concepts

### 1. 优化算法选择
- **网格搜索**: 全面的参数网格搜索，适合小规模参数空间
- **随机搜索**: 随机采样参数组合，效率高且效果好
- **贝叶斯优化**: 基于概率模型的智能优化，适合高成本评估
- **遗传算法**: 基于进化策略的参数优化，适合复杂搜索空间

### 2. 优化策略设计
- **分层优化**: 多层次参数优化，从粗调到细调
- **早停机制**: 基于验证性能提前停止不佳试验
- **并行优化**: 并行执行多个参数试验以提高效率
- **自适应优化**: 根据优化进度动态调整搜索策略

### 3. 性能评估框架
- **交叉验证**: 稳健的性能评估方法
- **分层采样**: 确保各类别样本的均匀分布
- **时间序列分割**: 时间序列数据的特殊分割策略
- **多指标优化**: 考虑多个性能指标的综合优化

### 4. 优化结果分析
- **参数重要性**: 分析不同参数对性能的影响程度
- **参数交互**: 研究参数间的交互效应
- **收敛分析**: 分析优化过程的收敛情况
- **鲁棒性测试**: 测试最优参数组合的稳定性

## Code Examples

### 贝叶斯优化系统
```python
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Callable
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import optuna
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class HyperparameterOptimizer:
    def __init__(self, 
                 objective_function: Callable,
                 search_space: Dict[str, Any],
                 optimizer_type: str = 'bayesian',
                 cv_folds: int = 5,
                 scoring: str = 'accuracy',
                 random_state: int = 42):
        self.objective_function = objective_function
        self.search_space = search_space
        self.optimizer_type = optimizer_type
        self.cv_folds = cv_folds
        self.scoring = scoring
        self.random_state = random_state
        self.optimization_history = []
        self.best_params = None
        self.best_score = None
        self.study = None
    
    def optimize(self, 
                 n_trials: int = 100,
                 timeout: int = None,
                 n_jobs: int = 1) -> Dict[str, Any]:
        """执行超参数优化"""
        
        if self.optimizer_type == 'bayesian':
            return self._optimize_bayesian(n_trials, timeout, n_jobs)
        elif self.optimizer_type == 'grid':
            return self._optimize_grid(n_trials)
        elif self.optimizer_type == 'random':
            return self._optimize_random(n_trials, n_jobs)
        else:
            raise ValueError(f"不支持的优化器类型: {self.optimizer_type}")
    
    def _optimize_bayesian(self, 
                          n_trials: int = 100,
                          timeout: int = None,
                          n_jobs: int = 1) -> Dict[str, Any]:
        """贝叶斯优化"""
        # 创建Optuna学习器
        self.study = optuna.create_study(
            direction='maximize',
            sampler=optuna.samplers.TPESampler(seed=self.random_state)
        )
        
        # 定义目标函数
        def objective(trial):
            params = {}
            for param_name, param_config in self.search_space.items():
                param_type = param_config['type']
                param_args = param_config.get('args', {})
                
                if param_type == 'int':
                    params[param_name] = trial.suggest_int(
                        param_name,
                        param_args['low'],
                        param_args['high'],
                        step=param_args.get('step', 1)
                    )
                elif param_type == 'float':
                    params[param_name] = trial.suggest_float(
                        param_name,
                        param_args['low'],
                        param_args['high'],
                        log=param_args.get('log', False)
                    )
                elif param_type == 'categorical':
                    params[param_name] = trial.suggest_categorical(
                        param_name,
                        param_args['choices']
                    )
            
            # 计算目标函数值
            score = self.objective_function(params)
            
            # 记录优化历史
            self.optimization_history.append({
                'trial_number': trial.number,
                'params': params.copy(),
                'score': score,
                'timestamp': pd.Timestamp.now()
            })
            
            return score
        
        # 执行优化
        self.study.optimize(
            objective,
            n_trials=n_trials,
            timeout=timeout,
            n_jobs=n_jobs,
            show_progress_bar=True
        )
        
        # 保存结果
        self.best_params = self.study.best_params
        self.best_score = self.study.best_value
        
        return {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'n_trials': len(self.study.trials),
            'optimization_time': self.study.trials[-1].datetime_complete - self.study.trials[0].datetime_start,
            'study': self.study
        }
    
    def _optimize_grid(self, n_trials: int = None) -> Dict[str, Any]:
        """网格搜索优化"""
        from itertools import product
        
        # 生成参数网格
        param_names = list(self.search_space.keys())
        param_values = []
        
        for param_name, param_config in self.search_space.items():
            param_type = param_config['type']
            param_args = param_config.get('args', {})
            
            if param_type == 'int':
                values = list(range(
                    param_args['low'], 
                    param_args['high'] + 1, 
                    param_args.get('step', 1)
                ))
            elif param_type == 'float':
                # 浮点数网格化
                num_points = param_args.get('num_points', 10)
                values = list(np.linspace(
                    param_args['low'],
                    param_args['high'],
                    num_points
                ))
            elif param_type == 'categorical':
                values = param_args['choices']
            
            param_values.append(values)
        
        # 生成所有参数组合
        param_combinations = list(product(*param_values))
        
        # 限制试验数量
        if n_trials and n_trials < len(param_combinations):
            param_combinations = param_combinations[:n_trials]
        
        best_score = -np.inf
        best_params = None
        results = []
        
        print(f"执行网格搜索，总共 {len(param_combinations)} 个参数组合")
        
        for i, param_combo in enumerate(param_combinations):
            # 构建参数字典
            params = dict(zip(param_names, param_combo))
            
            # 计算目标函数值
            try:
                score = self.objective_function(params)
                
                results.append({
                    'trial_number': i,
                    'params': params.copy(),
                    'score': score
                })
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                
                if (i + 1) % 10 == 0:
                    print(f"已完成 {i + 1}/{len(param_combinations)} 个试验")
                    
            except Exception as e:
                print(f"试验 {i} 失败: {e}")
                continue
        
        self.best_params = best_params
        self.best_score = best_score
        self.optimization_history = results
        
        return {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'n_trials': len(results),
            'results': results
        }
    
    def _optimize_random(self, n_trials: int = 100, n_jobs: int = 1) -> Dict[str, Any]:
        """随机搜索优化"""
        import random
        
        results = []
        best_score = -np.inf
        best_params = None
        
        print(f"执行随机搜索，总共 {n_trials} 个随机试验")
        
        for i in range(n_trials):
            # 随机生成参数
            params = {}
            for param_name, param_config in self.search_space.items():
                param_type = param_config['type']
                param_args = param_config.get('args', {})
                
                if param_type == 'int':
                    params[param_name] = random.randint(
                        param_args['low'],
                        param_args['high']
                    )
                elif param_type == 'float':
                    params[param_name] = random.uniform(
                        param_args['low'],
                        param_args['high']
                    )
                elif param_type == 'categorical':
                    params[param_name] = random.choice(param_args['choices'])
            
            # 计算目标函数值
            try:
                score = self.objective_function(params)
                
                results.append({
                    'trial_number': i,
                    'params': params.copy(),
                    'score': score
                })
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                
                if (i + 1) % 10 == 0:
                    print(f"已完成 {i + 1}/{n_trials} 个试验")
                    
            except Exception as e:
                print(f"试验 {i} 失败: {e}")
                continue
        
        self.best_params = best_params
        self.best_score = best_score
        self.optimization_history = results
        
        return {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'n_trials': len(results),
            'results': results
        }
    
    def analyze_optimization_results(self) -> Dict[str, Any]:
        """分析优化结果"""
        if not self.optimization_history:
            return {"error": "没有优化历史记录"}
        
        results_df = pd.DataFrame(self.optimization_history)
        
        # 基本统计信息
        stats_info = {
            'total_trials': len(results_df),
            'mean_score': results_df['score'].mean(),
            'std_score': results_df['score'].std(),
            'min_score': results_df['score'].min(),
            'max_score': results_df['score'].max(),
            'best_score': self.best_score
        }
        
        # 参数重要性分析
        param_importance = self._analyze_parameter_importance(results_df)
        
        # 收敛分析
        convergence_analysis = self._analyze_convergence(results_df)
        
        return {
            'statistics': stats_info,
            'parameter_importance': param_importance,
            'convergence_analysis': convergence_analysis,
            'optimization_data': results_df
        }
    
    def _analyze_parameter_importance(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """分析参数重要性"""
        importance_scores = {}
        
        for param_name in self.search_space.keys():
            if param_name in results_df['params'].iloc[0]:
                param_values = results_df['params'].apply(lambda x: x[param_name])
                correlation = abs(param_values.corr(results_df['score']))
                importance_scores[param_name] = correlation
        
        return dict(sorted(importance_scores.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_convergence(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """分析优化收敛情况"""
        # 计算滑动平均
        window_size = min(10, len(results_df) // 4)
        if window_size > 0:
            results_df['score_ma'] = results_df['score'].rolling(window=window_size).mean()
            
            # 检查最后几个试验的方差
            if len(results_df) >= window_size:
                final_scores = results_df['score'].tail(window_size)
                convergence_score = 1.0 / (1.0 + final_scores.var())
            else:
                convergence_score = 0.0
        else:
            convergence_score = 0.0
        
        return {
            'convergence_score': convergence_score,
            'is_converged': convergence_score > 0.9,
            'window_size': window_size
        }

# 自动超参数优化系统
class AutoHyperparameterTuner:
    def __init__(self, 
                 model_class,
                 X_train,
                 y_train,
                 X_val=None,
                 y_val=None,
                 cv_folds: int = 5,
                 scoring: str = 'accuracy',
                 random_state: int = 42):
        self.model_class = model_class
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        self.cv_folds = cv_folds
        self.scoring = scoring
        self.random_state = random_state
        
        # 预定义的搜索空间
        self.search_spaces = self._get_model_search_spaces()
    
    def _get_model_search_spaces(self) -> Dict[str, Dict]:
        """获取不同模型的搜索空间"""
        return {
            'RandomForest': {
                'n_estimators': {'type': 'int', 'args': {'low': 50, 'high': 500, 'step': 50}},
                'max_depth': {'type': 'int', 'args': {'low': 3, 'high': 20}},
                'min_samples_split': {'type': 'int', 'args': {'low': 2, 'high': 20}},
                'min_samples_leaf': {'type': 'int', 'args': {'low': 1, 'high': 10}},
                'max_features': {'type': 'float', 'args': {'low': 0.1, 'high': 1.0}}
            },
            'LogisticRegression': {
                'C': {'type': 'float', 'args': {'low': 0.01, 'high': 100, 'log': True}},
                'penalty': {'type': 'categorical', 'args': {'choices': ['l1', 'l2', 'elasticnet']}},
                'solver': {'type': 'categorical', 'args': {'choices': ['liblinear', 'saga']}},
                'max_iter': {'type': 'int', 'args': {'low': 100, 'high': 1000, 'step': 100}}
            },
            'SVC': {
                'C': {'type': 'float', 'args': {'low': 0.1, 'high': 100, 'log': True}},
                'kernel': {'type': 'categorical', 'args': {'choices': ['rbf', 'poly', 'sigmoid']}},
                'gamma': {'type': 'float', 'args': {'low': 0.001, 'high': 10, 'log': True}},
                'degree': {'type': 'int', 'args': {'low': 2, 'high': 5}}
            },
            'XGBoost': {
                'n_estimators': {'type': 'int', 'args': {'low': 50, 'high': 500, 'step': 50}},
                'max_depth': {'type': 'int', 'args': {'low': 3, 'high': 10}},
                'learning_rate': {'type': 'float', 'args': {'low': 0.01, 'high': 0.3, 'log': True}},
                'subsample': {'type': 'float', 'args': {'low': 0.6, 'high': 1.0}},
                'colsample_bytree': {'type': 'float', 'args': {'low': 0.6, 'high': 1.0}}
            }
        }
    
    def auto_tune(self, 
                  model_name: str = 'Auto',
                  optimizer_type: str = 'bayesian',
                  n_trials: int = 100,
                  timeout: int = None) -> Dict[str, Any]:
        """自动调优模型参数"""
        
        # 自动选择最佳模型
        if model_name == 'Auto':
            model_name = self._select_best_model(optimizer_type, n_trials)
        
        # 获取搜索空间
        if model_name not in self.search_spaces:
            raise ValueError(f"不支持的模型类型: {model_name}")
        
        search_space = self.search_spaces[model_name]
        
        # 创建目标函数
        def objective_function(params):
            return self._evaluate_model(params)
        
        # 创建优化器
        optimizer = HyperparameterOptimizer(
            objective_function=objective_function,
            search_space=search_space,
            optimizer_type=optimizer_type,
            cv_folds=self.cv_folds,
            scoring=self.scoring,
            random_state=self.random_state
        )
        
        # 执行优化
        optimization_result = optimizer.optimize(
            n_trials=n_trials,
            timeout=timeout
        )
        
        # 创建最终模型
        final_model = self.model_class(**optimization_result['best_params'])
        
        return {
            'model_name': model_name,
            'optimization_result': optimization_result,
            'final_model': final_model,
            'analysis': optimizer.analyze_optimization_results()
        }
    
    def _select_best_model(self, 
                          optimizer_type: str = 'bayesian',
                          n_trials: int = 20) -> str:
        """自动选择最佳模型"""
        model_scores = {}
        
        for model_name in self.search_spaces.keys():
            try:
                # 为每个模型创建简化的优化器
                search_space = self.search_spaces[model_name]
                
                def objective_function(params):
                    return self._evaluate_model(params, model_name=model_name)
                
                optimizer = HyperparameterOptimizer(
                    objective_function=objective_function,
                    search_space=search_space,
                    optimizer_type=optimizer_type,
                    cv_folds=min(3, self.cv_folds),  # 减少CV折数以提高速度
                    scoring=self.scoring,
                    random_state=self.random_state
                )
                
                # 执行少量试验
                result = optimizer.optimize(n_trials=n_trials, n_jobs=1)
                model_scores[model_name] = result['best_score']
                
                print(f"模型 {model_name} 最佳得分: {result['best_score']:.4f}")
                
            except Exception as e:
                print(f"模型 {model_name} 评估失败: {e}")
                model_scores[model_name] = -np.inf
        
        # 选择得分最高的模型
        best_model = max(model_scores, key=model_scores.get)
        print(f"自动选择模型: {best_model} (得分: {model_scores[best_model]:.4f})")
        
        return best_model
    
    def _evaluate_model(self, 
                       params: Dict[str, Any],
                       model_name: str = None) -> float:
        """评估模型性能"""
        
        # 确定模型名称
        if model_name is None:
            # 根据参数推断模型类型
            if 'n_estimators' in params and 'max_depth' in params:
                model_name = 'RandomForest'
            elif 'C' in params and 'penalty' in params:
                model_name = 'LogisticRegression'
            else:
                model_name = 'RandomForest'  # 默认模型
        
        # 创建模型实例
        try:
            if model_name == 'RandomForest':
                model = RandomForestClassifier(**params, random_state=self.random_state)
            elif model_name == 'LogisticRegression':
                # 处理正则化参数组合
                if params['penalty'] == 'elasticnet':
                    model = LogisticRegression(
                        C=params['C'],
                        penalty='elasticnet',
                        solver='saga',
                        max_iter=params['max_iter'],
                        random_state=self.random_state
                    )
                else:
                    model = LogisticRegression(
                        C=params['C'],
                        penalty=params['penalty'],
                        solver=params['solver'],
                        max_iter=params['max_iter'],
                        random_state=self.random_state
                    )
            else:
                # 其他模型类型的默认处理
                model = self.model_class(**params)
            
            # 交叉验证评估
            if self.X_val is not None and self.y_val is not None:
                # 使用验证集
                model.fit(self.X_train, self.y_train)
                score = model.score(self.X_val, self.y_val)
            else:
                # 使用交叉验证
                scores = cross_val_score(
                    model, self.X_train, self.y_train,
                    cv=StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state),
                    scoring=self.scoring
                )
                score = scores.mean()
            
            return score
            
        except Exception as e:
            print(f"模型评估失败: {e}")
            return -np.inf  # 返回很低的分数
    
    def batch_optimize(self, 
                      models: List[str],
                      optimizer_configs: Dict[str, Dict] = None) -> Dict[str, Any]:
        """批量优化多个模型"""
        
        results = {}
        
        for model_name in models:
            if optimizer_configs and model_name in optimizer_configs:
                config = optimizer_configs[model_name]
                optimizer_type = config.get('optimizer_type', 'bayesian')
                n_trials = config.get('n_trials', 50)
                timeout = config.get('timeout', None)
            else:
                optimizer_type = 'bayesian'
                n_trials = 50
                timeout = None
            
            print(f"\n开始优化模型: {model_name}")
            
            try:
                result = self.auto_tune(
                    model_name=model_name,
                    optimizer_type=optimizer_type,
                    n_trials=n_trials,
                    timeout=timeout
                )
                results[model_name] = result
                print(f"模型 {model_name} 优化完成，最佳得分: {result['optimization_result']['best_score']:.4f}")
                
            except Exception as e:
                print(f"模型 {model_name} 优化失败: {e}")
                results[model_name] = {'error': str(e)}
        
        return results
    
    def compare_models(self, results: Dict[str, Any]) -> pd.DataFrame:
        """比较不同模型的优化结果"""
        comparison_data = []
        
        for model_name, result in results.items():
            if 'error' not in result:
                optimization_result = result['optimization_result']
                comparison_data.append({
                    'model': model_name,
                    'best_score': optimization_result['best_score'],
                    'n_trials': optimization_result['n_trials'],
                    'best_params': optimization_result['best_params']
                })
        
        return pd.DataFrame(comparison_data)

# 高级优化技术
class AdvancedHyperparameterOptimizer:
    def __init__(self, base_optimizer: HyperparameterOptimizer):
        self.base_optimizer = base_optimizer
        self.multi_objective_optimizer = MultiObjectiveOptimizer()
        self.early_stopping = EarlyStoppingOptimizer()
    
    def optimize_with_early_stopping(self, 
                                    patience: int = 10,
                                    min_delta: float = 0.001) -> Dict[str, Any]:
        """带早停的优化"""
        return self.early_stopping.optimize(
            self.base_optimizer,
            patience=patience,
            min_delta=min_delta
        )
    
    def multi_objective_optimize(self, 
                               objectives: Dict[str, Callable],
                               weights: Dict[str, float]) -> Dict[str, Any]:
        """多目标优化"""
        return self.multi_objective_optimizer.optimize(
            self.base_optimizer,
            objectives=objectives,
            weights=weights
        )

class EarlyStoppingOptimizer:
    def __init__(self):
        self.patience_trials = []
    
    def optimize(self, 
                optimizer: HyperparameterOptimizer,
                patience: int = 10,
                min_delta: float = 0.001) -> Dict[str, Any]:
        """早停优化实现"""
        
        best_score = -np.inf
        patience_counter = 0
        early_stopped = False
        
        for i in range(100):  # 最大迭代次数
            # 执行单个试验
            trial_params = optimizer._generate_random_params()
            score = optimizer.objective_function(trial_params)
            
            # 检查改进
            if score > best_score + min_delta:
                best_score = score
                patience_counter = 0
            else:
                patience_counter += 1
            
            # 早停检查
            if patience_counter >= patience:
                early_stopped = True
                print(f"早停在第 {i + 1} 次试验，最佳得分: {best_score}")
                break
        
        return {
            'best_score': best_score,
            'n_trials': len(optimizer.optimization_history),
            'early_stopped': early_stopped,
            'optimization_history': optimizer.optimization_history
        }

# 使用示例
async def main():
    # 生成示例数据
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    
    X, y = make_classification(
        n_samples=1000, n_features=20, n_informative=15,
        n_redundant=5, n_classes=2, random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 初始化自动调优器
    tuner = AutoHyperparameterTuner(
        model_class=RandomForestClassifier,
        X_train=X_train,
        y_train=y_train,
        X_val=X_test,
        y_val=y_test,
        cv_folds=3,
        scoring='accuracy'
    )
    
    # 自动选择和调优模型
    print("开始自动超参数优化...")
    result = tuner.auto_tune(
        model_name='Auto',
        optimizer_type='bayesian',
        n_trials=50
    )
    
    print(f"\n最佳模型: {result['model_name']}")
    print(f"最佳得分: {result['optimization_result']['best_score']:.4f}")
    print(f"最佳参数: {result['optimization_result']['best_params']}")
    
    # 分析优化结果
    analysis = result['analysis']
    print(f"\n参数重要性: {analysis['parameter_importance']}")
    print(f"收敛状态: {analysis['convergence_analysis']}")
    
    # 批量优化多个模型
    print("\n开始批量优化多个模型...")
    batch_results = tuner.batch_optimize(
        models=['RandomForest', 'LogisticRegression'],
        optimizer_configs={
            'RandomForest': {'optimizer_type': 'bayesian', 'n_trials': 30},
            'LogisticRegression': {'optimizer_type': 'random', 'n_trials': 30}
        }
    )
    
    # 比较结果
    comparison_df = tuner.compare_models(batch_results)
    print("\n模型对比:")
    print(comparison_df)
    
    return {
        'single_model_result': result,
        'batch_results': batch_results,
        'comparison': comparison_df
    }

# 运行示例
if __name__ == "__main__":
    result = asyncio.run(main())
```

## Best Practices

### 1. 优化策略设计
- **分层优化**: 先优化最重要的参数，再优化次要参数
- **搜索空间**: 根据经验设置合理的参数范围
- **资源分配**: 合理分配计算资源给不同试验
- **并行优化**: 使用并行化加速优化过程

### 2. 性能评估
- **稳健评估**: 使用交叉验证确保结果的稳健性
- **多指标**: 同时考虑多个性能指标
- **统计显著性**: 使用统计检验验证结果
- **过拟合检查**: 检查是否存在过拟合

### 3. 结果分析
- **参数重要性**: 识别对性能影响最大的参数
- **参数交互**: 分析参数间的交互效应
- **稳定性**: 测试最优参数组合的稳定性
- **可解释性**: 提供优化结果的可解释性分析

### 4. 生产部署
- **部署测试**: 在部署前测试优化后的参数
- **监控性能**: 持续监控生产环境的性能
- **增量优化**: 基于新数据持续优化参数
- **版本管理**: 管理不同版本的参数配置

## Integration Patterns

### 1. MLOps管道集成
```python
# MLOps管道中的HPO集成
class MLOpsHyperparameterTuner:
    def __init__(self, ml_pipeline):
        self.ml_pipeline = ml_pipeline
        self.tuner = AutoHyperparameterTuner(...)
    
    def optimize_in_pipeline(self, 
                           data_version: str,
                           model_version: str,
                           optimization_config: Dict):
        """在MLOps管道中执行HPO"""
        
        # 获取训练数据
        train_data = self.ml_pipeline.load_data(data_version)
        
        # 执行超参数优化
        optimization_result = self.tuner.auto_tune(**optimization_config)
        
        # 更新模型配置
        model_config = self.ml_pipeline.get_model_config(model_version)
        model_config.update({
            'hyperparameters': optimization_result['optimization_result']['best_params'],
            'optimization_score': optimization_result['optimization_result']['best_score'],
            'optimization_date': datetime.now().isoformat()
        })
        
        # 保存优化后的模型
        optimized_model = self.ml_pipeline.save_model(
            model_config, 
            optimization_result['final_model']
        )
        
        return optimized_model
```

### 2. 云原生部署
```yaml
# Kubernetes HPO任务
apiVersion: batch/v1
kind: Job
metadata:
  name: hyperparameter-optimization
spec:
  template:
    spec:
      containers:
      - name: hpo-runner
        image: ml-hpo:latest
        command: ["python", "run_hpo.py"]
        env:
        - name: OPTUNA_STORAGE
          value: "postgresql://user:pass@postgres-service:5432/mlops"
        - name: REDIS_URL
          value: "redis://redis-service:6379"
      restartPolicy: Never
  backoffLimit: 3
```

## Success Metrics

### 1. 优化效果指标
- **性能提升**: 优化前后模型性能的改进幅度
- **优化效率**: 达到目标性能所需的试验次数
- **收敛速度**: 优化过程的收敛速度
- **稳定性**: 多次优化结果的一致性

### 2. 资源利用指标
- **计算成本**: 优化过程消耗的计算资源
- **时间成本**: 优化过程消耗的时间
- **并行效率**: 并行优化的效率
- **资源利用**: 计算资源的利用效率

### 3. 自动化程度指标
- **人工干预**: 优化过程需要的人工干预程度
- **自动化比例**: 完全自动化优化的比例
- **错误率**: 优化过程中的错误率
- **用户体验**: 用户对HPO工具的满意度

---

*超参数优化是机器学习模型性能提升的关键环节，通过系统化的搜索策略和智能化的优化算法，可以显著提升模型性能并减少人工调优工作量。*
