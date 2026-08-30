from app.database.database import get_connection
import json

def create_task(task: str) -> int:
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (task, status)
        VALUES (?, ?)
        """,
        (task, "running"),
    )

    task_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return task_id


def get_task(task_id: int):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, task, status, created_at, completed_at
        FROM tasks
        WHERE id = ?
        """,
        (task_id,),
    )

    task = cursor.fetchone()

    connection.close()

    return task


def update_task_status(
    task_id: int,
    status: str,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status = ?
        WHERE id = ?
        """,
        (status, task_id),
    )

    connection.commit()
    connection.close()

def create_agent_run(
    task_id: int,
    iteration: int,
) -> int:
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO agent_runs (task_id, iteration, status)
        VALUES (?, ?, ?)
        """,
        (task_id, iteration, "running"),
    )

    run_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return run_id


def get_agent_run(run_id: int):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, task_id, iteration, status, created_at
        FROM agent_runs
        WHERE id = ?
        """,
        (run_id,),
    )

    run = cursor.fetchone()

    connection.close()

    return run


def update_agent_run_status(
    run_id: int,
    status: str,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE agent_runs
        SET status = ?
        WHERE id = ?
        """,
        (status, run_id),
    )

    connection.commit()
    connection.close()

def create_tool_call(
    run_id: int,
    tool_name: str,
    arguments: str,
    result: str,
) -> int:
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO tool_calls (
            run_id,
            tool_name,
            arguments,
            result
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            run_id,
            tool_name,
            arguments,
            result,
        ),
    )

    tool_call_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return tool_call_id


def get_tool_calls(run_id: int):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            run_id,
            tool_name,
            arguments,
            result,
            created_at
        FROM tool_calls
        WHERE run_id = ?
        ORDER BY id
        """,
        (run_id,),
    )

    tool_calls = cursor.fetchall()

    connection.close()

    return tool_calls

def create_code_chunk(
    file_path: str,
    chunk_index: int,
    content: str,
    start_line: int,
    end_line: int,
    embedding: list[float],
) -> int:
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO code_chunks (
            file_path,
            chunk_index,
            content,
            start_line,
            end_line,
            embedding
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            file_path,
            chunk_index,
            content,
            start_line,
            end_line,
            json.dumps(embedding),
        ),
    )

    chunk_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return chunk_id

def get_code_chunks():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            file_path,
            chunk_index,
            content,
            start_line,
            end_line,
            embedding,
            created_at
        FROM code_chunks
        ORDER BY id
        """
    )

    chunks = cursor.fetchall()

    connection.close()

    return chunks