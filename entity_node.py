#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Node2: 实体识别
从问题中识别出人名、地名、朝代、书体、流派等实体。
"""

from entity_parser import extract_person, extract_dynasty, extract_all_entities


def entity_node(state):
    """实体识别节点

        从问题中识别实体，包括人名、朝代、地名、书体、流派等。
        优先识别人名，如无人名则尝试识别朝代等。
    """
    question = state.get("question", "")

    # 识别人名
    person = extract_person(question)

    # 识别朝代（用于"明代的书法家"这类查询）
    dynasty = None
    if not person:
        dynasty = extract_dynasty(question)

    # 识别所有实体
    all_entities = extract_all_entities(question)

    # 优先使用人名，其次朝代
    state["person"] = person or dynasty
    state["entities"] = all_entities

    if person:
        print(f"[Node2] 实体识别: person={person}")
    elif dynasty:
        print(f"[Node2] 实体识别: dynasty={dynasty}")
    else:
        print(f"[Node2] 实体识别: 未识别到实体, entities={all_entities}")

    return state
