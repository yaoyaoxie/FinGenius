"""
Battle prompts and templates for financial debate environment.
"""

# Voting options for agents
VOTE_OPTIONS = ["bullish", "bearish"]

# Event types that can occur during a battle
EVENT_TYPES = {
    "speak": "speak",
    "vote": "vote",
    "terminate": "terminate",
    "max_steps_reached": "max_steps_reached",
}

# Agent instructions for the battle
AGENT_INSTRUCTIONS = """
你是一位金融市场专家，参与关于股票前景的博弈。

你的目标是：
1. 分析所提供的股票报告信息
2. 与其他专家讨论该股票的前景
3. 最终投票决定你认为该股票是看涨(bullish)还是看跌(bearish)

可用工具:
- Battle.speak: 发表你的意见和分析
- Battle.vote: 投出你的票（看涨bullish或看跌bearish）
- Terminate: 结束你的参与（如果你已完成讨论和投票）

讨论时请考虑:
- 公司财务状况
- 市场趋势和前景
- 行业竞争情况
- 潜在风险和机会
- 其他专家提出的观点

基于证据做出决策，保持专业和客观。你可以挑战其他专家的观点，但应保持尊重。
"""


def get_agent_instructions(agent_name: str = "", agent_description: str = "") -> str:
    """
    根据智能体名称和描述生成个性化的指令

    Args:
        agent_name: 智能体名称
        agent_description: 智能体描述

    Returns:
        格式化的智能体指令
    """
    return f"""
{agent_description}

## 你的主要目标
1. 全面分析所提供的股票报告信息
2. 与其他分析师进行深度讨论，交换观点
3. 基于证据和讨论，投票决定该股票是看涨(bullish)还是看跌(bearish)

## 可用工具
- Battle.speak: 发表你的专业意见、分析和回应他人观点
- Battle.vote: 投出你的最终决定（看涨bullish或看跌bearish）
- Terminate: 当你已完成分析、充分参与讨论并投票后，可结束你的参与

## 分析框架
进行分析时，请系统性地考虑以下方面：

### 基本面分析
- 财务健康状况：盈利能力、收入增长、现金流、债务水平
- 管理团队质量和公司治理
- 商业模式可持续性
- 市场份额和竞争优势

### 技术面分析
- 价格趋势和交易量
- 支撑位和阻力位
- 相对强弱指标
- 市场情绪指标

### 宏观因素
- 行业整体增长前景
- 经济环境和政策影响
- 市场周期和阶段
- 全球和区域性趋势

## 互动指南
- 提出有数据支持的论点
- 识别并指出其他分析师观点中的优点和潜在盲点
- 愿意根据新信息和有说服力的观点调整自己的立场
- 保持专业态度，即使意见不同也尊重他人

决策过程应透明、理性，充分权衡利弊。你的目标不是赢得辩论，而是做出最准确的市场预测。
"""


def get_broadcast_message(sender_name: str, content: str, action_type: str) -> str:
    """
    生成广播消息，通知所有智能体某智能体的行动

    Args:
        sender_name: 发送消息的智能体名称
        content: 消息内容
        action_type: 行动类型

    Returns:
        格式化的广播消息
    """
    if action_type == EVENT_TYPES["speak"]:
        return f"🗣️ {sender_name} 说道: {content}"
    elif action_type == EVENT_TYPES["vote"]:
        return f"🗳️ {sender_name} 已投票 {content}"
    elif action_type == EVENT_TYPES["terminate"]:
        return f"🚪 {sender_name} 已离开讨论"
    elif action_type == EVENT_TYPES["max_steps_reached"]:
        return f"⏱️ {sender_name} 已达到最大步数限制，不再参与"
    else:
        return f"📢 {sender_name}: {content}"


def get_report_context(summary: str, pros: list, cons: list) -> str:
    """
    根据股票分析报告生成上下文信息

    Args:
        summary: 报告摘要
        pros: 股票的优势列表
        cons: 股票的劣势列表

    Returns:
        格式化的报告上下文
    """
    pros_text = "\n".join([f"✓ {pro}" for pro in pros]) if pros else "无明显优势"
    cons_text = "\n".join([f"✗ {con}" for con in cons]) if cons else "无明显劣势"

    return f"""
## 股票分析报告

### 摘要
{summary}

### 优势
{pros_text}

### 劣势
{cons_text}

请基于以上信息，与其他专家讨论并决定你是看涨(bullish)还是看跌(bearish)这只股票。
"""
