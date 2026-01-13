# Framework Integration

Guide to integrating CGP SDK with popular AI agent frameworks.

## CrewAI

### Basic Integration

```python
from crewai import Agent, Task, Crew, LLM
from cgp_sdk import CGPClient

def handle_feedback(trace_id, data):
    print(f"Feedback for {trace_id}: {data.get('feedback')}")

client = CGPClient(
    api_key="sk_...",
    on_feedback=handle_feedback,
)

# Create CrewAI agent
llm = LLM(model="anthropic/claude-sonnet-4-20250514")
agent = Agent(
    role="Research Analyst",
    goal="Analyze market trends",
    backstory="Expert analyst with 10 years experience",
    llm=llm,
)

task = Task(
    description="Analyze Q4 2024 market trends",
    agent=agent,
    expected_output="Market analysis report",
)

crew = Crew(agents=[agent], tasks=[task])

# Wrap execution with trace
with client.trace(agent_type="unified", goal="Analyze market trends") as trace:
    result = crew.kickoff()
    trace.set_output(str(result.raw))
    trace.set_reasoning("CrewAI workflow completed")
    trace.add_context("framework", "crewai")

client.wait_for_feedback(timeout=30)
client.close()
```

### Multi-Agent Crew

```python
# Trace each agent separately
planner = Agent(role="Planner", ...)
executor = Agent(role="Executor", ...)

plan_task = Task(description="Create plan", agent=planner)
exec_task = Task(description="Execute plan", agent=executor)

crew = Crew(agents=[planner, executor], tasks=[plan_task, exec_task])

# Unfortunately CrewAI runs tasks sequentially internally,
# so we trace the entire workflow as one
with client.trace(agent_type="unified", goal="Multi-agent workflow") as trace:
    result = crew.kickoff()
    trace.set_output(str(result.raw))
```

---

## LangChain

### Basic Agent

```python
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from cgp_sdk import CGPClient

client = CGPClient(api_key="sk_...", on_feedback=handle_feedback)

llm = ChatOpenAI(model="gpt-4")
agent = initialize_agent(
    tools=[...],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

with client.trace(agent_type="executor", goal=user_query) as trace:
    result = agent.run(user_query)
    trace.set_output(result)
    trace.add_context("framework", "langchain")

client.wait_for_feedback(timeout=30)
client.close()
```

### LangGraph

```python
from langgraph.graph import StateGraph
from cgp_sdk import CGPClient

client = CGPClient(api_key="sk_...", on_feedback=handle_feedback)

# Define your graph
graph = StateGraph(...)
app = graph.compile()

with client.trace(agent_type="unified", goal="Process workflow") as trace:
    result = app.invoke({"input": user_input})
    trace.set_output(str(result))
    trace.add_context("framework", "langgraph")

client.wait_for_feedback(timeout=30)
client.close()
```

### LCEL Chains

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template("Analyze: {input}")
llm = ChatOpenAI()
chain = prompt | llm

with client.trace(agent_type="executor", goal="Analyze input") as trace:
    result = chain.invoke({"input": user_input})
    trace.set_output(result.content)
```

---

## AutoGen

```python
from autogen import AssistantAgent, UserProxyAgent
from cgp_sdk import CGPClient

client = CGPClient(api_key="sk_...", on_feedback=handle_feedback)

assistant = AssistantAgent(name="assistant", ...)
user_proxy = UserProxyAgent(name="user_proxy", ...)

with client.trace(agent_type="unified", goal=task) as trace:
    user_proxy.initiate_chat(assistant, message=task)

    # Capture conversation
    messages = assistant.chat_messages[user_proxy]
    output = "\n".join([m["content"] for m in messages if m["role"] == "assistant"])
    trace.set_output(output)
    trace.add_context("framework", "autogen")

client.wait_for_feedback(timeout=30)
client.close()
```

---

## GPT-Researcher

```python
from gpt_researcher import GPTResearcher
from cgp_sdk import CGPClient

client = CGPClient(api_key="sk_...", on_feedback=handle_feedback)
researcher = GPTResearcher(query=query)

# Trace planning phase
with client.trace(agent_type="planner", goal=f"Plan research: {query}") as trace:
    context = await researcher.conduct_research()
    trace.set_output(f"Agent: {researcher.agent}, Role: {researcher.role}")
    trace.add_context("framework", "gpt-researcher")

# Trace report generation
with client.trace(agent_type="executor", goal=f"Generate report: {query}") as trace:
    report = await researcher.write_report()
    sources = researcher.get_source_urls()
    trace.set_output(report)
    trace.add_context("sources_count", len(sources))

client.wait_for_feedback(timeout=30)
client.close()
```

---

## OpenAI Assistants API

```python
from openai import OpenAI
from cgp_sdk import CGPClient

openai_client = OpenAI()
cgp_client = CGPClient(api_key="sk_...", on_feedback=handle_feedback)

assistant = openai_client.beta.assistants.create(...)
thread = openai_client.beta.threads.create()

with cgp_client.trace(agent_type="executor", goal=user_message) as trace:
    # Add message and run
    openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message,
    )

    run = openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Get response
    messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
    response = messages.data[0].content[0].text.value

    trace.set_output(response)
    trace.add_context("framework", "openai-assistants")

cgp_client.wait_for_feedback(timeout=30)
cgp_client.close()
```

---

## Custom Agents

For custom agent implementations:

```python
from cgp_sdk import CGPClient

client = CGPClient(api_key="sk_...", on_feedback=handle_feedback)

class MyCustomAgent:
    def __init__(self):
        self.reasoning_log = []

    def think(self, query):
        # Your reasoning logic
        self.reasoning_log.append(f"Analyzing: {query}")
        return "thought"

    def act(self, thought):
        # Your action logic
        self.reasoning_log.append(f"Acting on: {thought}")
        return "result"

    def run(self, query):
        thought = self.think(query)
        result = self.act(thought)
        return result

agent = MyCustomAgent()

with client.trace(agent_type="unified", goal=query) as trace:
    result = agent.run(query)
    trace.set_output(result)
    trace.set_reasoning("\n".join(agent.reasoning_log))
    trace.add_context("framework", "custom")

client.wait_for_feedback(timeout=30)
client.close()
```

---

## Best Practices for Framework Integration

### 1. Trace at the Right Level

- **Planner traces**: Decision-making, routing, planning phases
- **Executor traces**: Action execution, tool use, response generation
- **Unified traces**: Single-agent workflows where separation isn't clear

### 2. Capture Meaningful Context

```python
trace.add_context("framework", "crewai")
trace.add_context("model", "gpt-4")
trace.add_context("temperature", 0.7)
trace.add_context("tools_used", ["search", "calculator"])
```

### 3. Include Reasoning When Available

Many frameworks expose intermediate reasoning:

```python
# CrewAI
trace.set_reasoning(str(result.tasks_output))

# LangChain (with verbose)
trace.set_reasoning(agent.agent.llm_chain.verbose_output)

# Custom
trace.set_reasoning("\n".join(agent.thought_log))
```

### 4. Handle Async Frameworks

```python
# For async frameworks like GPT-Researcher
async def traced_research(query):
    with client.trace(agent_type="planner", goal=query) as trace:
        result = await researcher.conduct_research()
        trace.set_output(result)

# Run with asyncio
import asyncio
asyncio.run(traced_research("My query"))
```
