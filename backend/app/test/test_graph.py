import app.agents.toy_graph


app_graph = app.agents.toy_graph.build_graph()

for test_pressure in [0.2, 0.6, 0.96]:
    result = app_graph.invoke({
        "pressure": test_pressure,
        "classification": "",
        "action": "",
    })
    print(f"pressure={test_pressure}")
    print(f"  classification: {result['classification']}")
    print(f"  action: {result['action']}")
    print()