# BigPlanet Refactoring and Testing Development Plan

## Executive Summary

This document outlines a comprehensive plan to upgrade the BigPlanet repository to meet modern software engineering standards while adhering to the project's style guide and testing philosophy. The work will proceed in three major phases: comprehensive testing development, code style standardization, and architectural refactoring.

**Current State Assessment**: BigPlanet is a functional tool for compressing and analyzing VPLanet simulation data, but it suffers from inconsistent coding practices, inadequate test coverage, and numerous style guide violations accumulated from multiple contributors.

**Development Priority**: Testing infrastructure first, then style improvements, then refactoring. This ensures we can verify correctness throughout the upgrade process.

---

## Phase 1: Comprehensive Testing Infrastructure (Highest Priority)

### 1.1 Current Testing State Analysis

**Strengths:**
- 10 integration tests covering main workflows
- Tests validate end-to-end functionality with vspace/multiplanet integration
- GitHub Actions CI configured for Python 3.6-3.9

**Critical Weaknesses:**
- Most tests are currently commented out (only setup/teardown running)
- No unit tests for individual functions
- No tests for error handling and edge cases
- No coverage reporting configured in local development
- Test data dependencies on external tools (vspace, multiplanet, vplanet)
- Tests only verify file existence, not data correctness
- No parametric tests for different input combinations
- Deprecated regex escape sequence warning in read.py:227

**Coverage Gaps by Module:**

1. **archive.py (238 lines, 4 functions)**
   - `Archive()`: Main archiving function - tested only via integration
   - `CreateCP()`: Checkpoint creation - not unit tested
   - `ReCreateCP()`: Checkpoint recovery - not tested
   - `par_worker()`: Parallel worker - no concurrency testing

2. **bigplanet.py (145 lines, 2 functions)**
   - `Main()`: Entry point - basic integration test only
   - `Arguments()`: CLI parsing - no validation tests
   - Error handling paths not tested

3. **process.py (560 lines, 7 functions)**
   - `ProcessLogFile()`: 157 lines - no unit tests
   - `ProcessOutputfile()`: 48 lines - no unit tests
   - `ProcessSeasonalClimatefile()`: 52 lines - no unit tests
   - `ProcessInputfile()`: 72 lines - no unit tests
   - `ProcessInfileUnits()`: 79 lines - no unit tests (complex logic)
   - `GatherData()`: 75 lines - no unit tests
   - `DictToBP()`: 47 lines - no unit tests

4. **extract.py (574 lines, 16 functions)**
   - `BPLFile()`: File validation - no error path tests
   - `ExtractColumn()`: 87 lines - only integration tests
   - Statistical functions (mean, stddev, min, max, mode, geomean) - not tested
   - `Md5CheckSum()`: Critical security function - minimal testing

5. **read.py (329 lines, 7 functions)**
   - `ReadFile()`: 127 lines - complex parsing logic untested
   - `GetVplanetHelp()`: Subprocess call - no mocking/error tests
   - `DollarSign()`: Recursive function - no unit tests
   - Input validation not tested

6. **filter.py (265 lines, 2 functions)**
   - `Filter()`: 199 lines - only integration tests
   - `SplitsaKey()`: List processing - no unit tests

7. **bpstatus.py (50 lines, 2 functions)**
   - `bpstatus()`: Basic integration test
   - File not found error handling not tested

### 1.2 Testing Development Strategy

**Objective**: Achieve >90% code coverage with comprehensive unit and integration tests

#### 1.2.1 Unit Test Development (Priority Order)

**Phase 1A: Critical Path Functions**
1. `ProcessLogFile()` - Core data extraction
2. `ProcessInputfile()` - Input parsing
3. `ProcessInfileUnits()` - Unit conversion logic
4. `DictToBP()` - HDF5 writing
5. `ExtractColumn()` - Data retrieval
6. `Md5CheckSum()` - Data integrity

**Phase 1B: Support Functions**
7. `ReadFile()` - Input file parsing
8. `GetVplanetHelp()` - VPLanet metadata
9. `ProcessOutputfile()` - Output file processing
10. `ProcessSeasonalClimatefile()` - Climate data
11. `GatherData()` - Data aggregation
12. Statistical functions (mean, stddev, etc.)

