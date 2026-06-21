#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Node3: 意图识别
识别用户的查询意图（查什么关系）。
"""

from intent_parser import parse_intent, get_relation_zh


def intent_node(state):
    """意图识别节点"""
    question = state.get("question", "")
    intent = parse_intent(question)

    state["intent"] = intent

    if intent:
        relation_zh = get_relation_zh(intent)
        state["relation_zh"] = relation_zh
        print(f"[Node3] 意图识别: intent={intent}, 关系={relation_zh}")
    else:
        state["relation_zh"] = None
        print(f"[Node3] 意图识别: 未识别到意图")

    return state
