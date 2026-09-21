from pathlib import Path

from nova.main import main


def test_version(capsys):
    result = main(["--version"])

    captured = capsys.readouterr()

    assert result == 0
    assert "Nova 0.1.0" in captured.out


def test_run_file(tmp_path, capsys):
    source = """
let x = 10;
let y = 20;

print(x + y);
"""

    file = tmp_path / "hello.nova"
    file.write_text(source, encoding="utf-8")

    result = main([str(file)])

    captured = capsys.readouterr()

    assert result == 0
    assert "30" in captured.out


def test_run_file_with_function(tmp_path, capsys):
    source = """
fn add(a, b) {
    return a + b;
}

print(add(5, 7));
"""

    file = tmp_path / "function.nova"
    file.write_text(source, encoding="utf-8")

    result = main([str(file)])

    captured = capsys.readouterr()

    assert result == 0
    assert "12" in captured.out


def test_missing_file(capsys):
    result = main(["does-not-exist.nova"])

    captured = capsys.readouterr()

    assert result == 1
    assert "does-not-exist.nova" in captured.err
