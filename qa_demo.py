#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行问答 Demo（测试用）

用法:
    python qa_demo.py
"""

from graph_builder import app

print("=" * 60)
print("  中国书法知识图谱 · 问答系统")
print("  输入 'quit' 退出")
print("=" * 60)

while True:
    try:
        question = input("\n问题: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n再见！")
        break

    if not question:
        continue
    if question.lower() in ("quit", "exit", "q"):
        break

    try:
        result = app.invoke({"question": question})
        answer = result.get("answer", "无答案")
        sparql = result.get("sparql_query", "")
        print(f"答案: {answer}")
        if sparql:
            print(f"SPARQL: {sparql}")
    except Exception as e:
        print(f"错误: {e}")
