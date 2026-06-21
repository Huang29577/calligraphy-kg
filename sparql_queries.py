#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一 Fuseki 查询模块
封装所有 SPARQL 查询，业务代码不直接写 SPARQL。
"""

from sparql_tool import run_sparql

PREFIX = "PREFIX ex: <http://example.org/>\n"

# ── 关系中文名 → 属性名 映射（与 generate_ttl.py 保持一致） ──
REL_TO_PROP = {
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

# 反向：属性 → 中文
PROP_TO_REL = {v: k for k, v in REL_TO_PROP.items()}


def _sparql(query_str):
    """执行 SPARQL 并返回绑定的结果列表"""
    full_query = PREFIX + query_str
    data = run_sparql(full_query)
    return data.get("results", {}).get("bindings", [])


def _val(binding, key, strip_prefix=True):
    """安全取值"""
    v = binding.get(key, {}).get("value", "")
    if strip_prefix and "/" in v:
        v = v.split("/")[-1]
    return v


def _single_value(bindings, key="o"):
    """取单结果的值"""
    if not bindings:
        return None
    v = _val(bindings[0], key)
    return v if v else None


# ═══════════════════════════════════════════════════════════
# 基础查询
# ═══════════════════════════════════════════════════════════

def query_all_properties(person_name):
    """查询一个实体的所有属性"""
    return _sparql(f"""
        SELECT ?p ?o WHERE {{ ex:{person_name} ?p ?o }}
    """)


def query_person_info(person_name):
    """查询人物基本信息：返回 dict"""
    bindings = query_all_properties(person_name)
    info = {"name": person_name, "type": None, "properties": {}}
    for b in bindings:
        p = _val(b, "p").split("#")[-1]
        o = b["o"]["value"]
        if "rdf-syntax-ns#type" in b["p"]["value"] or p == "type":
            info["type"] = o.split("/")[-1]
        else:
            info["properties"][p] = o.split("/")[-1] if "/" in o else o
    return info


# ═══════════════════════════════════════════════════════════
# 关系查询 (按中文关系名)
# ═══════════════════════════════════════════════════════════

def query_by_relation(person_name, relation_zh):
    """通用：通过中文关系名查询

        例: query_by_relation("王羲之", "师承") → 返回老师列表
        例: query_by_relation("王羲之", "字") → 返回字号
    """
    prop = REL_TO_PROP.get(relation_zh)
    if not prop:
        return []
    bindings = _sparql(f"""
        SELECT ?o WHERE {{ ex:{person_name} ex:{prop} ?o }}
    """)
    results = []
    for b in bindings:
        val = b["o"]["value"]
        if "/" in val:
            results.append(val.split("/")[-1])
        else:
            results.append(val.replace('"', ""))
    return results


def query_subjects_by_relation(person_name, relation_zh):
    """反向查询：找出与某人有指定关系的主体

        例: query_subjects_by_relation("王羲之", "师承")
            → 谁是王羲之的学生（即: ?s 师承 王羲之）
    """
    prop = REL_TO_PROP.get(relation_zh)
    if not prop:
        return []
    bindings = _sparql(f"""
        SELECT ?s WHERE {{ ?s ex:{prop} ex:{person_name} }}
    """)
    return [_val(b, "s") for b in bindings if _val(b, "s")]


# ═══════════════════════════════════════════════════════════
# 便捷查询函数
# ═══════════════════════════════════════════════════════════

def query_courtesy_name(person_name):
    """查询字号"""
    return query_by_relation(person_name, "字")


def query_style_name(person_name):
    """查询号"""
    return query_by_relation(person_name, "号")


def query_dynasty(person_name):
    """查询所处时代"""
    return query_by_relation(person_name, "所处时代")


def query_birthplace(person_name):
    """查询籍贯"""
    return query_by_relation(person_name, "籍贯")


def query_teacher(person_name):
    """查询老师（师承）"""
    return query_by_relation(person_name, "师承")


def query_students(person_name):
    """查询学生（反向师承）"""
    return query_subjects_by_relation(person_name, "师承")


def query_father(person_name):
    """查询父亲（父子关系中 head=父, tail=子）"""
    return query_by_relation(person_name, "父子")


def query_children(person_name):
    """查询子女（反向父子）"""
    return query_subjects_by_relation(person_name, "父子")


def query_brothers(person_name):
    """查询兄弟"""
    return query_by_relation(person_name, "兄弟")


def query_friends(person_name):
    """查询好友"""
    return query_by_relation(person_name, "好友")


def query_style(person_name):
    """查询擅长书体"""
    return query_by_relation(person_name, "擅长书体")


def query_school(person_name):
    """查询所属流派"""
    return query_by_relation(person_name, "所属流派")


def query_founded_school(person_name):
    """查询开创的流派"""
    return query_by_relation(person_name, "开创流派")


def query_influenced_by(person_name):
    """查询受谁影响"""
    return query_by_relation(person_name, "受其影响")


def query_influenced(person_name):
    """查询影响了谁（反向受其影响）"""
    return query_subjects_by_relation(person_name, "受其影响")


def query_works(person_name):
    """查询代表作"""
    return query_by_relation(person_name, "代表作")


def query_books(person_name):
    """查询著述"""
    return query_by_relation(person_name, "著述")


def query_style_feature(person_name):
    """查询风格特征"""
    return query_by_relation(person_name, "风格特征")


def query_relationship(person_name, relation_type):
    """统一关系查询入口，relation_type 支持中文和英文"""
    if relation_type in PROP_TO_REL:
        relation_type = PROP_TO_REL[relation_type]
    return query_by_relation(person_name, relation_type)


# ═══════════════════════════════════════════════════════════
# 高级查询
# ═══════════════════════════════════════════════════════════

def query_all_persons():
    """列出所有人物"""
    bindings = _sparql("""
        SELECT ?s WHERE { ?s a ex:Person }
    """)
    return sorted(set(_val(b, "s") for b in bindings if _val(b, "s")))


def query_persons_by_dynasty(dynasty_name):
    """按朝代查询人物"""
    bindings = _sparql(f"""
        SELECT ?s WHERE {{
            ?s ex:dynasty ex:{dynasty_name} .
            ?s a ex:Person .
        }}
    """)
    return sorted(set(_val(b, "s") for b in bindings if _val(b, "s")))


def query_persons_by_style(style_name):
    """按书体查询人物"""
    bindings = _sparql(f"""
        SELECT ?s WHERE {{
            ?s ex:goodAt ex:{style_name} .
            ?s a ex:Person .
        }}
    """)
    return sorted(set(_val(b, "s") for b in bindings if _val(b, "s")))


def query_relationship_between(person1, person2):
    """查询两人之间的关系"""
    bindings = _sparql(f"""
        SELECT ?p WHERE {{ ex:{person1} ?p ex:{person2} }}
    """)
    results = []
    for b in bindings:
        p = _val(b, "p").split("#")[-1]
        if p in PROP_TO_REL:
            results.append(PROP_TO_REL[p])
        else:
            results.append(p)
    return results


# ═══════════════════════════════════════════════════════════
# SPARQL 构建工具
# ═══════════════════════════════════════════════════════════

def build_sparql(person_name, prop_name):
    """构建一个简单的 SPARQL 查询

        Args:
            person_name: 人物名称
            prop_name: 属性名（英文，如 "courtesyName", "fatherOf"）
        Returns:
            SPARQL 查询字符串
    """
    return f"""{PREFIX}
    SELECT ?value WHERE {{
        ex:{person_name} ex:{prop_name} ?value .
    }}
    """


def execute_sparql(sparql_str):
    """执行任意 SPARQL 并返回结果"""
    data = run_sparql(PREFIX + "\n" + sparql_str)
    bindings = data.get("results", {}).get("bindings", [])
    return bindings


if __name__ == "__main__":
    # 简单测试
    import sys
    person = sys.argv[1] if len(sys.argv) > 1 else "文彭"
    print(f"=== {person} 的信息 ===")
    info = query_person_info(person)
    print(f"类型: {info['type']}")
    for k, v in info["properties"].items():
        rel = PROP_TO_REL.get(k, k)
        print(f"  {rel}: {v}")

    print(f"\n=== {person} 的老师 ===")
    print(query_teacher(person))

    print(f"\n=== {person} 的学生 ===")
    print(query_students(person))
