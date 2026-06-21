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

    # 识别所有实体（含书体、流派等）
    all_entities = extract_all_entities(question)

    # 判断使用哪个实体作为主实体
    main_entity = None
    if dynasty and person:
        if person in dynasty:
            main_entity = dynasty  # "明"从"明朝"提取
        elif dynasty in person and len(person) > len(dynasty):
            main_entity = person   # "明"在"文徵明"中
        else:
            main_entity = person   # 不同实体，以人名为准
    elif dynasty:
        main_entity = dynasty
    elif person:
        main_entity = person
    else:
        # 尝试提取其他实体（书体、流派等）
        for ent in all_entities:
            if ent["type"] in ("书体/印风", "流派", "地名", "字号"):
                main_entity = ent["name"]
                break

    state["person"] = main_entity
    state["entities"] = all_entities

    if person:
        print(f"[Node2] 实体识别: person={person}")
    elif dynasty:
        print(f"[Node2] 实体识别: dynasty={dynasty}")
    elif main_entity:
        print(f"[Node2] 实体识别: entity={main_entity}")
    else:
        print(f"[Node2] 实体识别: 未识别到实体, entities={all_entities}")

    return state
