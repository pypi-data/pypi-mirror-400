"""Tools module for wafer-core.

Provides CUDA tool finding, compilation utilities, CuTeDSL analysis, documentation queries,
and Perfetto trace profiling.
"""

from wafer_core.tools.backend import (
    get_api_url,
    get_auth_token,
    list_captures,
    upload_artifact,
    upload_capture,
)
from wafer_core.tools.compiler import (
    ArchDetectResult,
    CompileResult,
    compile_cuda,
    detect_arch,
)
from wafer_core.tools.cutedsl_analyzer import (
    # Data types
    AnalysisResult,
    CorrelationEdge,
    DiffResult,
    EntityId,
    LayoutInfo,
    MemoryPath,
    MLIROp,
    ParsedMLIR,
    ParsedPTX,
    ParsedSASS,
    PipelineStage,
    PTXInstruction,
    SASSInstruction,
    # Main functions
    analyze_kernel,
    # Feature extractors
    build_correlation_graph,
    diff_kernels,
    extract_layouts,
    extract_memory_paths,
    extract_pipeline_structure,
    get_lineage,
    # Parsers
    parse_mlir,
    parse_ptx,
    parse_sass,
)
from wafer_core.tools.docs import (
    DocsRAGChunk,
    DocsSearchResponse,
    DocsSearchResult,
    query_docs,
    search_docs,
)
from wafer_core.tools.tool_finder import (
    find_nvcc,
    find_nvdisasm,
    get_nvcc_version,
    get_platform,
)

# Lazy imports for Perfetto to avoid loading heavy dependencies
__all__ = [
    # Tool finder
    "find_nvcc",
    "find_nvdisasm",
    "get_nvcc_version",
    "get_platform",
    # Compiler
    "compile_cuda",
    "detect_arch",
    "CompileResult",
    "ArchDetectResult",
    # CuTeDSL Analyzer - Functions
    "analyze_kernel",
    "diff_kernels",
    "get_lineage",
    "parse_mlir",
    "parse_ptx",
    "parse_sass",
    "build_correlation_graph",
    "extract_layouts",
    "extract_memory_paths",
    "extract_pipeline_structure",
    # CuTeDSL Analyzer - Types
    "AnalysisResult",
    "DiffResult",
    "EntityId",
    "CorrelationEdge",
    "LayoutInfo",
    "MemoryPath",
    "PipelineStage",
    "MLIROp",
    "PTXInstruction",
    "SASSInstruction",
    "ParsedMLIR",
    "ParsedPTX",
    "ParsedSASS",
    # Docs - Functions
    "search_docs",
    "query_docs",
    # Docs - Types
    "DocsSearchResult",
    "DocsSearchResponse",
    "DocsRAGChunk",
    # Backend - Functions
    "upload_capture",
    "upload_artifact",
    "list_captures",
    "get_api_url",
    "get_auth_token",
    # Perfetto - Lazy loaded
    "PerfettoTool",
    "PerfettoConfig",
    "TraceManager",
    "TraceMeta",
    "TraceProcessorManager",
    "TraceProcessorStatus",
]


def __getattr__(name: str):
    """Lazy import Perfetto tool components."""
    if name in ("PerfettoTool", "PerfettoConfig"):
        from wafer_core.tools.perfetto.perfetto_tool import PerfettoConfig, PerfettoTool
        if name == "PerfettoTool":
            return PerfettoTool
        return PerfettoConfig
    
    if name in ("TraceManager", "TraceMeta"):
        from wafer_core.tools.perfetto.trace_manager import TraceManager, TraceMeta
        if name == "TraceManager":
            return TraceManager
        return TraceMeta
    
    if name in ("TraceProcessorManager", "TraceProcessorStatus"):
        from wafer_core.tools.perfetto.trace_processor import (
            TraceProcessorManager,
            TraceProcessorStatus,
        )
        if name == "TraceProcessorManager":
            return TraceProcessorManager
        return TraceProcessorStatus
    
    raise AttributeError(f"module 'wafer_core.tools' has no attribute {name!r}")
