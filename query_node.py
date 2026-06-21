#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Node5: SPARQL 执行
执行 SPARQL 查询，返回原始结果。
"""

from sparql_tool import run_sparql


def query_node(state):
    """SPARQL 执行节点"""
    sparql = state.get("sparql_query", "")

    if not sparql:
        state["error"] = "没有可执行的 SPARQL"
        state["raw_results"] = []
        print(f"[Node5] SPARQL执行: 失败 - 无查询语句")
        return state

    try:
        data = run_sparql(sparql)
        bindings = data.get("results", {}).get("bindings", [])
        state["raw_results"] = bindings
        print(f"[Node5] SPARQL执行: 查询完成，共 {len(bindings)} 条结果")
    except Exception as e:
        state["error"] = f"查询执行失败: {str(e)}"
        state["raw_results"] = []
        print(f"[Node5] SPARQL执行: 失败 - {e}")

    return state
