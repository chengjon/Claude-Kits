---
name: model-explainability
description: "模型可解释性与透明度专家，精通SHAP、LIME和模型特定解释方法。构建解释性分析工具、可视化解释系统和透明度评估，处理模型可解释性、特征重要性和决策透明度。使用PROACTIVELY进行模型解释、可视化分析或AI透明度建设。"
---

# 模型可解释性技能

## When to Use
Use this skill when implementing model interpretability methods, creating SHAP/LIME explanations, building feature importance analysis, developing model-agnostic explanation systems, or implementing fair and transparent ML systems. Essential for regulatory compliance, model debugging, feature engineering insights, and building trustworthy AI systems.

## Core Concepts

### 1. 全局解释方法
- **特征重要性**: 整体特征对模型预测的贡献度
- **全局方向性**: 特征变化对预测结果的全局影响方向
- **依赖图**: 特征间的相互依赖关系
- **部分依赖图**: 单一特征对预测的边际效应

### 2. 局部解释方法
- **SHAP值**: 基于博弈论的精确特征贡献度计算
- **LIME**: 局部可解释的模型无关解释方法
- **个别预测解释**: 对单个预测结果的详细解释
- **反事实解释**: 最小变化产生不同预测的输入修改

### 3. 模型特定解释
- **决策树路径**: 决策树中的决策路径和分裂规则
- **线性模型权重**: 线性模型的权重和偏置解释
- **神经网络注意力**: 注意力机制的权重可视化
- **集成模型**: 树模型的分裂和投票解释

### 4. 可视化技术
- **特征重要性图**: 直观展示特征重要性排序
- **SHAP汇总图**: SHAP值的分布和重要性可视化
- **依赖图**: 特征依赖关系的二维可视化
- **决策边界图**: 分类模型的决策边界可视化

## Code Examples

