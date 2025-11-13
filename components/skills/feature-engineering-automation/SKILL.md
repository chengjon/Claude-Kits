---
name: feature-engineering-automation
description: "特征工程自动化与智能特征发现专家，精通自动化特征生成、智能特征选择和时间序列特征工程。构建特征工程流水线、特征库管理系统和特征质量评估，处理特征自动化、特征选择优化和特征工程最佳实践。使用PROACTIVELY进行特征工程、特征自动化或ML特征优化。"
---

# 特征工程自动化技能

## When to Use
Use this skill when building automated feature engineering pipelines, implementing intelligent feature selection, creating time-series feature generators, developing text feature extractors, or automating data preprocessing for ML models. Essential for reducing manual feature engineering effort, improving ML model performance through optimal features, and building scalable data processing pipelines.

## Core Concepts

### 1. 自动化特征发现
- **统计特征生成**: 自动生成数值、分类、时间序列统计特征
- **交互特征构造**: 智能识别和生成特征间交互
- **领域特征模板**: 基于特定行业的特征模板库
- **自动编码**: 自动特征编码和变换

### 2. 智能特征选择
- **多标准选择**: 基于相关性、重要性和信息增益的特征选择
- **递归特征消除**: 递归特征消除(RFE)的自动化实现
- **正则化方法**: L1/L2正则化的特征选择应用
- **树模型特征重要性**: 基于树模型的特征重要性评估

### 3. 时间序列特征工程
- **滞后特征**: 自动生成时间滞后特征
- **滚动统计**: 窗口统计特征自动化生成
- **趋势分解**: 趋势、季节性、残差特征提取
- **傅里叶变换**: 频域特征自动提取

### 4. 文本特征工程
- **TF-IDF优化**: 自动TF-IDF参数优化
- **文本统计特征**: 长度、复杂度、情感等统计特征
- **词向量聚合**: 文本嵌入特征的平均池化、最大池化
- **主题特征**: LDA主题模型特征提取

## Code Examples

