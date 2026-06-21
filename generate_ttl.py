#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 entity.csv 和 relation.csv 自动生成：
  - ontology.ttl   (本体定义：类、属性)
  - knowledge_graph.ttl (完整知识图谱数据)

用法：
    python generate_ttl.py
"""

import csv
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENTITY_CSV = os.path.join(BASE_DIR, "entity.csv")
RELATION_CSV = os.path.join(BASE_DIR, "relation.csv")
ONTOLOGY_TTL = os.path.join(BASE_DIR, "ontology.ttl")
KG_TTL = os.path.join(BASE_DIR, "knowledge_graph.ttl")

# ── 实体类型 → RDF 类 ──
TYPE_CLASS_MAP = {
    "人名": "Person",
    "字号": "CourtesyName",
    "时间": "TimePeriod",
    "地名": "Place",
    "书体/印风": "CalligraphyStyle",
    "流派": "School",
}

# ── 关系类型 → RDF 属性 ── (枚举所有中文关系名)
RELATION_PROP_MAP = {
    "字": "courtesyName",
    "号": "styleName",
    "所处时代": "dynasty",
    "籍贯": "birthplace",
    "擅长书体": "goodAt",
    "师承": "teacherOf",
    "父子": "fatherOf",
    "兄弟": "brotherOf",
    "好友": "friendOf",
    "交游": "acquaintedWith",
    "同好": "sameInterest",
    "受其影响": "influencedBy",
    "开创流派": "founderOf",
    "所属流派": "memberOf",
    "代表作": "representativeWork",
    "著述": "authorOf",
    "风格特征": "styleFeature",
}

# 需要生成字面量（而非 URI 引用）的关系
LITERAL_RELS = {"字", "号", "风格特征", "代表作", "著述"}


def load_entities():
    """加载 entity.csv → { name: {id, name, type} }
       同时补全 relation.csv 中缺失的主语实体（如颜真卿等）。
    """
    entities = {}
    with open(ENTITY_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["entity_name"].strip()
            etype = row["entity_type"].strip()
            eid = row["entity_id"].strip()
            if name:
                entities[name] = {"id": eid, "name": name, "type": etype}
                # 对带注释的实体名称注册别名，如 "王羲之（父）" → "王羲之"
                import re as _re
                m = _re.match(r'^(.+?)[（(]', name)
                if m and m.group(1) not in entities:
                    entities[m.group(1)] = {"id": eid, "name": name, "type": etype}

    # 补全 relation.csv 中缺失的主语实体
    with open(RELATION_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            head = row["head"].strip()
            if head and head not in entities:
                entities[head] = {"id": "auto", "name": head, "type": "人名"}
    return entities


def load_relations():
    """加载 relation.csv → [(head, rel, tail)]"""
    relations = []
    with open(RELATION_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            head = row["head"].strip()
            rel = row["relation"].strip()
            tail = row["tail"].strip()
            if head and rel and tail:
                relations.append((head, rel, tail))
    return relations


def safe_uri_name(name):
    """将实体名称转为合法的 Turtle 本地名（PN_CHARS）"""
    name = name.strip()
    # 替换不可用于 prefixed name 的字符（括号、逗号、空格等）
    name = re.sub(r'[^\w一-鿿\-]', '_', name)
    if not name:
        name = "unknown"
    return name


def generate_ontology(entities, relations):
    """生成 ontology.ttl"""
    classes_used = set()
    props_used = set()

    for e in entities.values():
        t = e["type"]
        if t in TYPE_CLASS_MAP:
            classes_used.add(TYPE_CLASS_MAP[t])

    for _, rel, _ in relations:
        if rel in RELATION_PROP_MAP:
            props_used.add(RELATION_PROP_MAP[rel])

    lines = []
    lines.append("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
    lines.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    lines.append("@prefix owl: <http://www.w3.org/2002/07/owl#> .")
    lines.append("@prefix ex: <http://example.org/> .")
    lines.append("")

    # 类定义
    for cls in sorted(classes_used):
        lines.append(f"ex:{cls} a rdfs:Class ;")
        lines.append(f'    rdfs:label "{cls}"@en .')
        lines.append("")

    # 属性定义
    domain_range = {
        "courtesyName": ("Person", None),
        "styleName": ("Person", None),
        "styleFeature": (None, None),
        "dynasty": ("Person", "TimePeriod"),
        "birthplace": ("Person", "Place"),
        "goodAt": ("Person", "CalligraphyStyle"),
        "teacherOf": ("Person", "Person"),
        "fatherOf": ("Person", "Person"),
        "brotherOf": ("Person", "Person"),
        "friendOf": ("Person", "Person"),
        "acquaintedWith": ("Person", "Person"),
        "sameInterest": ("Person", "Person"),
        "influencedBy": ("Person", "Person"),
        "founderOf": ("Person", "School"),
        "memberOf": ("Person", "School"),
        "representativeWork": ("Person", None),
        "authorOf": ("Person", None),
    }

    for prop in sorted(props_used):
        lines.append(f"ex:{prop} a rdf:Property ;")
        if prop in domain_range:
            d, r = domain_range[prop]
            if d:
                lines.append(f"    rdfs:domain ex:{d} ;")
            if r:
                lines.append(f"    rdfs:range ex:{r} ;")
        lines.append("")

    return "\n".join(lines)


def generate_knowledge_graph(entities, relations):
    """
    生成 knowledge_graph.ttl（完整数据）
    策略：先收集所有需写的实体，统一排序输出，避免 URI 冲突与重复。
    """
    lines = []
    lines.append("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
    lines.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    lines.append("@prefix ex: <http://example.org/> .")
    lines.append("")

    # 将关系按主语分组
    subject_relations = {}
    all_tail_entities = set()
    for head, rel, tail in relations:
        if head not in entities:
            continue
        if rel not in RELATION_PROP_MAP:
            continue
        if head not in subject_relations:
            subject_relations[head] = []
        subject_relations[head].append((rel, tail))
        if rel not in LITERAL_RELS:
            all_tail_entities.add(tail)

    # 收集所有需要写出的实体 (主语 + 尾实体)
    to_write = set()
    for name in entities:
        if entities[name]["type"] in TYPE_CLASS_MAP:
            to_write.add(name)
    # 尾实体中有些不在 entity.csv 里，但也要写出基本声明
    for t in all_tail_entities:
        to_write.add(t)

    # 按类型排序：Person -> Place -> TimePeriod -> CalligraphyStyle -> ...
    type_order = {"Person": 0, "CourtesyName": 1, "Place": 2,
                  "TimePeriod": 3, "CalligraphyStyle": 4, "School": 5}

    def sort_key(name):
        if name in entities:
            et = entities[name]["type"]
            cls = TYPE_CLASS_MAP.get(et, "Unknown")
        else:
            cls = "Unknown"
        return (type_order.get(cls, 99), name)

    written_uris = set()

    for name in sorted(to_write, key=sort_key):
        uri_name = safe_uri_name(name)
        if uri_name in written_uris:
            continue

        # 确定类型
        if name in entities:
            etype = entities[name]["type"]
            if etype not in TYPE_CLASS_MAP:
                continue
            cls = TYPE_CLASS_MAP[etype]
        else:
            # 不在 entity.csv 中的尾实体，类型推断为 Person（最常见）
            cls = "Person"

        rels = subject_relations.get(name, [])
        if rels:
            lines.append(f"ex:{uri_name} a ex:{cls} ;")
            for rel, tail in rels:
                prop = RELATION_PROP_MAP[rel]
                if rel in LITERAL_RELS:
                    safe_tail = tail.replace("\\", "\\\\").replace('"', '\\"')
                    lines.append(f'    ex:{prop} "{safe_tail}"@zh ;')
                else:
                    tail_uri = safe_uri_name(tail)
                    lines.append(f"    ex:{prop} ex:{tail_uri} ;")
            # 去掉最后一个分号后的空格，用句点结束
            # 用 . 代替最后的 ;
            last_line = lines[-1]
            if last_line.endswith(" ;"):
                lines[-1] = last_line[:-2] + " ."
            else:
                # 如果只有 a ex:xxx ; 没有关系
                lines.append(" .")
            lines.append("")
        else:
            # 孤立实体，简单声明
            lines.append(f"ex:{uri_name} a ex:{cls} .")
            lines.append("")

        written_uris.add(uri_name)

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    print("加载 entity.csv ...")
    entities = load_entities()
    print(f"  共 {len(entities)} 个实体")

    # 输出类型统计
    type_counts = {}
    for e in entities.values():
        t = e["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    for t, c in sorted(type_counts.items()):
        mapped = TYPE_CLASS_MAP.get(t, "未映射")
        print(f"    {t} → {mapped}: {c}个")

    print("加载 relation.csv ...")
    relations = load_relations()
    print(f"  共 {len(relations)} 条关系")
    rel_counts = {}
    for _, r, _ in relations:
        rel_counts[r] = rel_counts.get(r, 0) + 1
    for r, c in sorted(rel_counts.items()):
        mapped = RELATION_PROP_MAP.get(r, "未映射")
        print(f"    {r} → {mapped}: {c}条")

    print("生成 ontology.ttl ...")
    ontology = generate_ontology(entities, relations)
    with open(ONTOLOGY_TTL, "w", encoding="utf-8") as f:
        f.write(ontology)
    print(f"  完成 ({len(ontology)} chars)")

    print("生成 knowledge_graph.ttl ...")
    kg = generate_knowledge_graph(entities, relations)
    with open(KG_TTL, "w", encoding="utf-8") as f:
        f.write(kg)
    print(f"  完成 ({len(kg)} chars, {kg.count(chr(10))} lines)")

    print("\n全部生成完毕！")
    print(f"  - {ONTOLOGY_TTL}")
    print(f"  - {KG_TTL}")
