#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Node4: SPARQL 生成
根据实体 + 意图生成 SPARQL 查询语句。
"""

from sparql_generator import generate_sparql, generate_sparql_with_examples


def sparql_node(state):
    """SPARQL 生成节点"""
    person = state.get("person")
    intent = state.get("intent")

    if not person or not intent:
        state["error"] = "缺少实体或意图"
        state["sparql_query"] = ""
        print(f"[Node4] SPARQL生成: 失败 - 缺少实体/意图")
        return state

    # 生成 SPARQL
    sparql = generate_sparql(person, intent)
    state["sparql_query"] = sparql

    print(f"[Node4] SPARQL生成: 成功")
    print(f"  SPARQL: {sparql[:100]}...")

    return state
