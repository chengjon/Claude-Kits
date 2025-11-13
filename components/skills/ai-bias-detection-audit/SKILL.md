---
name: ai-bias-detection-audit
description: "AI偏差检测与公平性审计专家，精通公平性度量方法、偏差检测算法和公平性优化技术。构建偏差监控体系、公平性评估工具和合规报告系统，处理AI伦理、偏差检测和公平性保障。使用PROACTIVELY进行偏差检测、公平性审计或AI伦理合规。"
---

# AI偏差检测审计技能

## When to Use
Use this skill when implementing AI fairness monitoring systems, conducting bias audits for ML models, developing algorithmic accountability frameworks, implementing ethical AI practices, or building regulatory compliance systems for AI bias. Essential for financial services, healthcare, hiring systems, criminal justice, and any AI application requiring fairness validation.

## Core Concepts

### 1. 公平性度量方法
- **统计平等**: 不同群体间正例率的一致性
- **机会均等**: 不同群体间的真正例率相等
- **预测等值**: 不同群体的预测值分布一致
- **个体公平性**: 相似个体获得相似预测结果

### 2. 偏差检测算法
- **群体偏差检测**: 分析群体间的系统性偏差
- **个体偏差检测**: 识别个体层面的预测偏差
- **时间序列偏差**: 监控偏差随时间的变化
- **交叉偏差**: 多维度交叉群体的偏差分析

### 3. 公平性优化技术
- **训练数据重采样**: 平衡不同群体的训练数据
- **对抗性去偏**: 使用对抗训练移除偏差
- **公平性约束**: 在优化中嵌入公平性约束
- **后处理调整**: 对预测结果进行后处理

### 4. 审计和合规系统
- **自动化审计**: 定期自动执行偏差检测
- **合规报告**: 生成标准化的合规审计报告
- **风险评估**: 评估偏差导致的潜在风险
- **改进建议**: 提供偏差缓解的改进建议

## Code Examples

