#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Node1: 问题理解
分析用户问题，提取问题类型和关键词。
"""


def understanding_node(state):
    """问题理解节点

        分析问题类型（人物查询、关系查询、一般查询等）
        提取关键词
    """
    question = state.get("question", "")
    if not question:
        state["error"] = "问题为空"
        state["question_type"] = "unknown"
        state["keywords"] = []
        return state

    # 判断问题类型
    question_type = "general"
    if "谁" in question or "什么人" in question:
        question_type = "person_query"
    elif "什么" in question or "哪些" in question or "是什么" in question:
        question_type = "relation_query"

    # 提取关键词（简单分词）
    import re
    # 去除非中文/英文/数字字符后分词
    keywords = []
    for token in re.split(r'[的?？，。！、；：""''【】《》\s]+', question):
        token = token.strip()
        if token and len(token) >= 1:
            keywords.append(token)

    state["question_type"] = question_type
    state["keywords"] = keywords

    print(f"[Node1] 问题理解: type={question_type}, keywords={keywords}")

    return state
