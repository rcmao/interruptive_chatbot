"""
针对团队协作场景的干预策略
"""

class TeamCollaborationInterventions:
    """团队协作干预策略"""
    
    def __init__(self):
        # 基于实验设计的干预模板
        self.intervention_templates = {
            # 当组长表达不满时
            "leader_frustration": [
                "🧘 或许我们可以先确认一下大家对任务的理解是否一致？",
                "💬 看起来大家都很在意小组表现，也许可以从现在还可以做什么开始谈起？",
                "🔄 有没有可能组员有些困难未表达？可以先问问对方需要什么支持？"
            ],
            
            # 当组员表现防御时
            "member_defense": [
                "💡 理解大家都有各自的挑战。也许可以分享一下具体遇到的困难？",
                "🤝 每个人的处境都不同，让我们一起找找解决方案。",
                "⏰ 时间管理确实不容易，有什么方式可以帮助更好地平衡各种安排？"
            ],
            
            # 当对话开始升级时
            "escalation_prevention": [
                "⏸️ 让我们暂停一下，深呼吸。大家的目标都是完成好这个项目。",
                "🎯 我们都希望项目成功，也许可以重新聚焦在解决方案上？",
                "🔄 换个角度思考：如果是你处在对方的位置，会希望如何被理解？"
            ],
            
            # Thomas模型特定阶段干预
            "thomas_specific": {
                "frustration": "🧘 感受到一些挫折感是很正常的。让我们一起理清楚具体的担忧点。",
                "conceptualization": "💭 看起来大家对问题的理解可能不太一样，我们来澄清一下？",
                "behavior": "⚡ 在采取行动之前，也许可以先确保双方都理解对方的立场？",
                "interaction": "🛑 对话有些激烈了。让我们先冷静一下，然后以更建设性的方式继续。"
            }
        }
    
    def select_intervention(self, conflict_signals: dict, context: dict) -> str:
        """选择最适合的干预策略"""
        
        # 1. 基于角色和情况选择
        if conflict_signals.get("leader_frustration", 0) > 0.5:
            return self._select_random_template("leader_frustration")
        
        elif conflict_signals.get("member_defense", 0) > 0.4:
            return self._select_random_template("member_defense")
        
        elif conflict_signals.get("score", 0) > 0.7:
            return self._select_random_template("escalation_prevention")
        
        # 2. 基于Thomas阶段选择
        thomas_stage = conflict_signals.get("thomas_stage")
        if thomas_stage in self.intervention_templates["thomas_specific"]:
            return self.intervention_templates["thomas_specific"][thomas_stage]
        
        # 3. 默认温和干预
        return "💬 看起来大家都很投入这个项目。让我们确保沟通保持建设性。"
    
    def _select_random_template(self, category: str) -> str:
        """随机选择模板避免重复"""
        import random
        templates = self.intervention_templates.get(category, [])
        return random.choice(templates) if templates else "让我们保持冷静，继续建设性的对话。" 