### AI偏差检测核心系统
```python
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.metrics import confusion_matrix, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

class FairnessMetric(Enum):
    """公平性指标枚举"""
    STATISTICAL_PARITY = "statistical_parity"
    EQUALIZED_OPPORTUNITY = "equalized_opportunity"
    EQUALIZED_ODDS = "equalized_odds"
    PREDICTIVE_PARITY = "predictive_parity"
    INDIVIDUAL_FAIRNESS = "individual_fairness"
    CALIBRATION = "calibration"

@dataclass
class BiasDetectionResult:
    """偏差检测结果"""
    metric_name: str
    bias_score: float
    threshold: float
    is_fair: bool
    group_statistics: Dict[str, float]
    recommendations: List[str]
    confidence_interval: Optional[Tuple[float, float]] = None

@dataclass
class AuditReport:
    """审计报告"""
    audit_id: str
    model_name: str
    audit_date: str
    protected_attributes: List[str]
    overall_bias_score: float
    findings: List[BiasDetectionResult]
    risk_level: str
    recommendations: List[str]
    compliance_status: Dict[str, bool]

class BiasDetector:
    """偏差检测器"""
    
    def __init__(self, protected_attributes: List[str]):
        self.protected_attributes = protected_attributes
        self.fairness_thresholds = {
            FairnessMetric.STATISTICAL_PARITY: 0.1,
            FairnessMetric.EQUALIZED_OPPORTUNITY: 0.1,
            FairnessMetric.EQUALIZED_ODDS: 0.1,
            FairnessMetric.PREDICTIVE_PARITY: 0.1,
            FairnessMetric.CALIBRATION: 0.05
        }
    
    def detect_bias(self, 
                   y_true: np.ndarray,
                   y_pred: np.ndarray,
                   y_pred_proba: Optional[np.ndarray] = None,
                   protected_attributes: Optional[pd.DataFrame] = None) -> List[BiasDetectionResult]:
        """检测模型偏差"""
        
        if protected_attributes is None:
            protected_attributes = pd.DataFrame({attr: np.ones(len(y_true)) for attr in self.protected_attributes})
        
        results = []
        
        # 计算各种公平性指标
        for metric in FairnessMetric:
            result = self._compute_fairness_metric(
                metric, y_true, y_pred, y_pred_proba, protected_attributes
            )
            results.append(result)
        
        return results
    
    def _compute_fairness_metric(self, 
                               metric: FairnessMetric,
                               y_true: np.ndarray,
                               y_pred: np.ndarray,
                               y_pred_proba: Optional[np.ndarray],
                               protected_attributes: pd.DataFrame) -> BiasDetectionResult:
        """计算单个公平性指标"""
        
        threshold = self.fairness_thresholds[metric]
        group_statistics = {}
        recommendations = []
        
        if metric == FairnessMetric.STATISTICAL_PARITY:
            bias_score, group_stats, recs = self._statistical_parity(y_pred, protected_attributes)
        elif metric == FairnessMetric.EQUALIZED_OPPORTUNITY:
            bias_score, group_stats, recs = self._equalized_opportunity(y_true, y_pred, protected_attributes)
        elif metric == FairnessMetric.EQUALIZED_ODDS:
            bias_score, group_stats, recs = self._equalized_odds(y_true, y_pred, protected_attributes)
        elif metric == FairnessMetric.PREDICTIVE_PARITY:
            bias_score, group_stats, recs = self._predictive_parity(y_true, y_pred, protected_attributes)
        elif metric == FairnessMetric.CALIBRATION:
            bias_score, group_stats, recs = self._calibration(y_true, y_pred_proba, protected_attributes)
        elif metric == FairnessMetric.INDIVIDUAL_FAIRNESS:
            bias_score, group_stats, recs = self._individual_fairness(y_pred, protected_attributes)
        else:
            bias_score, group_stats, recs = 1.0, {}, []
        
        group_statistics = group_stats
        recommendations = recs
        
        # 计算置信区间
        confidence_interval = self._compute_confidence_interval(bias_score, len(y_true))
        
        return BiasDetectionResult(
            metric_name=metric.value,
            bias_score=bias_score,
            threshold=threshold,
            is_fair=bias_score <= threshold,
            group_statistics=group_statistics,
            recommendations=recommendations,
            confidence_interval=confidence_interval
        )
    
    def _statistical_parity(self, 
                           y_pred: np.ndarray, 
                           protected_attributes: pd.DataFrame) -> Tuple[float, Dict[str, float], List[str]]:
        """统计平等（Demographic Parity）"""
        
        group_stats = {}
        positive_rates = {}
        
        for attribute in self.protected_attributes:
            for group_value in protected_attributes[attribute].unique():
                mask = protected_attributes[attribute] == group_value
                group_pred = y_pred[mask]
                
                positive_rate = np.mean(group_pred)
                positive_rates[f"{attribute}_{group_value}"] = positive_rate
                group_stats[f"{attribute}_{group_value}_positive_rate"] = positive_rate
        
        # 计算最大差异
        if len(positive_rates) >= 2:
            max_diff = max(positive_rates.values()) - min(positive_rates.values())
            bias_score = max_diff
        else:
            bias_score = 0.0
        
        recommendations = []
        if bias_score > 0.1:
            recommendations.append("存在统计平等偏差，建议重新平衡训练数据")
            recommendations.append("检查数据收集过程是否存在系统性偏差")
        
        return bias_score, group_stats, recommendations
    
    def _equalized_opportunity(self, 
                              y_true: np.ndarray,
                              y_pred: np.ndarray, 
                              protected_attributes: pd.DataFrame) -> Tuple[float, Dict[str, float], List[str]]:
        """机会均等（Equal Opportunity）"""
        
        group_stats = {}
        true_positive_rates = {}
        
        # 只考虑正例样本
        positive_mask = y_true == 1
        y_true_pos = y_true[positive_mask]
        y_pred_pos = y_pred[positive_mask]
        protected_pos = protected_attributes[positive_mask]
        
        for attribute in self.protected_attributes:
            for group_value in protected_pos[attribute].unique():
                mask = protected_pos[attribute] == group_value
                group_true = y_true_pos[mask]
                group_pred = y_pred_pos[mask]
                
                if len(group_true) > 0:
                    tpr = np.mean(group_pred)
                    true_positive_rates[f"{attribute}_{group_value}"] = tpr
                    group_stats[f"{attribute}_{group_value}_tpr"] = tpr
        
        # 计算TPR差异
        if len(true_positive_rates) >= 2:
            max_diff = max(true_positive_rates.values()) - min(true_positive_rates.values())
            bias_score = max_diff
        else:
            bias_score = 0.0
        
        recommendations = []
        if bias_score > 0.1:
            recommendations.append("存在机会均等偏差，建议调整决策阈值")
            recommendations.append("考虑使用公平性约束的正则化方法")
        
        return bias_score, group_stats, recommendations
    
    def _equalized_odds(self, 
                       y_true: np.ndarray,
                       y_pred: np.ndarray, 
                       protected_attributes: pd.DataFrame) -> Tuple[float, Dict[str, float], List[str]]:
        """等概率（Equalized Odds）"""
        
        # 分别计算TPR和FPR
        tpr_bias_score, tpr_stats, tpr_recs = self._equalized_opportunity(y_true, y_pred, protected_attributes)
        fpr_bias_score, fpr_stats, fpr_recs = self._equalized_odds_fpr(y_true, y_pred, protected_attributes)
        
        # 组合偏差分数
        bias_score = max(tpr_bias_score, fpr_bias_score)
        group_stats = {**tpr_stats, **fpr_stats}
        recommendations = list(set(tpr_recs + fpr_recs))
        
        return bias_score, group_stats, recommendations
    
    def _equalized_odds_fpr(self, 
                           y_true: np.ndarray,
                           y_pred: np.ndarray, 
                           protected_attributes: pd.DataFrame) -> Tuple[float, Dict[str, float], List[str]]:
        """计算等概率的FPR部分"""
        
        group_stats = {}
        false_positive_rates = {}
        
        # 只考虑负例样本
        negative_mask = y_true == 0
        y_true_neg = y_true[negative_mask]
        y_pred_neg = y_pred[negative_mask]
        protected_neg = protected_attributes[negative_mask]
        
        for attribute in self.protected_attributes:
            for group_value in protected_neg[attribute].unique():
                mask = protected_neg[attribute] == group_value
                group_true = y_true_neg[mask]
                group_pred = y_pred_neg[mask]
                
                if len(group_true) > 0:
                    fpr = np.mean(group_pred)
                    false_positive_rates[f"{attribute}_{group_value}"] = fpr
                    group_stats[f"{attribute}_{group_value}_fpr"] = fpr
        
        # 计算FPR差异
        if len(false_positive_rates) >= 2:
            max_diff = max(false_positive_rates.values()) - min(false_positive_rates.values())
            bias_score = max_diff
        else:
            bias_score = 0.0
        
        return bias_score, group_stats, []
    
    def _predictive_parity(self, 
                          y_true: np.ndarray,
                          y_pred: np.ndarray, 
                          protected_attributes: pd.DataFrame) -> Tuple[float, Dict[str, float], List[str]]:
        """预测等值（Predictive Parity）"""
        
        group_stats = {}
        precision_scores = {}
        
        for attribute in self.protected_attributes:
            for group_value in protected_attributes[attribute].unique():
                mask = protected_attributes[attribute] == group_value
                group_true = y_true[mask]
                group_pred = y_pred[mask]
                
                if np.sum(group_pred) > 0:
                    precision = np.sum((group_pred == 1) & (group_true == 1)) / np.sum(group_pred)
                    precision_scores[f"{attribute}_{group_value}"] = precision
                    group_stats[f"{attribute}_{group_value}_precision"] = precision
        
        # 计算精确率差异
        if len(precision_scores) >= 2:
            max_diff = max(precision_scores.values()) - min(precision_scores.values())
            bias_score = max_diff
        else:
            bias_score = 0.0
        
        recommendations = []
        if bias_score > 0.1:
            recommendations.append("存在预测等值偏差，建议重新校准模型")
        
        return bias_score, group_stats, recommendations
    
    def _calibration(self, 
                    y_true: np.ndarray,
                    y_pred_proba: np.ndarray, 
                    protected_attributes: pd.DataFrame) -> Tuple[float, Dict[str, float], List[str]]:
        """校准性分析"""
        
        if y_pred_proba is None:
            return 1.0, {}, ["需要预测概率进行校准分析"]
        
        group_stats = {}
        calibration_scores = {}
        
        for attribute in self.protected_attributes:
            for group_value in protected_attributes[attribute].unique():
                mask = protected_attributes[attribute] == group_value
                group_true = y_true[mask]
                group_proba = y_pred_proba[mask]
                
                if len(group_proba) > 0:
                    # 计算校准分数（简化版本）
                    calibration_error = np.abs(np.mean(group_proba) - np.mean(group_true))
                    calibration_scores[f"{attribute}_{group_value}"] = calibration_error
                    group_stats[f"{attribute}_{group_value}_calibration_error"] = calibration_error
        
        # 计算校准差异
        if len(calibration_scores) >= 2:
            max_diff = max(calibration_scores.values()) - min(calibration_scores.values())
            bias_score = max_diff
        else:
            bias_score = 0.0
        
        recommendations = []
        if bias_score > 0.05:
            recommendations.append("存在校准偏差，建议进行概率校准")
        
        return bias_score, group_stats, recommendations
    
    def _individual_fairness(self, 
                            y_pred: np.ndarray, 
                            protected_attributes: pd.DataFrame) -> Tuple[float, Dict[str, float], List[str]]:
        """个体公平性分析（简化版本）"""
        
        # 简化的个体公平性：检查相似个体的预测一致性
        # 实际实现中需要定义个体相似性度量
        
        group_stats = {}
        
        for attribute in self.protected_attributes:
            # 计算组内预测方差
            group_variances = []
            for group_value in protected_attributes[attribute].unique():
                mask = protected_attributes[attribute] == group_value
                group_pred = y_pred[mask]
                
                if len(group_pred) > 1:
                    variance = np.var(group_pred)
                    group_variances.append(variance)
                    group_stats[f"{attribute}_{group_value}_prediction_variance"] = variance
            
            if len(group_variances) > 1:
                variance_diff = max(group_variances) - min(group_variances)
                group_stats[f"{attribute}_variance_diff"] = variance_diff
        
        # 计算个体公平性分数
        variance_diffs = [v for k, v in group_stats.items() if 'variance_diff' in k]
        bias_score = max(variance_diffs) if variance_diffs else 0.0
        
        recommendations = []
        if bias_score > 0.1:
            recommendations.append("存在个体公平性问题，建议使用个体公平性约束")
        
        return bias_score, group_stats, recommendations
    
    def _compute_confidence_interval(self, bias_score: float, sample_size: int) -> Optional[Tuple[float, float]]:
        """计算偏差分数的置信区间"""
        
        # 简化的置信区间计算
        # 实际实现中需要考虑具体分布
        standard_error = np.sqrt(bias_score * (1 - bias_score) / sample_size)
        margin_error = 1.96 * standard_error  # 95%置信区间
        
        lower_bound = max(0, bias_score - margin_error)
        upper_bound = min(1, bias_score + margin_error)
        
        return (lower_bound, upper_bound)

# 高级偏差分析工具
class AdvancedBiasAnalyzer:
    """高级偏差分析器"""
    
    def __init__(self, bias_detector: BiasDetector):
        self.bias_detector = bias_detector
    
    def cross_sectional_analysis(self, 
                                y_true: np.ndarray,
                                y_pred: np.ndarray,
                                protected_attributes: pd.DataFrame) -> Dict[str, Any]:
        """交叉群体偏差分析"""
        
        results = {}
        
        # 单属性偏差分析
        for attribute in self.bias_detector.protected_attributes:
            attribute_result = self.bias_detector.detect_bias(
                y_true, y_pred, 
                protected_attributes=protected_attributes[[attribute]]
            )
            results[attribute] = attribute_result
        
        # 多属性交叉分析
        if len(self.bias_detector.protected_attributes) >= 2:
            cross_results = {}
            for i in range(len(self.bias_detector.protected_attributes)):
                for j in range(i + 1, len(self.bias_detector.protected_attributes)):
                    attr1 = self.bias_detector.protected_attributes[i]
                    attr2 = self.bias_detector.protected_attributes[j]
                    
                    # 创建交叉属性
                    cross_attr = protected_attributes[attr1].astype(str) + "_" + protected_attributes[attr2].astype(str)
                    cross_protected = pd.DataFrame({f"{attr1}_{attr2}": cross_attr})
                    
                    cross_result = self.bias_detector.detect_bias(
                        y_true, y_pred, 
                        protected_attributes=cross_protected
                    )
                    cross_results[f"{attr1}_{attr2}"] = cross_result
            
            results['cross_sectional'] = cross_results
        
        return results
    
    def temporal_bias_analysis(self, 
                              y_true: np.ndarray,
                              y_pred: np.ndarray,
                              protected_attributes: pd.DataFrame,
                              timestamps: pd.Series,
                              time_periods: str = 'M') -> Dict[str, Any]:
        """时间序列偏差分析"""
        
        temporal_results = {}
        
        # 按时间段分组
        time_groups = pd.to_datetime(timestamps).dt.to_period(time_periods)
        unique_periods = time_groups.unique()
        
        for period in unique_periods[:10]:  # 限制分析前10个周期
            period_mask = time_groups == period
            
            if np.sum(period_mask) > 10:  # 至少10个样本
                period_result = self.bias_detector.detect_bias(
                    y_true[period_mask], 
                    y_pred[period_mask],
                    protected_attributes=protected_attributes[period_mask]
                )
                temporal_results[str(period)] = period_result
        
        return temporal_results
    
    def bias_heatmap(self, 
                    results: List[BiasDetectionResult],
                    save_path: str = None) -> plt.Figure:
        """生成偏差热图"""
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 提取偏差分数
        metrics = [r.metric_name for r in results]
        scores = [r.bias_score for r in results]
        thresholds = [r.threshold for r in results]
        
        # 创建热图数据
        heatmap_data = pd.DataFrame({
            'Fairness_Metric': metrics,
            'Bias_Score': scores,
            'Threshold': thresholds,
            'Status': ['Fair' if r.is_fair else 'Biased' for r in results]
        })
        
        # 绘制热图
        colors = ['green' if status == 'Fair' else 'red' for status in heatmap_data['Status']]
        bars = ax.barh(heatmap_data['Fairness_Metric'], heatmap_data['Bias_Score'], color=colors, alpha=0.7)
        
        # 添加阈值线
        for i, threshold in enumerate(thresholds):
            ax.axvline(x=threshold, color='orange', linestyle='--', alpha=0.8)
        
        ax.set_xlabel('Bias Score')
        ax.set_title('Fairness Metrics Bias Detection')
        ax.legend(['Fair', 'Biased', 'Threshold'], loc='lower right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig

# 偏差缓解技术
class BiasMitigationTechniques:
    """偏差缓解技术"""
    
    def __init__(self):
        self.mitigation_strategies = {
            'preprocessing': self._preprocessing_mitigation,
            'inprocessing': self._inprocessing_mitigation,
            'postprocessing': self._postprocessing_mitigation
        }
    
    def apply_preprocessing_mitigation(self, 
                                     X: np.ndarray,
                                     y: np.ndarray,
                                     protected_attributes: np.ndarray,
                                     method: str = 'resampling') -> Tuple[np.ndarray, np.ndarray]:
        """预处理偏差缓解"""
        
        if method == 'resampling':
            return self._balanced_resampling(X, y, protected_attributes)
        elif method == 'reweighting':
            return self._reweighting(X, y, protected_attributes)
        else:
            raise ValueError(f"不支持的预处理方法: {method}")
    
    def _balanced_resampling(self, 
                           X: np.ndarray, 
                           y: np.ndarray, 
                           protected_attributes: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """平衡重采样"""
        
        # 简化的平衡重采样
        # 实际实现中需要更复杂的采样策略
        
        unique_protected = np.unique(protected_attributes)
        balanced_indices = []
        
        for protected_value in unique_protected:
            mask = protected_attributes == protected_value
            group_indices = np.where(mask)[0]
            
            # 如果组内样本过少，进行过采样
            if len(group_indices) < len(X) // len(unique_protected) * 0.5:
                # 重复采样
                oversample_indices = np.random.choice(group_indices, size=int(len(X) / len(unique_protected)), replace=True)
                balanced_indices.extend(oversample_indices)
            else:
                balanced_indices.extend(group_indices)
        
        balanced_indices = np.array(balanced_indices)
        np.random.shuffle(balanced_indices)
        
        return X[balanced_indices], y[balanced_indices]
    
    def _reweighting(self, 
                    X: np.ndarray, 
                    y: np.ndarray, 
                    protected_attributes: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """重加权"""
        
        # 计算样本权重
        unique_protected = np.unique(protected_attributes)
        weights = np.ones(len(X))
        
        for protected_value in unique_protected:
            mask = protected_attributes == protected_value
            group_size = np.sum(mask)
            total_size = len(X)
            
            # 权重 = 总样本数 / (组数 * 组内样本数)
            weight = len(unique_protected) * total_size / (group_size * len(unique_protected))
            weights[mask] = weight
        
        return X, y  # 返回原始数据和权重（权重需要在训练时使用）
    
    def apply_inprocessing_mitigation(self, 
                                    model,
                                    X: np.ndarray,
                                    y: np.ndarray,
                                    protected_attributes: np.ndarray,
                                    fairness_constraint: str = 'demographic_parity') -> Any:
        """处理中偏差缓解"""
        
        if fairness_constraint == 'demographic_parity':
            return self._add_fairness_constraint(model, X, y, protected_attributes)
        else:
            # 简化的公平性约束实现
            # 实际实现中需要集成专门的公平性优化算法
            return model.fit(X, y)
    
    def _add_fairness_constraint(self, 
                               model, 
                               X: np.ndarray, 
                               y: np.ndarray, 
                               protected_attributes: np.ndarray):
        """添加公平性约束"""
        
        # 简化的公平性约束实现
        # 实际实现中需要使用专业的公平性优化库
        
        # 训练基础模型
        model.fit(X, y)
        
        # 预测并检查偏差
        y_pred = model.predict(X)
        
        # 简化的偏差校正
        bias_detector = BiasDetector(['protected'])
        protected_df = pd.DataFrame({'protected': protected_attributes})
        bias_results = bias_detector.detect_bias(y, y_pred, protected_attributes=protected_df)
        
        # 如果偏差过大，进行简单校正
        for result in bias_results:
            if not result.is_fair:
                print(f"警告: {result.metric_name} 存在偏差 {result.bias_score:.3f}")
        
        return model
    
    def apply_postprocessing_mitigation(self, 
                                      y_pred: np.ndarray,
                                      protected_attributes: np.ndarray,
                                      method: str = 'threshold_adjustment') -> np.ndarray:
        """后处理偏差缓解"""
        
        if method == 'threshold_adjustment':
            return self._adaptive_thresholding(y_pred, protected_attributes)
        elif method == 'calibration':
            return self._fair_calibration(y_pred, protected_attributes)
        else:
            raise ValueError(f"不支持的后处理方法: {method}")
    
    def _adaptive_thresholding(self, 
                              y_pred: np.ndarray, 
                              protected_attributes: np.ndarray) -> np.ndarray:
        """自适应阈值调整"""
        
        unique_protected = np.unique(protected_attributes)
        adjusted_predictions = y_pred.copy()
        
        # 为每个受保护群体设置不同的阈值
        thresholds = {}
        for protected_value in unique_protected:
            mask = protected_attributes == protected_value
            group_predictions = y_pred[mask]
            
            # 设置阈值使每个组的正例率相等
            threshold = np.median(group_predictions)
            thresholds[protected_value] = threshold
        
        # 应用阈值
        for protected_value in unique_protected:
            mask = protected_attributes == protected_value
            threshold = thresholds[protected_value]
            adjusted_predictions[mask] = (y_pred[mask] >= threshold).astype(int)
        
        return adjusted_predictions
    
    def _fair_calibration(self, 
                         y_pred: np.ndarray, 
                         protected_attributes: np.ndarray) -> np.ndarray:
        """公平校准"""
        
        # 简化的公平校准实现
        # 实际实现中需要更复杂的校准算法
        
        unique_protected = np.unique(protected_attributes)
        calibrated_predictions = y_pred.copy()
        
        for protected_value in unique_protected:
            mask = protected_attributes == protected_value
            group_predictions = y_pred[mask]
            
            # 简单的分位数校准
            calibrated_predictions[mask] = np.percentile(group_predictions, 50)
        
        return calibrated_predictions

# 审计报告生成器
class BiasAuditReporter:
    """偏差审计报告生成器"""
    
    def __init__(self, model_name: str, audit_date: str):
        self.model_name = model_name
        self.audit_date = audit_date
        self.audit_id = f"audit_{model_name}_{audit_date.replace('-', '')}"
    
    def generate_comprehensive_report(self, 
                                    bias_results: List[BiasDetectionResult],
                                    model_metadata: Dict[str, Any],
                                    risk_assessment: Dict[str, str]) -> AuditReport:
        """生成综合审计报告"""
        
        # 计算总体偏差分数
        overall_bias_score = np.mean([r.bias_score for r in bias_results])
        
        # 评估风险等级
        risk_level = self._assess_risk_level(overall_bias_score, bias_results)
        
        # 生成改进建议
        recommendations = self._generate_recommendations(bias_results)
        
        # 合规状态检查
        compliance_status = self._check_compliance(bias_results)
        
        return AuditReport(
            audit_id=self.audit_id,
            model_name=self.model_name,
            audit_date=self.audit_date,
            protected_attributes=list(set(r.group_statistics.keys())),
            overall_bias_score=overall_bias_score,
            findings=bias_results,
            risk_level=risk_level,
            recommendations=recommendations,
            compliance_status=compliance_status
        )
    
    def _assess_risk_level(self, overall_bias_score: float, bias_results: List[BiasDetectionResult]) -> str:
        """评估风险等级"""
        
        # 统计违规指标数量
        violations = sum(1 for result in bias_results if not result.is_fair)
        total_metrics = len(bias_results)
        violation_rate = violations / total_metrics
        
        if overall_bias_score < 0.05 and violation_rate < 0.2:
            return "低风险"
        elif overall_bias_score < 0.1 and violation_rate < 0.5:
            return "中等风险"
        else:
            return "高风险"
    
    def _generate_recommendations(self, bias_results: List[BiasDetectionResult]) -> List[str]:
        """生成改进建议"""
        
        recommendations = []
        
        # 收集所有建议
        for result in bias_results:
            if not result.is_fair:
                recommendations.extend(result.recommendations)
        
        # 添加通用建议
        recommendations.extend([
            "建立定期偏差审计机制",
            "实施模型监控和警报系统",
            "确保数据收集和处理过程的公平性",
            "提供模型决策的解释性"
        ])
        
        # 去重并排序
        unique_recommendations = list(set(recommendations))
        return sorted(unique_recommendations)
    
    def _check_compliance(self, bias_results: List[BiasDetectionResult]) -> Dict[str, bool]:
        """检查合规性"""
        
        return {
            "statistical_parity_compliant": next(
                (r.is_fair for r in bias_results if r.metric_name == "statistical_parity"), 
                True
            ),
            "equal_opportunity_compliant": next(
                (r.is_fair for r in bias_results if r.metric_name == "equalized_opportunity"), 
                True
            ),
            "overall_fairness_compliant": all(r.is_fair for r in bias_results)
        }
    
    def export_report_to_pdf(self, 
                           audit_report: AuditReport, 
                           save_path: str) -> None:
        """导出PDF报告"""
        
        # 简化的PDF生成
        # 实际实现中可以使用reportlab或其他PDF库
        
        content = f"""
# AI偏差审计报告

## 审计信息
- 审计ID: {audit_report.audit_id}
- 模型名称: {audit_report.model_name}
- 审计日期: {audit_report.audit_date}
- 风险等级: {audit_report.risk_level}

## 偏差检测结果
"""
        
        for finding in audit_report.findings:
            content += f"""
### {finding.metric_name}
- 偏差分数: {finding.bias_score:.4f}
- 阈值: {finding.threshold:.4f}
- 状态: {'公平' if finding.is_fair else '存在偏差'}
- 置信区间: {finding.confidence_interval}
"""
        
        content += f"""
## 总体评估
- 总体偏差分数: {audit_report.overall_bias_score:.4f}
- 合规状态: {audit_report.compliance_status}

## 改进建议
"""
        
        for recommendation in audit_report.recommendations:
            content += f"- {recommendation}\n"
        
        # 保存到文件
        with open(save_path.replace('.pdf', '.md'), 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"审计报告已导出到: {save_path}")

# 使用示例
async def main():
    # 生成示例数据
    np.random.seed(42)
    n_samples = 1000
    
    # 创建有偏差的模拟数据
    y_true = np.random.binomial(1, 0.6, n_samples)  # 60%的正例率
    
    # 创建受保护属性（性别：0=女性，1=男性）
    gender = np.random.binomial(1, 0.5, n_samples)  # 50%男性
    
    # 创建有偏差的预测结果
    # 男性群体的预测偏向更正面
    y_pred_proba = np.random.beta(2, 1, n_samples)
    y_pred_proba[gender == 1] *= 1.2  # 男性偏向
    y_pred_proba = np.clip(y_pred_proba, 0, 1)
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    # 创建受保护属性DataFrame
    protected_df = pd.DataFrame({
        'gender': gender,
        'age_group': np.random.choice(['young', 'middle', 'old'], n_samples)
    })
    
    print("=== AI偏差检测演示 ===")
    print(f"样本数量: {n_samples}")
    print(f"正例率: {np.mean(y_true):.3f}")
    print(f"预测正例率: {np.mean(y_pred):.3f}")
    print(f"男性比例: {np.mean(gender):.3f}")
    
    # 初始化偏差检测器
    bias_detector = BiasDetector(protected_attributes=['gender', 'age_group'])
    
    # 执行偏差检测
    print("\n执行偏差检测...")
    bias_results = bias_detector.detect_bias(y_true, y_pred, y_pred_proba, protected_df)
    
    # 打印结果
    print("\n偏差检测结果:")
    for result in bias_results:
        status = "✓ 公平" if result.is_fair else "✗ 存在偏差"
        print(f"  {result.metric_name}: {result.bias_score:.4f} (阈值: {result.threshold:.4f}) {status}")
        if not result.is_fair:
            print(f"    建议: {', '.join(result.recommendations)}")
    
    # 高级偏差分析
    print("\n=== 高级偏差分析 ===")
    
    advanced_analyzer = AdvancedBiasAnalyzer(bias_detector)
    
    # 交叉群体分析
    cross_sectional_results = advanced_analyzer.cross_sectional_analysis(
        y_true, y_pred, protected_df
    )
    
    print("\n交叉群体偏差分析:")
    for attr, results in cross_sectional_results.items():
        if attr != 'cross_sectional':
            for result in results:
                if not result.is_fair:
                    print(f"  {attr} - {result.metric_name}: 存在偏差")
    
    # 生成偏差热图
    print("\n生成偏差可视化...")
    visualizer = AdvancedBiasAnalyzer(bias_detector)
    heatmap_fig = visualizer.bias_heatmap(bias_results, 'bias_heatmap.png')
    print("偏差热图已保存为: bias_heatmap.png")
    
    # 偏差缓解演示
    print("\n=== 偏差缓解演示 ===")
    
    mitigation = BiasMitigationTechniques()
    
    # 预处理缓解
    X_dummy = np.random.randn(n_samples, 5)  # 模拟特征
    mitigated_X, mitigated_y = mitigation.apply_preprocessing_mitigation(
        X_dummy, y_true, gender, method='resampling'
    )
    print(f"预处理缓解后样本数: {len(mitigated_X)}")
    
    # 后处理缓解
    mitigated_pred = mitigation.apply_postprocessing_mitigation(
        y_pred_proba, gender, method='threshold_adjustment'
    )
    print(f"后处理缓解后预测正例率: {np.mean(mitigated_pred):.3f}")
    
    # 验证缓解效果
    print("\n验证缓解效果...")
    mitigated_results = bias_detector.detect_bias(y_true, mitigated_pred, protected_df=protected_df)
    improved_metrics = sum(1 for r in mitigated_results if r.is_fair) - sum(1 for r in bias_results if r.is_fair)
    print(f"缓解后改进的指标数: {improved_metrics}")
    
    # 生成审计报告
    print("\n=== 生成审计报告 ===")
    
    audit_reporter = BiasAuditReporter("sentiment_classifier", "2024-01-15")
    
    # 风险评估
    risk_assessment = {
        "financial_impact": "medium",
        "legal_compliance": "high",
        "reputational_risk": "medium"
    }
    
    # 模型元数据
    model_metadata = {
        "algorithm": "Random Forest",
        "training_data_size": n_samples,
        "features": ["sentiment_score", "text_length", "word_count"],
        "deployment_date": "2024-01-01"
    }
    
    audit_report = audit_reporter.generate_comprehensive_report(
        bias_results, model_metadata, risk_assessment
    )
    
    print(f"审计报告生成完成:")
    print(f"  - 审计ID: {audit_report.audit_id}")
    print(f"  - 风险等级: {audit_report.risk_level}")
    print(f"  - 总体偏差分数: {audit_report.overall_bias_score:.4f}")
    print(f"  - 建议数量: {len(audit_report.recommendations)}")
    
    # 导出报告
    audit_reporter.export_report_to_pdf(audit_report, 'bias_audit_report.pdf')
    
    # 合规性检查
    print("\n=== 合规性检查 ===")
    for check, status in audit_report.compliance_status.items():
        status_str = "✓ 通过" if status else "✗ 不通过"
        print(f"  {check}: {status_str}")
    
    return {
        'bias_results': bias_results,
        'mitigated_results': mitigated_results,
        'audit_report': audit_report,
        'heatmap_fig': heatmap_fig
    }

# 运行示例
if __name__ == "__main__":
    result = asyncio.run(main())
```

