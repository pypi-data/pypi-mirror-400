"""Tests for CuTeDSL Analyzer module.

Only tests the essential behaviors:
1. EntityId serialization (used across API boundaries)
2. Full analysis pipeline (integration test)
"""

from wafer_core.tools.cutedsl_analyzer import (
    AnalysisResult,
    DiffResult,
    EntityId,
    analyze_kernel,
    diff_kernels,
    get_lineage,
)

# =============================================================================
# Test Data
# =============================================================================

SAMPLE_MLIR = """
module {
  func.func @gemm_kernel(%arg0: tensor<128x64xf32>) {
    %0 = cute.layout %arg0 {shape = [128, 64], stride = [64, 1]}
    %1 = cute.partition %0 {tile_shape = [32, 16]}
    %2 = cute.copy %1, %smem {async = true}
    return
  }
}
"""

SAMPLE_PTX = """
.version 8.0
.target sm_89
.visible .entry gemm_kernel(.param .u64 param_A) {
    .reg .f32 %f<16>;
    .reg .b64 %rd<8>;
    
    ld.param.u64 %rd1, [param_A];
    ld.global.v4.f32 {%f1, %f2, %f3, %f4}, [%rd1];
    cp.async.ca.shared.global [smem], [%rd1], 16;
    mma.sync.aligned.m16n8k8.row.col.f32.f32.f32.f32 {%f5, %f6}, {%f1, %f2}, {%f3}, {%f5, %f6};
    st.global.v4.f32 [%rd2], {%f5, %f6, %f7, %f8};
    ret;
}
"""

SAMPLE_SASS = """
Function : gemm_kernel
.text.gemm_kernel:
/*0000*/ MOV R1, c[0x0][0x28];
/*0010*/ LDG.E.128 R4, [R2];
/*0020*/ LDS.128 R8, [0x0];
/*0030*/ HMMA.16816.F32 R12, R4, R8, R12;
/*0040*/ STG.E.128 [R2], R12;
/*0050*/ EXIT;
"""


# =============================================================================
# EntityId Tests - Important for API serialization
# =============================================================================

class TestEntityId:
    """EntityId serialization - critical for API boundaries."""
    
    def test_roundtrip_with_kernel(self):
        """EntityId roundtrips through string serialization."""
        original = EntityId(stage="mlir", entity_type="op", index=5, kernel_name="gemm")
        serialized = original.to_string()
        restored = EntityId.from_string(serialized)
        
        assert serialized == "mlir:op:5:gemm"
        assert restored == original
    
    def test_roundtrip_without_kernel(self):
        """EntityId without kernel_name roundtrips correctly."""
        original = EntityId(stage="ptx", entity_type="instruction", index=10)
        serialized = original.to_string()
        restored = EntityId.from_string(serialized)
        
        assert serialized == "ptx:instruction:10"
        assert restored.kernel_name is None


# =============================================================================
# Integration Test - Covers full pipeline
# =============================================================================

class TestAnalysisPipeline:
    """Integration test for full analysis pipeline."""
    
    def test_analyze_kernel_extracts_all_data(self):
        """analyze_kernel extracts MLIR ops, PTX instructions, SASS, layouts, memory paths, pipeline."""
        result = analyze_kernel(
            mlir_text=SAMPLE_MLIR,
            ptx_text=SAMPLE_PTX,
            sass_text=SAMPLE_SASS,
            source_code="// Sample source",
            kernel_name="gemm_kernel"
        )
        
        # Basic structure
        assert isinstance(result, AnalysisResult)
        assert result.kernel_name == "gemm_kernel"
        assert result.source_code == "// Sample source"
        
        # Parsing worked
        assert len(result.parsed_mlir.ops) > 0
        assert len(result.parsed_ptx.instructions) > 0
        assert len(result.parsed_sass.instructions) > 0
        assert "gemm_kernel" in result.parsed_mlir.kernels
        
        # Shapes extracted from MLIR
        assert any(s == (128, 64) for s in result.parsed_mlir.shapes.values())
        
        # Memory ops categorized
        assert len(result.parsed_ptx.memory_ops) > 0
        assert len(result.parsed_ptx.mma_ops) > 0
        
        # Features extracted
        assert len(result.layouts) > 0
        assert len(result.memory_paths) > 0
        assert len(result.pipeline_stages) > 0
        
        # Correlation graph built
        assert result.correlation_graph is not None
        
        # Entity registry populated
        assert len(result.entity_registry) > 0
    
    def test_analyze_kernel_infers_name(self):
        """Kernel name is inferred from MLIR if not provided."""
        result = analyze_kernel(mlir_text=SAMPLE_MLIR, ptx_text="", sass_text="")
        assert result.kernel_name == "gemm_kernel"
    
    def test_analyze_empty_inputs(self):
        """Empty inputs don't crash, return 'unknown' kernel."""
        result = analyze_kernel(mlir_text="", ptx_text="", sass_text="")
        assert result.kernel_name == "unknown"


class TestDiff:
    """Diff functionality tests."""
    
    def test_diff_identical_returns_no_changes(self):
        """Diffing identical kernels returns empty change sets."""
        result1 = analyze_kernel(SAMPLE_MLIR, SAMPLE_PTX, SAMPLE_SASS)
        result2 = analyze_kernel(SAMPLE_MLIR, SAMPLE_PTX, SAMPLE_SASS)
        
        diff = diff_kernels(result1, result2)
        
        assert isinstance(diff, DiffResult)
        assert len(diff.mlir_added) == 0
        assert len(diff.mlir_removed) == 0


class TestLineage:
    """Lineage tracking tests."""
    
    def test_get_lineage_returns_connections(self):
        """get_lineage returns upstream and downstream entities."""
        result = analyze_kernel(SAMPLE_MLIR, SAMPLE_PTX, SAMPLE_SASS)
        
        if result.parsed_mlir.ops:
            entity_id = result.parsed_mlir.ops[0].entity_id
            lineage = get_lineage(result, entity_id)
            
            assert "upstream" in lineage
            assert "downstream" in lineage
            assert isinstance(lineage["upstream"], list)
            assert isinstance(lineage["downstream"], list)
