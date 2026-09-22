import os

from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

client = Client()

dataset_name = "ai-software-engineering-agent-evaluation"

try:
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Basic evaluation dataset for the AI Software Engineering Agent",
    )
except Exception:
    datasets = list(client.list_datasets(dataset_name=dataset_name))
    dataset = datasets[0]


examples = [
    {
        "input": "List the files in the current repository.",
        "expected_output": "The agent should identify and list the files present in the repository.",
    },
    {
        "input": "Explain how the agent executes tools.",
        "expected_output": "The answer should explain the tool execution flow and mention ToolExecutor.",
    },
    {
        "input": "Explain how RAG retrieves repository context.",
        "expected_output": "The answer should explain retrieval using embeddings, SQLite code chunks, similarity, and context construction.",
    },
]


for example in examples:
    client.create_example(
        inputs={"task": example["input"]},
        outputs={"expected": example["expected_output"]},
        dataset_id=dataset.id,
    )

print(f"Dataset ready: {dataset_name}")