## Best Practices

### 1. 偏差检测策略
- **多维度检测**: 从多个角度检测偏差
- **持续监控**: 建立持续偏差监控机制
- **预警系统**: 设置偏差预警阈值
- **定期审计**: 建立定期审计流程

### 2. 数据质量管理
- **数据多样性**: 确保训练数据的多样性和代表性
- **数据清理**: 清理明显偏见的数据
- **平衡采样**: 使用平衡采样技术
- **质量评估**: 持续评估数据质量

### 3. 模型设计考虑
- **公平性约束**: 在模型设计中嵌入公平性约束
- **算法选择**: 选择相对公平的算法
- **参数调优**: 考虑公平性因素的参数调优
- **可解释性**: 确保模型决策的可解释性

### 4. 合规和治理
- **法规遵循**: 确保符合相关法律法规
- **伦理审查**: 建立伦理审查机制
- **文档管理**: 维护完整的审计文档
- **培训教育**: 对相关人员进行公平性培训

## Integration Patterns

### 1. MLOps管道集成
```python
# MLOps管道中的偏差检测
class BiasDetectionPipeline:
    def __init__(self):
        self.bias_detector = BiasDetector(protected_attributes)
        self.audit_reporter = BiasAuditReporter()
    
    def post_training_validation(self, model, X_test, y_test, protected_test):
        """训练后偏差验证"""
        y_pred = model.predict(X_test)
        bias_results = self.bias_detector.detect_bias(y_test, y_pred, protected_attributes=protected_test)
        
        # 生成合规报告
        audit_report = self.audit_reporter.generate_comprehensive_report(
            bias_results, model.get_metadata()
        )
        
        if not audit_report.compliance_status['overall_fairness_compliant']:
            raise ValueError(f"模型未通过公平性检查: {audit_report.risk_level}")
        
        return audit_report
```

