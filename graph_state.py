#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph 状态定义
"""

from typing import TypedDict, List, Optional


class QAState(TypedDict):
    """问答系统的完整状态"""

    # 输入
    question: str

    # Node1: 问题理解 — 问题类型/关键词分析
    question_type: Optional[str]  # "person_query", "relation_query", "general"
    keywords: List[str]  # 问题中的关键词

    # Node2: 实体识别
    person: Optional[str]  # 识别到的人物
    entities: List[dict]  # 识别到的所有实体

    # Node3: 意图识别
    intent: Optional[str]  # 查询意图

    # Node4: SPARQL 生成
    sparql_query: Optional[str]  # 生成的 SPARQL
    relation_zh: Optional[str]  # 中文关系名

    # Node5: SPARQL 执行
    raw_results: List[dict]  # 原始查询结果

    # Node6: 答案生成
    answer: Optional[str]  # 最终答案

    # 错误处理
    error: Optional[str]  # 错误信息
