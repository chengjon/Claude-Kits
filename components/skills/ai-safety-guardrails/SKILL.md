---
name: ai-safety-guardrails
description: "AI安全防护与合规实施专家，精通多层安全防护、实时安全检测和智能内容过滤。构建安全架构、审计追踪系统和违规检测机制，处理AI系统安全、内容审核和数据保护。使用PROACTIVELY进行AI安全实施、内容过滤或安全合规检查。"
---

# AI安全防护和内容过滤技能

## When to Use
Use this skill when building AI safety systems, implementing content moderation, preventing jailbreak attacks, handling bias mitigation, ensuring ethical AI deployment, or creating guardrails for sensitive AI applications. Critical for production AI systems, chatbots, content generation tools, and regulated AI applications.

## Core Concepts

### 1. 多层安全防护架构
- **输入验证层**: 检测恶意输入、越狱尝试、注入攻击
- **内容过滤层**: 识别和过滤有害、不当或敏感内容  
- **输出控制层**: 审查生成内容，确保符合安全标准
- **用户权限层**: 基于角色和权限的访问控制
- **审计日志层**: 完整的安全事件记录和监控

### 2. 实时安全检测
- **模式识别**: 使用机器学习检测已知攻击模式
- **行为分析**: 分析用户行为和交互模式异常
- **上下文理解**: 基于对话上下文的智能安全判断
- **动态更新**: 实时更新安全规则和黑名单

### 3. 智能内容过滤
- **分类算法**: 多分类器系统处理不同类型内容
- **语义理解**: 深度理解内容语义而非仅依赖关键词
- **文化适应**: 支持多语言和不同文化背景的安全标准
- **自定义规则**: 可配置的业务特定安全策略

## Code Examples