### 自动化特征工程管道
```python
class AutoFeatureEngineer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feature_generators = self._initialize_generators()
        self.feature_selector = AutoFeatureSelector()
        self.feature_validator = FeatureValidator()
        self.feature_registry = FeatureRegistry()
    
    async def engineer_features(self, 
                              data: pd.DataFrame, 
                              target: str = None,
                              task_type: str = 'classification') -> FeatureSet:
        """自动化特征工程主流程"""
        
        # 1. 数据分析
        data_analysis = await self._analyze_data(data, target)
        
        # 2. 生成基础特征
        base_features = await self._generate_base_features(data, data_analysis)
        
        # 3. 生成统计特征
        statistical_features = await self._generate_statistical_features(
            data, data_analysis, base_features
        )
        
        # 4. 生成交互特征
        interaction_features = await self._generate_interaction_features(
            data, base_features, data_analysis
        )
        
        # 5. 生成领域特定特征
        domain_features = await self._generate_domain_features(
            data, data_analysis, task_type
        )
        
        # 6. 合并所有特征
        all_features = pd.concat([
            base_features,
            statistical_features,
            interaction_features,
            domain_features
        ], axis=1)
        
        # 7. 特征选择
        selected_features = await self.feature_selector.select_features(
            all_features, target, task_type
        )
        
        # 8. 特征验证
        validated_features = await self.feature_validator.validate_features(
            selected_features, target
        )
        
        # 9. 特征注册
        feature_metadata = await self.feature_registry.register_features(
            validated_features, {
                'source': 'auto_engineered',
                'task_type': task_type,
                'generation_time': datetime.now(),
                'data_hash': hashlib.md5(data.values.tobytes()).hexdigest()
            }
        )
        
        return FeatureSet(
            features=validated_features,
            metadata=feature_metadata,
            feature_importance=await self._calculate_feature_importance(
                validated_features, target
            )
        )
    
    def _initialize_generators(self) -> Dict[str, BaseFeatureGenerator]:
        """初始化特征生成器"""
        return {
            'numerical': NumericalFeatureGenerator(),
            'categorical': CategoricalFeatureGenerator(),
            'datetime': DateTimeFeatureGenerator(),
            'text': TextFeatureGenerator(),
            'time_series': TimeSeriesFeatureGenerator(),
            'interaction': InteractionFeatureGenerator(),
            'statistical': StatisticalFeatureGenerator()
        }
    
    async def _generate_base_features(self, 
                                    data: pd.DataFrame, 
                                    analysis: DataAnalysis) -> pd.DataFrame:
        """生成基础特征"""
        base_features = pd.DataFrame()
        
        for column in data.columns:
            column_data = data[column]
            column_type = analysis.column_types[column]
            
            generator = self.feature_generators.get(column_type)
            if generator:
                column_features = await generator.generate_base_features(
                    column_data, column
                )
                base_features = pd.concat([base_features, column_features], axis=1)
        
        return base_features
    
    async def _generate_statistical_features(self, 
                                           data: pd.DataFrame,
                                           analysis: DataAnalysis,
                                           existing_features: pd.DataFrame) -> pd.DataFrame:
        """生成统计特征"""
        stat_gen = self.feature_generators['statistical']
        
        statistical_features = pd.DataFrame()
        
        for column in data.select_dtypes(include=[np.number]).columns:
            # 数值特征统计
            num_stats = await stat_gen.generate_numerical_stats(
                data[column], column
            )
            
            # 分布特征
            distribution_features = await stat_gen.generate_distribution_features(
                data[column], column
            )
            
            # 分箱特征
            binned_features = await stat_gen.generate_binned_features(
                data[column], column, bins=self.config.get('n_bins', 10)
            )
            
            column_stat_features = pd.concat([num_stats, distribution_features, binned_features], axis=1)
            statistical_features = pd.concat([statistical_features, column_stat_features], axis=1)
        
        # 生成特征间相关性特征
        if len(existing_features.columns) > 1:
            correlation_features = await stat_gen.generate_correlation_features(
                existing_features
            )
            statistical_features = pd.concat([statistical_features, correlation_features], axis=1)
        
        return statistical_features

class NumericalFeatureGenerator:
    async def generate_base_features(self, 
                                   series: pd.Series, 
                                   column_name: str) -> pd.DataFrame:
        """生成数值特征"""
        features = pd.DataFrame()
        
        # 基础统计特征
        features[f'{column_name}_mean'] = [series.mean()]
        features[f'{column_name}_std'] = [series.std()]
        features[f'{column_name}_min'] = [series.min()]
        features[f'{column_name}_max'] = [series.max()]
        features[f'{column_name}_median'] = [series.median()]
        features[f'{column_name}_skew'] = [series.skew()]
        features[f'{column_name}_kurtosis'] = [series.kurtosis()]
        
        # 分位数特征
        quantiles = [0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
        for q in quantiles:
            features[f'{column_name}_q{q}'] = [series.quantile(q)]
        
        # 四分位距
        features[f'{column_name}_iqr'] = [series.quantile(0.75) - series.quantile(0.25)]
        
        # 变异系数
        features[f'{column_name}_cv'] = [series.std() / series.mean() if series.mean() != 0 else 0]
        
        # 零值比例
        features[f'{column_name}_zero_ratio'] = [(series == 0).mean()]
        
        # 缺失值比例
        features[f'{column_name}_missing_ratio'] = [series.isnull().mean()]
        
        return features

class InteractionFeatureGenerator:
    def __init__(self):
        self.interaction_methods = {
            'multiplication': self._multiply_features,
            'division': self._divide_features,
            'addition': self._add_features,
            'subtraction': self._subtract_features,
            'polynomial': self._create_polynomial_features,
            'ratio': self._create_ratio_features
        }
    
    async def generate_interaction_features(self,
                                          data: pd.DataFrame,
                                          base_features: pd.DataFrame,
                                          analysis: DataAnalysis) -> pd.DataFrame:
        """生成交互特征"""
        interaction_features = pd.DataFrame()
        
        numerical_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        # 生成两两交互特征
        if len(numerical_columns) >= 2:
            for i, col1 in enumerate(numerical_columns):
                for col2 in numerical_columns[i+1:]:
                    # 乘法交互
                    multiply_feature = self._multiply_features(
                        data[col1], data[col2], f'{col1}_{col2}_multiply'
                    )
                    interaction_features = pd.concat([interaction_features, multiply_feature], axis=1)
                    
                    # 除法交互
                    divide_feature = self._divide_features(
                        data[col1], data[col2], f'{col1}_{col2}_divide'
                    )
                    interaction_features = pd.concat([interaction_features, divide_feature], axis=1)
                    
                    # 加法交互
                    add_feature = self._add_features(
                        data[col1], data[col2], f'{col1}_{col2}_add'
                    )
                    interaction_features = pd.concat([interaction_features, add_feature], axis=1)
        
        # 高阶交互特征
        if len(numerical_columns) >= 3:
            # 三元交互
            triple_interactions = await self._generate_triple_interactions(
                data[numerical_columns[:3]]
            )
            interaction_features = pd.concat([interaction_features, triple_interactions], axis=1)
        
        return interaction_features
    
    def _multiply_features(self, 
                          series1: pd.Series, 
                          series2: pd.Series, 
                          feature_name: str) -> pd.DataFrame:
        """生成乘法交互特征"""
        feature = pd.DataFrame()
        feature[feature_name] = series1 * series2
        
        # 处理无效值
        feature[feature_name] = feature[feature_name].replace([np.inf, -np.inf], np.nan)
        
        return feature
    
    def _divide_features(self, 
                        series1: pd.Series, 
                        series2: pd.Series, 
                        feature_name: str) -> pd.DataFrame:
        """生成除法交互特征"""
        feature = pd.DataFrame()
        
        # 避免除零
        denominator = series2.replace(0, np.nan)
        feature[feature_name] = series1 / denominator
        
        # 处理无效值
        feature[feature_name] = feature[feature_name].replace([np.inf, -np.inf], np.nan)
        
        return feature
    
    async def _generate_triple_interactions(self, 
                                          triple_data: pd.DataFrame) -> pd.DataFrame:
        """生成三元交互特征"""
        triple_features = pd.DataFrame()
        
        columns = triple_data.columns.tolist()
        
        # 三个特征的乘积
        triple_features['triple_product'] = (
            triple_data[columns[0]] * 
            triple_data[columns[1]] * 
            triple_data[columns[2]]
        )
        
        # 三个特征的和
        triple_features['triple_sum'] = (
            triple_data[columns[0]] + 
            triple_data[columns[1]] + 
            triple_data[columns[2]]
        )
        
        return triple_features

class TimeSeriesFeatureGenerator:
    def __init__(self):
        self.window_sizes = [3, 5, 7, 14, 30]
        self.lag_periods = [1, 2, 3, 7, 14, 30]
    
    async def generate_time_series_features(self,
                                          time_series: pd.Series,
                                          timestamp_column: pd.Series,
                                          column_name: str) -> pd.DataFrame:
        """生成时间序列特征"""
        ts_features = pd.DataFrame()
        ts_data = pd.DataFrame({
            'value': time_series,
            'timestamp': timestamp_column
        }).sort_values('timestamp')
        
        # 滞后特征
        for lag in self.lag_periods:
            ts_features[f'{column_name}_lag_{lag}'] = ts_data['value'].shift(lag)
        
        # 滚动统计特征
        for window in self.window_sizes:
            # 滚动均值
            ts_features[f'{column_name}_rolling_mean_{window}'] = (
                ts_data['value'].rolling(window=window).mean()
            )
            
            # 滚动标准差
            ts_features[f'{column_name}_rolling_std_{window}'] = (
                ts_data['value'].rolling(window=window).std()
            )
            
            # 滚动最小值
            ts_features[f'{column_name}_rolling_min_{window}'] = (
                ts_data['value'].rolling(window=window).min()
            )
            
            # 滚动最大值
            ts_features[f'{column_name}_rolling_max_{window}'] = (
                ts_data['value'].rolling(window=window).max()
            )
            
            # 滚动偏度
            ts_features[f'{column_name}_rolling_skew_{window}'] = (
                ts_data['value'].rolling(window=window).skew()
            )
        
        # 差分特征
        ts_features[f'{column_name}_diff_1'] = ts_data['value'].diff()
        ts_features[f'{column_name}_diff_2'] = ts_data['value'].diff().diff()
        
        # 百分比变化
        ts_features[f'{column_name}_pct_change_1'] = ts_data['value'].pct_change()
        ts_features[f'{column_name}_pct_change_7'] = ts_data['value'].pct_change(periods=7)
        
        return ts_features

class AutoFeatureSelector:
    def __init__(self):
        self.selection_methods = {
            'correlation': CorrelationBasedSelector(),
            'mutual_info': MutualInfoSelector(),
            'chi_square': ChiSquareSelector(),
            'rfe': RecursiveFeatureElimination(),
            'tree_importance': TreeImportanceSelector()
        }
    
    async def select_features(self,
                            features: pd.DataFrame,
                            target: pd.Series,
                            task_type: str = 'classification') -> pd.DataFrame:
        """自动特征选择"""
        selection_results = {}
        
        # 应用多种选择方法
        for method_name, selector in self.selection_methods.items():
            try:
                selected_features = await selector.select_features(
                    features, target, task_type
                )
                selection_results[method_name] = selected_features
            except Exception as e:
                print(f"特征选择方法 {method_name} 失败: {e}")
                continue
        
        # 集成选择结果
        if selection_results:
            ensemble_selection = await self._ensemble_feature_selection(
                selection_results, features
            )
            return ensemble_selection
        else:
            # 如果所有方法都失败，返回相关性过滤的结果
            return await self._correlation_filter(features, target)
    
    async def _ensemble_feature_selection(self,
                                        selection_results: Dict[str, pd.DataFrame],
                                        original_features: pd.DataFrame) -> pd.DataFrame:
        """集成特征选择结果"""
        feature_scores = pd.DataFrame(index=original_features.columns)
        
        # 收集每个特征被选择的次数和重要性
        for method, selected_features in selection_results.items():
            for feature in selected_features.columns:
                if feature not in feature_scores.index:
                    feature_scores.loc[feature, 'count'] = 0
                    feature_scores.loc[feature, 'total_score'] = 0
                
                feature_scores.loc[feature, 'count'] += 1
                
                # 如果有重要性分数，添加
                if hasattr(selected_features, 'feature_importance'):
                    feature_scores.loc[feature, 'total_score'] += (
                        selected_features.feature_importance.get(feature, 0)
                    )
        
        # 计算综合分数
        feature_scores['composite_score'] = (
            feature_scores['count'] / len(selection_results) * 0.6 +
            feature_scores['total_score'] / len(selection_results) * 0.4
        )
        
        # 选择高分特征
        threshold = feature_scores['composite_score'].quantile(0.8)
        selected_features = feature_scores[
            feature_scores['composite_score'] >= threshold
        ].index
        
        return original_features[selected_features]

class FeatureValidator:
    def __init__(self):
        self.validation_rules = {
            'variance_threshold': 0.01,
            'missing_threshold': 0.5,
            'correlation_threshold': 0.95
        }
    
    async def validate_features(self,
                              features: pd.DataFrame,
                              target: pd.Series) -> pd.DataFrame:
        """验证特征质量"""
        valid_features = pd.DataFrame()
        
        for column in features.columns:
            feature_series = features[column]
            
            # 检查方差
            if feature_series.var() < self.validation_rules['variance_threshold']:
                continue  # 低方差特征被移除
            
            # 检查缺失值比例
            missing_ratio = feature_series.isnull().mean()
            if missing_ratio > self.validation_rules['missing_threshold']:
                continue  # 缺失值过多的特征被移除
            
            # 检查与目标变量的相关性
            if target is not None and not target.isnull().all():
                correlation = abs(feature_series.corr(target))
                if pd.notna(correlation) and correlation < 0.01:
                    continue  # 与目标相关性太低的特征被移除
            
            # 检查与其他特征的共线性
            is_redundant = await self._check_feature_redundancy(
                feature_series, valid_features
            )
            
            if not is_redundant:
                valid_features[column] = feature_series
        
        return valid_features
    
    async def _check_feature_redundancy(self,
                                      feature: pd.Series,
                                      existing_features: pd.DataFrame) -> bool:
        """检查特征冗余性"""
        for existing_feature in existing_features.columns:
            correlation = abs(feature.corr(existing_features[existing_feature]))
            if pd.notna(correlation) and correlation > 0.95:
                return True  # 高度相关的特征被标记为冗余
        return False

# 使用示例
async def main():
    # 初始化特征工程系统
    feature_engineer = AutoFeatureEngineer({
        'n_bins': 10,
        'correlation_threshold': 0.95,
        'variance_threshold': 0.01,
        'missing_threshold': 0.5
    })
    
    # 准备数据
    data = pd.DataFrame({
        'age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
        'income': [50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 140000],
        'education': ['high_school', 'bachelor', 'master', 'phd', 'bachelor', 
                     'master', 'high_school', 'phd', 'bachelor', 'master'],
        'experience': [2, 5, 8, 12, 6, 9, 3, 15, 7, 10]
    })
    
    target = pd.Series([0, 1, 1, 1, 0, 1, 0, 1, 0, 1])  # 二分类目标
    
    # 执行自动化特征工程
    feature_set = await feature_engineer.engineer_features(
        data, target, task_type='classification'
    )
    
    print(f"生成的特征数量: {len(feature_set.features.columns)}")
    print(f"特征重要性前10:")
    print(feature_set.feature_importance.head(10))
    
    return feature_set

# 运行示例
if __name__ == "__main__":
    asyncio.run(main())
```