**Phase 1C: Infrastructure Functions**
13. `CreateCP()` - Checkpoint management
14. `ReCreateCP()` - Checkpoint recovery
15. `SplitsaKey()` - Key parsing
16. `DollarSign()` - Line continuation
17. Archive/filter helper functions

#### 1.2.2 Test Coverage Requirements

For each function, develop tests covering:

1. **Happy Path Tests**
   - Valid inputs with expected outputs
   - Multiple realistic scenarios
   - Boundary conditions within valid range

2. **Error Handling Tests**
   - Invalid inputs (wrong type, out of range)
   - Missing files or corrupted data
   - Malformed input formats
   - Edge cases (empty files, single entry, maximum size)

3. **Integration Tests**
   - Function interactions
   - Data flow through processing pipeline
   - Concurrent execution (for parallel functions)

4. **Regression Tests**
   - Known bug fixes
   - Previous failure cases
   - Version compatibility

#### 1.2.3 Test Infrastructure Improvements

**Test Fixtures and Utilities**
- Create `tests/fixtures/` directory with minimal test data
- Develop mock VPLanet output generators
- Build reusable test data factories
- Create assertion helpers for floating-point comparisons
- Develop HDF5 file comparison utilities

**Test Organization**
```
tests/
├── unit/                    # New: Unit tests for individual functions
│   ├── test_archive.py
│   ├── test_process.py
│   ├── test_extract.py
│   ├── test_read.py
│   ├── test_filter.py
│   └── test_bpstatus.py
├── integration/             # Rename existing tests
│   ├── test_archive_workflow.py
│   ├── test_filter_workflow.py
│   ├── test_stats_workflow.py
│   └── test_ulysses_workflow.py
├── fixtures/                # New: Test data
│   ├── minimal_sim/         # Minimal valid simulation
│   ├── corrupt_data/        # Corrupted data for error tests
│   └── generators.py        # Test data generation
└── conftest.py             # Pytest configuration and shared fixtures
```

**Coverage Configuration**
- Configure pytest-cov for detailed coverage reports
- Set minimum coverage threshold: 90%
- Enable branch coverage analysis
- Add coverage badge to README
- Generate HTML coverage reports for local development

**Continuous Integration Enhancements**
- Add coverage reporting to GitHub Actions
- Configure CodeCov integration
- Add test performance monitoring
- Enable parallel test execution
- Add test failure notifications

#### 1.2.4 Test Documentation

Each test file should include:
- Module-level docstring explaining test scope
- Test function docstrings with Given/When/Then structure
- Comments for non-obvious test setup
- References to requirement/bug tracking if applicable

### 1.3 Testing Deliverables

1. **Unit Test Suite**: ~100-150 unit tests covering all functions
2. **Integration Test Suite**: 15-20 comprehensive workflow tests
3. **Test Fixtures**: Minimal, reusable test data sets
4. **Coverage Reports**: Automated coverage tracking >90%
5. **Test Documentation**: Clear test purpose and structure
6. **CI/CD Updates**: Enhanced GitHub Actions workflow

---

## Phase 2: Code Style Standardization

### 2.1 Current Style Guide Violations

**Critical Violations:**

1. **Naming Conventions (Hungarian Notation)**
   - Most variables lack type prefixes (b, i, f, d, dict, list)
   - Examples from process.py:
     - `prop` should be `sProp` (string)
     - `body` should be `sBody` (string)
     - `data` should be `dictData` (dictionary)
     - `units` should be `listUnits` or `sUnits` (list or string)
     - `verbose` should be `bVerbose` (boolean)
     - `next` should be `bNext` (boolean)
     - `num` should be `iNum` (integer)

2. **Function Naming**
   - Functions don't follow `f<returntype>` convention
   - Examples:
     - `Archive()` should be `fnArchive()` (no return)
     - `GetSims()` should be `flistGetSims()` (returns list)
     - `ReadFile()` should be `ftReadFile()` (returns tuple)
     - `BPLFile()` should be `fBPLFile()` or `fhBPLFile()` (returns h5py.File handle)

