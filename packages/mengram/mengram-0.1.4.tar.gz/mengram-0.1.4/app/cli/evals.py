from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.evals.diff import diff_eval_result_json
from app.evals.io import write_json_atomic
from app.evals.suite import run_eval_suite, run_eval_suite_dir
from mengram import ChatMemory, ChatMemoryConfig, MemoryClient, get_preset


def _make_chat_factory(preset: str):
    def factory():
        tmp = tempfile.TemporaryDirectory()
        db_path = Path(tmp.name) / "eval.db"
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

        def fake_embed(_: str):
            return np.ones(384, dtype=np.float32)

        client = MemoryClient(session_factory=SessionLocal, embed_fn=fake_embed)
        cfg = get_preset(preset)
        cfg.return_reports = True
        cfg.extractor = None
        chat = ChatMemory(client, scope="session", entity_id="eval", config=cfg)
        chat._tmpdir = tmp
        return chat

    return factory


def add_eval_subcommand(subparsers):
    eval_parser = subparsers.add_parser("eval", help="Eval suite runner/diff")
    eval_sub = eval_parser.add_subparsers(dest="eval_cmd", required=True)

    run_cmd = eval_sub.add_parser("run", help="Run eval suite")
    run_cmd.add_argument("path", help="Transcript file or directory")
    run_cmd.add_argument("--preset", default="CHAT_DEFAULT")
    run_cmd.add_argument("--out", default="eval_results.json")
    run_cmd.add_argument("--pattern", default="*.json")
    run_cmd.add_argument("--recursive", action="store_true", default=True)

    diff_cmd = eval_sub.add_parser("diff", help="Diff eval suite results")
    diff_cmd.add_argument("before")
    diff_cmd.add_argument("after")
    diff_cmd.add_argument("--out", default="eval_diff.json")

    return eval_parser


def handle_eval(args):
    if args.eval_cmd == "run":
        factory = _make_chat_factory(args.preset)
        path = Path(args.path)
        if path.is_dir():
            result = run_eval_suite_dir(path, factory, pattern=args.pattern, recursive=args.recursive)
        else:
            result = run_eval_suite([path], factory)
        write_json_atomic(result.to_dict(), args.out)
        return 0
    if args.eval_cmd == "diff":
        diff = diff_eval_result_json(args.before, args.after)
        write_json_atomic(diff.to_dict(), args.out)
        return 0
    return 1
