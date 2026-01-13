from tsb_tools_core import SbTyper

app = SbTyper(app_name="tsb")


def main():
    app.load_plugins()
    app()


if __name__ == "__main__":
    main()
