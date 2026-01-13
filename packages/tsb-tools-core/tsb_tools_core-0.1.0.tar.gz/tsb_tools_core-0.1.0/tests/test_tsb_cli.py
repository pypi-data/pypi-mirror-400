from tsb_cli_tools import SbTyper


def test_tsb_cli_app_load_plugins():
    app = SbTyper("foo")
    app.load_plugins()
    assert app


def test_tsb_cli_invoke_repo(invoke_cli):
    result = invoke_cli("tsb", "repo", "generate", "docs")
    assert result.exit_code == 0
