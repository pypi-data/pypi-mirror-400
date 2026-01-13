
from crewai import Agent, Task, Crew, Process
# Use langchain_community FakeListLLM as CrewAI supports LangChain LLMs
from langchain_community.llms import FakeListLLM
from ati_crewai import CrewAIInstrumentor

def main():
    # 1. Instrument
    print("Instrumenting CrewAI...")
    CrewAIInstrumentor().instrument()

    # 2. Setup Dummy LLM
    # CrewAI agents chat with LLM. We need to provide responses.
    # The flow might be complex, so we provide many generic responses.
    # Note: CrewAI might expect ChatModel (messages input). FakeListLLM is a completion model.
    # It usually adapts, but if it fails we might need a FakeChatModel.
    responses = [
        "Thought: I will start working.\nFinal Answer: Task Completed.",
    ]
    llm = FakeListLLM(responses=responses)

    # 3. Define Agents
    researcher = Agent(
        role='Researcher',
        goal='Analyze ATI',
        backstory='Expert researcher',
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # 4. Define Tasks
    task = Task(
        description='Analyze the ATI project structure.',
        agent=researcher,
        expected_output='A report.'
    )

    # 5. Define Crew
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    # 6. Kickoff
    print("\n--- Starting Crew Kickoff ---\n")
    result = crew.kickoff()
    print(f"\nResult: {result}")

    # 7. Uninstrument
    CrewAIInstrumentor().uninstrument()

if __name__ == "__main__":
    main()
