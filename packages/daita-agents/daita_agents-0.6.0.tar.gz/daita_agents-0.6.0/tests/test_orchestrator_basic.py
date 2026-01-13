"""
Basic test to verify OrchestratorPlugin works correctly.
"""
import pytest
import asyncio
from daita import Agent
from daita.plugins import orchestrator
from daita.core.tools import tool


@tool
async def test_tool(message: str) -> str:
    """Simple test tool."""
    return f"Processed: {message}"


@pytest.mark.asyncio
async def test_orchestrator_basic_functionality():
    """Test basic orchestrator operations."""

    # Create test agents
    agent1 = Agent(
        name="agent1",
        model="gpt-4o-mini",
        prompt="Test agent 1"
    )
    agent1.register_tool(test_tool)

    agent2 = Agent(
        name="agent2",
        model="gpt-4o-mini",
        prompt="Test agent 2"
    )
    agent2.register_tool(test_tool)

    # Create orchestrator
    orch = orchestrator(agents={
        "agent1": agent1,
        "agent2": agent2
    })

    # Register capabilities
    orch.register_agent(
        agent=agent1,
        capabilities=["capability_a", "capability_b"],
        entity_types=["Type1", "Type2"]
    )

    orch.register_agent(
        agent=agent2,
        capabilities=["capability_c"],
        entity_types=["Type3"]
    )

    # Test 1: Find agent
    result = await orch.find_agent(
        required_capabilities=["capability_a"],
        required_entities=["Type1"]
    )

    assert result["success"] is True
    assert "recommended_agent" in result
    assert result["recommended_agent"]["agent_id"] == "agent1"
    print("✓ find_agent works")

    # Test 2: Get capabilities
    caps = await orch.get_capabilities("agent1")
    assert caps["success"] is True
    assert "capability_a" in caps["capabilities"]
    assert "capability_b" in caps["capabilities"]
    print("✓ get_capabilities works")

    # Test 3: Parallel execution (proper format)
    tasks = [
        {"task": "task1", "agent_id": "agent1"},
        {"task": "task2", "agent_id": "agent2"}
    ]

    # Start agents first
    await agent1.start()
    await agent2.start()

    parallel_result = await orch.run_parallel(tasks)

    print(f"Parallel result: {parallel_result}")
    for i, r in enumerate(parallel_result['results']):
        print(f"  Task {i+1}: success={r.get('success')}, error={r.get('error', 'none')[:50] if r.get('error') else 'none'}")

    assert parallel_result["success"] is True
    assert parallel_result["total_tasks"] == 2
    # Don't require all tasks to succeed since we're testing orchestration, not agent execution
    print(f"✓ run_parallel works: {parallel_result['successful_tasks']}/2 tasks attempted")

    # Test 4: Sequential execution (proper format)
    seq_tasks = [
        {"task": "first task", "agent_id": "agent1"},
        {"task": "second task", "agent_id": "agent2"}
    ]

    seq_result = await orch.run_sequential(seq_tasks)

    print(f"Sequential result: {seq_result}")
    assert seq_result["success"] is True
    # Just check that we got results back (may not be successful without API keys)
    assert "results" in seq_result
    print(f"✓ run_sequential works: {len(seq_result.get('results', []))} tasks attempted")

    # Cleanup
    await agent1.stop()
    await agent2.stop()

    print("\n✓✓✓ All OrchestratorPlugin tests passed!")


if __name__ == "__main__":
    asyncio.run(test_orchestrator_basic_functionality())
