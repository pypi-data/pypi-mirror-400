"""Tests for analyze_kernel tool in CodingEnvironment."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from wafer_core.environments.coding import CodingEnvironment
from wafer_core.rollouts.dtypes import Actor, AgentState, Endpoint, ToolCall, Trajectory

# Constants
TEST_KERNEL_NAME = "test_kernel"
TEST_TOOL_CALL_ID_1 = "test-1"
TEST_TOOL_CALL_ID_2 = "test-2"
TEST_TOOL_CALL_ID_3 = "test-3"
TEST_TOOL_CALL_ID_4 = "test-4"

TEST_MLIR_TEXT = "module { func @kernel() { } }"
TEST_PTX_TEXT = ".version 8.0\n.target sm_80"
TEST_SASS_TEXT = "// SASS code"

KERNEL_ANALYSIS_HEADER = "Kernel Analysis"
LAYOUTS_HEADER = "Layouts"
MEMORY_PATHS_HEADER = "Memory Paths"
PIPELINE_STAGES_HEADER = "Pipeline Stages"

MUST_BE_PROVIDED_ERROR = "must be provided"
ANALYSIS_FAILED_ERROR = "Analysis failed"


class TestAnalyzeKernelTool:
    """Tests for analyze_kernel tool execution."""

    @pytest.fixture
    def env(self) -> CodingEnvironment:
        """Create CodingEnvironment instance for testing."""
        return CodingEnvironment(working_dir=Path.cwd())

    @pytest.mark.asyncio
    async def test_analyze_kernel_tool_success(self, env: CodingEnvironment) -> None:
        """Test successful analyze_kernel tool execution."""
        assert env is not None
        
        tool_call = ToolCall(
            id=TEST_TOOL_CALL_ID_1,
            name="analyze_kernel",
            args={
                "mlir_text": TEST_MLIR_TEXT,
                "ptx_text": TEST_PTX_TEXT,
                "sass_text": TEST_SASS_TEXT,
                "kernel_name": TEST_KERNEL_NAME,
            },
        )

        # Mock the analyze_kernel function
        with patch("wafer_core.tools.cutedsl_analyzer.analyze_kernel") as mock_analyze:
            # Create a mock result object
            mock_result = MagicMock()
            mock_result.__dataclass_fields__ = {"kernel_name": "test_kernel"}
            mock_result.kernel_name = "test_kernel"
            mock_result.parsed_mlir = MagicMock()
            mock_result.parsed_mlir.ops = [MagicMock(), MagicMock()]
            mock_result.parsed_ptx = MagicMock()
            mock_result.parsed_ptx.instructions = [MagicMock(), MagicMock()]
            mock_result.parsed_sass = MagicMock()
            mock_result.parsed_sass.instructions = [MagicMock(), MagicMock()]
            mock_result.layouts = [
                MagicMock(name="layout1", shape=[32, 64]),
                MagicMock(name="layout2", shape=[128, 256]),
            ]
            mock_result.memory_paths = [
                MagicMock(description="Path 1: Load -> Compute -> Store"),
                MagicMock(description="Path 2: Load -> Store"),
            ]
            mock_result.pipeline_stages = [
                MagicMock(stage_id=0, description="Fetch"),
                MagicMock(stage_id=1, description="Decode"),
            ]

            # Mock asdict in kernel_analyzer_tool module to return structured data
            def mock_asdict(obj):
                return {
                    "kernel_name": "test_kernel",
                    "parsed_mlir": {"ops": [{"name": "op1"}, {"name": "op2"}]},
                    "parsed_ptx": {"instructions": [{"name": "mov"}, {"name": "add"}]},
                    "parsed_sass": {"instructions": [{"name": "MOV"}, {"name": "ADD"}]},
                    "layouts": [
                        {"name": "layout1", "shape": [32, 64]},
                        {"name": "layout2", "shape": [128, 256]},
                    ],
                    "memory_paths": [
                        {"description": "Path 1: Load -> Compute -> Store"},
                        {"description": "Path 2: Load -> Store"},
                    ],
                    "pipeline_stages": [
                        {"stage_id": 0, "description": "Fetch"},
                        {"stage_id": 1, "description": "Decode"},
                    ],
                }

            with patch("wafer_core.environments.kernel_analyzer_tool.asdict", side_effect=mock_asdict):
                mock_analyze.return_value = mock_result

                state = AgentState(
                    actor=Actor(
                        trajectory=Trajectory(messages=[]),
                        endpoint=Endpoint(provider="test", model="test"),
                    ),
                    environment=env,
                )

                result = await env.exec_tool(
                    tool_call=tool_call,
                    current_state=state,
                    run_config=None,
                )

                assert result is not None
                assert not result.is_error
                assert result.tool_call_id == TEST_TOOL_CALL_ID_1
                assert result.content is not None
                assert KERNEL_ANALYSIS_HEADER in result.content
                assert TEST_KERNEL_NAME in result.content
                assert LAYOUTS_HEADER in result.content
                assert MEMORY_PATHS_HEADER in result.content
                assert PIPELINE_STAGES_HEADER in result.content

                mock_analyze.assert_called_once_with(
                    mlir_text=TEST_MLIR_TEXT,
                    ptx_text=TEST_PTX_TEXT,
                    sass_text=TEST_SASS_TEXT,
                    source_code=None,
                    kernel_name=TEST_KERNEL_NAME,
                )

    @pytest.mark.asyncio
    async def test_analyze_kernel_tool_missing_args(self, env: CodingEnvironment) -> None:
        """Test analyze_kernel tool with missing required args."""
        assert env is not None
        
        tool_call = ToolCall(
            id=TEST_TOOL_CALL_ID_2,
            name="analyze_kernel",
            args={},
        )

        state = AgentState(
            actor=Actor(
                trajectory=Trajectory(messages=[]),
                endpoint=Endpoint(provider="test", model="test"),
            ),
            environment=env,
        )

        result = await env.exec_tool(
            tool_call=tool_call,
            current_state=state,
            run_config=None,
        )

        assert result is not None
        assert result.is_error
        assert result.error is not None
        assert MUST_BE_PROVIDED_ERROR in result.error.lower()

    @pytest.mark.asyncio
    async def test_analyze_kernel_tool_empty_args(self, env: CodingEnvironment) -> None:
        """Test analyze_kernel tool with empty string args."""
        assert env is not None
        
        empty_mlir = ""
        empty_ptx = ""
        empty_sass = ""
        
        tool_call = ToolCall(
            id=TEST_TOOL_CALL_ID_3,
            name="analyze_kernel",
            args={
                "mlir_text": empty_mlir,
                "ptx_text": empty_ptx,
                "sass_text": empty_sass,
            },
        )

        state = AgentState(
            actor=Actor(
                trajectory=Trajectory(messages=[]),
                endpoint=Endpoint(provider="test", model="test"),
            ),
            environment=env,
        )

        result = await env.exec_tool(
            tool_call=tool_call,
            current_state=state,
            run_config=None,
        )

        assert result is not None
        assert result.is_error
        assert result.error is not None
        assert MUST_BE_PROVIDED_ERROR in result.error.lower()

    @pytest.mark.asyncio
    async def test_analyze_kernel_tool_error_handling(self, env: CodingEnvironment) -> None:
        """Test analyze_kernel tool error handling."""
        assert env is not None
        
        invalid_mlir = "invalid mlir"
        invalid_ptx = "invalid ptx"
        invalid_sass = "invalid sass"
        error_message = "Invalid MLIR syntax"
        
        tool_call = ToolCall(
            id=TEST_TOOL_CALL_ID_4,
            name="analyze_kernel",
            args={
                "mlir_text": invalid_mlir,
                "ptx_text": invalid_ptx,
                "sass_text": invalid_sass,
            },
        )

        with patch("wafer_core.tools.cutedsl_analyzer.analyze_kernel") as mock_analyze:
            mock_analyze.side_effect = ValueError(error_message)

            state = AgentState(
                actor=Actor(
                    trajectory=Trajectory(messages=[]),
                    endpoint=Endpoint(provider="test", model="test"),
                ),
                environment=env,
            )

            result = await env.exec_tool(
                tool_call=tool_call,
                current_state=state,
                run_config=None,
            )

            assert result is not None
            assert result.is_error
            assert result.error is not None
            assert ANALYSIS_FAILED_ERROR in result.error
            assert error_message in result.error

    def test_analyze_kernel_tool_discovery(self, env: CodingEnvironment) -> None:
        """Test that analyze_kernel tool is discoverable."""
        assert env is not None
        
        tools = env.get_tools()
        assert len(tools) > 0

        analyze_tool = None
        for tool in tools:
            if tool.function.name == "analyze_kernel":
                analyze_tool = tool
                break

        assert analyze_tool is not None
        assert analyze_tool.function.name == "analyze_kernel"
        assert analyze_tool.function.description is not None
        assert "MLIR" in analyze_tool.function.description
        assert "PTX" in analyze_tool.function.description
        assert "SASS" in analyze_tool.function.description

        required = analyze_tool.function.required
        assert required is not None
        assert "mlir_text" in required
        assert "ptx_text" in required
        assert "sass_text" in required

    def test_analyze_kernel_tool_filtering(self) -> None:
        """Test that analyze_kernel tool respects enabled_tools filtering."""
        enabled_tools_list = ["read", "analyze_kernel"]
        env_enabled = CodingEnvironment(enabled_tools=enabled_tools_list)
        tools_enabled = env_enabled.get_tools()
        tool_names_enabled = [t.function.name for t in tools_enabled]
        assert "analyze_kernel" in tool_names_enabled

        disabled_tools_list = ["read", "write"]
        env_disabled = CodingEnvironment(enabled_tools=disabled_tools_list)
        tools_disabled = env_disabled.get_tools()
        tool_names_disabled = [t.function.name for t in tools_disabled]
        assert "analyze_kernel" not in tool_names_disabled

        env_all = CodingEnvironment(enabled_tools=None)
        tools_all = env_all.get_tools()
        tool_names_all = [t.function.name for t in tools_all]
        assert "analyze_kernel" in tool_names_all
