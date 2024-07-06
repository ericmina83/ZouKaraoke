import subprocess
from ZouKaraoke import main


def test():
    subprocess.run(
        ["poetry", "run", "python", "-m", "unittest", "tests.TestEventBus", "-v"]
    )


def start():
    main()
