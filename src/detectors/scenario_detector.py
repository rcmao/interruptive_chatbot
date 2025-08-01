"""
针对"任务分工不均、成员拖延"场景的特化检测系统
"""

class TeamCollaborationConflictDetector:
    """团队协作冲突检测器"""
    
    def __init__(self):
        # 场景特定的关键词库
        self.scenario_keywords = {
            # 组长表达不满/愤怒的典型用词
            "leader_frustration": [
                "连续缺席", "未按时", "没有提交", "担忧", "不满", "愤怒",
                "always missing", "not submitted", "worried", "frustrated", "angry"
            ],
            
            # 组员防御/愧疚的典型表达
            "member_defense": [
                "课程压力", "个人安排", "没有做错", "不希望被批评", "处境",
                "course pressure", "personal schedule", "didn't do wrong", "don't want criticism"
            ],
            
            # 任务相关冲突词汇
            "task_conflict": [
                "PPT", "小组讨论", "组会", "责任", "deadline", "meeting", "responsibility"
            ],
            
            # 情绪升级信号
            "escalation_signals": [
                "你总是", "你从来", "为什么总是", "受够了",
                "you always", "you never", "why always", "fed up"
            ]
        }
        
        # Thomas阶段在此场景下的具体表现
        self.thomas_stage_indicators = {
            "frustration": {
                "patterns": ["我担心", "我不满", "我觉得", "I'm worried", "I'm upset"],
                "context": "leader_initial_concern"
            },
            "conceptualization": {
                "patterns": ["问题是", "我认为", "关键在于", "the issue is", "I think"],
                "context": "problem_definition"
            },
            "behavior": {
                "patterns": ["我要求", "你必须", "从现在开始", "I need you to", "you must"],
                "context": "demand_action"
            },
            "interaction": {
                "patterns": ["你说什么", "这不对", "你不理解", "what do you mean", "that's not right"],
                "context": "direct_confrontation"
            }
        }
    
    def detect_scenario_specific_conflict(self, message: str, author_role: str, context: dict) -> dict:
        """场景特定的冲突检测"""
        signals = {}
        
        # 1. 角色特定检测
        if author_role == "leader":
            signals.update(self._detect_leader_frustration(message))
        elif author_role == "member":
            signals.update(self._detect_member_defense(message))
        
        # 2. Thomas阶段检测（场景特化）
        thomas_stage = self._detect_thomas_stage_in_context(message, context)
        signals["thomas_stage"] = thomas_stage
        
        # 3. 干预时机判断（基于实验设计）
        intervention_trigger = self._check_intervention_trigger(signals, context)
        signals["should_intervene"] = intervention_trigger
        
        return signals
    
    def _detect_leader_frustration(self, message: str) -> dict:
        """检测组长的挫折感和不满"""
        frustration_score = 0.0
        evidence = []
        
        # 检测任务相关抱怨
        task_complaints = sum(1 for word in self.scenario_keywords["leader_frustration"] 
                            if word.lower() in message.lower())
        
        if task_complaints > 0:
            frustration_score += min(task_complaints * 0.3, 0.6)
            evidence.append(f"任务抱怨: {task_complaints}个")
        
        # 检测情绪升级
        escalation_count = sum(1 for phrase in self.scenario_keywords["escalation_signals"]
                             if phrase.lower() in message.lower())
        
        if escalation_count > 0:
            frustration_score += min(escalation_count * 0.4, 0.8)
            evidence.append(f"情绪升级信号: {escalation_count}个")
        
        return {
            "leader_frustration": frustration_score,
            "evidence": evidence,
            "role_specific_score": frustration_score
        }
    
    def _detect_member_defense(self, message: str) -> dict:
        """检测组员的防御性回应"""
        defense_score = 0.0
        evidence = []
        
        # 检测防御性表达
        defense_count = sum(1 for phrase in self.scenario_keywords["member_defense"]
                          if phrase.lower() in message.lower())
        
        if defense_count > 0:
            defense_score += min(defense_count * 0.25, 0.5)
            evidence.append(f"防御性表达: {defense_count}个")
        
        # 检测回避责任的表达
        avoidance_phrases = ["不是我的错", "没办法", "不得已", "not my fault", "couldn't help"]
        avoidance_count = sum(1 for phrase in avoidance_phrases if phrase.lower() in message.lower())
        
        if avoidance_count > 0:
            defense_score += min(avoidance_count * 0.3, 0.6)
            evidence.append(f"回避责任: {avoidance_count}个")
        
        return {
            "member_defense": defense_score,
            "evidence": evidence,
            "role_specific_score": defense_score
        } 