### 基础安全防护系统
```python
class AISafetySystem:
    def __init__(self, config: Dict[str, Any]):
        self.input_validator = InputValidator()
        self.content_filter = ContentFilter()
        self.output_controller = OutputController()
        self.audit_logger = AuditLogger()
        self.config = config
        self.security_rules = self._load_security_rules()
    
    async def process_message(self, message: str, user_context: Dict) -> Dict:
        """处理用户消息的完整安全检查流程"""
        start_time = time.time()
        
        # 1. 输入验证
        validation_result = await self.input_validator.validate(message)
        if not validation_result.is_safe:
            return await self._handle_unsafe_input(message, validation_result)
        
        # 2. 内容过滤
        content_analysis = await self.content_filter.analyze_content(message)
        if content_analysis.risk_level > self.config['max_risk_level']:
            return await self._handle_high_risk_content(message, content_analysis)
        
        # 3. 上下文安全检查
        context_analysis = await self._analyze_context_safety(user_context, message)
        
        # 4. 生成安全响应
        safe_response = await self._generate_safe_response(message, user_context)
        
        # 5. 输出控制
        final_response = await self.output_controller.review(safe_response)
        
        # 6. 审计记录
        await self.audit_logger.log_security_event({
            'timestamp': start_time,
            'user_id': user_context.get('user_id'),
            'message_hash': hashlib.md5(message.encode()).hexdigest(),
            'risk_assessment': content_analysis.risk_level,
            'actions_taken': content_analysis.actions,
            'response_time': time.time() - start_time,
            'success': final_response is not None
        })
        
        return final_response
    
    def _load_security_rules(self) -> Dict:
        """加载安全规则配置"""
        return {
            'blocked_patterns': [
                r'\b(hack|crack|exploit)\w*',
                r'\b(bypass|circumvent)\w*\s+\w*(security|restriction)',
                r'\b(illegal|unlawful)\w*\s+activities',
                # 更多安全规则...
            ],
            'sensitive_topics': [
                'violence', 'self_harm', 'illegal_activities',
                'hate_speech', 'discrimination', 'harassment'
            ],
            'escalation_triggers': [
                'repeated_violations', 'escalating_behavior',
                'sophisticated_attack_patterns'
            ]
        }

class InputValidator:
    def __init__(self):
        self.jailbreak_detector = JailbreakDetector()
        self.inject_detector = InjectionDetector()
        self.pattern_matcher = PatternMatcher()
    
    async def validate(self, input_text: str) -> ValidationResult:
        """验证输入文本的安全性"""
        validation_score = 0
        issues = []
        
        # 检测越狱尝试
        jailbreak_result = await self.jailbreak_detector.detect(input_text)
        if jailbreak_result.is_detected:
            validation_score += 0.8
            issues.append(f"越狱尝试: {jailbreak_result.pattern}")
        
        # 检测注入攻击
        injection_result = await self.inject_detector.detect(input_text)
        if injection_result.is_detected:
            validation_score += 0.9
            issues.append(f"注入攻击: {injection_result.type}")
        
        # 模式匹配检查
        pattern_results = await self.pattern_matcher.match_patterns(input_text)
        for pattern, match in pattern_results.items():
            if match:
                validation_score += 0.3
                issues.append(f"危险模式: {pattern}")
        
        # 长度和复杂度检查
        if len(input_text) > 5000:
            validation_score += 0.2
            issues.append("输入过长")
        
        if self._detect_obfuscation(input_text):
            validation_score += 0.4
            issues.append("存在混淆模式")
        
        return ValidationResult(
            is_safe=validation_score < 0.7,
            score=validation_score,
            issues=issues,
            recommendations=self._generate_recommendations(issues)
        )
    
    def _detect_obfuscation(self, text: str) -> bool:
        """检测文本混淆"""
        # 检测字符替换、编码绕过等
        obfuscation_patterns = [
            r'\b\w+\s*=\s*\w+\s*\+\s*\w+',  # 字符串拼接
            r'\\x[0-9a-fA-F]{2}',           # 十六进制编码
            r'\\u[0-9a-fA-F]{4}',           # Unicode编码
            # 更多混淆模式...
        ]
        
        for pattern in obfuscation_patterns:
            if re.search(pattern, text):
                return True
        return False

class ContentFilter:
    def __init__(self):
        self.toxicity_classifier = ToxicityClassifier()
        self.hate_speech_detector = HateSpeechDetector()
        self.bias_detector = BiasDetector()
        self.semantic_analyzer = SemanticAnalyzer()
    
    async def analyze_content(self, text: str) -> ContentAnalysis:
        """分析内容的安全性和适当性"""
        analyses = await asyncio.gather(
            self.toxicity_classifier.analyze(text),
            self.hate_speech_detector.detect(text),
            self.bias_detector.detect_bias(text),
            self.semantic_analyzer.analyze(text),
            return_exceptions=True
        )
        
        toxicity, hate_speech, bias, semantics = analyses
        
        # 计算综合风险评分
        risk_factors = {
            'toxicity': getattr(toxicity, 'score', 0),
            'hate_speech': getattr(hate_speech, 'score', 0),
            'bias': getattr(bias, 'score', 0),
            'semantic_risk': getattr(semantics, 'risk_score', 0)
        }
        
        # 加权风险评分
        weighted_score = sum(
            score * weight for score, weight in zip(
                risk_factors.values(),
                [0.4, 0.3, 0.2, 0.1]  # 权重分配
            )
        )
        
        # 生成处理建议
        actions = self._generate_action_plan(risk_factors, weighted_score)
        
        return ContentAnalysis(
            risk_level=min(weighted_score, 1.0),
            risk_factors=risk_factors,
            actions=actions,
            categories=self._categorize_content(risk_factors),
            confidence=self._calculate_confidence(analyses)
        )
    
    def _generate_action_plan(self, risk_factors: Dict, weighted_score: float) -> List[str]:
        """生成内容处理行动计划"""
        actions = []
        
        if risk_factors['toxicity'] > 0.7:
            actions.append("标记为有害内容，限制生成")
        elif risk_factors['toxicity'] > 0.4:
            actions.append("降低生成内容强度")
        
        if risk_factors['hate_speech'] > 0.5:
            actions.append("阻止生成任何内容")
        
        if risk_factors['bias'] > 0.6:
            actions.append("增加平衡性建议")
        
        if weighted_score > 0.8:
            actions.append("升级到人工审核")
        elif weighted_score > 0.5:
            actions.append("增加安全检查点")
        
        return actions

class BiasMonitor:
    """专门的偏差监控和公平性检查"""
    
    def __init__(self, protected_attributes: List[str]):
        self.protected_attributes = protected_attributes
        self.fairness_metrics = FairnessMetrics()
        self.bias_detectors = {
            attr: BiasDetector(attr) for attr in protected_attributes
        }
    
    async def check_model_bias(self, model, test_data: pd.DataFrame) -> BiasReport:
        """检查模型的偏差情况"""
        predictions = await model.predict(test_data)
        report = BiasReport()
        
        for attribute in self.protected_attributes:
            if attribute in test_data.columns:
                bias_score = await self._calculate_bias_score(
                    predictions, test_data[attribute], attribute
                )
                report.add_attribute_analysis(attribute, bias_score)
        
        # 计算综合公平性指标
        overall_fairness = self.fairness_metrics.calculate_overall_fairness(report)
        report.overall_score = overall_fairness
        
        if overall_fairness < 0.8:  # 阈值可配置
            report.recommendations = await self._generate_bias_mitigation_strategies(report)
        
        return report
    
    async def _calculate_bias_score(self, predictions, attribute_column, attribute_name) -> Dict:
        """计算特定属性的偏差分数"""
        grouped_stats = pd.DataFrame({
            'prediction': predictions,
            attribute_name: attribute_column
        }).groupby(attribute_name)
        
        # 计算各种公平性指标
        metrics = {}
        
        # 人口统计均衡 (Demographic Parity)
        metrics['demographic_parity'] = self._calculate_demographic_parity(grouped_stats)
        
        # 等机会 (Equalized Odds)
        metrics['equalized_odds'] = await self._calculate_equalized_odds(grouped_stats)
        
        # 校准 (Calibration)
        metrics['calibration'] = self._calculate_calibration(grouped_stats)
        
        return {
            'attribute': attribute_name,
            'metrics': metrics,
            'overall_score': np.mean(list(metrics.values())),
            'violations': self._identify_violations(metrics)
        }
```

