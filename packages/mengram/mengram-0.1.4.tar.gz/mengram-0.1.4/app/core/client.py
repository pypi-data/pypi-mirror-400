from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Iterable, List, Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.auto.models import (
    ALLOWED_MEMORY_TYPES,
    ALLOWED_SCOPES,
    Extractor,
    Interaction,
    MemoryCandidate,
)
from app.models.memory import Experience, Memory
from app.models.memory import Event, Rule
from app.rules.models import (
    InjectMemoryAction,
    NotifyAction,
    RuleAction,
    RuleCondition,
    RuleEvaluationResult,
    RuleOut,
    normalize_actions,
)
from app.schemas.memory import (
    ForgetIn,
    MemoryOut,
    ReflectIn,
    RememberIn,
)
from app.schemas.experience import ExperienceIn, ExperienceOut
from app.services.memory_service import (
    forget_memory,
    recall_memories,
    reflect_session,
    remember_memory,
)
from app.services.embedding import embed_text
from app.utils.text import normalize_text
from app.utils.experience import summarize_state, flatten_env, env_similarity
from app.utils.time import new_id, now_utc
from app.services.embedding import vec_to_str, str_to_vec
from app.services.scoring import cosine_sim


class MemoryClient:
    """Programmatic interface that mirrors the REST API surface."""

    def __init__(
        self,
        *,
        session_factory: Optional[Callable[[], Session]] = None,
        embed_fn: Optional[Callable[[str], Any]] = None,
        redact_pii: bool = True,
    ):
        self._session_factory = session_factory or SessionLocal
        self._embed_fn = embed_fn or embed_text
        self._redact_pii = redact_pii

    @contextmanager
    def _get_session(self, session: Optional[Session] = None):
        if session is not None:
            yield session
            return
        db = self._session_factory()
        try:
            yield db
        finally:
            db.close()

    def remember(
        self,
        *,
        content: str,
        type: str,
        scope: str,
        entity_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.0,
        ttl_hours: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        session: Optional[Session] = None,
    ) -> MemoryOut:
        payload = RememberIn(
            content=content,
            type=type,
            scope=scope,
            entity_id=entity_id,
            tags=tags,
            importance=importance,
            ttl_hours=ttl_hours,
            metadata=metadata,
        )
        with self._get_session(session) as db:
            return remember_memory(db, payload, embed_fn=self._embed_fn, redact=self._redact_pii)

    def recall(
        self,
        *,
        query: str,
        k: int = 8,
        scope: Optional[str] = None,
        entity_id: Optional[str] = None,
        as_of: Optional[datetime | str] = None,
        session: Optional[Session] = None,
    ) -> List[MemoryOut]:
        as_of_value: Optional[str]
        if isinstance(as_of, datetime):
            as_of_value = as_of.isoformat()
        else:
            as_of_value = as_of
        with self._get_session(session) as db:
            return recall_memories(
                db,
                query=query,
                k=k,
                scope=scope,
                entity_id=entity_id,
                as_of=as_of_value,
                embed_fn=self._embed_fn,
            )

    def reflect(
        self,
        *,
        session_id: str,
        budget_tokens: int = 1500,
        session: Optional[Session] = None,
    ):
        payload = ReflectIn(session_id=session_id, budget_tokens=budget_tokens)
        with self._get_session(session) as db:
            return reflect_session(db, payload, embed_fn=self._embed_fn)

    def create_rule(
        self,
        *,
        condition: RuleCondition | Dict[str, Any],
        actions: Iterable[RuleAction | Dict[str, Any]] | Dict[str, Any],
        description: Optional[str] = None,
        enabled: bool = True,
        session: Optional[Session] = None,
    ) -> RuleOut:
        if isinstance(condition, dict):
            rule_condition = RuleCondition(**condition)
        else:
            rule_condition = condition

        actions_input: Iterable[RuleAction | Dict[str, Any]]
        if isinstance(actions, dict) and "actions" in actions:
            actions_input = actions["actions"]
        else:
            actions_input = actions

        action_models = normalize_actions(list(actions_input))
        with self._get_session(session) as db:
            rid = new_id()
            rule = Rule(
                id=rid,
                if_json=rule_condition.model_dump(),
                then_json={"actions": [a.model_dump() for a in action_models]},
                guardrails_json={},
                active=enabled,
                description=description,
                created_at=now_utc(),
            )
            db.add(rule)
            db.commit()
            db.refresh(rule)

            return RuleOut(
                id=rule.id,
                condition=rule_condition,
                actions=action_models,
                description=rule.description,
                enabled=rule.active,
                created_at=rule.created_at,
                last_triggered_at=rule.last_triggered_at,
            )

    def record_event(
        self,
        *,
        event_type: str,
        tool_name: Optional[str] = None,
        scope: Optional[str] = None,
        entity_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        session: Optional[Session] = None,
    ) -> RuleEvaluationResult:
        with self._get_session(session) as db:
            now = now_utc()
            event = Event(
                id=new_id(),
                event_type=event_type,
                tool_name=tool_name,
                scope=scope,
                entity_id=entity_id,
                payload=payload or {},
                created_at=now,
            )
            db.add(event)
            db.flush()

            triggered_rule_ids: List[str] = []
            actions: List[RuleAction] = []
            new_memories: List[Dict[str, Any]] = []

            rules = db.query(Rule).filter(Rule.active.is_(True)).all()
            for rule in rules:
                if not rule.if_json:
                    continue
                try:
                    condition = RuleCondition(**rule.if_json)
                except Exception:
                    continue

                if condition.event_type != event_type:
                    continue
                if condition.tool_name and condition.tool_name != tool_name:
                    continue
                if condition.scope and condition.scope != scope:
                    continue
                if condition.entity_id and condition.entity_id != entity_id:
                    continue

                eval_scope = condition.scope or scope
                eval_entity = condition.entity_id or entity_id
                if eval_scope is None:
                    continue

                window_start = now - timedelta(minutes=condition.window_minutes)
                q = db.query(Event).filter(
                    Event.created_at >= window_start,
                    Event.event_type == condition.event_type,
                    Event.scope == eval_scope,
                )
                if condition.tool_name:
                    q = q.filter(Event.tool_name == condition.tool_name)
                if eval_entity:
                    q = q.filter(Event.entity_id == eval_entity)

                count = q.count()
                if count < condition.threshold_count:
                    continue

                if rule.last_triggered_at and rule.last_triggered_at >= window_start:
                    continue

                rule.last_triggered_at = now
                triggered_rule_ids.append(rule.id)

                rule_actions = normalize_actions((rule.then_json or {}).get("actions", []))
                for action in rule_actions:
                    actions.append(action)
                    if isinstance(action, InjectMemoryAction):
                        mem = self.remember(
                            content=action.content,
                            type="semantic",
                            scope=action.scope or eval_scope,
                            entity_id=action.entity_id or eval_entity,
                            tags=action.tags,
                            importance=action.importance or 0.0,
                            metadata={"source": "rule", "rule_id": rule.id},
                            session=db,
                        )
                        new_memories.append(mem.model_dump())

            db.commit()

            return RuleEvaluationResult(
                triggered_rule_ids=triggered_rule_ids,
                actions=actions,
                new_memories=new_memories,
            )

    def list_rules(
        self,
        *,
        scope: Optional[str] = None,
        entity_id: Optional[str] = None,
        enabled_only: bool = True,
        session: Optional[Session] = None,
    ) -> List[RuleOut]:
        with self._get_session(session) as db:
            q = db.query(Rule)
            if enabled_only:
                q = q.filter(Rule.active.is_(True))
            if scope:
                q = q.filter(Rule.if_json["scope"].as_string() == scope)
            if entity_id:
                q = q.filter(Rule.if_json["entity_id"].as_string() == entity_id)

            rules = q.order_by(Rule.created_at.desc()).all()
            results: List[RuleOut] = []
            for rule in rules:
                try:
                    condition = RuleCondition(**(rule.if_json or {}))
                except Exception:
                    continue
                actions = normalize_actions((rule.then_json or {}).get("actions", []))
                results.append(
                    RuleOut(
                        id=rule.id,
                        condition=condition,
                        actions=actions,
                        description=rule.description,
                        enabled=rule.active,
                        created_at=rule.created_at,
                        last_triggered_at=rule.last_triggered_at,
                    )
                )
            return results

    def get_rule(
        self,
        rule_id: str,
        *,
        session: Optional[Session] = None,
    ) -> RuleOut:
        with self._get_session(session) as db:
            rule = db.query(Rule).filter(Rule.id == rule_id).first()
            if not rule:
                raise ValueError(f"Rule not found: {rule_id}")
            condition = RuleCondition(**(rule.if_json or {}))
            actions = normalize_actions((rule.then_json or {}).get("actions", []))
            return RuleOut(
                id=rule.id,
                condition=condition,
                actions=actions,
                description=rule.description,
                enabled=rule.active,
                created_at=rule.created_at,
                last_triggered_at=rule.last_triggered_at,
            )

    def disable_rule(
        self,
        rule_id: str,
        *,
        session: Optional[Session] = None,
    ) -> RuleOut:
        with self._get_session(session) as db:
            rule = db.query(Rule).filter(Rule.id == rule_id).first()
            if not rule:
                raise ValueError(f"Rule not found: {rule_id}")
            rule.active = False
            db.commit()
            condition = RuleCondition(**(rule.if_json or {}))
            actions = normalize_actions((rule.then_json or {}).get("actions", []))
            return RuleOut(
                id=rule.id,
                condition=condition,
                actions=actions,
                description=rule.description,
                enabled=rule.active,
                created_at=rule.created_at,
                last_triggered_at=rule.last_triggered_at,
            )

    def forget(
        self,
        *,
        id: Optional[str] = None,
        policy: Optional[str] = None,
        reason: Optional[str] = "unspecified",
        session: Optional[Session] = None,
    ):
        payload = ForgetIn(id=id, policy=policy, reason=reason)
        with self._get_session(session) as db:
            return forget_memory(db, payload)

    def auto_ingest(
        self,
        *,
        interactions: List[Interaction],
        extractor: Extractor,
        scope: Optional[str] = None,
        entity_id: Optional[str] = None,
        max_memories: Optional[int] = None,
        min_importance: Optional[float] = None,
        session: Optional[Session] = None,
    ) -> List[MemoryOut]:
        if not interactions:
            return []
        if extractor is None:
            raise ValueError("auto_ingest requires a non-null extractor")

        candidates = extractor(interactions)
        normalized: List[MemoryCandidate] = []
        for candidate in candidates:
            content = (candidate.content or "").strip()
            if not content:
                continue

            ctype = candidate.type if candidate.type in ALLOWED_MEMORY_TYPES else "semantic"
            importance = candidate.importance
            if min_importance is not None and importance is not None and importance < min_importance:
                continue

            scoped = candidate.model_copy()
            scoped.content = content
            scoped.type = ctype

            # Clamp scope to allowed values; default to provided scope or "session".
            effective_scope = scope or "session"
            if scoped.scope in ALLOWED_SCOPES:
                effective_scope = scoped.scope
            scoped.scope = effective_scope

            # Use candidate entity_id when provided, else fallback to outer entity_id.
            scoped.entity_id = scoped.entity_id or entity_id

            normalized.append(scoped)

        # Deduplicate against existing memories per (scope, entity_id) and within this batch
        with self._get_session(session) as db:
            seen_by_key: Dict[tuple, set] = {}

            def get_seen(scope_val: str, entity_val: Optional[str]) -> set:
                key = (scope_val, entity_val)
                if key not in seen_by_key:
                    q = db.query(Memory).filter(Memory.scope == scope_val)
                    if entity_val:
                        q = q.filter(Memory.entity_id == entity_val)
                    existing = q.all()
                    seen_by_key[key] = {normalize_text(mem.content) for mem in existing}
                return seen_by_key[key]

            deduped: List[MemoryCandidate] = []
            for candidate in normalized:
                eff_scope = candidate.scope or "session"
                eff_entity = candidate.entity_id
                seen = get_seen(eff_scope, eff_entity)
                norm_content = normalize_text(candidate.content)
                if norm_content in seen:
                    continue
                seen.add(norm_content)
                deduped.append(candidate)

            # Apply max_memories after dedupe, sorted by importance desc (None -> 0.0)
            deduped.sort(key=lambda c: c.importance if c.importance is not None else 0.0, reverse=True)
            if max_memories is not None:
                deduped = deduped[:max_memories]

            stored: List[MemoryOut] = []
            for candidate in deduped:
                stored.append(
                    self.remember(
                        content=candidate.content,
                        type=candidate.type,
                        scope=candidate.scope or "session",
                        entity_id=candidate.entity_id,
                        tags=candidate.tags,
                        importance=candidate.importance or 0.0,
                        metadata=candidate.metadata,
                        session=db,
                    )
                )
        return stored

    # ==== Procedural memory (experiences) ====
    def record_experience(
        self,
        trace: ExperienceIn | Dict[str, Any],
        *,
        session: Optional[Session] = None,
    ) -> ExperienceOut:
        if isinstance(trace, dict):
            payload = ExperienceIn(**trace)
        else:
            payload = trace

        summary = summarize_state(payload.env_pre, payload.internal_state)
        vec = self._embed_fn(summary)
        env_tokens = flatten_env(payload.env_pre)
        with self._get_session(session) as db:
            exp = Experience(
                id=new_id(),
                scope=payload.scope,
                entity_id=payload.entity_id,
                task_type=payload.task_type,
                env_pre=payload.env_pre,
                env_post=payload.env_post,
                env_tokens=env_tokens,
                internal_state=payload.internal_state,
                internal_repr=summary,
                internal_embedding=vec_to_str(vec),
                action_type=payload.action_type,
                action_payload=payload.action_payload,
                reasoning_summary=payload.reasoning_summary,
                success=payload.success,
                reward=payload.reward,
                error_type=payload.error_type,
                latency_ms=payload.latency_ms,
                cost=payload.cost,
                tags=payload.tags,
                episode_id=payload.episode_id,
                step_index=payload.step_index,
                created_at=now_utc(),
            )
            db.add(exp)
            db.commit()
            db.refresh(exp)
            return ExperienceOut(
                id=exp.id,
                scope=exp.scope,
                entity_id=exp.entity_id,
                task_type=exp.task_type,
                env_pre=exp.env_pre,
                env_post=exp.env_post,
                internal_state=exp.internal_state,
                action_type=exp.action_type,
                action_payload=exp.action_payload,
                reasoning_summary=exp.reasoning_summary,
                success=exp.success,
                reward=exp.reward,
                error_type=exp.error_type,
                latency_ms=exp.latency_ms,
                cost=exp.cost,
                tags=exp.tags,
                episode_id=exp.episode_id,
                step_index=exp.step_index,
                created_at=exp.created_at,
            )

    def retrieve_experiences(
        self,
        *,
        env_state: Optional[Dict[str, Any]] = None,
        internal_state: Optional[Dict[str, Any]] = None,
        scope: Optional[str] = None,
        entity_id: Optional[str] = None,
        task_type: Optional[str] = None,
        action_type: Optional[str] = None,
        success_only: bool = False,
        k: int = 5,
        mode: str = "legacy",
        tau_env: float = 0.0,
        k_env: Optional[int] = None,
        context_window: Optional[int] = None,
        session: Optional[Session] = None,
    ) -> List[ExperienceOut]:
        summary = summarize_state(env_state, internal_state)
        query_vec = self._embed_fn(summary)
        query_env_tokens = flatten_env(env_state)
        with self._get_session(session) as db:
            q = db.query(Experience)
            if scope:
                q = q.filter(Experience.scope == scope)
            if entity_id:
                q = q.filter(Experience.entity_id == entity_id)
            if task_type:
                q = q.filter(Experience.task_type == task_type)
            if action_type:
                q = q.filter(Experience.action_type == action_type)
            if success_only:
                q = q.filter(Experience.success.is_(True))

            experiences = q.all()
            results: List[ExperienceOut] = []

            if mode == "legacy":
                scored: List[tuple[float, Experience]] = []
                for exp in experiences:
                    vec = str_to_vec(exp.internal_embedding or exp.internal_repr or "")
                    sim = cosine_sim(query_vec, vec)
                    scored.append((sim, exp))
                scored.sort(key=lambda t: t[0], reverse=True)
                top = scored[:k]
                for score, exp in top:
                    results.append(
                        ExperienceOut(
                            id=exp.id,
                            scope=exp.scope,
                            entity_id=exp.entity_id,
                            task_type=exp.task_type,
                            env_pre=exp.env_pre,
                            env_post=exp.env_post,
                            internal_state=exp.internal_state,
                            action_type=exp.action_type,
                            action_payload=exp.action_payload,
                            reasoning_summary=exp.reasoning_summary,
                            success=exp.success,
                            reward=exp.reward,
                            error_type=exp.error_type,
                            latency_ms=exp.latency_ms,
                            cost=exp.cost,
                            tags=exp.tags,
                            episode_id=exp.episode_id,
                            step_index=exp.step_index,
                            created_at=exp.created_at,
                            score=float(score),
                        )
                    )
                return results

            # PRAXIS mode: env gate -> internal rerank
            env_scored: List[tuple[float, Experience]] = []
            for exp in experiences:
                env_score = env_similarity(query_env_tokens, exp.env_tokens or [])
                env_scored.append((env_score, exp))
            env_scored.sort(key=lambda t: t[0], reverse=True)

            if tau_env > 0.0:
                env_scored = [item for item in env_scored if item[0] >= tau_env]

            if k_env is not None:
                env_scored = env_scored[:k_env]

            reranked: List[tuple[float, float, Experience]] = []
            for env_score, exp in env_scored:
                vec = str_to_vec(exp.internal_embedding or exp.internal_repr or "")
                internal_sim = cosine_sim(query_vec, vec)
                reranked.append((internal_sim, env_score, exp))

            reranked.sort(
                key=lambda t: (
                    t[0],  # internal sim
                    t[1],  # env sim
                    (t[2].reward or 0.0) + (0.2 if t[2].success else 0.0),
                    t[2].created_at.timestamp() if t[2].created_at else 0.0,
                ),
                reverse=True,
            )

            top = reranked[:k]
            for internal_sim, env_score, exp in top:
                ctx: Optional[List[ExperienceOut]] = None
                if context_window is not None and exp.episode_id is not None:
                    low = (exp.step_index or 0) - context_window
                    high = (exp.step_index or 0) + context_window
                    ctx_q = (
                        db.query(Experience)
                        .filter(
                            Experience.episode_id == exp.episode_id,
                            Experience.step_index >= low,
                            Experience.step_index <= high,
                        )
                        .order_by(Experience.step_index.asc())
                        .all()
                    )
                    ctx = [
                        ExperienceOut(
                            id=e.id,
                            scope=e.scope,
                            entity_id=e.entity_id,
                            task_type=e.task_type,
                            env_pre=e.env_pre,
                            env_post=e.env_post,
                            internal_state=e.internal_state,
                            action_type=e.action_type,
                            action_payload=e.action_payload,
                            reasoning_summary=e.reasoning_summary,
                            success=e.success,
                            reward=e.reward,
                            error_type=e.error_type,
                            latency_ms=e.latency_ms,
                            cost=e.cost,
                            tags=e.tags,
                            episode_id=e.episode_id,
                            step_index=e.step_index,
                            created_at=e.created_at,
                        )
                        for e in ctx_q
                    ]

                results.append(
                    ExperienceOut(
                        id=exp.id,
                        scope=exp.scope,
                        entity_id=exp.entity_id,
                        task_type=exp.task_type,
                        env_pre=exp.env_pre,
                        env_post=exp.env_post,
                        internal_state=exp.internal_state,
                        action_type=exp.action_type,
                        action_payload=exp.action_payload,
                        reasoning_summary=exp.reasoning_summary,
                        success=exp.success,
                        reward=exp.reward,
                        error_type=exp.error_type,
                        latency_ms=exp.latency_ms,
                        cost=exp.cost,
                        tags=exp.tags,
                        episode_id=exp.episode_id,
                        step_index=exp.step_index,
                        created_at=exp.created_at,
                        score=float(internal_sim),
                        env_score=float(env_score),
                        context_steps=ctx,
                    )
                )
            return results

    def suggest_actions(
        self,
        *,
        env_state: Optional[Dict[str, Any]] = None,
        internal_state: Optional[Dict[str, Any]] = None,
        scope: Optional[str] = None,
        entity_id: Optional[str] = None,
        task_type: Optional[str] = None,
        top_n: int = 3,
        use_praxis: bool = False,
        tau_env: float = 0.0,
        k_env: Optional[int] = None,
        context_window: Optional[int] = None,
        session: Optional[Session] = None,
    ) -> List[ExperienceOut]:
        experiences = self.retrieve_experiences(
            env_state=env_state,
            internal_state=internal_state,
            scope=scope,
            entity_id=entity_id,
            task_type=task_type,
            success_only=False,
            k=50,
            mode="prax" if use_praxis else "legacy",
            tau_env=tau_env,
            k_env=k_env,
            context_window=context_window,
            session=session,
        )
        def rank_key(exp: ExperienceOut):
            reward_adj = exp.reward if exp.reward is not None else 0.0
            success_bonus = 0.2 if exp.success else 0.0
            sim_score = exp.score or 0.0
            recency = exp.created_at.timestamp() if exp.created_at else 0.0
            return sim_score + reward_adj * 0.1 + success_bonus + recency * 1e-9

        ranked = sorted(experiences, key=rank_key, reverse=True)
        return ranked[:top_n]

    def debug_retrieval(
        self,
        *,
        env_state: Optional[Dict[str, Any]] = None,
        internal_state: Optional[Dict[str, Any]] = None,
        scope: Optional[str] = None,
        entity_id: Optional[str] = None,
        task_type: Optional[str] = None,
        mode: str = "prax",
        tau_env: float = 0.0,
        k_env: Optional[int] = None,
        k: int = 5,
        session: Optional[Session] = None,
    ) -> List[Dict[str, Any]]:
        results = self.retrieve_experiences(
            env_state=env_state,
            internal_state=internal_state,
            scope=scope,
            entity_id=entity_id,
            task_type=task_type,
            mode=mode,
            tau_env=tau_env,
            k_env=k_env,
            k=k,
            session=session,
        )
        debug_list: List[Dict[str, Any]] = []
        for r in results:
            debug_list.append(
                {
                    "id": r.id,
                    "scope": r.scope,
                    "entity_id": r.entity_id,
                    "action_type": r.action_type,
                    "success": r.success,
                    "reward": r.reward,
                    "score_internal": r.score,
                    "score_env": r.env_score,
                    "episode_id": r.episode_id,
                    "step_index": r.step_index,
                    "created_at": r.created_at,
                }
            )
        return debug_list
