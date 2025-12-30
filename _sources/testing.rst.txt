Testing Strategy
=================

BigPlanet uses a comprehensive two-tier testing approach that balances speed, reliability, and API compatibility verification.

Overview
--------

The BigPlanet test suite consists of:

- **133 unit tests** using synthetic VPLanet data (~1 second total runtime)
- **12 integration tests** using real VPLanet simulations (several minutes runtime)
- **74% code coverage** and growing

This hybrid approach provides:

1. **Fast feedback** during development (unit tests complete in <1 second)
2. **Platform independence** (unit tests work without VPLanet binary installed)
3. **API compatibility verification** (integration tests detect VPLanet format changes)
4. **Comprehensive coverage** (both synthetic edge cases and real-world scenarios)

Unit Tests: Synthetic Data
---------------------------

Location
~~~~~~~~

All unit tests are in ``tests/unit/``:

- ``test_read.py`` - Configuration file parsing (22 tests)
- ``test_process.py`` - Log file and output file processing (31 tests)
- ``test_extract.py`` - Data extraction and statistics (42 tests)
- ``test_filter.py`` - Key categorization (25 tests)
- ``test_bigplanet.py`` - CLI argument parsing (15 tests)

Why Synthetic Data?
~~~~~~~~~~~~~~~~~~~

Unit tests use hand-crafted VPLanet output files created in test fixtures. This approach provides:

**Speed**
  - Unit test suite completes in <1 second
  - No VPLanet binary execution required
  - Ideal for rapid development iteration

**Platform Independence**
  - Tests pass without VPLanet installation
  - Works on fresh developer machines
  - Compatible with minimal CI environments
  - No dependency on VPLanet version or build configuration

**Test Isolation**
  - Tests verify BigPlanet code only, not VPLanet correctness
  - Clear failure attribution (BigPlanet bug vs VPLanet bug)
  - Deterministic results across all platforms

**Edge Case Coverage**
  - Easy to create malformed files for error handling tests
  - Can test extreme values without long simulations
  - Complete control over input structure

Example: Synthetic Log File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unit tests use fixtures like this::

    @pytest.fixture
    def minimal_vplanet_log(tempdir):
        """Hand-crafted VPLanet log file for testing."""
        log_content = \"\"\"
    ---- FINAL SYSTEM PROPERTIES ----
    System Age: 4.500000e+09 years

    ----- BODY: earth ------
    Mass (Mearth): 1.000000e+00
    Radius (Rearth): 1.000000e+00
    \"\"\"
        log_file = tempdir / "earth.log"
        log_file.write_text(log_content)
        return log_file

This synthetic approach means:

- **No VPLanet execution** - file created instantly
- **Controlled values** - test exactly what you need
- **Portable** - works on any system

Fixtures and Test Data
~~~~~~~~~~~~~~~~~~~~~~

All synthetic test data is created using pytest fixtures in:

- ``tests/conftest.py`` - Shared fixtures for all tests
- ``tests/fixtures/generators.py`` - Helper functions to create simulation structures

Key fixtures include:

``tempdir``
  Temporary directory (pathlib.Path) automatically cleaned up after each test

``minimal_simulation_dir``
  Complete simulation directory structure with synthetic VPLanet files::

    test_sims/sim_00/
    ├── vpl.in          # Primary input file
    ├── earth.in        # Body input file
    ├── earth.log       # Synthetic log file
    └── earth.earth.forward  # Synthetic forward evolution file

``sample_vplanet_help_dict``
  Mock VPLanet parameter dictionary (replaces ``vplanet -H`` output)::

    {
        "dMass": {
            "Type": "Double",
            "Dimension(s)": "mass",
            "Default value": "0.0"
        },
        ...
    }

``mock_vplanet_help``
  Monkeypatch fixture that mocks ``GetVplanetHelp()`` across all modules

Running Unit Tests
~~~~~~~~~~~~~~~~~~

Run all unit tests::

    pytest tests/unit/ -v

Run with coverage report::

    pytest tests/unit/ --cov=bigplanet --cov-report=term-missing

Run specific test file::

    pytest tests/unit/test_read.py -v

Run specific test::

    pytest tests/unit/test_read.py::TestReadFile::test_read_file_basic -v

Integration Tests: Real VPLanet
--------------------------------

Test Scenarios
~~~~~~~~~~~~~~

Integration tests are in scenario-specific directories::

    tests/CreateHDF5/           # Archive creation
    tests/SingleSim/            # Single simulation archive
    tests/ExtractArchive/       # Archive extraction
    tests/ExtractFilterArchive/ # Filtered archive extraction
    tests/ExtractFilterRawData/ # Raw data filtering
    tests/Stats/                # Statistical aggregations
    tests/UlyssesAggregated/    # Ulysses MCMC format
    tests/UlyssesForward/       # Ulysses forward mode
    tests/MD5CheckSum/          # Deprecated MD5 tests
    tests/Bpstatus/             # Status checking
    tests/Fletcher32CheckSum/   # HDF5 checksum verification