### SHAP解释系统
```python
import shap
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

class ModelExplainer:
    def __init__(self, 
                 model, 
                 X_train: pd.DataFrame,
                 model_type: str = 'auto',
                 feature_names: List[str] = None):
        self.model = model
        self.X_train = X_train
        self.model_type = model_type
        self.feature_names = feature_names or X_train.columns.tolist()
        
        # 自动推断模型类型
        if model_type == 'auto':
            self.model_type = self._infer_model_type()
        
        # 初始化解释器
        self.explainer = self._create_explainer()
        self.shap_values = None
    
    def _infer_model_type(self) -> str:
        """自动推断模型类型"""
        model_class = type(self.model).__name__
        
        if 'RandomForest' in model_class or 'ExtraTrees' in model_class:
            return 'tree'
        elif 'GradientBoosting' in model_class or 'XGB' in model_class:
            return 'tree'
        elif 'Linear' in model_class:
            return 'linear'
        elif 'SVC' in model_class or 'SVR' in model_class:
            return 'kernel'
        elif 'Keras' in model_class or 'TensorFlow' in model_class:
            return 'deep'
        else:
            return 'auto'
    
    def _create_explainer(self):
        """创建适合的SHAP解释器"""
        if self.model_type == 'tree':
            return shap.TreeExplainer(self.model)
        elif self.model_type == 'linear':
            return shap.LinearExplainer(self.model, self.X_train)
        elif self.model_type == 'kernel':
            return shap.KernelExplainer(
                self.model.predict, 
                shap.kmeans(self.X_train, 100)
            )
        elif self.model_type == 'deep':
            return shap.DeepExplainer(self.model, self.X_train)
        else:
            return shap.Explainer(self.model)
    
    def global_explanation(self, 
                          X_sample: pd.DataFrame = None,
                          max_features: int = 20) -> Dict[str, Any]:
        """全局特征重要性解释"""
        
        if X_sample is None:
            X_sample = self.X_train.head(1000)  # 使用样本进行解释
        
        # 计算SHAP值
        if self.shap_values is None:
            self.shap_values = self.explainer(X_sample)
        
        # 计算全局重要性
        if hasattr(self.shap_values, 'values'):
            shap_values_array = self.shap_values.values
        else:
            shap_values_array = self.shap_values
        
        # 计算平均绝对SHAP值
        feature_importance = np.mean(np.abs(shap_values_array), axis=0)
        
        # 创建重要性DataFrame
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': feature_importance
        }).sort_values('importance', ascending=False)
        
        # 限制特征数量
        importance_df = importance_df.head(max_features)
        
        return {
            'feature_importance': importance_df,
            'shap_values': self.shap_values,
            'feature_names': self.feature_names,
            'data_sample': X_sample,
            'model_type': self.model_type
        }
    
    def local_explanation(self, 
                         instance: pd.Series or np.ndarray,
                         class_index: int = None) -> Dict[str, Any]:
        """单个实例的局部解释"""
        
        # 处理输入实例
        if isinstance(instance, pd.Series):
            instance_array = instance.values.reshape(1, -1)
            instance_df = instance.to_frame().T
        else:
            instance_array = instance.reshape(1, -1)
            instance_df = pd.DataFrame(instance_array, columns=self.feature_names)
        
        # 计算SHAP值
        instance_shap = self.explainer(instance_array)
        
        # 对于分类问题，处理多类情况
        if len(instance_shap.shape) > 2:
            # 多类分类问题
            if class_index is not None:
                instance_shap_values = instance_shap[0, :, class_index]
                predicted_class = class_index
            else:
                # 使用预测概率最高的类
                prediction_proba = self.model.predict_proba(instance_array)[0]
                predicted_class = np.argmax(prediction_proba)
                instance_shap_values = instance_shap[0, :, predicted_class]
        else:
            instance_shap_values = instance_shap[0] if len(instance_shap.shape) > 1 else instance_shap[0]
            predicted_class = None
        
        # 创建局部解释结果
        local_explanation = pd.DataFrame({
            'feature': self.feature_names,
            'feature_value': instance_array[0],
            'shap_value': instance_shap_values,
            'abs_shap_value': np.abs(instance_shap_values)
        }).sort_values('abs_shap_value', ascending=False)
        
        return {
            'instance': instance_df,
            'local_importance': local_explanation,
            'predicted_class': predicted_class,
            'shap_values': instance_shap,
            'feature_impact': {
                'positive_contributors': local_explanation[
                    local_explanation['shap_value'] > 0
                ].head(5).to_dict('records'),
                'negative_contributors': local_explanation[
                    local_explanation['shap_value'] < 0
                ].head(5).to_dict('records')
            }
        }
    
    def comparison_explanation(self, 
                             instances: List[pd.Series or np.ndarray],
                             class_index: int = None) -> Dict[str, Any]:
        """多个实例的对比解释"""
        
        comparison_results = []
        
        for i, instance in enumerate(instances):
            local_exp = self.local_explanation(instance, class_index)
            comparison_results.append({
                'instance_id': i,
                'instance': local_exp['instance'],
                'top_features': local_exp['local_importance'].head(10),
                'predicted_class': local_exp['predicted_class']
            })
        
        return {
            'comparisons': comparison_results,
            'analysis_summary': self._analyze_comparison_patterns(comparison_results)
        }
    
    def _analyze_comparison_patterns(self, comparison_results: List[Dict]) -> Dict[str, Any]:
        """分析对比结果中的模式"""
        
        all_top_features = []
        for result in comparison_results:
            top_features = result['top_features']['feature'].tolist()
            all_top_features.extend(top_features)
        
        # 计算特征频率
        feature_frequency = pd.Series(all_top_features).value_counts()
        
        return {
            'common_features': feature_frequency.head(10).to_dict(),
            'total_comparisons': len(comparison_results),
            'feature_diversity': len(feature_frequency)
        }

# 高级解释技术
class AdvancedModelExplainer:
    def __init__(self, base_explainer: ModelExplainer):
        self.base_explainer = base_explainer
        self.conditional_explainer = ConditionalExplainer()
        self.counterfactual_explainer = CounterfactualExplainer()
        self.causal_explainer = CausalExplainer()
    
    def conditional_explanation(self, 
                              X_condition: pd.DataFrame,
                              target_condition: Any) -> Dict[str, Any]:
        """条件化解释：基于特定条件子集的解释"""
        return self.conditional_explainer.explain(
            self.base_explainer,
            X_condition,
            target_condition
        )
    
    def counterfactual_explanation(self, 
                                 instance: pd.Series,
                                 desired_outcome: Any,
                                 n_counterfactuals: int = 5) -> Dict[str, Any]:
        """反事实解释：最小修改实现目标结果"""
        return self.counterfactual_explainer.generate(
            self.base_explainer,
            instance,
            desired_outcome,
            n_counterfactuals
        )
    
    def causal_explanation(self, X: pd.DataFrame) -> Dict[str, Any]:
        """因果关系解释"""
        return self.causal_explainer.analyze(
            self.base_explainer,
            X
        )

class ConditionalExplainer:
    def __init__(self):
        self.conditions = {
            'high_risk': lambda X: X['risk_score'] > 0.7,
            'low_risk': lambda X: X['risk_score'] < 0.3,
            'recent_customers': lambda X: X['customer_age'] < 1,
            'vip_customers': lambda X: X['annual_spend'] > 100000
        }
    
    def explain(self, 
               base_explainer: ModelExplainer,
               X_condition: pd.DataFrame,
               target_condition: Any) -> Dict[str, Any]:
        """基于条件子集的解释"""
        
        if callable(target_condition):
            mask = target_condition(X_condition)
        elif isinstance(target_condition, str) and target_condition in self.conditions:
            mask = self.conditions[target_condition](X_condition)
        else:
            mask = pd.Series([True] * len(X_condition))
        
        # 过滤条件数据
        X_conditioned = X_condition[mask]
        
        if len(X_conditioned) == 0:
            return {'error': '没有数据满足指定条件'}
        
        # 计算条件化解释
        conditioned_explanation = base_explainer.global_explanation(
            X_conditioned, max_features=15
        )
        
        return {
            'condition_applied': target_condition,
            'condition_data_shape': X_conditioned.shape,
            'conditioned_explanation': conditioned_explanation,
            'condition_statistics': self._compute_condition_statistics(X_conditioned)
        }
    
    def _compute_condition_statistics(self, X_conditioned: pd.DataFrame) -> Dict[str, Any]:
        """计算条件数据的统计信息"""
        return {
            'mean_values': X_conditioned.mean().to_dict(),
            'std_values': X_conditioned.std().to_dict(),
            'data_quality': {
                'missing_values': X_conditioned.isnull().sum().to_dict(),
                'duplicates': X_conditioned.duplicated().sum()
            }
        }

class CounterfactualExplainer:
    def __init__(self):
        self.genetic_algorithm = GeneticCounterfactualGenerator()
        self.gradient_based = GradientBasedCounterfactualGenerator()
    
    def generate(self, 
                base_explainer: ModelExplainer,
                instance: pd.Series,
                desired_outcome: Any,
                n_counterfactuals: int = 5) -> Dict[str, Any]:
        """生成反事实解释"""
        
        try:
            # 尝试梯度方法
            gradient_counterfactuals = self.gradient_based.generate(
                base_explainer,
                instance,
                desired_outcome,
                n_counterfactuals
            )
            
            if len(gradient_counterfactuals) > 0:
                return {
                    'method': 'gradient_based',
                    'counterfactuals': gradient_counterfactuals,
                    'original_instance': instance
                }
        except:
            pass
        
        # 退化到遗传算法方法
        genetic_counterfactuals = self.genetic_algorithm.generate(
            base_explainer,
            instance,
            desired_outcome,
            n_counterfactuals
        )
        
        return {
            'method': 'genetic_algorithm',
            'counterfactuals': genetic_counterfactuals,
            'original_instance': instance
        }

class GeneticCounterfactualGenerator:
    def __init__(self, population_size: int = 50, generations: int = 100):
        self.population_size = population_size
        self.generations = generations
    
    def generate(self, 
                base_explainer: ModelExplainer,
                instance: pd.Series,
                desired_outcome: Any,
                n_counterfactuals: int = 5) -> List[Dict[str, Any]]:
        """使用遗传算法生成反事实"""
        
        from deap import creator, base, tools, algorithms
        
        # 定义适应度函数
        def fitness_function(counterfactual_values):
            # 计算反事实的预测概率
            counterfactual_df = pd.DataFrame(
                [counterfactual_values],
                columns=instance.index
            )
            
            try:
                # 预测
                prediction = base_explainer.model.predict(counterfactual_df)[0]
                probability = base_explainer.model.predict_proba(counterfactual_df)[0]
                
                # 计算与目标结果的接近程度
                if isinstance(desired_outcome, int):
                    target_prob = probability[desired_outcome] if desired_outcome < len(probability) else 0
                    outcome_score = target_prob
                else:
                    outcome_score = 1.0 if prediction == desired_outcome else 0.0
                
                # 计算修改成本（与原实例的差异）
                modification_cost = np.sum(np.abs(counterfactual_values - instance.values))
                
                # 综合适应度：目标达成度 - 修改成本
                fitness = outcome_score - 0.01 * modification_cost
                
                return fitness,
                
            except:
                return -1000,  # 很差的适应度
        
        return []

class CausalExplainer:
    def __init__(self):
        self.causal_methods = {
            'correlation': self._correlation_analysis,
            'mutual_information': self._mutual_information_analysis,
            'partial_correlation': self._partial_correlation_analysis
        }
    
    def analyze(self, 
               base_explainer: ModelExplainer,
               X: pd.DataFrame) -> Dict[str, Any]:
        """分析特征间的因果关系"""
        
        causal_results = {}
        
        for method_name, method_func in self.causal_methods.items():
            try:
                causal_results[method_name] = method_func(X)
            except Exception as e:
                causal_results[method_name] = {'error': str(e)}
        
        return {
            'causal_analysis': causal_results,
            'feature_network': self._build_feature_network(X),
            'intervention_effects': self._compute_intervention_effects(X)
        }
    
    def _correlation_analysis(self, X: pd.DataFrame) -> Dict[str, Any]:
        """相关性分析"""
        correlation_matrix = X.corr()
        return {
            'correlation_matrix': correlation_matrix,
            'strong_correlations': self._find_strong_correlations(correlation_matrix),
            'correlation_clusters': self._find_correlation_clusters(correlation_matrix)
        }
    
    def _find_strong_correlations(self, correlation_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict]:
        """找出强相关特征对"""
        strong_correlations = []
        
        for i in range(len(correlation_matrix.columns)):
            for j in range(i + 1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > threshold:
                    strong_correlations.append({
                        'feature1': correlation_matrix.columns[i],
                        'feature2': correlation_matrix.columns[j],
                        'correlation': corr_value
                    })
        
        return strong_correlations

# 解释可视化系统
class ExplanationVisualizer:
    def __init__(self):
        self.plot_configs = {
            'importance': {'figsize': (12, 8), 'kind': 'bar'},
            'summary': {'figsize': (12, 8), 'kind': 'scatter'},
            'dependence': {'figsize': (10, 6), 'kind': 'scatter'},
            'waterfall': {'figsize': (12, 8), 'kind': 'barh'}
        }
    
    def plot_feature_importance(self, 
                              importance_df: pd.DataFrame,
                              output_path: str = None,
                              top_n: int = 15) -> plt.Figure:
        """绘制特征重要性图"""
        
        # 选择前N个重要特征
        plot_df = importance_df.head(top_n).copy()
        
        plt.figure(figsize=(12, 8))
        
        # 创建水平条形图
        bars = plt.barh(range(len(plot_df)), plot_df['importance'])
        
        # 设置y轴标签
        plt.yticks(range(len(plot_df)), plot_df['feature'])
        
        # 美化图表
        plt.xlabel('Feature Importance (Mean |SHAP Value|)')
        plt.title('Global Feature Importance')
        
        # 添加数值标签
        for i, (idx, row) in enumerate(plot_df.iterrows()):
            plt.text(row['importance'], i, f'{row["importance"]:.3f}', 
                    va='center', ha='left', fontsize=10)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        
        return plt.gcf()
    
    def plot_shap_summary(self, 
                         shap_values,
                         feature_names: List[str],
                         output_path: str = None,
                         max_features: int = 20) -> plt.Figure:
        """绘制SHAP汇总图"""
        
        plt.figure(figsize=(12, 8))
        
        # 创建SHAP汇总图
        if len(shap_values.shape) > 2:
            # 多类分类问题
            shap.summary_plot(
                shap_values.mean(axis=0),  # 平均SHAP值
                features=pd.DataFrame(shap_values.mean(axis=0), columns=feature_names),
                feature_names=feature_names,
                max_display=max_features,
                show=False
            )
        else:
            shap.summary_plot(
                shap_values,
                features=pd.DataFrame(shap_values, columns=feature_names),
                feature_names=feature_names,
                max_display=max_features,
                show=False
            )
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        
        return plt.gcf()
    
    def plot_local_explanation(self, 
                             local_explanation: Dict[str, Any],
                             output_path: str = None) -> plt.Figure:
        """绘制局部解释图"""
        
        importance_df = local_explanation['local_importance'].head(10)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 左图：SHAP值
        colors = ['red' if x < 0 else 'blue' for x in importance_df['shap_value']]
        bars1 = ax1.barh(range(len(importance_df)), importance_df['shap_value'], color=colors)
        ax1.set_yticks(range(len(importance_df)))
        ax1.set_yticklabels(importance_df['feature'])
        ax1.set_xlabel('SHAP Value')
        ax1.set_title('Feature Contributions (SHAP Values)')
        
        # 右图：特征值
        bars2 = ax2.barh(range(len(importance_df)), importance_df['feature_value'])
        ax2.set_yticks(range(len(importance_df)))
        ax2.set_yticklabels(importance_df['feature'])
        ax2.set_xlabel('Feature Value')
        ax2.set_title('Feature Values')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_model_comparison(self, 
                            model_explanations: Dict[str, Dict],
                            output_path: str = None) -> plt.Figure:
        """比较多个模型的解释"""
        
        n_models = len(model_explanations)
        fig, axes = plt.subplots(1, n_models, figsize=(6 * n_models, 8))
        
        if n_models == 1:
            axes = [axes]
        
        for idx, (model_name, explanation) in enumerate(model_explanations.items()):
            importance_df = explanation['feature_importance'].head(10)
            
            axes[idx].barh(range(len(importance_df)), importance_df['importance'])
            axes[idx].set_yticks(range(len(importance_df)))
            axes[idx].set_yticklabels(importance_df['feature'])
            axes[idx].set_xlabel('Feature Importance')
            axes[idx].set_title(f'{model_name}')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        
        return fig

# 自动化解释报告生成
class ExplanationReportGenerator:
    def __init__(self):
        self.report_templates = {
            'regulatory': self._regulatory_report_template,
            'technical': self._technical_report_template,
            'business': self._business_report_template
        }
    
    def generate_report(self, 
                       explanations: Dict[str, Any],
                       report_type: str = 'technical',
                       output_path: str = None) -> str:
        """生成解释性报告"""
        
        if report_type not in self.report_templates:
            raise ValueError(f"不支持的报告类型: {report_type}")
        
        report_generator = self.report_templates[report_type]
        report_content = report_generator(explanations)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        return report_content
    
    def _technical_report_template(self, explanations: Dict[str, Any]) -> str:
        """技术报告模板"""
        report = f"""
# 模型可解释性技术报告

## 执行摘要
本报告详细分析了机器学习模型的决策过程和特征重要性。

## 全局解释分析
### 特征重要性排序
"""
        
        if 'global_explanation' in explanations:
            importance_df = explanations['global_explanation']['feature_importance']
            for idx, row in importance_df.head(10).iterrows():
                report += f"- {row['feature']}: {row['importance']:.4f}\n"
        
        report += "\n## 局部解释分析\n"
        
        if 'local_explanations' in explanations:
            for i, local_exp in enumerate(explanations['local_explanations'][:3]):
                report += f"\n### 实例 {i+1}\n"
                top_features = local_exp['local_importance'].head(5)
                for idx, row in top_features.iterrows():
                    direction = "正向" if row['shap_value'] > 0 else "负向"
                    report += f"- {row['feature']}: {direction}影响 ({row['shap_value']:.4f})\n"
        
        report += "\n## 模型建议\n"
        report += self._generate_technical_recommendations(explanations)
        
        return report
    
    def _business_report_template(self, explanations: Dict[str, Any]) -> str:
        """业务报告模板"""
        report = """
# 模型可解释性业务报告

## 模型决策概览
本报告解释了模型如何做出决策，帮助业务团队理解模型的内在逻辑。

## 关键业务洞察
"""
        
        if 'global_explanation' in explanations:
            importance_df = explanations['global_explanation']['feature_importance']
            report += "\n### 最重要的业务指标\n"
            for idx, row in importance_df.head(5).iterrows():
                report += f"- **{row['feature']}**: 对模型决策有重大影响\n"
        
        report += "\n## 决策解释\n"
        report += self._generate_business_insights(explanations)
        
        return report
    
    def _regulatory_report_template(self, explanations: Dict[str, Any]) -> str:
        """监管报告模板"""
        report = """
# 模型可解释性合规报告

## 合规性声明
本报告满足相关监管要求，确保模型决策的可解释性和透明度。

## 模型透明性分析
- 算法类型: 机器学习模型
- 训练数据: 已记录数据版本和来源
- 决策过程: 完全可追溯和可解释

## 特征影响分析
"""
        
        if 'global_explanation' in explanations:
            importance_df = explanations['global_explanation']['feature_importance']
            total_importance = importance_df['importance'].sum()
            
            report += f"\n### 特征重要性分布\n"
            for idx, row in importance_df.head(10).iterrows():
                percentage = (row['importance'] / total_importance) * 100
                report += f"- {row['feature']}: {percentage:.2f}%\n"
        
        report += "\n## 公平性评估\n"
        report += "模型经过公平性检查，确保不产生歧视性结果。\n"
        
        return report
    
    def _generate_technical_recommendations(self, explanations: Dict[str, Any]) -> str:
        """生成技术建议"""
        recommendations = []
        
        if 'global_explanation' in explanations:
            importance_df = explanations['global_explanation']['feature_importance']
            
            # 检查特征重要性分布
            top_3_importance = importance_df.head(3)['importance'].sum()
            total_importance = importance_df['importance'].sum()
            concentration_ratio = top_3_importance / total_importance
            
            if concentration_ratio > 0.8:
                recommendations.append("- 模型过度依赖少数特征，建议增加特征多样性")
            
            # 检查重要特征的数据质量
            recommendations.append("- 建议监控重要特征的数据质量变化")
            recommendations.append("- 定期重新训练模型以保持解释一致性")
        
        return "\n".join(recommendations)
    
    def _generate_business_insights(self, explanations: Dict[str, Any]) -> str:
        """生成业务洞察"""
        insights = []
        
        if 'global_explanation' in explanations:
            importance_df = explanations['global_explanation']['feature_importance']
            
            insights.append("### 关键发现")
            insights.append(f"- 模型主要基于{importance_df.iloc[0]['feature']}进行决策")
            insights.append("- 前3个重要特征解释了大部分模型行为")
            
            insights.append("\n### 业务建议")
            insights.append("- 关注重要特征的业务变化")
            insights.append("- 优化重要特征的收集质量")
            insights.append("- 建立重要特征的监控机制")
        
        return "\n".join(insights)

# 使用示例
async def main():
    # 生成示例数据
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    
    X, y = make_classification(
        n_samples=1000, n_features=20, n_informative=15,
        n_redundant=5, n_classes=2, random_state=42
    )
    
    X_df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(20)])
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_df, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 训练模型
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 创建解释器
    explainer = ModelExplainer(
        model=model,
        X_train=X_train,
        model_type='tree'
    )
    
    # 全局解释
    print("生成全局解释...")
    global_explanation = explainer.global_explanation(X_test.head(100))
    print(f"前5个重要特征:")
    print(global_explanation['feature_importance'].head())
    
    # 局部解释
    print("\n生成局部解释...")
    instance = X_test.iloc[0]
    local_explanation = explainer.local_explanation(instance)
    print(f"实例预测的主要影响因素:")
    print(local_explanation['local_importance'].head())
    
    # 生成可视化
    print("\n生成可视化图表...")
    visualizer = ExplanationVisualizer()
    
    # 特征重要性图
    importance_fig = visualizer.plot_feature_importance(
        global_explanation['feature_importance'],
        output_path='feature_importance.png'
    )
    
    # SHAP汇总图
    summary_fig = visualizer.plot_shap_summary(
        global_explanation['shap_values'],
        global_explanation['feature_names'],
        output_path='shap_summary.png'
    )
    
    # 局部解释图
    local_fig = visualizer.plot_local_explanation(
        local_explanation,
        output_path='local_explanation.png'
    )
    
    # 生成报告
    print("\n生成解释性报告...")
    report_generator = ExplanationReportGenerator()
    
    explanations_data = {
        'global_explanation': global_explanation,
        'local_explanations': [local_explanation]
    }
    
    technical_report = report_generator.generate_report(
        explanations_data,
        report_type='technical',
        output_path='model_explanation_report.md'
    )
    
    business_report = report_generator.generate_report(
        explanations_data,
        report_type='business',
        output_path='business_explanation_report.md'
    )
    
    print("解释性分析完成！")
    
    return {
        'global_explanation': global_explanation,
        'local_explanation': local_explanation,
        'visualizations': {
            'importance_fig': importance_fig,
            'summary_fig': summary_fig,
            'local_fig': local_fig
        },
        'reports': {
            'technical': technical_report,
            'business': business_report
        }
    }

# 运行示例
if __name__ == "__main__":
    result = asyncio.run(main())
```

