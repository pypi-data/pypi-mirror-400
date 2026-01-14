import tempfile
from pathlib import Path
import unittest

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from mengram import ExperienceIn, MemoryClient


def embed_len(text: str):
    val = float(len(text))
    return np.array([val, val], dtype=np.float32)


class PraxisRetrievalTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tmpdir.name) / "praxis.db"
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=engine)
        session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        self.client = MemoryClient(session_factory=session_factory, embed_fn=embed_len)

        # Seed experiences
        # Env A, internal goal X (success)
        self.client.record_experience(
            ExperienceIn(
                scope="user",
                entity_id="u1",
                env_pre={"screen": "checkout", "error": "timeout"},
                internal_state={"goal": "complete purchase"},
                action_type="retry",
                success=True,
                reward=1.0,
            )
        )
        # Env A, internal goal Y (different goal)
        self.client.record_experience(
            ExperienceIn(
                scope="user",
                entity_id="u1",
                env_pre={"screen": "checkout", "error": "timeout"},
                internal_state={"goal": "check network"},
                action_type="inspect_network",
                success=True,
                reward=0.5,
            )
        )
        # Env B (different)
        self.client.record_experience(
            ExperienceIn(
                scope="user",
                entity_id="u1",
                env_pre={"screen": "home"},
                internal_state={"goal": "complete purchase"},
                action_type="noop",
                success=False,
                reward=0.0,
            )
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_env_gate_filters_by_tau(self):
        results = self.client.retrieve_experiences(
            env_state={"screen": "profile"},  # disjoint env
            internal_state={"goal": "complete purchase"},
            scope="user",
            entity_id="u1",
            mode="prax",
            tau_env=0.5,
        )
        self.assertEqual(len(results), 0)

    def test_env_match_internal_rerank(self):
        results = self.client.retrieve_experiences(
            env_state={"screen": "checkout", "error": "timeout"},
            internal_state={"goal": "complete purchase"},
            scope="user",
            entity_id="u1",
            mode="prax",
            tau_env=0.1,
        )
        self.assertGreaterEqual(len(results), 2)
        # Internal goal complete purchase should rank above check network for same env
        self.assertEqual(results[0].action_type, "retry")

    def test_scope_isolation_in_prax(self):
        results = self.client.retrieve_experiences(
            env_state={"screen": "checkout", "error": "timeout"},
            internal_state={"goal": "complete purchase"},
            scope="user",
            entity_id="other",
            mode="prax",
            tau_env=0.1,
        )
        self.assertEqual(len(results), 0)

    def test_episode_context_window(self):
        # Build an episode with 4 steps
        for idx in range(4):
            self.client.record_experience(
                ExperienceIn(
                    scope="user",
                    entity_id="u2",
                    episode_id="ep1",
                    step_index=idx,
                    env_pre={"screen": "flow", "step": idx},
                    internal_state={"goal": "flow"},
                    action_type=f"step_{idx}",
                    success=True,
                    reward=1.0,
                )
            )
        results = self.client.retrieve_experiences(
            env_state={"screen": "flow", "step": 2},
            internal_state={"goal": "flow"},
            scope="user",
            entity_id="u2",
            mode="prax",
            tau_env=0.1,
            context_window=1,
            k=1,
        )
        self.assertEqual(len(results), 1)
        ctx = results[0].context_steps or []
        self.assertEqual([c.step_index for c in ctx], [1, 2, 3])

    def test_tie_break_by_reward_and_success(self):
        # Same env/internal, different rewards
        self.client.record_experience(
            ExperienceIn(
                scope="user",
                entity_id="u3",
                env_pre={"screen": "checkout"},
                internal_state={"goal": "purchase"},
                action_type="low_reward",
                success=False,
                reward=0.1,
            )
        )
        self.client.record_experience(
            ExperienceIn(
                scope="user",
                entity_id="u3",
                env_pre={"screen": "checkout"},
                internal_state={"goal": "purchase"},
                action_type="high_reward",
                success=True,
                reward=0.9,
            )
        )
        results = self.client.retrieve_experiences(
            env_state={"screen": "checkout"},
            internal_state={"goal": "purchase"},
            scope="user",
            entity_id="u3",
            mode="prax",
            tau_env=0.0,
            k=2,
        )
        self.assertEqual(results[0].action_type, "high_reward")


if __name__ == "__main__":
    unittest.main()
