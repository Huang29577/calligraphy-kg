#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
意图识别模块
根据问题文本识别用户查询意图，支持所有 15+ 种关系类型。
"""

from few_shot_examples import INTENT_KEYWORDS, INTENT_TO_RELATION_ZH


def parse_intent(question):
    """从问题中识别查询意图

        基于关键词匹配，按意图优先级和关键词长度匹配。
        先按意图顺序，在每个意图内按关键词长度降序匹配。
        如无法识别返回 None。
    """
    if not question:
        return None

    for intent, keywords in INTENT_KEYWORDS.items():
        # 每个意图内按关键词长度降序（长关键词优先匹配）
        sorted_kw = sorted(keywords, key=lambda x: (-len(x), x))
        for kw in sorted_kw:
            if kw in question:
                return intent

    return None


def get_relation_zh(intent):
    """根据意图获取中文关系名"""
    return INTENT_TO_RELATION_ZH.get(intent, intent)


def get_all_intents():
    """获取所有支持的意图"""
    return list(INTENT_KEYWORDS.keys())


# 快速测试
if __name__ == "__main__":
    test_questions = [
        "王羲之的父亲是谁",
        "文彭的字号是什么",
        "颜真卿的老师是谁",
        "苏轼擅长什么书体",
        "文彭的籍贯是什么",
        "欧阳询是什么朝代的人",
        "米芾的好友有哪些",
        "王献之的兄弟是谁",
        "赵孟頫属于哪个流派",
        "王羲之的代表作是什么",
    ]
    for q in test_questions:
        intent = parse_intent(q)
        rel_zh = get_relation_zh(intent) if intent else "未知"
        print(f"Q: {q}")
        print(f"   → 意图: {intent}, 关系: {rel_zh}")
        print()
