from sparql_generator import generate_sparql

def courtesy_sparql_node(state):

    state["query"] = generate_sparql(
        state["person"],
        "courtesyName"
    )

    print("进入字号查询节点")

    return state