## Best Practices

### 1. 特征工程策略
- **渐进式生成**: 从简单到复杂，逐步增加特征复杂度
- **领域知识**: 结合业务知识设计有意义的特征
- **交叉验证**: 使用交叉验证评估特征工程效果
- **性能监控**: 持续监控特征对模型性能的影响

### 2. 自动化优化
- **参数搜索**: 自动优化特征工程参数
- **特征模板**: 建立可重用的特征模板库
- **版本控制**: 特征工程的版本控制和可重现性
- **A/B测试**: 自动化特征效果的A/B测试

### 3. 数据质量保证
- **数据清洗**: 自动化数据清洗和预处理
- **异常检测**: 自动识别和处理异常值
- **数据验证**: 自动验证数据质量和一致性
- **特征监控**: 实时监控特征分布变化

### 4. 性能优化
- **并行处理**: 特征生成的并行化处理
- **内存优化**: 大数据集的特征工程优化
- **缓存机制**: 特征计算结果的缓存
- **增量更新**: 新数据的增量特征更新

## Integration Patterns

### 1. ML Pipeline集成
```python
class MLFeaturePipeline:
    def __init__(self):
        self.feature_engineer = AutoFeatureEngineer()
        self.feature_selector = AutoFeatureSelector()
        self.preprocessor = DataPreprocessor()
    
    async def transform(self, data: pd.DataFrame, target: pd.Series):
        # 特征工程
        engineered_features = await self.feature_engineer.engineer_features(
            data, target
        )
        
        # 预处理
        processed_features = await self.preprocessor.fit_transform(
            engineered_features.features
        )
        
        return processed_features
```

