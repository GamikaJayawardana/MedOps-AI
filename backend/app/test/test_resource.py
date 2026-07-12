from app.agents.resource import resource_agent

situation = (
    "The respiratory ward is at 100% occupancy with 0 beds free and patients "
    "still arriving. What does policy say we should do, and can we do it?"
)

print("=== SITUATION ===")
print(situation)
print("\n=== RESOURCE RECOMMENDATION ===")
print(resource_agent(situation))