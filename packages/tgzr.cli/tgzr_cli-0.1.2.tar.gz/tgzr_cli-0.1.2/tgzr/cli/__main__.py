import sys

if __name__ == "__main__":
    # NB: we need a absolute imports here for pyinstaller to work
    import tgzr.cli.main

    tgzr.cli.main.main()
