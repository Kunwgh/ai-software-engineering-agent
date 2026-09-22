from dotenv import load_dotenv
from langsmith import evaluate

from app.graph.graph import graph
from langchain_core.messages import HumanMessage


load_dotenv()


DATASET_NAME = "ai-software-engineering-agent-evaluation"


def run_agent(inputs):
    """
    Run our LangGraph agent for one LangSmith dataset example.
    """

    task = inputs["task"]

    result = graph.invoke(
        {
            "task": task,
            "messages": [
                HumanMessage(content=task)
            ],
        }
    )

    final_message = result["messages"][-1]

    return {
        "output": final_message.content
    }


def extract_text(value):
    """
    Convert LangChain structured content into plain text.

    Gemini/LangChain can return content as either:
    - a string
    - a list of content blocks
    """

    if isinstance(value, str):
        return value

    if isinstance(value, list):
        parts = []

        for item in value:

            # Example:
            # ["some text"]
            if isinstance(item, str):
                parts.append(item)

            # Example:
            # [{"type": "text", "text": "some text"}]
            elif isinstance(item, dict):
                text = item.get("text")

                if text:
                    parts.append(text)

        return " ".join(parts)

    return str(value)


def evaluator(run, example):
    """
    Basic evaluator.

    Checks whether the agent output contains
    at least some of the important words from
    the expected answer.
    """

    output = extract_text(
        run.outputs["output"]
    )

    expected = extract_text(
        example.outputs["expected"]
    )

    output_lower = output.lower()
    expected_lower = expected.lower()

    # Extract meaningful words from expected answer
    keywords = [
        word
        for word in expected_lower.split()
        if len(word) > 5
    ]

    matched = sum(
        1
        for keyword in keywords
        if keyword in output_lower
    )

    score = 1 if matched > 0 else 0

    return {
        "key": "basic_relevance",
        "score": score,
        "comment": (
            f"Matched {matched}/{len(keywords)} "
            "expected keywords"
        ),
    }


if __name__ == "__main__":

    print(
        f"Running evaluation on dataset: "
        f"{DATASET_NAME}"
    )

    results = evaluate(
        run_agent,
        data=DATASET_NAME,
        evaluators=[
            evaluator
        ],
        experiment_prefix="agent-evaluation",
    )

    print("\nEvaluation completed.")
    print(results)