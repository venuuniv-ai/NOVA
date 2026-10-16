import os

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import make_url

from app.database import engine
from app.main import app
from app.seed import DEMO_DEVICES, seed_demo


@pytest.fixture(scope="session", autouse=True)
def migrated_database():
    # Refuse destructive test cleanup on a non-test database, even if misconfigured.
    url = make_url(os.environ.get("DATABASE_URL", ""))
    if not url.database or not url.database.endswith("_test"):
        pytest.exit("Tests require a dedicated PostgreSQL database ending in _test.")
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    command.check(config)
    seed_demo()
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_tasks(migrated_database):
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE auth_device_registrations, event_dead_letters, event_jobs, "
                "event_subscriptions, "
                "event_task_projections, "
                "event_inbox, event_outbox, auth_identities, experiment_results, "
                "experiment_assignments, experiment_definitions, "
                "evaluation_scenario_results, evaluation_runs, evaluation_datasets, "
                "memory_retrievals, memory_mutations, memory_audits, memory_embeddings, "
                "memory_records, media_artifacts, visual_observations, processor_runs, "
                "perception_runs, "
                "media_assets, model_calls, model_budget_days, action_mutations, "
                "action_executions, approval_decisions, audit_events, "
                "action_proposals, proactive_triggers, context_events, "
                "tool_calls, agent_runs, agent_executions, task_events, tasks"
            )
        )

    from app.memory.service import seed_memories

    seed_memories()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def devices():
    return {device["type"]: str(device["id"]) for device in DEMO_DEVICES}


@pytest.fixture
def task(client, devices):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Find somewhere for dinner with Sarah tomorrow after my meeting.",
            "description": "Deterministic Phase 1 continuity demonstration.",
            "origin_device_id": devices["DESKTOP"],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()
