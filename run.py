#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一启动脚本

用法:
    python run.py             启动 Flask Web 服务
    python run.py --demo      运行命令行问答测试
    python run.py --check     检查环境
"""

import sys
import os

# 确保项目根目录在 path 中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def check_environment():
    """检查运行环境"""
    print("=" * 50)
    print("环境检查")
    print("=" * 50)

    # Python 版本
    print(f"Python: {sys.version}")

    # 检查依赖
    deps = {
        "flask": False,
        "requests": False,
        "langgraph": False,
    }
    for dep in deps:
        try:
            __import__(dep)
            deps[dep] = True
        except ImportError:
            pass

    for dep, ok in deps.items():
        status = "✅" if ok else "❌"
        print(f"  {status} {dep}")

    # 检查数据文件
    files = [
        "entity.csv", "relation.csv",
        "knowledge_graph.ttl", "ontology.ttl",
        "graph_builder.py", "sparql_queries.py",
        "templates/index.html",
    ]
    print()
    for f in files:
        exists = os.path.exists(os.path.join(BASE_DIR, f))
        status = "✅" if exists else "❌"
        print(f"  {status} {f}")

    # 检查 Fuseki
    print()
    try:
        import requests
        r = requests.post(
            "http://localhost:3030/calligraphy/sparql",
            data={"query": "SELECT (COUNT(*) AS ?c) WHERE { ?s ?p ?o }"},
            headers={"Accept": "application/sparql-results+json"},
            timeout=3
        )
        if r.status_code == 200:
            count = r.json()["results"]["bindings"][0]["c"]["value"]
            print(f"  ✅ Fuseki 连接正常 (数据集: calligraphy, {count} 条三元组)")
        else:
            print(f"  ❌ Fuseki 返回状态码 {r.status_code}")
    except Exception as e:
        print(f"  ❌ Fuseki 连接失败: {e}")

    print()
    return True


def run_cli_demo():
    """命令行问答测试"""
    from graph_builder import app as langgraph_app

    print("=" * 50)
    print("  中国书法知识图谱 · 命令行问答测试")
    print("=" * 50)
    print("  输入 'quit' 退出")
    print("  输入 'check' 检查环境")
    print()

    while True:
        try:
            question = input("\n请输入问题: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            break
        if question.lower() == "check":
            check_environment()
            continue

        print(f"\n🤔 正在查询: {question}")
        try:
            result = langgraph_app.invoke({"question": question})
            answer = result.get("answer", "未能生成答案")
            sparql = result.get("sparql_query", "")
            print(f"💡 答案: {answer}")
            if sparql:
                print(f"🔍 SPARQL: {sparql}")
        except Exception as e:
            print(f"❌ 错误: {e}")


def run_web_server():
    """启动 Flask Web 服务"""
    from app import app

    print("=" * 60)
    print("  中国历代书法家图表 · 知识图谱查询系统")
    print("=" * 60)
    print("  启动地址: http://localhost:5000")
    print("  智能问答: POST /ask")
    print("  SPARQL查询: POST /sparql")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--check" in args:
        check_environment()
    elif "--demo" in args:
        run_cli_demo()
    else:
        run_web_server()
