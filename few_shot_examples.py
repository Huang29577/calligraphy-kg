#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Few-shot SPARQL 示例库

提供自然语言 → SPARQL 的示例，用于指导 SPARQL 生成。
新关系类型只需在此添加示例即可自动支持。
"""

FEW_SHOT_EXAMPLES = [
    # ── 1. 字号查询 ──
    {
        "question": "文彭的字号是什么",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:文彭 ex:courtesyName ?value .
}""",
        "relation_zh": "字",
        "intent": "courtesyName",
        "explanation": "查询人物的'字'（表字）"
    },
    {
        "question": "文徵明的字号是什么",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:文徵明 ex:courtesyName ?value .
}""",
        "relation_zh": "字",
        "intent": "courtesyName",
        "explanation": "查询人物的'字'"
    },

    # ── 2. 号查询 ──
    {
        "question": "文彭的号是什么",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:文彭 ex:styleName ?value .
}""",
        "relation_zh": "号",
        "intent": "styleName",
        "explanation": "查询人物的'号'（别号）"
    },

    # ── 3. 父子关系 ──
    {
        "question": "文彭的父亲是谁",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:文彭 ex:fatherOf ?value .
}""",
        "relation_zh": "父子",
        "intent": "fatherOf",
        "explanation": "查询人物的父亲（注意：父子关系中主语是父亲，宾语是子女）"
    },
    {
        "question": "王羲之的父亲是谁",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:王羲之 ex:fatherOf ?value .
}""",
        "relation_zh": "父子",
        "intent": "fatherOf",
        "explanation": "查询人物的父亲"
    },

    # ── 4. 师承 ──
    {
        "question": "文彭的老师是谁",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:文彭 ex:teacherOf ?value .
}""",
        "relation_zh": "师承",
        "intent": "teacherOf",
        "explanation": "查询人物的老师（师承关系）"
    },
    {
        "question": "颜真卿的老师是谁",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:颜真卿 ex:teacherOf ?value .
}""",
        "relation_zh": "师承",
        "intent": "teacherOf",
        "explanation": "查询人物的老师"
    },

    # ── 5. 籍贯 ──
    {
        "question": "王羲之的籍贯是什么",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:王羲之 ex:birthplace ?value .
}""",
        "relation_zh": "籍贯",
        "intent": "birthplace",
        "explanation": "查询人物的籍贯（出生地）"
    },

    # ── 6. 所处时代 ──
    {
        "question": "文彭是什么朝代的人",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:文彭 ex:dynasty ?value .
}""",
        "relation_zh": "所处时代",
        "intent": "dynasty",
        "explanation": "查询人物所处的朝代或时代"
    },

    # ── 7. 擅长书体 ──
    {
        "question": "王羲之擅长什么书体",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:王羲之 ex:goodAt ?value .
}""",
        "relation_zh": "擅长书体",
        "intent": "goodAt",
        "explanation": "查询人物擅长的书法风格或书体"
    },
    {
        "question": "颜真卿擅长什么书体",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:颜真卿 ex:goodAt ?value .
}""",
        "relation_zh": "擅长书体",
        "intent": "goodAt",
        "explanation": "查询人物擅长的书体"
    },

    # ── 8. 兄弟 ──
    {
        "question": "王羲之的兄弟是谁",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:王羲之 ex:brotherOf ?value .
}""",
        "relation_zh": "兄弟",
        "intent": "brotherOf",
        "explanation": "查询人物的兄弟"
    },

    # ── 9. 好友 ──
    {
        "question": "文彭的好友有哪些",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:文彭 ex:friendOf ?value .
}""",
        "relation_zh": "好友",
        "intent": "friendOf",
        "explanation": "查询人物的好友"
    },

    # ── 10. 所属流派 ──
    {
        "question": "苏轼属于哪个流派",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:苏轼 ex:memberOf ?value .
}""",
        "relation_zh": "所属流派",
        "intent": "memberOf",
        "explanation": "查询人物所属的流派"
    },

    # ── 11. 开创流派 ──
    {
        "question": "王羲之开创了什么流派",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:王羲之 ex:founderOf ?value .
}""",
        "relation_zh": "开创流派",
        "intent": "founderOf",
        "explanation": "查询人物开创的流派"
    },

    # ── 12. 受其影响 ──
    {
        "question": "文彭受谁的影响",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:文彭 ex:influencedBy ?value .
}""",
        "relation_zh": "受其影响",
        "intent": "influencedBy",
        "explanation": "查询人物受谁的影响"
    },

    # ── 13. 代表作 ──
    {
        "question": "王羲之的代表作是什么",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:王羲之 ex:representativeWork ?value .
}""",
        "relation_zh": "代表作",
        "intent": "representativeWork",
        "explanation": "查询人物的代表作"
    },

    # ── 14. 著述 ──
    {
        "question": "孙过庭的著作是什么",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:孙过庭 ex:authorOf ?value .
}""",
        "relation_zh": "著述",
        "intent": "authorOf",
        "explanation": "查询人物的著作"
    },

    # ── 15. 风格特征 ──
    {
        "question": "文彭的书风特点是什么",
        "sparql": """
