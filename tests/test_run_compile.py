from pathlib import Path
import shutil

from click.testing import CliRunner
import pytest

from scss_compile import run_compile


@pytest.fixture()
def scss_folder(tmp_path):
    src = tmp_path / "scss"
    shutil.copytree(Path(__file__).parent / "example_scss", src)
    yield src
    shutil.rmtree(tmp_path)


def test_help():
    result = CliRunner().invoke(run_compile, ["--help"])
    assert result.exit_code == 0, result.output


def test_file(scss_folder):
    result = CliRunner().invoke(
        run_compile, ["--no-git-add", str(scss_folder / "example1.scss")]
    )
    assert result.exit_code == 2, result.output
    assert (scss_folder / "example1.css").exists(), result.output

    # should not change any files
    result = CliRunner().invoke(
        run_compile, ["--no-git-add", str(scss_folder / "example1.scss")]
    )
    assert result.exit_code == 0, result.output
    assert (scss_folder / "example1.css").exists(), result.output


def test_file_hash(scss_folder):
    result = CliRunner().invoke(
        run_compile,
        ["--no-git-add", str(scss_folder / "example1.scss"), "--hash-filenames"],
    )
    assert result.exit_code == 2, result.output
    assert len(list(scss_folder.glob("example1#*.css"))) == 1, result.output
    path = list(scss_folder.glob("example1#*.css"))[0]

    # should create same hash
    result = CliRunner().invoke(
        run_compile,
        ["--no-git-add", str(scss_folder / "example1.scss"), "--hash-filenames"],
    )
    assert result.exit_code == 0, result.output
    assert len(list(scss_folder.glob("example1#*.css"))) == 1, result.output
    assert path.exists(), result.output


def test_file_sourcemap(scss_folder):
    result = CliRunner().invoke(
        run_compile, ["--no-git-add", str(scss_folder / "example1.scss"), "--sourcemap"]
    )
    assert result.exit_code == 2, result.output
    assert (scss_folder / "example1.css").exists(), result.output
    assert (scss_folder / "example1.scss.map.json").exists(), result.output


def test_partials(scss_folder):
    result = CliRunner().invoke(
        run_compile, ["--no-git-add", str(scss_folder / "partials" / "_example1.scss")]
    )
    assert result.exit_code == 0, result.output
    assert not (scss_folder / "example1.css").exists(), result.output

    result = CliRunner().invoke(
        run_compile,
        [
            "--no-git-add",
            str(scss_folder / "partials" / "_example1.scss"),
            "--partial-depth=1",
        ],
    )
    assert result.exit_code == 2, result.output
    assert (scss_folder / "example1.css").exists(), result.output


def test_folder(scss_folder):
    result = CliRunner().invoke(run_compile, ["--no-git-add", str(scss_folder)])
    assert result.exit_code == 2, result.output
    assert (scss_folder / "example1.css").exists(), result.output
    assert (scss_folder / "example2.css").exists(), result.output


def test_translate(scss_folder):
    result = CliRunner().invoke(
        run_compile,
        [
            "--no-git-add",
            str(scss_folder / "example1.scss"),
            "--translate",
            str(scss_folder) + ":" + str(scss_folder.parent / "css"),
        ],
    )
    assert result.exit_code == 2, result.output
    assert not (scss_folder / "example1.css").exists(), result.output
    assert (scss_folder.parent / "css" / "example1.css").exists(), result.output
