#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPARQL 生成器
根据人物 + 意图自动生成 SPARQL 查询。
使用 few-shot 示例作为模板，自动替换人名。
"""

import re
from few_shot_examples import (
    INTENT_TO_RELATION_ZH,
    FEW_SHOT_EXAMPLES,
    get_few_shot_by_intent,
)

# 意图 → SPARQL 属性名映射
INTENT_TO_PROP = {
    "courtesyName": "courtesyName",
    "styleName": "styleName",
    "fatherOf": "fatherOf",
    "teacherOf": "teacherOf",
    "birthplace": "birthplace",
    "dynasty": "dynasty",
    "goodAt": "goodAt",
    "brotherOf": "brotherOf",
    "friendOf": "friendOf",
    "sameInterest": "sameInterest",
    "acquaintedWith": "acquaintedWith",
    "memberOf": "memberOf",
    "founderOf": "founderOf",
    "influencedBy": "influencedBy",
    "representativeWork": "representativeWork",
    "authorOf": "authorOf",
    "styleFeature": "styleFeature",
}


def _replace_person_in_sparql(sparql_template, new_person):
    """将 SPARQL 模板中的人物名替换为目标人物

        查找 WHERE { 子句中的 ex:某某某（非属性名），替换为目标人物。
    """
    # 查找 WHERE 子句中的第一个 ex:实体名 (实体名在 property 之前或之后)
    # 模式: ex:实体名 ex:属性 或 ex:属性 ex:实体名
    where_match = re.search(r'WHERE\s*\{', sparql_template)
    if not where_match:
        return sparql_template.replace("文彭", new_person)

    where_clause = sparql_template[where_match.start():]

    # 查找 ex:中文名（非 ex:courtesyName 等英文属性）
    # 匹配 ex: 后跟中文字符（或中文+字母的组合）
    entity_match = re.search(
        r'ex:([一-鿿\w]+)\s+ex:(?:courtesyName|styleName|fatherOf|teacherOf|'
        r'birthplace|dynasty|goodAt|brotherOf|friendOf|memberOf|founderOf|'
        r'influencedBy|representativeWork|authorOf|styleFeature|sameInterest|acquaintedWith)',
        where_clause
    )
    if entity_match:
        old_name = entity_match.group(1)
        # 确保这是一个人名（包含中文，不是纯英文）
        if re.search(r'[一-鿿]', old_name):
            return sparql_template.replace(f"ex:{old_name}", f"ex:{new_person}")

    # 兜底：直接替换固定的属性值对模式
    # 如 ex:王羲之 ex:birthplace → ex:文彭 ex:birthplace
    for known_person in ["王羲之", "文彭", "文徵明", "颜真卿", "苏轼", "欧阳询",
                         "赵孟頫", "孙过庭", "王献之"]:
        if known_person in sparql_template:
            return sparql_template.replace(f"ex:{known_person}", f"ex:{new_person}")

    # 最后兜底：直接用生成模板
    return sparql_template


def generate_sparql(person_name, intent):
    """根据人物和意图生成 SPARQL 查询字符串

        特殊处理：
        - "courtesyName"(字号)：同时查询 courtesyName(字) 和 styleName(号)
        - "listByDynasty"(朝代书法家)：按朝代列出人物
    """

    # ── 特殊：按朝代列出人物（必须在 prop 检查之前） ──
    if intent == "listByDynasty":
        return f"""
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {{
    ?value a ex:Person .
    ?value ex:dynasty ex:{person_name} .
}}
ORDER BY ?value
""".strip()

    # ── 特殊：按书体列出人物（反向擅长） ──
    if intent == "listByStyle":
        return f"""
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {{
    ?value a ex:Person .
    ?value ex:goodAt ex:{person_name} .
}}
ORDER BY ?value
""".strip()

    # ── 特殊：查询弟子/学生（反向师承） ──
    if intent == "studentsOf":
        return f"""
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {{
    ?value ex:teacherOf ex:{person_name} .
}}
ORDER BY ?value
""".strip()

    prop = INTENT_TO_PROP.get(intent)
    if not prop:
        return ""

    # ── 特殊：字号查询同时查"字"和"号" ──
    if intent == "courtesyName":
        return f"""
PREFIX ex: <http://example.org/>
SELECT ?value ?prop WHERE {{
    {{ ex:{person_name} ex:courtesyName ?value . BIND("字" AS ?prop) }}
    UNION
    {{ ex:{person_name} ex:styleName ?value . BIND("号" AS ?prop) }}
}}
""".strip()

    # 先用 few-shot 模板
    examples = get_few_shot_by_intent(intent)
    if examples:
        template = examples[0]["sparql"]
        # 替换模板中的人名
        result = _replace_person_in_sparql(template, person_name)
        return result.strip()

    # 兜底：简单模板
    return f"""
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {{
    ex:{person_name} ex:{prop} ?value .
}}
""".strip()


def generate_sparql_with_examples(person_name, intent, num_examples=3):
    """生成包含 few-shot 示例提示的 SPARQL（供大模型使用）"""
    intents_list = list(INTENT_TO_PROP.keys())
    if intent not in intents_list:
        return "", ""

    # 同意图示例
    examples = get_few_shot_by_intent(intent)
    prompt_parts = []
    for ex in examples[:num_examples]:
        prompt_parts.append(f"问题: {ex['question']}")
        prompt_parts.append(f"SPARQL:\n{ex['sparql'].strip()}")
        prompt_parts.append("")

    rel_zh = INTENT_TO_RELATION_ZH.get(intent, intent)
    prompt_parts.append(f"问题: {person_name}的{rel_zh}是什么")
    prompt_parts.append("SPARQL:")
    prompt = "\n".join(prompt_parts)

    # 生成 SPARQL
    sparql = generate_sparql(person_name, intent)
    return sparql, prompt


# 快速测试
if __name__ == "__main__":
    tests = [
        ("文彭", "courtesyName"),
        ("文彭", "fatherOf"),
        ("文彭", "birthplace"),
        ("颜真卿", "teacherOf"),
        ("苏轼", "goodAt"),
        ("欧阳询", "dynasty"),
        ("赵孟頫", "memberOf"),
    ]
    for person, intent in tests:
        sparql = generate_sparql(person, intent)
        print(f"=== {person} / {intent} ===")
        print(sparql)
        print()