PREFIX ex: <http://example.org/>
SELECT ?value WHERE {
    ex:文彭 ex:styleFeature ?value .
}""",
        "relation_zh": "风格特征",
        "intent": "styleFeature",
        "explanation": "查询人物的书法风格特征"
    },
]

# ── 关键意图关键词映射 ──
INTENT_KEYWORDS = {
    "courtesyName": ["字号", "字是什么", "表字", "字什么"],
    "styleName": ["号是什么", "别号", "号是", "号什么", "号"],
    "fatherOf": ["父亲", "爸爸", "爹", "父是", "父亲是谁"],
    "teacherOf": ["老师", "师父", "师傅", "师承", "从师"],
    "birthplace": ["籍贯", "出生地", "故乡", "哪里人"],
    "dynasty": ["朝代", "时代", "什么朝"],
    "goodAt": ["擅长", "书体", "字体", "什么体", "书法风格"],
    "brotherOf": ["兄弟", "哥哥", "弟弟", "兄长"],
    "friendOf": ["好友", "朋友", "交游"],
    "memberOf": ["流派", "什么派", "属于"],
    "founderOf": ["开创", "创立", "创始", "开派"],
    "influencedBy": ["影响", "受谁"],
    "representativeWork": ["代表作", "代表作品", "作品"],
    "authorOf": ["著作", "著述", "写", "撰"],
    "styleFeature": ["风格", "特点", "特征", "书风"],
    "listByDynasty": ["有哪些书法家", "书法家有哪些", "书法家谁", "书法家人", "有哪些人物"],
}

# 意图 → 中文关系名映射
INTENT_TO_RELATION_ZH = {
    "courtesyName": "字",
    "styleName": "号",
    "fatherOf": "父子",
    "teacherOf": "师承",
    "birthplace": "籍贯",
    "dynasty": "所处时代",
    "goodAt": "擅长书体",
    "brotherOf": "兄弟",
    "friendOf": "好友",
    "memberOf": "所属流派",
    "founderOf": "开创流派",
    "influencedBy": "受其影响",
    "representativeWork": "代表作",
    "authorOf": "著述",
    "styleFeature": "风格特征",
    "listByDynasty": "朝代查询",
}


def get_few_shot_by_intent(intent):
    """根据意图获取对应的 few-shot 示例"""
    examples = []
    for ex in FEW_SHOT_EXAMPLES:
        if ex["intent"] == intent:
            examples.append(ex)
    return examples


def get_all_examples():
    """获取所有 few-shot 示例"""
    return FEW_SHOT_EXAMPLES


if __name__ == "__main__":
    print(f"共 {len(FEW_SHOT_EXAMPLES)} 个 Few-shot 示例")
    for ex in FEW_SHOT_EXAMPLES:
        print(f"  [{ex['intent']}] {ex['question']}")
