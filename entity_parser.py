#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实体识别模块
从 entity.csv 和 relation.csv 加载所有人物名称，用于问题中的实体识别。

支持从以下来源加载：
  1. entity.csv 中类型为 "人名" 的实体
  2. relation.csv 中所有主语
  3. Fuseki 中所有 Person 实例（备用）
  4. 已知书法家补充列表（覆盖常见缺失）
"""

import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENTITY_CSV = os.path.join(BASE_DIR, "entity.csv")
RELATION_CSV = os.path.join(BASE_DIR, "relation.csv")

# 已知书法家补充列表（当 CSV 数据缺失时使用）
KNOWN_CALLIGRAPHERS = [
    "何震", "文彭", "文徵明", "王羲之", "王献之",
    "颜真卿", "柳公权", "欧阳询", "赵孟頫", "苏轼",
    "黄庭坚", "米芾", "蔡襄", "褚遂良", "虞世南",
    "张旭", "怀素", "孙过庭", "钟繇", "李斯",
    "邓石如", "吴昌硕", "齐白石", "徐渭", "董其昌",
]


def load_all_persons():
    """加载所有人名"""
    persons = set()

    # 1. 从 entity.csv 加载
    if os.path.exists(ENTITY_CSV):
        with open(ENTITY_CSV, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["entity_type"].strip() == "人名":
                    name = row["entity_name"].strip()
                    if name:
                        # 处理 "王羲之（父）" → 也添加 "王羲之"
                        import re
                        m = re.match(r'^(.+?)[（(]', name)
                        if m:
                            persons.add(m.group(1))
                        persons.add(name)

    # 2. 从 relation.csv 加载所有主语
    if os.path.exists(RELATION_CSV):
        with open(RELATION_CSV, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                head = row["head"].strip()
                if head:
                    persons.add(head)

    # 3. 补充已知书法家
    for name in KNOWN_CALLIGRAPHERS:
        persons.add(name)

    # 去重并排序（长名称优先）
    persons = list(persons)
    persons.sort(key=lambda x: (-len(x), x))
    return persons


# 全局缓存
_all_persons = None


def get_all_persons():
    """获取所有人名列表（惰性加载）"""
    global _all_persons
    if _all_persons is None:
        _all_persons = load_all_persons()
    return _all_persons


def extract_person(question):
    """从问题中提取人名

        按名称长度降序匹配，优先匹配长名称。
        返回匹配到的人名，未匹配返回 None。
    """
    if not question:
        return None
    persons = get_all_persons()
    for p in persons:
        if p in question:
            return p
    return None


def extract_all_entities(question):
    """从问题中提取所有实体（人、地、书体、流派等）"""
    if not question:
        return []
    found = []

    # 加载所有实体名
    entities = {}
    if os.path.exists(ENTITY_CSV):
        with open(ENTITY_CSV, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["entity_name"].strip()
                etype = row["entity_type"].strip()
                if name:
                    entities[name] = etype
                    # 别名注册
                    import re
                    m = re.match(r'^(.+?)[（(]', name)
                    if m and m.group(1) not in entities:
                        entities[m.group(1)] = etype

    # 按长度降序匹配
    for name in sorted(entities.keys(), key=lambda x: (-len(x), x)):
        if name in question:
            found.append({"name": name, "type": entities[name]})

    return found


def extract_dynasty(question):
    """从问题中提取朝代名称

        匹配朝代实体（时间类型），同时支持"明代"→"明"、"唐代"→"唐"等变体。
    """
    if not question:
        return None

    # 从 entity.csv 加载朝代实体
    dynasties = []
    if os.path.exists(ENTITY_CSV):
        with open(ENTITY_CSV, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["entity_type"].strip() == "时间":
                    dynasties.append(row["entity_name"].strip())

    # 也支持带"代"或"朝"的称呼
    dynasty_map = {}
    for d in dynasties:
        dynasty_map[d] = d
        dynasty_map[d + "代"] = d  # 明→明代, 唐→唐代
        dynasty_map[d + "朝"] = d  # 明→明朝, 唐→唐朝

    # 按长度降序匹配
    for name in sorted(dynasty_map.keys(), key=lambda x: (-len(x), x)):
        if name in question:
            return dynasty_map[name]

    return None


# 快速测试
if __name__ == "__main__":
    persons = get_all_persons()
    print(f"共加载 {len(persons)} 个人名")

    test_questions = [
        "王羲之的父亲是谁",
        "文徵明的字号是什么",
        "颜真卿的老师是谁",
        "苏轼擅长什么书体",
        "何震的字号是什么",
        "邓石如的籍贯是什么",
    ]
    for q in test_questions:
        p = extract_person(q)
        print(f"问题: {q} → 识别: {p}")