### 实时安全监控系统
```python
class RealTimeSafetyMonitor:
    def __init__(self, config: Dict):
        self.config = config
        self.alert_system = AlertSystem()
        self.dashboard = SafetyDashboard()
        self.ml_detector = MLAttackDetector()
    
    async def monitor_session(self, session_id: str, user_interactions: List[Dict]):
        """实时监控用户会话的安全状态"""
        session_analysis = SessionAnalysis(session_id)
        interaction_patterns = []
        
        for interaction in user_interactions:
            # 分析每次交互
            interaction_analysis = await self._analyze_interaction(interaction)
            interaction_patterns.append(interaction_analysis)
            
            # 更新会话模式
            session_analysis.update_patterns(interaction_analysis)
            
            # 实时风险评估
            current_risk = session_analysis.calculate_current_risk()
            
            if current_risk > self.config['alert_threshold']:
                await self._trigger_real_time_alert(session_id, current_risk, interaction)
        
        # 生成会话安全报告
        final_report = await self._generate_session_report(session_id, session_analysis)
        return final_report
    
    async def _analyze_interaction(self, interaction: Dict) -> InteractionAnalysis:
        """分析单次用户交互"""
        return InteractionAnalysis(
            timestamp=interaction.get('timestamp'),
            user_input=interaction.get('input'),
            model_response=interaction.get('response'),
            input_safety_score=await self._score_input_safety(interaction.get('input')),
            response_safety_score=await self._score_response_safety(interaction.get('response')),
            interaction_context=interaction.get('context', {}),
            behavioral_flags=self._detect_behavioral_flags(interaction),
            escalation_indicators=self._detect_escalation_indicators(interaction)
        )

class AdaptiveSafetySystem:
    """自适应安全系统，根据攻击模式动态调整防护策略"""
    
    def __init__(self):
        self.attack_patterns = AttackPatternDB()
        self.strategy_optimizer = StrategyOptimizer()
        self.ml_classifier = AdaptiveMLClassifier()
    
    async def adapt_to_new_attacks(self, attack_samples: List[str]):
        """根据新攻击样本自适应调整安全策略"""
        # 1. 分析新攻击模式
        new_patterns = await self.attack_patterns.extract_patterns(attack_samples)
        
        # 2. 更新检测模型
        await self.ml_classifier.update_with_new_data(new_patterns)
        
        # 3. 优化防护策略
        optimized_strategies = await self.strategy_optimizer.optimize_strategies(new_patterns)
        
        # 4. 部署更新
        await self._deploy_updated_strategies(optimized_strategies)
        
        return {
            'patterns_detected': len(new_patterns),
            'strategies_updated': len(optimized_strategies),
            'deployment_status': 'success'
        }

# 使用示例
async def main():
    # 初始化安全系统
    safety_system = AISafetySystem({
        'max_risk_level': 0.6,
        'alert_threshold': 0.8,
        'audit_retention_days': 90
    })
    
    # 处理用户消息
    user_message = "请帮我分析这个产品的市场潜力"
    user_context = {
        'user_id': 'user_123',
        'session_id': 'session_456',
        'permissions': ['standard_access']
    }
    
    response = await safety_system.process_message(user_message, user_context)
    
    if response.is_safe:
        print(f"安全响应: {response.content}")
    else:
        print(f"安全警告: {response.warning_message}")
        print(f"建议操作: {response.recommended_actions}")

# 运行示例
if __name__ == "__main__":
    asyncio.run(main())
```