3. **Function Length**
   - `ProcessLogFile()`: 157 lines (max 20 allowed)
   - `ProcessInputfile()`: 72 lines (max 20 allowed)
   - `ProcessInfileUnits()`: 79 lines (max 20 allowed)
   - `Filter()`: 199 lines (max 20 allowed)
   - `par_worker()`: 79 lines (max 20 allowed)
   - `Main()`: 75 lines (max 20 allowed)

4. **Code Duplication**
   - Repeated include/exclude list checking in process.py (lines 57-66, 95-102, 144-152, etc.)
   - Repeated data dictionary updates
   - Repeated file path construction
   - Duplicate error messages

5. **Comment Overuse**
   - Many inline comments explaining obvious operations
   - Code should be self-documenting with better names

**Minor Violations:**

6. **Import Organization**
   - Wildcard imports (`from .extract import *`)
   - Non-standard import order

7. **Error Handling**
   - Many `exit()` calls without proper exception raising
   - Inconsistent error messages
   - Some functions don't validate inputs

8. **Documentation**
   - Inconsistent docstring format
   - Missing parameter descriptions
   - No return type documentation

### 2.2 Style Standardization Strategy

#### 2.2.1 Automated Fixes (Safe, Low Risk)

1. **Import Cleanup**
   - Remove wildcard imports, use explicit imports
   - Organize imports: stdlib, third-party, local
   - Remove unused imports

2. **Regex Escape Sequences**
   - Fix deprecation warning in read.py:227
   - Use raw strings for regex patterns

3. **Whitespace Standardization**
   - Consistent indentation (4 spaces)
   - Remove trailing whitespace
   - Consistent blank line usage

#### 2.2.2 Manual Refactoring (Requires Careful Testing)

**Priority 1: Variable Renaming**
- Rename variables to follow Hungarian notation
- Update all references consistently
- Run full test suite after each module

**Priority 2: Function Decomposition**
For each oversized function:
1. Identify logical blocks (5-15 line segments)
2. Extract reusable blocks as new functions
3. Follow single responsibility principle
4. Name new functions descriptively with type prefixes
5. Test extracted functions independently

Example: `ProcessLogFile()` decomposition
```python
# Current: 157 lines
def ProcessLogFile(logfile, data, folder, verbose, incl=None, excl=None):
    # ... 157 lines of mixed logic

# Target: ~10 lines calling subfunctions
def fdictProcessLogFile(sLogfile, dictData, sFolder, bVerbose, listIncl=None, listExcl=None):
    """Process log file and extract data into dictionary."""
    listContent = flistReadLogFile(sLogfile, sFolder)
    dictData = fdictExtractInitialProperties(listContent, dictData, listIncl, listExcl)
    dictData = fdictExtractFinalProperties(listContent, dictData, listIncl, listExcl)
    dictData = fdictExtractBodyProperties(listContent, dictData, listIncl, listExcl)
    return dictData

def flistReadLogFile(sLogfile, sFolder):
    """Read log file and return stripped lines."""
    sPath = os.path.join(sFolder, sLogfile)
    with open(sPath, "r+", errors="ignore") as fileLog:
        return [line.strip() for line in fileLog.readlines()]

def fdictExtractInitialProperties(listContent, dictData, listIncl, listExcl):
    """Extract initial system properties from log content."""
    # Extract logic for initial properties (< 20 lines)
    ...

def fdictExtractFinalProperties(listContent, dictData, listIncl, listExcl):
    """Extract final system properties from log content."""
    # Extract logic for final properties (< 20 lines)
    ...

def fdictExtractBodyProperties(listContent, dictData, listIncl, listExcl):
    """Extract body-specific properties from log content."""
    # Extract logic for body properties (< 20 lines)
    ...
```

**Priority 3: Eliminate Code Duplication**
1. Identify repeated patterns
2. Extract to utility functions
3. Update all call sites
4. Verify with tests

