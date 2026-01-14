"""CUDA-grep eval config: grep/glob/read only (classic CUDA-grep)."""

from pathlib import Path

from rollouts.dtypes import Endpoint

from .eval_cuda_grep import CudaGrepConfig

# Classic CUDA-grep toolset (no semantic search)
config = CudaGrepConfig(
    corpus_path=Path("/path/to/corpus"),
    questions_path=Path(__file__).parent / "cuda_questions.jsonl",
    agent_endpoint=Endpoint(provider="anthropic", model="claude-sonnet-4-5-20250929"),
    grader_endpoint=Endpoint(provider="anthropic", model="claude-sonnet-4-5-20250929"),
    tools=["grep", "glob", "read", "submit"],  # No search
    search_backend=None,
    max_turns=15,
    max_samples=None,
)
