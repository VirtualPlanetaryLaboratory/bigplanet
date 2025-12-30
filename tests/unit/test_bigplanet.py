"""
Unit tests for bigplanet CLI module.

Tests the main command-line interface functionality including argument
parsing and dispatching to Archive/Filter functions.
"""

import os
import pytest

from bigplanet import bigplanet


class TestMain:
    """Tests for Main() function."""

    def test_main_archive_mode(self, tempdir, monkeypatch):
        """
        Given: Input file with archive=True
        When: Main is called
        Then: Calls Archive function
        """
        pathInput = tempdir / "test.in"
        pathInput.write_text("sDestFolder test_sims\nsArchiveFile test.bpa\n")

        # Mock Archive to avoid actual archive creation
        archive_called = []
        def mock_archive(*args, **kwargs):
            archive_called.append((args, kwargs))

        monkeypatch.setattr('bigplanet.bigplanet.Archive', mock_archive)

        bigplanet.Main(
            str(pathInput),
            cores=1,
            quiet=True,
            overwrite=False,
            verbose=False,
            archive=True,
            deleterawdata=False,
            ignorecorrupt=False
        )

        assert len(archive_called) == 1

    def test_main_filter_mode(self, tempdir, monkeypatch):
        """
        Given: Input file with archive=False
        When: Main is called
        Then: Calls Filter function
        """
        pathInput = tempdir / "test.in"
        pathInput.write_text("sDestFolder test_sims\nsArchiveFile test.bpa\n")

        # Mock Filter to avoid actual filter creation
        filter_called = []
        def mock_filter(*args, **kwargs):
            filter_called.append((args, kwargs))

        monkeypatch.setattr('bigplanet.bigplanet.Filter', mock_filter)

        bigplanet.Main(
            str(pathInput),
            cores=1,
            quiet=True,
            overwrite=False,
            verbose=False,
            archive=False,
            deleterawdata=False,
            ignorecorrupt=False
        )

        assert len(filter_called) == 1

    # TODO: Add tests for deleterawdata functionality
    # These require complete BPL input files with all required fields
    # (sPrimaryFile, saBodyFiles, etc.) to avoid UnboundLocalError in ReadFile