What They Test
~~~~~~~~~~~~~~

Integration tests run the complete BigPlanet pipeline:

1. **vspace** - Generate VPLanet input parameter space
2. **multiplanet** - Run VPLanet simulations (real binary execution)
3. **bigplanet** - Create archive or filtered files
4. **Verification** - Check output correctness

Example: CreateHDF5 Integration Test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``tests/CreateHDF5/test_CreateHDF5.py`` test:

1. Runs ``vspace vspace.in`` to generate 3 simulation directories
2. Runs ``multiplanet vspace.in`` to execute 3 VPLanet simulations
3. Runs ``bigplanet bpl.in -a`` to create archive
4. Verifies archive contains all expected data

**VPLanet Configuration:**

- Modules: ``radheat`` + ``thermint`` (thermal evolution)
- Duration: 4.5 billion years
- Runtime per simulation: ~1.1 seconds
- Total test time: ~5 seconds (3 sims + overhead)

VPLanet API Contract Verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration tests **automatically detect VPLanet API changes**:

**Log File Format Changes**
  If VPLanet changes how it writes log files (e.g., different parameter names,
  different formatting), BigPlanet's ``ProcessLogFile()`` will fail to parse
  the output, causing integration tests to fail.

**Forward File Format Changes**
  If VPLanet changes time series output formats, ``ProcessOutputfile()`` will
  fail to read forward evolution data.

**Help Output Changes**
  If ``vplanet -H`` output format changes, ``GetVplanetHelp()`` will fail to
  parse parameter metadata.

This provides **implicit API contract testing** - any breaking change in VPLanet's
output format is immediately detected by integration test failures.

Requirements
~~~~~~~~~~~~

Integration tests require:

- VPLanet binary in ``PATH`` or ``/Users/rory/src/vplanet/bin/vplanet``
- vspace installed (``pip install vspace``)
- multiplanet installed (``pip install multi-planet``)

Running Integration Tests
~~~~~~~~~~~~~~~~~~~~~~~~~

Run all integration tests::

    pytest tests/CreateHDF5/ tests/SingleSim/ tests/ExtractArchive/ -v

Run specific scenario::

    pytest tests/CreateHDF5/test_CreateHDF5.py -v

**Warning:** Integration tests take several minutes due to VPLanet simulation time.

Why Not Use Real VPLanet in Unit Tests?
----------------------------------------

We **intentionally avoid** using real VPLanet in unit tests because:

Time Cost
~~~~~~~~~

- **Current unit tests:** <1 second
- **With real VPLanet (best case):** 22 seconds (20 VPLanet runs × 1.1 sec)
- **With real VPLanet (worst case):** 146 seconds (133 tests × 1.1 sec)
- **CI/CD pipeline:** 12 test matrix cells → 4-29 minutes vs <12 seconds

Environmental Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~

Unit tests would fail on:

- Fresh developer machines before VPLanet installation
- CI environments without VPLanet pre-installed
- Systems with incompatible VPLanet versions
- Platforms with different VPLanet compilation flags

Platform Variability
~~~~~~~~~~~~~~~~~~~~

VPLanet behavior can vary across:

- Python versions (3.9 vs 3.13 subprocess differences)
- Operating systems (macOS Intel vs ARM vs Ubuntu 22.04 vs 24.04)
- VPLanet versions (development branch vs release)
- Numerical precision (floating point rounding differences)

This creates **flaky tests** that pass sometimes and fail other times.

Test Isolation Violation
~~~~~~~~~~~~~~~~~~~~~~~~~

Unit tests should test **BigPlanet code**, not VPLanet correctness.

**Current approach:**
  Tests verify BigPlanet can parse *any* valid VPLanet output format

**With real VPLanet:**
  Test failures could indicate VPLanet bugs, BigPlanet bugs, or both - making
  debugging difficult

Non-Determinism
~~~~~~~~~~~~~~~

Real VPLanet may have:

- Floating point rounding variations across platforms
- Different numerical integration behavior
- Platform-specific SIMD optimizations
- Build-specific configurations

This makes tests **unreliable** and hard to debug.

Coverage Strategy
-----------------

Current Coverage by Module
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    Module              Coverage    Lines    Tests    Uncovered Lines
    ================================================================
    read.py                92%      179       22      Lines 66-67, 77-80, etc.
    process.py             83%      322       31      Lines 241-270, 346-423
    extract.py             73%      242       42      Lines 416-451
    archive.py             67%      117       30      Lines 61-88 (multiprocessing)
    filter.py              40%      121       25      Lines 208-271 (orchestration)
    bigplanet.py           24%       49       15      Lines 35-73 (deleterawdata)
    bpstatus.py             0%       35        0      Not yet tested
    ================================================================
    TOTAL                  74%     1107      133

Coverage Goals
~~~~~~~~~~~~~~

