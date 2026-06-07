# Problem statement: Student Learning assistant
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-5.2"
)

prompt = ChatPromptTemplate.from_messages(
    [
        # system prompt
        (
            "System",
            """
            You are a beginner friendly instructor
            
            Rules:
            -Explain the topic clearly.
            -Add some real-life analogy to explain the topic.
            -Give the explanation in exactly 3 bullet points.
            -Each bullet point should be short."""
        ),
        # user prompt
        (
            "Human",
            """
            Explain {topic} in {tone} way."""
        )
    ]
)

parser = StrOutputParser()

# Chain = PromptTemplate -> Model -> StrOutputParser
# Using LangChain Expression Language: prompt | model | StrOutputParser

chain = prompt | model | parser

# Invoke the chain
result = chain.invoke(
    {
        "topic": "LCEL in LangChain",
        "tone": "Beginner"
    }
)

print(result)