Example: Include/exclude checking
```python
# Create utility function
def fbShouldIncludeKey(sKeyName, listIncl, listExcl):
    """Determine if key should be included based on include/exclude lists."""
    if listIncl is not None:
        return sKeyName in listIncl
    if listExcl is not None:
        return sKeyName not in listExcl
    return True

def fnAddDataIfIncluded(dictData, sKeyName, value, sUnits, listIncl, listExcl):
    """Add data to dictionary if key should be included."""
    if fbShouldIncludeKey(sKeyName, listIncl, listExcl):
        if sKeyName in dictData:
            dictData[sKeyName].append(value)
        else:
            dictData[sKeyName] = [sUnits, value]
```

**Priority 4: Error Handling Improvement**
- Replace `exit()` with proper exceptions
- Create custom exception classes
- Add try/except blocks for file operations
- Provide actionable error messages

**Priority 5: Function Renaming**
- Rename all functions to follow style guide
- Update all call sites
- Update tests
- Update documentation

### 2.3 Style Standardization Deliverables

1. **Renamed Variables**: All variables follow Hungarian notation
2. **Refactored Functions**: All functions <20 lines
3. **Renamed Functions**: All functions follow naming convention
4. **Reduced Duplication**: Utility functions for common patterns
5. **Improved Error Handling**: Custom exceptions, no raw exit() calls
6. **Updated Tests**: All tests pass with new names/structure
7. **Style Guide Compliance Document**: Verification checklist

---

## Phase 3: Architectural Refactoring

### 3.1 Current Architecture Issues

1. **Module Responsibilities**
   - `process.py`: Too many responsibilities (log, input, output, climate processing)
   - `extract.py`: Mixes extraction, statistics, conversion, and checksum
   - No clear separation of concerns

2. **Code Organization**
   - Related functions scattered across files
   - No clear data flow
   - Tight coupling between modules

3. **Data Structures**
   - Heavy reliance on dictionaries with string keys (error-prone)
   - No validation of dictionary structure
   - Units stored as strings alongside data

4. **Dependency Management**
   - Tight coupling to VPLanet command-line interface
   - Subprocess calls without proper error handling
   - No abstraction for external dependencies

### 3.2 Proposed Architecture

**Module Reorganization:**

```
bigplanet/
├── __init__.py              # Package initialization
├── cli/
│   ├── __init__.py
│   ├── bigplanet.py         # Main CLI entry
│   └── bpstatus.py          # Status CLI entry
├── core/
│   ├── __init__.py
│   ├── archive.py           # Archive creation/management
│   ├── filter.py            # Filtered file creation
│   └── checkpoint.py        # New: Checkpoint management
├── parsers/
│   ├── __init__.py
│   ├── logfile.py           # New: Log file parsing
│   ├── inputfile.py         # New: Input file parsing
│   ├── outputfile.py        # New: Output file parsing
│   └── climatefile.py       # New: Climate file parsing
├── extractors/
│   ├── __init__.py
│   ├── column.py            # New: Column extraction
│   ├── statistics.py        # New: Statistical functions
│   └── units.py             # New: Unit handling
├── converters/
│   ├── __init__.py
│   ├── hdf5.py              # New: HDF5 conversion
│   ├── csv.py               # New: CSV conversion
│   └── ulysses.py           # New: Ulysses format
├── validators/
│   ├── __init__.py
│   ├── checksum.py          # New: MD5 validation
│   └── structure.py         # New: Data structure validation
├── utils/
│   ├── __init__.py
│   ├── vplanet.py           # New: VPLanet interface
│   └── io.py                # New: File I/O utilities
└── models/                  # New: Data models
    ├── __init__.py
    ├── simulation.py        # Simulation data structure
    └── archive.py           # Archive data structure
```

**Benefits:**
- Clear separation of concerns
- Easier to test individual components
- Reduced coupling between modules
- More discoverable API
- Easier to maintain and extend

### 3.3 Refactoring Strategy

**This phase should only begin after Phases 1 and 2 are complete.**

1. Create new module structure alongside existing code
2. Migrate one function at a time
3. Update tests as functions move
4. Update imports gradually
5. Remove old code only when fully replaced
6. Maintain backward compatibility during transition

### 3.4 Architectural Refactoring Deliverables

