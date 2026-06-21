#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试 LangGraph 问答系统
"""

from graph_builder import app

test_questions = [
    "文彭的字号是什么",
    "文彭的父亲是谁",
    "何震的字号是什么",
    "王羲之的父亲是谁",
    "苏轼属于哪个流派",
    "王羲之擅长什么书体",
    "文彭的老师是谁",
    "文彭的籍贯是什么",
    "文彭是什么朝代的人",
]

print("=" * 60)
print("  LangGraph 问答系统测试")
print("=" * 60)

for q in test_questions:
    print(f"\nQ: {q}")
    try:
        result = app.invoke({"question": q})
        print(f"A: {result.get('answer', '无答案')}")
    except Exception as e:
        print(f"E: {e}")

print("\n" + "=" * 60)
print("测试完成")
