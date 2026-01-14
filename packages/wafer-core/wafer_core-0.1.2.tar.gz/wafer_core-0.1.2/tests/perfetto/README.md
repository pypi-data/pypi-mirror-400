# Perfetto Test Suite

Comprehensive test suite for the Perfetto trace profiling tool, covering both backend Python implementation and frontend TypeScript handlers.

## 📊 Test Coverage Summary

| Component | Tests | Type |
|-----------|-------|------|
| Backend (wafer-core) | **78 tests** | Unit + Integration |
| Frontend (wevin-extension) | **47 tests** | Unit + Integration |
| **Total** | **125 tests** | |

---

## 🐍 Backend Tests

### `test_trace_manager.py` — TraceManager Unit Tests

Tests for trace file storage, listing, retrieval, and deletion operations.

#### Test Classes

| Class | Description | Tests |
|-------|-------------|-------|
| `TestTraceMetaSerialization` | `to_dict()` / `from_dict()` serialization roundtrip | 3 |
| `TestTraceManagerBasicOperations` | Store, copy, metadata creation, .gz handling | 7 |
| `TestTraceManagerListTraces` | Listing, sorting by timestamp (newest first) | 2 |
| `TestTraceManagerGetTrace` | Retrieval, error handling, path traversal security | 4 |
| `TestTraceManagerDeleteTrace` | Deletion, idempotency, security checks | 4 |
| `TestTraceManagerValidation` | File validation (empty, invalid JSON, nonexistent) | 4 |

#### Key Tests

- **Path Traversal Security**: Blocks attempts like `../../../etc/passwd`, `foo/../bar`
- **Gzip Handling**: Preserves `.gz` extension for compressed traces
- **Timestamp Sorting**: Traces sorted newest-first in listings

---

### `test_trace_processor.py` — TraceProcessorManager Unit Tests

Tests for binary management, version detection, and server operations.

#### Test Classes

| Class | Description | Tests |
|-------|-------------|-------|
| `TestTraceProcessorStatusSerialization` | Status object serialization | 2 |
| `TestTraceProcessorServerState` | `is_running()`, `stop()` lifecycle | 3 |
| `TestTraceProcessorManagerPlatformDetection` | Platform-specific binary names | 7 |
| `TestTraceProcessorVersionDetection` | UI/TP version compatibility | 4 |
| `TestTraceProcessorManagerStatus` | Binary availability checks | 2 |
| `TestTraceProcessorManagerServerOperations` | Server start/stop | 4 |
| `TestTraceProcessorManagerInvariants` | Property-based invariant tests | 3 |

#### Platform Binary Mapping

```
darwin-arm64   → trace_processor_mac_arm64
darwin-x86_64  → trace_processor_mac_x64
linux-arm64    → trace_processor_linux_arm64
linux-x86_64   → trace_processor_linux_x64
```

---

### `test_perfetto_tool.py` — PerfettoTool Unit Tests

Tests for the main orchestration layer that combines TraceManager + TraceProcessorManager.

#### Test Classes

| Class | Description | Tests |
|-------|-------------|-------|
| `TestPerfettoConfig` | Frozen dataclass immutability | 3 |
| `TestPerfettoToolTraceManagement` | Delegation to TraceManager | 5 |
| `TestPerfettoToolValidation` | Trace file validation | 2 |
| `TestPerfettoToolProcessorManagement` | trace_processor status/server | 3 |
| `TestPerfettoToolCLI` | CLI command functions | 4 |
| `TestPerfettoToolInvariants` | Property-based invariants | 3 |

#### CLI Commands Tested

- `cmd_list` — Returns traces dict
- `cmd_store` — Success and failure cases
- `cmd_delete` — Successful deletion

---

### `test_perfetto_integration.py` — E2E Integration Tests

Real file system operations testing complete workflows.

#### Test Classes

| Class | Description | Tests |
|-------|-------------|-------|
| `TestTraceWorkflowE2E` | Complete trace lifecycle | 3 |
| `TestDirectoryStructureE2E` | `.wafer/traces/` structure verification | 2 |
| `TestCLIIntegration` | CLI command execution | 1 |
| `TestErrorHandlingE2E` | Error scenarios | 2 |
| `TestConcurrentOperations` | Stress testing | 1 |

#### Complete Lifecycle Test

```
store → list → get → verify content → delete → verify removal
```

#### Stress Test

- 20 rapid store/delete cycles
- Verifies no state corruption

---

