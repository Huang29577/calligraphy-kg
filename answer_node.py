#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Node6: 答案生成
根据 SPARQL 查询结果组织自然语言答案。
"""

from intent_parser import get_relation_zh


def _clean_name(raw):
    """清理显示名称：将 URI 片段转为可读文字

        处理 "王羲之_父_" → "王羲之", "长洲_今江苏苏州_" → "长洲(今江苏苏州)" 等
    """
    import re
    name = raw.strip()

    # 先去掉末尾的 _数字_ 或父/子标注
    # "王羲之_父_" → "王羲之"
    name = re.sub(r'[（(]父[）)]', '', name)
    name = re.sub(r'_父_?$', '', name)
    name = re.sub(r'_第\d+子_?$', '', name)

    # 地名格式 "长洲_今江苏苏州_" → "长洲(今江苏苏州)"
    # 只转换有明显地名的格式
    if '_今' in name or '_今' in name:
        name = name.replace('_', '')

    # 简单清理残余下划线
    name = name.replace('_', '')

    return name if name else raw


def answer_node(state):
    """答案生成节点"""
    person = state.get("person", "")
    intent = state.get("intent", "")
    relation_zh = state.get("relation_zh", intent)
    raw_results = state.get("raw_results", [])
    error = state.get("error", "")

    # 如果有错误
    if error:
        state["answer"] = f"查询出错：{error}"
        return state

    # 没有结果
    if not raw_results:
        # 尝试给个友好回复
        if person and relation_zh:
            state["answer"] = f'知识图谱中暂无"{person}"的{relation_zh}记录。'
        elif person:
            state["answer"] = f'知识图谱中暂无"{person}"的相关信息。'
        else:
            state["answer"] = "未找到相关结果，请换个问题试试。"
        return state

    # 提取结果值（支持 UNION 查询的 prop 字段）
    values = []
    prop_values = {"字": [], "号": []}
    for b in raw_results:
        has_prop = "prop" in b
        prop_name = _clean_name(b["prop"]["value"]) if has_prop else ""

        for key in ("value", "o", "s", "person", "name"):
            if key in b:
                val = b[key]["value"]
                if "/" in val:
                    val = val.split("/")[-1]
                val = _clean_name(val)
                values.append(val)
                if has_prop and prop_name in prop_values:
                    prop_values[prop_name].append(val)
                break

    # 去重
    values = list(dict.fromkeys(values))

    if not values:
        state["answer"] = "查询到结果，但无法解析。"
        return state

    # 构建友好回答
    if intent == "courtesyName":
        parts = []
        if prop_values["字"]:
            parts.append("字：" + "、".join(prop_values["字"]))
        if prop_values["号"]:
            parts.append("号：" + "、".join(prop_values["号"]))
        if parts:
            state["answer"] = f"{person}的" + "，".join(parts)
        else:
            state["answer"] = f"{person}的字号是：{values[0]}"
    elif intent == "styleName":
        state["answer"] = f"{person}的号是：{values[0]}"
    elif intent == "fatherOf":
        state["answer"] = f"{person}的父亲是：{values[0]}"
    elif intent == "teacherOf":
        answer = "、".join(values)
        state["answer"] = f"{person}的老师是：{answer}"
    elif intent == "studentsOf":
        answer = "、".join(values)
        state["answer"] = f"{person}的弟子/学生有：{answer}"
    elif intent == "birthplace":
        state["answer"] = f"{person}的籍贯是：{values[0]}"
    elif intent == "dynasty":
        state["answer"] = f"{person}是{values[0]}时期的人物"
    elif intent == "goodAt":
        answer = "、".join(values)
        state["answer"] = f"{person}擅长：{answer}"
    elif intent == "brotherOf":
        answer = "、".join(values)
        state["answer"] = f"{person}的兄弟有：{answer}"
    elif intent == "friendOf":
        answer = "、".join(values)
        state["answer"] = f"{person}的好友有：{answer}"
    elif intent == "memberOf":
        state["answer"] = f"{person}所属流派：{values[0]}"
    elif intent == "founderOf":
        state["answer"] = f"{person}开创了：{values[0]}"
    elif intent == "influencedBy":
        answer = "、".join(values)
        state["answer"] = f"{person}受{answer}的影响"
    elif intent == "representativeWork":
        answer = "、".join(values)
        state["answer"] = f"{person}的代表作有：{answer}"
    elif intent == "authorOf":
        answer = "、".join(values)
        state["answer"] = f"{person}的著作有：{answer}"
    elif intent == "styleFeature":
        state["answer"] = f"{person}的书风特点：{values[0]}"
    elif intent == "listByDynasty":
        shown = "、".join(values)
        state["answer"] = f"{person}时期的书法家共有{len(values)}位：{shown}"
    elif intent == "listByStyle":
        shown = "、".join(values)
        state["answer"] = f"擅长{person}的书法家共有{len(values)}位：{shown}"
    else:
        answer = "、".join(values)
        state["answer"] = f"{person}的{relation_zh}：{answer}"

    print(f"[Node6] 答案生成: {state['answer']}")

    return state
