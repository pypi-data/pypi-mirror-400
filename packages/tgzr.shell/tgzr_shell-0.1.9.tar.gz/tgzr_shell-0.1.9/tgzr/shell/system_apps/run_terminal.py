if __name__ == "__main__":
    from .register import terminal_app
    from tgzr.shell.session import get_default_session

    session = get_default_session(ensure_set=True)
    terminal_app.run_app(session=session, version=None)