## 🟦 Frontend Tests

Located in `apps/wevin-extension/`:

### `handlers.test.ts` — Handler Unit Tests

**25 tests** covering all Perfetto handlers.

#### Test Suites

| Suite | Description | Tests |
|-------|-------------|-------|
| `Perfetto Feature Click Tracking` | All 5 features (Timeline, Query, Viz, Metrics, Stats) | 6 |
| `PerfettoHandler Class` | Core handler methods | 8 |
| `handlePanelPerfettoListTraces` | List traces handler | 3 |
| `handlePanelPerfettoOpenTrace` | Open trace handler | 3 |
| `handlePanelPerfettoDeleteTrace` | Delete trace handler | 3 |
| `handlePanelPerfettoDownloadTrace` | Download trace handler | 2 |

### `perfetto.integration.test.ts` — E2E Integration Tests

**22 tests** testing real file operations in temp directories.

#### Test Suites

| Suite | Description | Tests |
|-------|-------------|-------|
| `Trace Storage` | Store, unique IDs, content preservation | 3 |
| `Trace Listing` | Empty workspace, all traces, sorting, corrupted skip | 4 |
| `Trace Deletion` | Remove directory, remove from list, isolation | 4 |
| `Complete Workflow` | Full lifecycle test | 2 |
| `Directory Structure` | `.wafer/traces/{traceId}/` verification | 2 |
| `Error Handling` | Nonexistent files, rapid cycles | 2 |
| `Perfetto UI Server` | Port constant, MIME types | 2 |
| `Trace Validation` | JSON structure, empty files, gzip | 3 |

---

## 🚀 Running Tests

### Backend (Python)

```bash
# Run all Perfetto tests
cd packages/wafer-core
uv run pytest tests/perfetto/ -v

# Run specific test file
uv run pytest tests/perfetto/test_trace_manager.py -v

# Run with coverage
uv run pytest tests/perfetto/ --cov=wafer_core.tools.perfetto --cov-report=html

# Run only unit tests (faster)
uv run pytest tests/perfetto/test_trace_manager.py tests/perfetto/test_trace_processor.py tests/perfetto/test_perfetto_tool.py -v

# Run only integration tests
uv run pytest tests/perfetto/test_perfetto_integration.py -v
```

### Frontend (TypeScript)

```bash
# Run all Perfetto tests
cd apps/wevin-extension
yarn test:webview src/pages/perfetto/extension/__tests__/handlers.test.ts src/test/perfetto.integration.test.ts

# Run unit tests only
yarn test:webview src/pages/perfetto/extension/__tests__/handlers.test.ts

# Run integration tests only
yarn test:webview src/test/perfetto.integration.test.ts

# Run with verbose output
yarn test:webview --reporter=verbose src/pages/perfetto/
```

---

## 📁 Test Fixtures

### Backend Fixtures

| Fixture | Description |
|---------|-------------|
| `tmp_workspace` | Temporary workspace directory (auto-cleanup) |
| `sample_trace_file` | Chrome trace JSON with kernel events |
| `realistic_trace_file` | Trace with CUDA, CPU, and memory events |
| `gz_trace_file` | Gzip-compressed trace file |
| `e2e_workspace` | Isolated workspace for E2E tests |

### Frontend Fixtures

| Fixture | Description |
|---------|-------------|
| `createTestWorkspace()` | Creates temp directory with `.wafer/traces/` |
| `createTraceFile()` | Creates JSON trace file |
| `storeTrace()` | Stores trace with metadata |
| `listTraces()` | Lists traces from workspace |
| `deleteTrace()` | Deletes trace by ID |

---

## 🏗️ Test Structure Comparison

This test suite follows the same patterns as the workspaces test suite:

| Workspaces | Perfetto |
|------------|----------|
| `services/wafer-api/tests/workspaces/` | `packages/wafer-core/tests/perfetto/` |
| `handlers.test.ts` | `handlers.test.ts` (extended) |
| `workspaces.integration.test.ts` | `perfetto.integration.test.ts` |

---

## ✅ Test Results

```
Backend:  78 passed in 0.36s
Frontend: 47 passed (25 unit + 22 integration)
Total:    125 passed
```

---

## 📝 Notes

- Tests use `tmp_path` / `mkdtempSync` for isolation (no side effects)
- All tests are independent and can run in any order
- Integration tests perform real file system operations
- Path traversal attacks are explicitly tested and blocked
- Corrupted metadata is gracefully handled (skipped, not crashed)