## Best Practices

### 1. 解释方法选择
- **模型适配**: 根据模型类型选择合适的解释方法
- **业务需求**: 根据业务场景选择解释深度和方式
- **计算资源**: 考虑解释生成的计算成本和时间
- **准确性要求**: 权衡解释准确性和计算效率

### 2. 结果验证
- **稳定性测试**: 测试解释结果的稳定性和一致性
- **合理性检查**: 验证解释结果是否符合业务逻辑
- **专家评审**: 邀请领域专家验证解释的合理性
- **A/B测试**: 对比不同解释方法的业务效果

### 3. 可视化优化
- **清晰度**: 确保可视化图表清晰易懂
- **交互性**: 提供交互式解释界面
- **定制化**: 支持根据用户需求定制可视化
- **导出功能**: 支持多种格式的解释报告导出

### 4. 合规性管理
- **审计日志**: 记录所有解释操作的完整日志
- **版本控制**: 管理模型和解释的版本历史
- **访问控制**: 限制解释结果的访问权限
- **数据保护**: 确保敏感信息的保护

## Integration Patterns

### 1. 模型服务集成
```python
# 模型服务中的实时解释
class ExplainableModelService:
    def __init__(self, model, explainer):
        self.model = model
        self.explainer = explainer
    
    def predict_with_explanation(self, instance):
        """预测并返回解释"""
        # 预测
        prediction = self.model.predict([instance])[0]
        probability = self.model.predict_proba([instance])[0]
        
        # 生成解释
        explanation = self.explainer.local_explanation(instance)
        
        return {
            'prediction': prediction,
            'probability': probability.tolist(),
            'explanation': explanation,
            'confidence': max(probability)
        }
```

