from langchain_core.runnables import RunnableLambda


def log_graph_step(step_name: str) -> RunnableLambda:
    return RunnableLambda(lambda x: print(f"LangGraph Step => {step_name}") or x)