### 2. 云原生部署
```yaml
# 特征工程服务API
apiVersion: v1
kind: Service
metadata:
  name: feature-engineering-service
spec:
  selector:
    app: feature-engineering
  ports:
  - port: 8080
    targetPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: feature-engineering-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: feature-engineering
  template:
    metadata:
      labels:
        app: feature-engineering
    spec:
      containers:
      - name: feature-engineer
        image: feature-engineering:latest
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: DB_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## Success Metrics

### 1. 特征质量指标
- **特征数量增长**: 原始特征vs生成特征的比例
- **特征重要性**: 特征对模型性能的贡献度
- **特征稳定性**: 特征在时间上的稳定性
- **特征相关性**: 特征间相关性控制

### 2. 性能提升指标
- **模型性能**: 特征工程前后模型性能对比
- **训练时间**: 特征工程对训练时间的影响
- **推理速度**: 特征工程对推理速度的影响
- **内存使用**: 特征工程的内存开销

### 3. 自动化效果指标
- **手动工作减少**: 减少手动特征工程工作量的比例
- **特征复用率**: 特征模板和模式的复用程度
- **错误率**: 特征工程过程中的错误率
- **用户满意度**: 用户对自动化特征工程的满意度

---

*自动化特征工程是现代ML系统的核心组件，通过智能化的特征发现、选择和验证，显著提升模型性能并减少人工工作量。*