class TestArguments:
    """Tests for Arguments() function and argument parsing."""

    def test_arguments_default_cores(self, monkeypatch):
        """
        Given: No -c flag provided
        When: Arguments is called
        Then: Uses all available cores
        """
        pathInput = "/tmp/test.in"

        # Mock sys.argv and Main
        monkeypatch.setattr('sys.argv', ['bigplanet', pathInput])

        main_called = []
        def mock_main(*args, **kwargs):
            main_called.append(args)

        monkeypatch.setattr('bigplanet.bigplanet.Main', mock_main)

        bigplanet.Arguments()

        # Should have been called with max cores
        assert len(main_called) == 1
        assert main_called[0][1] > 0  # cores argument

    def test_arguments_custom_cores(self, monkeypatch):
        """
        Given: -c 4 flag provided
        When: Arguments is called
        Then: Uses 4 cores
        """
        pathInput = "/tmp/test.in"

        monkeypatch.setattr('sys.argv', ['bigplanet', pathInput, '-c', '4'])

        main_called = []
        def mock_main(*args, **kwargs):
            main_called.append(args)

        monkeypatch.setattr('bigplanet.bigplanet.Main', mock_main)

        bigplanet.Arguments()

        assert main_called[0][1] == 4  # cores argument

    def test_arguments_quiet_flag(self, monkeypatch):
        """
        Given: -q flag provided
        When: Arguments is called
        Then: quiet=True passed to Main
        """
        pathInput = "/tmp/test.in"

        monkeypatch.setattr('sys.argv', ['bigplanet', pathInput, '-q'])

        main_called = []
        def mock_main(*args, **kwargs):
            main_called.append(args)

        monkeypatch.setattr('bigplanet.bigplanet.Main', mock_main)

        bigplanet.Arguments()

        assert main_called[0][2] == True  # quiet argument

    def test_arguments_verbose_flag(self, monkeypatch):
        """
        Given: -v flag provided
        When: Arguments is called
        Then: verbose=True passed to Main
        """
        pathInput = "/tmp/test.in"

        monkeypatch.setattr('sys.argv', ['bigplanet', pathInput, '-v'])

        main_called = []
        def mock_main(*args, **kwargs):
            main_called.append(args)

        monkeypatch.setattr('bigplanet.bigplanet.Main', mock_main)

        bigplanet.Arguments()

        assert main_called[0][4] == True  # verbose argument

    def test_arguments_archive_flag(self, monkeypatch):
        """
        Given: -a flag provided
        When: Arguments is called
        Then: archive=True passed to Main
        """
        pathInput = "/tmp/test.in"

        monkeypatch.setattr('sys.argv', ['bigplanet', pathInput, '-a'])

        main_called = []
        def mock_main(*args, **kwargs):
            main_called.append(args)

        monkeypatch.setattr('bigplanet.bigplanet.Main', mock_main)

        bigplanet.Arguments()

        assert main_called[0][5] == True  # archive argument

    def test_arguments_overwrite_flag(self, monkeypatch):
        """
        Given: -o flag provided
        When: Arguments is called
        Then: overwrite=True passed to Main
        """
        pathInput = "/tmp/test.in"

        monkeypatch.setattr('sys.argv', ['bigplanet', pathInput, '-o'])

        main_called = []
        def mock_main(*args, **kwargs):
            main_called.append(args)

        monkeypatch.setattr('bigplanet.bigplanet.Main', mock_main)

        bigplanet.Arguments()

        assert main_called[0][3] == True  # overwrite argument

    def test_arguments_deleterawdata_flag(self, monkeypatch):
        """
        Given: -deleterawdata flag provided
        When: Arguments is called
        Then: deleterawdata=True passed to Main
        """
        pathInput = "/tmp/test.in"

        monkeypatch.setattr('sys.argv', ['bigplanet', pathInput, '-deleterawdata'])

        main_called = []
        def mock_main(*args, **kwargs):
            main_called.append(args)

        monkeypatch.setattr('bigplanet.bigplanet.Main', mock_main)

        bigplanet.Arguments()

        assert main_called[0][6] == True  # deleterawdata argument

    def test_arguments_ignorecorrupt_flag(self, monkeypatch):
        """
        Given: -ignorecorrupt flag provided
        When: Arguments is called
        Then: ignorecorrupt=True passed to Main
        """
        pathInput = "/tmp/test.in"

        monkeypatch.setattr('sys.argv', ['bigplanet', pathInput, '-ignorecorrupt'])

        main_called = []
        def mock_main(*args, **kwargs):
            main_called.append(args)

        monkeypatch.setattr('bigplanet.bigplanet.Main', mock_main)

        bigplanet.Arguments()

        assert main_called[0][7] == True  # ignorecorrupt argument

    def test_arguments_missing_input_file(self, monkeypatch):
        """
        Given: No input file provided
        When: Arguments is called
        Then: argparse raises SystemExit
        """
        monkeypatch.setattr('sys.argv', ['bigplanet'])

        with pytest.raises(SystemExit):
            bigplanet.Arguments()

    def test_arguments_combined_flags(self, monkeypatch):
        """
        Given: Multiple flags provided
        When: Arguments is called
        Then: All flags passed correctly to Main
        """
        pathInput = "/tmp/test.in"

        monkeypatch.setattr('sys.argv',
            ['bigplanet', pathInput, '-a', '-c', '2', '-q', '-o'])

        main_called = []
        def mock_main(*args, **kwargs):
            main_called.append(args)

        monkeypatch.setattr('bigplanet.bigplanet.Main', mock_main)

        bigplanet.Arguments()

        # Verify: cores=2, quiet=True, overwrite=True, archive=True
        assert main_called[0][1] == 2  # cores
        assert main_called[0][2] == True  # quiet
        assert main_called[0][3] == True  # overwrite
        assert main_called[0][5] == True  # archive
