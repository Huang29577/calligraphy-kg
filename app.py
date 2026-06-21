#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web 应用 — 知识图谱问答系统

API：
  GET  /             问答页面
  GET  /stats        知识图谱统计
  GET  /graph-data   图谱数据（前端渲染用）
  POST /ask          智能问答
  POST /sparql       高级SPARQL查询
"""

import re
import os
from flask import Flask, request, jsonify, render_template

from graph_builder import app as langgraph_app
from sparql_tool import run_sparql
from sparql_queries import query_all_persons, query_person_info

app = Flask(__name__)


# ═══════════════════════════════════════════════════════════════
# TTL 解析（用于前端图谱展示）
# ═══════════════════════════════════════════════════════════════

def parse_ttl():
    """解析 knowledge_graph.ttl，返回结构化的实体和关系数据"""
    ttl_path = os.path.join(os.path.dirname(__file__), "knowledge_graph.ttl")
    if not os.path.exists(ttl_path):
        return {"entities": [], "predicates": []}

    with open(ttl_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 去掉前缀声明
    content = re.sub(r"@prefix\s+\w+:\s*<[^>]+>\s*\.", "", content)

    # 按块分拆（每个实体定义块由句点 + 换行结束）
    blocks = re.split(r"\.\s*\n\s*", content)
    blocks = [b.strip() for b in blocks if b.strip()]

    entities = []
    predicates_set = set()
    entity_names = set()

    for block in blocks:
        # 匹配主语: ex:Name a ex:Type ;
        subj_match = re.match(r"ex:(\w+)\s+a\s+ex:(\w+)", block)
        if not subj_match:
            continue

        name = subj_match.group(1)
        etype = subj_match.group(2)
        entity_names.add(name)

        relations = []
        rest = block[subj_match.end():]
        # 匹配每一行 ex:predicate value ;
        for m in re.finditer(
            r"ex:(\w+)\s+"
            r"(?:ex:(\w+)|'''([^']*)'''|\"([^\"]*)\")\s*;?",
            rest
        ):
            pred = m.group(1)
            if pred in ("Person", "Place", "TimePeriod", "CalligraphyStyle",
                         "School", "CourtesyName"):
                continue
            predicates_set.add(pred)

            obj_entity = m.group(2)
            obj_literal_triple = m.group(3)
            obj_literal_double = m.group(4)
            obj_literal = obj_literal_triple or obj_literal_double

            if obj_entity:
                relations.append({
                    "predicate": pred,
                    "object": obj_entity,
                    "objectType": "entity"
                })
                entity_names.add(obj_entity)
            elif obj_literal is not None:
                relations.append({
                    "predicate": pred,
                    "object": obj_literal,
                    "objectType": "literal"
                })

        entities.append({
            "name": name,
            "type": etype,
            "relations": relations
        })

    return {
        "entities": entities,
        "predicates": sorted(list(predicates_set)),
        "entity_count": len(entity_names),
        "relation_count": len(predicates_set)
    }


# ═══════════════════════════════════════════════════════════════
# 路由
# ═══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """问答页面"""
    return render_template("index.html")


@app.route("/stats", methods=["GET"])
def stats():
    """知识图谱统计信息"""
    data = parse_ttl()
    return jsonify({
        "entity_count": data["entity_count"],
        "relation_count": data["relation_count"],
        "tech_stack": ["RDF", "Fuseki", "SPARQL", "LangGraph", "Flask"],
    })


@app.route("/graph-data", methods=["GET"])
def graph_data():
    """知识图谱完整数据（用于前端渲染）"""
    data = parse_ttl()
    return jsonify(data)


@app.route("/ask", methods=["POST"])
def ask():
    """智能问答

        请求体: {"question": "王羲之的父亲是谁"}
        响应体: {"answer": "王献之的父亲是：王羲之", "sparql": "...", "raw": [...]}
    """
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "请输入问题", "sparql": "", "raw": []})

    try:
        result = langgraph_app.invoke({"question": question})
        return jsonify({
            "answer": result.get("answer", "未能生成答案"),
            "sparql": result.get("sparql_query", ""),
            "raw": result.get("raw_results", []),
        })
    except Exception as e:
        return jsonify({
            "answer": f"查询出错：{str(e)}",
            "sparql": "",
            "raw": [],
        })


@app.route("/sparql", methods=["POST"])
def sparql_query():
    """高级 SPARQL 查询

        请求体: {"query": "SELECT ..."}
        响应体: {"results": [...], "error": null}
    """
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "查询语句为空", "results": []})

    try:
        result = run_sparql(query)
        bindings = result.get("results", {}).get("bindings", [])
        return jsonify({"results": bindings, "error": None})
    except Exception as e:
        return jsonify({"error": str(e), "results": []})


@app.route("/persons", methods=["GET"])
def list_persons():
    """列出所有人名"""
    try:
        persons = query_all_persons()
        return jsonify({"persons": persons, "count": len(persons)})
    except Exception as e:
        return jsonify({"persons": [], "count": 0, "error": str(e)})


if __name__ == "__main__":
    print("=" * 60)
    print("  中国历代书法家图表 · 知识图谱查询系统")
    print("=" * 60)
    print("  启动地址: http://localhost:5000")
    print("  智能问答: POST /ask")
    print("  SPARQL查询: POST /sparql")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
