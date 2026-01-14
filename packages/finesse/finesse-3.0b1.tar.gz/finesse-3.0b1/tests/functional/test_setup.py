# import pytest
# from pathlib import Path

# import setup


# def test_check_pyx_files(tmpdir: Path, monkeypatch: pytest.MonkeyPatch):
#     tmpdir = Path(tmpdir)
#     monkeypatch.setattr(setup, "FINESSE_DIR", tmpdir)
#     fn = "foo.pyx"
#     pyx_file = Path(tmpdir / fn)
#     pyx_file.touch()
#     setup.check_pyx_files(pyx_files=[fn])


# def test_check_pyx_files_missing(tmpdir: Path, monkeypatch: pytest.MonkeyPatch):
#     tmpdir = Path(tmpdir)
#     monkeypatch.setattr(setup, "FINESSE_DIR", tmpdir)
#     fn = "foo.pyx"
#     with pytest.raises(FileNotFoundError):
#         setup.check_pyx_files(pyx_files=[fn])


# def test_check_pyx_files_ignore_hidden(tmpdir: Path, monkeypatch: pytest.MonkeyPatch):
#     tmpdir = Path(tmpdir)
#     monkeypatch.setattr(setup, "FINESSE_DIR", tmpdir)
#     fn = "foo.pyx"
#     pyx_file = tmpdir / fn
#     pyx_file.touch()
#     hidden_dir = tmpdir / ".ipynb_checkpoints"
#     hidden_dir.mkdir()
#     (hidden_dir / "bar.pyx").touch()
#     setup.check_pyx_files(pyx_files=[fn])