**Target: 90% coverage** through:

1. **Unit test expansion** (in progress)

   - filter.py refactoring and testing
   - archive.py multiprocessing tests
   - bpstatus.py basic tests
   - Edge case coverage in process.py

2. **Integration test maintenance** (complete)

   - Already covers all major workflows
   - Provides VPLanet API compatibility verification
   - No additional integration tests needed

3. **Synthetic fixtures** (ongoing)

   - Expand fixtures in conftest.py
   - Add edge case generators
   - Mock multiprocessing where possible

GitHub Actions CI/CD
--------------------

BigPlanet uses GitHub Actions to test across multiple environments:

Test Matrix
~~~~~~~~~~~

::

    Python Versions: 3.9, 3.10, 3.11, 3.12
    Operating Systems: Ubuntu 22.04, Ubuntu 24.04, macOS-13 (Intel), macOS-14 (ARM)

    Total combinations: 4 × 4 = 16 test matrix cells

Unit Tests in CI
~~~~~~~~~~~~~~~~

**Always run** on every commit:

- Fast (<1 second per matrix cell)
- Platform independent (synthetic data)
- No VPLanet installation required
- Catches BigPlanet regressions immediately

Integration Tests in CI
~~~~~~~~~~~~~~~~~~~~~~~~

**Run selectively** (comprehensive CI only):

- Require VPLanet binary installation
- Take several minutes per matrix cell
- Verify VPLanet API compatibility
- Run before releases or major merges

Running Tests Locally
----------------------

Quick Development Feedback
~~~~~~~~~~~~~~~~~~~~~~~~~~

During active development, run unit tests only::

    pytest tests/unit/ -v

This provides sub-second feedback for BigPlanet code changes.

Pre-Commit Verification
~~~~~~~~~~~~~~~~~~~~~~~

Before committing, run unit tests with coverage::

    pytest tests/unit/ --cov=bigplanet --cov-report=term-missing

Verify coverage hasn't decreased and new code is tested.

Pre-Push Verification
~~~~~~~~~~~~~~~~~~~~~

Before pushing to GitHub, run integration tests::

    pytest tests/CreateHDF5/ tests/SingleSim/ tests/ExtractArchive/ -v

This catches any VPLanet API incompatibilities.

Full Test Suite
~~~~~~~~~~~~~~~

To run everything (takes several minutes)::

    pytest tests/ -v

This runs all 133 unit tests + 12 integration tests.

Test Development Guidelines
----------------------------

When writing new tests, follow these principles:

1. **Unit tests use synthetic data**

   - Create fixtures in conftest.py
   - Hand-craft minimal VPLanet output files
   - Mock external dependencies (GetVplanetHelp, subprocess calls)

2. **Integration tests use real VPLanet**

   - Create new test scenario directory
   - Include VPLanet input files (vpl.in, body.in)
   - Run full vspace → multiplanet → bigplanet pipeline

3. **Test one thing at a time**

   - Unit tests should test a single function or behavior
   - Use Given-When-Then documentation format
   - Assert specific expected outcomes

4. **Keep functions testable**

   - Functions <20 lines are easier to test
   - Pure functions (no side effects) are easiest to test
   - Extract complex logic into separate testable functions

5. **Use descriptive test names**

   - ``test_process_log_file_with_grid_output_order()`` is better than ``test_log()``
   - Name should describe the scenario being tested
   - Someone should understand what's tested without reading the code

Example: Adding a New Test
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Good - Unit test with synthetic data:**

.. code-block:: python

    def test_process_log_file_missing_body_section(tempdir):
        \"\"\"
        Given: Log file without a body section
        When: ProcessLogFile is called
        Then: Returns empty data dictionary
        \"\"\"
        log_content = \"\"\"
    ---- FINAL SYSTEM PROPERTIES ----
    System Age: 0.0 sec
    \"\"\"
        log_file = tempdir / "test.log"
        log_file.write_text(log_content)

        result = process.ProcessLogFile("test.log", {}, str(tempdir))

        assert result == {}

**Bad - Unit test calling real VPLanet:**

.. code-block:: python

    def test_process_log_file_real_vplanet(tempdir):
        # DON'T DO THIS in unit tests
        subprocess.run(["vplanet", "vpl.in"], cwd=tempdir)
        result = process.ProcessLogFile("earth.log", {}, str(tempdir))
        # This belongs in integration tests, not unit tests

Summary
-------

BigPlanet's testing strategy provides:

✅ **Fast development iteration** (<1 second unit tests)

✅ **Platform independence** (synthetic data works everywhere)

✅ **VPLanet API verification** (integration tests catch format changes)

✅ **Comprehensive coverage** (74% → 90% goal)

✅ **Reliable CI/CD** (deterministic test results)

The two-tier approach (synthetic unit tests + real integration tests) balances
speed, reliability, and API compatibility verification without sacrificing any
of these critical goals.