### 2. 实时监控集成
```python
# 实时偏差监控
class RealTimeBiasMonitor:
    def __init__(self, bias_detector: BiasDetector):
        self.bias_detector = bias_detector
        self.alert_system = AlertSystem()
        self.data_buffer = deque(maxlen=1000)
    
    def monitor_prediction(self, y_true, y_pred, protected_attributes):
        """监控单次预测的偏差"""
        self.data_buffer.append((y_true, y_pred, protected_attributes))
        
        if len(self.data_buffer) >= 100:  # 每100个样本检查一次
            batch_data = list(self.data_buffer)
            y_true_batch = np.array([d[0] for d in batch_data])
            y_pred_batch = np.array([d[1] for d in batch_data])
            protected_batch = pd.DataFrame([d[2] for d in batch_data])
            
            bias_results = self.bias_detector.detect_bias(y_true_batch, y_pred_batch, protected_attributes=protected_batch)
            
            for result in bias_results:
                if not result.is_fair:
                    self.alert_system.send_alert(f"检测到偏差: {result.metric_name} = {result.bias_score:.4f}")
```

## Success Metrics

### 1. 偏差检测效果指标
- **检测准确率**: 偏差检测算法的准确性
- **检测覆盖度**: 覆盖的偏差类型比例
- **误报率**: 错误检测偏差的比例
- **漏报率**: 未能检测到实际偏差的比例

### 2. 公平性改进指标
- **偏差减少率**: 应用缓解技术后偏差的减少程度
- **公平性指标提升**: 各公平性指标的改善情况
- **模型性能保持**: 在提高公平性的同时保持模型性能
- **收敛速度**: 偏差缓解算法的收敛速度

### 3. 合规性指标
- **审计完成率**: 完成审计任务的比例
- **合规检查通过率**: 通过合规检查的比例
- **法规要求满足度**: 满足特定法规要求的程度
- **文档完整性**: 审计文档的完整程度

### 4. 运营效率指标
- **检测速度**: 偏差检测的执行速度
- **处理时间**: 从检测到偏差到完成缓解的总时间
- **自动化程度**: 自动执行的检测和缓解比例
- **人工干预**: 需要人工干预的程度

---

*AI偏差检测审计是构建负责任AI系统的核心组件，通过系统化的偏差检测、智能化的缓解技术和标准化的审计流程，确保AI系统的公平性、透明性和合规性。*