## Best Practices

### 1. 分层防护策略
- **预防层**: 输入验证、模式识别、预过滤
- **检测层**: 实时监控、异常检测、行为分析  
- **响应层**: 自动拦截、警告提示、人工介入
- **学习层**: 模式更新、策略优化、经验积累

### 2. 性能优化
- **缓存机制**: 缓存常见安全检查结果
- **异步处理**: 避免安全检查阻塞用户体验
- **批量处理**: 批量处理多个检查任务
- **优先级队列**: 高风险内容优先处理

### 3. 合规性管理
- **法规遵循**: 支持GDPR、CCPA等隐私法规
- **审计跟踪**: 完整的操作日志和审计追踪
- **数据保护**: 加密存储、访问控制、数据脱敏
- **透明度**: 提供安全决策的可解释性

### 4. 部署考虑
- **灰度发布**: 新安全策略的渐进式部署
- **回滚机制**: 快速回滚有问题的安全更新
- **监控告警**: 实时监控系统性能和错误率
- **负载均衡**: 高并发情况下的安全检查扩展

## Integration Patterns

### 1. 独立安全服务
```python
# 安全微服务架构
class SafetyMicroservice:
    def __init__(self):
        self.gateway = APIGateway()
        self.safety_engine = AISafetySystem()
        self.audit_service = AuditService()
    
    @app.post("/api/v1/safety/check")
    async def safety_check(self, request: SafetyCheckRequest):
        return await self.safety_engine.process_message(
            request.message, 
            request.context
        )
```

### 2. 中间件集成
```python
# 安全中间件
class SafetyMiddleware:
    async def __call__(self, request: Request, call_next):
        # 请求前安全检查
        safety_result = await self.check_request_safety(request)
        
        if not safety_result.is_safe:
            return JSONResponse(
                status_code=403,
                content={"error": "Content blocked by safety policies"}
            )
        
        # 处理请求
        response = await call_next(request)
        
        # 响应后安全检查
        if response.headers.get('content-type', '').startswith('text/'):
            await self.check_response_safety(response)
        
        return response
```

### 3. 云原生部署
```yaml
# Kubernetes部署配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-safety-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-safety
  template:
    metadata:
      labels:
        app: ai-safety
    spec:
      containers:
      - name: safety-engine
        image: ai-safety:latest
        ports:
        - containerPort: 8080
        env:
        - name: SAFETY_LEVEL
          value: "high"
        - name: AUDIT_RETENTION
          value: "90d"
```

## Common Challenges

### 1. 误报问题
- **挑战**: 过度保护可能阻止正常用户使用
- **解决**: 细化分类器、多层次验证、用户反馈机制

### 2. 性能开销
- **挑战**: 严格安全检查增加响应时间
- **解决**: 异步处理、缓存策略、智能预筛选

### 3. 攻击者适应
- **挑战**: 攻击者会不断寻找新的绕过方法
- **解决**: 自适应学习、威胁情报更新、多模型集成

### 4. 法规合规
- **挑战**: 不同地区有不同的安全和隐私要求
- **解决**: 可配置策略、地理定位、审计日志

## Success Metrics

### 1. 安全效果指标
- **拦截准确率**: 正确拦截恶意内容比例
- **误报率**: 错误拦截正常内容比例
- **响应时间**: 安全检查的平均处理时间
- **覆盖率**: 安全规则覆盖的威胁类型比例

### 2. 合规性指标
- **审计完整性**: 审计日志的完整性和准确性
- **法规符合度**: 满足相关法规要求的程度
- **数据保护**: 用户数据的安全处理水平
- **透明度**: 安全决策的可解释性水平

### 3. 运营指标
- **系统可用性**: 安全服务的可用时间比例
- **扩展性能**: 高负载下的性能保持情况
- **运维效率**: 安全系统的维护和管理成本
- **用户满意度**: 用户对安全系统的接受度

---

*AI安全防护是一个持续演进的领域，需要结合技术实现、业务需求和合规要求，建立全面的安全治理体系。*
