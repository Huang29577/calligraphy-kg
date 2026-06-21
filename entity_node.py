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

    # 先识别朝代（避免"明朝"中的"明"被误识为人名）
    dynasty = extract_dynasty(question)

    # 识别人名
    person = extract_person(question)

    # 如果同时有人名和朝代，判断是否为误匹配
    if dynasty and person:
        if person in dynasty or dynasty in person:
            # 人名是由朝代词中提取的（如"明"从"明朝"提取），使用朝代
            state["person"] = dynasty
        else:
            # 真正的人名（如"王羲之"）与朝代不同时，以人名为准
            state["person"] = person
    else:
        # 优先使用朝代，其次人名
        state["person"] = dynasty or person

    # 识别所有实体
    all_entities = extract_all_entities(question)
    state["entities"] = all_entities

    if person:
        print(f"[Node2] 实体识别: person={person}")
    elif dynasty:
        print(f"[Node2] 实体识别: dynasty={dynasty}")
    else:
        print(f"[Node2] 实体识别: 未识别到实体, entities={all_entities}")

    return state
