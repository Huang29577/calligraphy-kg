#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph 路由函数
"""


def route_by_intent(state):
    """根据意图决定下一步节点

        如果识别人物和意图 → 进入 SPARQL 生成
        如果只有人物无意图 → 尝试全信息查询
        如果无人无意图 → 直接结束
    """
    person = state.get("person")
    intent = state.get("intent")

    if person and intent:
        return "sparql_gen"
    elif person:
        return "sparql_gen"  # 至少还能查基本信息
    else:
        return "end"  # 无法处理


def route_after_sparql(state):
    """SPARQL 生成后的路由

        有 SPARQL → 执行查询
        无 SPARQL → 结束
    """
    sparql = state.get("sparql_query", "")
    if sparql:
        return "sparql_exec"
    else:
        return "answer"


def route_after_query(state):
    """查询后的路由"""
    return "answer"
