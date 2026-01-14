#!/usr/bin/env python3
"""Run CUDA-grep evaluation with grep/glob/read tools."""

import sys
from pathlib import Path

# Adjust imports
sys.path.insert(0, str(Path(__file__).parent))

import trio
from wafer_core.rollouts.examples.eval.cuda_grep.eval_cuda_grep import (
    CudaGrepConfig,
    run_evaluation,
)

from wafer_core.rollouts.dtypes import Endpoint

# Find corpus path
corpus_path = Path(__file__).parent.parent / "curriculum"
questions_path = (
    Path(__file__).parent
    / "wafer_core/rollouts/examples/eval/cuda_grep/cuda_questions.jsonl"
)

print(f"Corpus path: {corpus_path}")
print(f"Questions path: {questions_path}")
print(f"Corpus exists: {corpus_path.exists()}")
print(f"Questions exist: {questions_path.exists()}")

# Config for grep/glob/read only (no semantic search)
config = CudaGrepConfig(
    corpus_path=corpus_path,
    questions_path=questions_path,
    agent_endpoint=Endpoint(
        provider="anthropic",
        model="claude-sonnet-4-20250514",
        temperature=0.0,
    ),
    grader_endpoint=Endpoint(
        provider="anthropic",
        model="claude-sonnet-4-20250514",
        temperature=0.0,
    ),
    tools=["grep", "glob", "read", "submit"],  # No search
    search_backend=None,
    max_turns=15,
    max_samples=5,  # Start with 5 for testing
)

print(f"\nRunning CUDA-grep eval with {len(config.tools)} tools: {config.tools}")
print(f"Max turns: {config.max_turns}, Max samples: {config.max_samples}\n")

trio.run(run_evaluation, config)
