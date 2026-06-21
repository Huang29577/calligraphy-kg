from sparql_generator import generate_sparql

def father_sparql_node(state):

    state["query"] = generate_sparql(
        state["person"],
        "fatherOf"
    )

    print("进入父亲查询节点")

    return state