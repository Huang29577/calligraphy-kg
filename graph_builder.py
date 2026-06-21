#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph 知识图谱问答系统工作流

完整的6节点工作流：
  Node1: 问题理解 (understanding)
  Node2: 实体识别 (entity)
  Node3: 意图识别 (intent)
  Node4: SPARQL生成 (sparql_gen)
  Node5: SPARQL执行 (sparql_exec)
  Node6: 答案生成 (answer)

用户问题 → LangGraph → 自动生成SPARQL → Fuseki查询 → 组织答案 → 返回结果
"""

from langgraph.graph import StateGraph, END
from graph_state import QAState
from understanding_node import understanding_node
from entity_node import entity_node
from intent_node import intent_node
from sparql_node import sparql_node
from query_node import query_node
from answer_node import answer_node
from router import route_by_intent, route_after_sparql, route_after_query

# 构建图
graph = StateGraph(QAState)

# 添加节点
graph.add_node("understanding", understanding_node)  # Node1: 问题理解
graph.add_node("entity", entity_node)                 # Node2: 实体识别
graph.add_node("intent", intent_node)                 # Node3: 意图识别
graph.add_node("sparql_gen", sparql_node)             # Node4: SPARQL生成
graph.add_node("sparql_exec", query_node)             # Node5: SPARQL执行
graph.add_node("answer", answer_node)                 # Node6: 答案生成

# 设置入口
graph.set_entry_point("understanding")

# ── 连接节点 ──

# Node1 → Node2
graph.add_edge("understanding", "entity")

# Node2 → Node3
graph.add_edge("entity", "intent")

# Node3 → Node4 (conditional: 根据是否有意图路由)
graph.add_conditional_edges(
    "intent",
    route_by_intent,
    {
        "sparql_gen": "sparql_gen",
        "end": "answer"
    }
)

# Node4 → Node5
graph.add_edge("sparql_gen", "sparql_exec")

# Node5 → Node6
graph.add_edge("sparql_exec", "answer")

# Node6 → END
graph.add_edge("answer", END)

# 编译
app = graph.compile()
