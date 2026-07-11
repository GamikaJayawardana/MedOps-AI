from app.agents.llm import get_llm

llm = get_llm()
response = llm.invoke("In one sentence, what is an emergency department?")
print(response.content)