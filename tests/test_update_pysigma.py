from unittest.mock import patch, mock_open

import pytest
from packaging.specifiers import SpecifierSet
from packaging.version import Version

import scripts.update_pysigma as updater


class TestUpdatePysigma:
    @pytest.fixture
    def mock_toml_file(self):
        return """
        [tool.poetry.dependencies]
        pysigma = ">=0.9.1, <=0.10.6"
        """

    @pytest.fixture
    def mock_toml_file_caret(self):
        return """
        [tool.poetry.dependencies]
        pysigma = "^0.10.0"
        """

    @pytest.fixture
    def mock_toml_file_minimum(self):
        return """
        [tool.poetry.dependencies]
        pysigma = ">=0.9.0"
        """

    @pytest.fixture
    def mock_toml_file_maximum(self):
        return """
        [tool.poetry.dependencies]
        pysigma = "<=0.10.6"
        """

    @pytest.fixture
    def mock_toml_file_exact(self):
        return """
        [tool.poetry.dependencies]
        pysigma = "==0.10.7"
        """

    @pytest.fixture
    def mock_toml_file_no_dependency(self):
        return """
        [tool.poetry.dependencies]
        another-dependency = "1.0.0"
        """

    @pytest.fixture
    def mock_toml_file_multiple_specifiers(self):
        return """
        [tool.poetry.dependencies]
        pysigma = ">=0.9.0, <0.11.0, !=0.10.5"
        """

    @pytest.fixture
    def mock_toml_file_multiple_dependencies(self):
        return """
        [tool.poetry.dependencies]
        pysigma = ">=0.9.1, <=0.10.6"
        another-dependency = "1.0.0"
        """

    @patch("scripts.update_pysigma.get_latest_release")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        [tool.poetry.dependencies]
        pysigma = ">=0.9.1, <=0.10.6"
    """,
    )
    @patch("toml.dump")
    def test_update_version(self, mock_toml_dump, mock_open, mock_get_latest_release, mock_toml_file):
        mock_get_latest_release.return_value = Version("0.10.7")
        with patch("scripts.update_pysigma.read_pyproject_version", return_value=SpecifierSet(">=0.9.1, <=0.10.6")):
            with pytest.raises(SystemExit) as e:
                updater.main(dry_run=False)
            assert e.type == SystemExit
            assert e.value.code == 1
            updated_specifier = SpecifierSet(">=0.9.1, <=0.10.7")
            mock_toml_dump.assert_called_once()
            updated_toml = mock_toml_dump.call_args[0][0]
            assert SpecifierSet(updated_toml["tool"]["poetry"]["dependencies"]["pysigma"]) == updated_specifier

    @patch("scripts.update_pysigma.get_latest_release")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
            [tool.poetry.dependencies]
            pysigma = "^0.10.0"
        """,
    )
    @patch("toml.dump")
    def test_update_version_caret(self, mock_toml_dump, mock_open, mock_get_latest_release, mock_toml_file_caret):
        mock_get_latest_release.return_value = Version("0.10.7")
        preprocessed_spec = SpecifierSet(">=0.10.0, <0.11.0")
        with patch("scripts.update_pysigma.read_pyproject_version", return_value=preprocessed_spec):
            with pytest.raises(SystemExit) as e:
                updater.main(dry_run=False)
            assert e.type == SystemExit
            assert e.value.code == 0
            mock_toml_dump.assert_not_called()

    @patch("scripts.update_pysigma.get_latest_release")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        [tool.poetry.dependencies]
        pysigma = "^0.10.0"
    """,
    )
    @patch("toml.dump")
    def test_update_version_caret_update_needed(self, mock_toml_dump, mock_open, mock_get_latest_release):
        mock_get_latest_release.return_value = Version("0.11.0")
        preprocessed_spec = SpecifierSet(">=0.10.0, <0.11.0")
        with patch("scripts.update_pysigma.read_pyproject_version", return_value=preprocessed_spec):
            with pytest.raises(SystemExit) as e:
                updater.main(dry_run=False)
            assert e.type == SystemExit
            assert e.value.code == 1
            updated_specifier = SpecifierSet(">=0.10.0, <=0.11.0")
            mock_toml_dump.assert_called_once()
            updated_toml = mock_toml_dump.call_args[0][0]
            assert SpecifierSet(updated_toml["tool"]["poetry"]["dependencies"]["pysigma"]) == updated_specifier

    @patch("scripts.update_pysigma.get_latest_release")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        [tool.poetry.dependencies]
        pysigma = ">=0.9.0"
    """,
    )
    @patch("toml.dump")
    def test_update_version_minimum_only(
        self, mock_toml_dump, mock_open, mock_get_latest_release, mock_toml_file_minimum
    ):
        mock_get_latest_release.return_value = Version("0.10.7")
        with patch("scripts.update_pysigma.read_pyproject_version", return_value=SpecifierSet(">=0.9.0")):
            with pytest.raises(SystemExit) as e:
                updater.main(dry_run=False)
            assert e.type == SystemExit
            assert e.value.code == 0
            mock_toml_dump.assert_not_called()

    @patch("scripts.update_pysigma.get_latest_release")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        [tool.poetry.dependencies]
        pysigma = "<=0.10.6"
    """,
    )
    @patch("toml.dump")
    def test_update_version_maximum_only(
        self, mock_toml_dump, mock_open, mock_get_latest_release, mock_toml_file_maximum
    ):
        mock_get_latest_release.return_value = Version("0.10.7")
        with patch("scripts.update_pysigma.read_pyproject_version", return_value=SpecifierSet("<=0.10.6")):
            with pytest.raises(SystemExit) as e:
                updater.main(dry_run=False)
            assert e.type == SystemExit
            assert e.value.code == 1
            updated_specifier = SpecifierSet("<=0.10.7")
            mock_toml_dump.assert_called_once()
            updated_toml = mock_toml_dump.call_args[0][0]
            assert SpecifierSet(updated_toml["tool"]["poetry"]["dependencies"]["pysigma"]) == updated_specifier

    @patch("scripts.update_pysigma.get_latest_release")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        [tool.poetry.dependencies]
        pysigma = "==0.10.7"
    """,
    )
    @patch("toml.dump")
    def test_update_version_exact_match(self, mock_toml_dump, mock_open, mock_get_latest_release, mock_toml_file_exact):
        mock_get_latest_release.return_value = Version("0.10.7")
        with patch("scripts.update_pysigma.read_pyproject_version", return_value=SpecifierSet("==0.10.7")):
            with pytest.raises(SystemExit) as e:
                updater.main(dry_run=False)
            assert e.type == SystemExit
            assert e.value.code == 0
            mock_toml_dump.assert_not_called()

    @patch("scripts.update_pysigma.get_latest_release")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        [tool.poetry.dependencies]
        another-dependency = "1.0.0"
    """,
    )
    @patch("toml.dump")
    def test_no_pysigma_dependency(
        self, mock_toml_dump, mock_open, mock_get_latest_release, mock_toml_file_no_dependency
    ):
        mock_get_latest_release.return_value = Version("0.10.7")
        with patch("scripts.update_pysigma.read_pyproject_version", side_effect=KeyError):
            with pytest.raises(KeyError):
                updater.main(dry_run=False)
            mock_toml_dump.assert_not_called()

    @patch("scripts.update_pysigma.get_latest_release")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        [tool.poetry.dependencies]
        pysigma = ">=0.9.0, <0.11.0, !=0.10.5"
    """,
    )
    @patch("toml.dump")
    def test_update_version_multiple_specifiers(
        self, mock_toml_dump, mock_open, mock_get_latest_release, mock_toml_file_multiple_specifiers
    ):
        mock_get_latest_release.return_value = Version("0.11.0")
        with patch(
            "scripts.update_pysigma.read_pyproject_version", return_value=SpecifierSet(">=0.9.0, <0.11.0, !=0.10.5")
        ):
            with pytest.raises(SystemExit) as e:
                updater.main(dry_run=False)
            assert e.type == SystemExit
            assert e.value.code == 1
            updated_specifier = SpecifierSet(">=0.9.0, !=0.10.5, <=0.11.0")
            mock_toml_dump.assert_called_once()
            updated_toml = mock_toml_dump.call_args[0][0]
            assert SpecifierSet(updated_toml["tool"]["poetry"]["dependencies"]["pysigma"]) == updated_specifier

    @patch("scripts.update_pysigma.get_latest_release")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        [tool.poetry.dependencies]
        pysigma = ">=0.9.1, <=0.10.6"
        another-dependency = "1.0.0"
    """,
    )
    @patch("toml.dump")
    def test_update_version_multiple_dependencies(
        self, mock_toml_dump, mock_open, mock_get_latest_release, mock_toml_file_multiple_dependencies
    ):
        mock_get_latest_release.return_value = Version("0.10.7")
        with patch("scripts.update_pysigma.read_pyproject_version", return_value=SpecifierSet(">=0.9.1, <=0.10.6")):
            with pytest.raises(SystemExit) as e:
                updater.main(dry_run=False)
            assert e.type == SystemExit
            assert e.value.code == 1
            updated_specifier = SpecifierSet(">=0.9.1, <=0.10.7")
            mock_toml_dump.assert_called_once()
            updated_toml = mock_toml_dump.call_args[0][0]
            assert SpecifierSet(updated_toml["tool"]["poetry"]["dependencies"]["pysigma"]) == updated_specifier
            assert updated_toml["tool"]["poetry"]["dependencies"]["another-dependency"] == "1.0.0"


if __name__ == "__main__":
    pytest.main()