1. **New Module Structure**: Organized by responsibility
2. **Data Models**: Typed data structures for simulations/archives
3. **Abstraction Layers**: Clean interfaces between components
4. **Backward Compatibility**: Maintain existing CLI/API
5. **Migration Guide**: Documentation for users of internal APIs

---

## Phase 4: Documentation and Quality Assurance

### 4.1 Documentation Updates

1. **Code Documentation**
   - Add comprehensive docstrings to all functions
   - Include parameter types and descriptions
   - Document return values
   - Add usage examples
   - Document exceptions raised

2. **API Documentation**
   - Update Sphinx documentation
   - Add auto-generated API docs
   - Include code examples
   - Document breaking changes

3. **Testing Documentation**
   - Document test organization
   - Explain how to run tests
   - Describe test data requirements
   - Document coverage expectations

4. **Developer Guide**
   - Explain architecture
   - Code style requirements
   - Contribution workflow
   - Release process

### 4.2 Quality Assurance

1. **Continuous Integration**
   - Update Python version matrix (3.6-3.14 target, 3.9+ required)
   - Add code quality checks (pylint, flake8)
   - Add security scanning
   - Add dependency vulnerability checks

2. **Pre-commit Hooks**
   - Auto-formatting (black)
   - Import sorting (isort)
   - Linting
   - Test execution

3. **Version Control**
   - Clear commit message standards
   - Branch naming conventions
   - Pull request templates
   - Code review checklist

---

## Implementation Phases

### Phase 1: Testing Infrastructure (Weeks 1-4)
- Week 1: Test fixtures and utilities
- Week 2: Critical path unit tests (Process functions)
- Week 3: Support function unit tests (Read, Extract)
- Week 4: Integration tests and coverage reporting

### Phase 2: Style Standardization (Weeks 5-8)
- Week 5: Variable renaming
- Week 6: Function decomposition (process.py, extract.py)
- Week 7: Function decomposition (filter.py, read.py)
- Week 8: Function renaming and duplication removal

### Phase 3: Architectural Refactoring (Weeks 9-12)
- Week 9: New module structure and models
- Week 10: Migrate parsers and extractors
- Week 11: Migrate converters and validators
- Week 12: Cleanup and backward compatibility

### Phase 4: Documentation and QA (Weeks 13-14)
- Week 13: Documentation updates
- Week 14: CI/CD enhancements and final QA

---

## Success Criteria

1. **Testing**
   - ✓ >90% code coverage
   - ✓ All tests passing on Python 3.9-3.14
   - ✓ No commented-out test code
   - ✓ Fast test execution (<5 min full suite)

2. **Style Compliance**
   - ✓ 100% compliance with Hungarian notation
   - ✓ All functions <20 lines
   - ✓ All functions follow naming convention
   - ✓ No code duplication
   - ✓ Proper error handling (no raw exit())

3. **Architecture**
   - ✓ Clear module organization
   - ✓ Low coupling between components
   - ✓ High cohesion within modules
   - ✓ Documented APIs

4. **Quality**
   - ✓ Comprehensive documentation
   - ✓ Automated quality checks
   - ✓ CI/CD pipeline functioning
   - ✓ No deprecation warnings

---

## Risk Mitigation

1. **Breaking Changes**: Maintain backward compatibility through deprecation warnings
2. **Test Failures**: Implement one change at a time with full test verification
3. **Performance Regression**: Benchmark critical paths before/after
4. **Data Corruption**: Extensive testing of HDF5 read/write operations
5. **Scope Creep**: Strict adherence to phase boundaries

---

## Notes for Development

- **Never modify scientific calculations** without explicit direction
- **Test rigorously** after each module is refactored
- **Commit frequently** with clear messages
- **Run full test suite** before each commit
- **Document all breaking changes**
- **Prioritize correctness over performance** during refactoring
- **Maintain Python 3.9+ compatibility** (targeting 3.6-3.14)
- **No new dependencies** without approval
- **Follow the style guide strictly** - it's non-negotiable

---

## Current Status

**Phase**: Planning Complete
**Next Steps**:
1. Create test fixtures and utilities
2. Begin unit tests for ProcessLogFile()
3. Set up coverage reporting

**Blockers**: None
**Dependencies**: vplanet, vspace, multiplanet (for integration tests)