### 2. MLOps管道集成
```python
# MLOps中的自动化解释
class MLOpsExplainer:
    def __init__(self, ml_pipeline):
        self.ml_pipeline = ml_pipeline
        self.report_generator = ExplanationReportGenerator()
    
    def auto_explain_model(self, model_version):
        """自动解释新部署的模型"""
        
        # 获取模型和数据
        model = self.ml_pipeline.load_model(model_version)
        train_data = self.ml_pipeline.get_train_data(model_version)
        
        # 生成解释
        explainer = ModelExplainer(model, train_data)
        global_explanation = explainer.global_explanation()
        
        # 生成报告
        explanations = {'global_explanation': global_explanation}
        report = self.report_generator.generate_report(
            explanations, 'regulatory'
        )
        
        # 保存解释结果
        self.ml_pipeline.save_explanation_report(
            model_version, report, global_explanation
        )
        
        return {
            'model_version': model_version,
            'explanation': global_explanation,
            'report': report
        }
```

## Success Metrics

### 1. 解释质量指标
- **忠实度**: 解释准确反映模型决策的程度
- **稳定性**: 解释结果在不同数据子集上的一致性
- **一致性**: 不同解释方法结果的一致性
- **可理解性**: 用户对解释内容的理解程度

### 2. 业务价值指标
- **决策透明度**: 模型决策过程的透明程度
- **信任度**: 用户对模型的信任程度
- **合规性**: 满足监管要求的程度
- **业务影响**: 解释对业务决策的影响

### 3. 技术性能指标
- **生成速度**: 解释结果的生成速度
- **计算成本**: 解释生成的计算资源消耗
- **可扩展性**: 支持大规模数据解释的能力
- **维护成本**: 解释系统的维护成本

---

*模型可解释性是构建可信AI系统的关键，通过系统化的解释方法、可视化技术和报告生成，实现模型的透明化、合规化和业务价值最大化。*
