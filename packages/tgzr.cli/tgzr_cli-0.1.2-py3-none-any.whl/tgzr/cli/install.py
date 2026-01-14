from typing import Callable

import os
import sys
from pathlib import Path
import tempfile
import platform

import uv


def install(
    home: Path | str,
    studio_name: str,
    python_version: str | None = "3.12",
    default_index: str | None = None,
    find_links: str | None = None,
    allow_prerelease: bool = False,
    echo: Callable[[str], None] | None = None,
):
    """
    Install TGZR by creating a tmp venv with tgzr.shell, then
    using this tgzr.cli to create a Studio at the requested location.

    May raise: FileExistsError, ChildProcessError.
    """
    if echo is None:
        echo = lambda message: print(message)

    home = Path(home)
    studio_path = home / "Workspace" / studio_name
    if studio_path.exists():
        raise FileExistsError(f"The Studio {studio_path} already exists. Aborting.")

    echo(f"Installing tgzr at {home}, creating Studio {studio_name}")

    # We need to create the `.tgzr` file at requested home first, or
    # the cli may discover existing locations and create the Studio
    # in an existing installation:
    home.mkdir(exist_ok=True, parents=True)
    (home / ".tgzr").touch()

    venv_path = tempfile.mkdtemp(prefix="tgzr_install_tmp_venv")
    echo(f"Creating temp venv: {venv_path}")

    # Clean up PATH
    # (we've seen situations where things in the PATH would mess up the installation )
    PATH = os.environ.get("PATH", "")
    path = PATH.split(os.pathsep)
    banned_words = ["python", ".poetry"]
    clean_path = []
    for i in path:
        keep = True
        for word in banned_words:
            if word in i.lower():
                keep = False
                break
        if keep:
            clean_path.append(i)
    os.environ["PATH"] = os.pathsep.join(clean_path)

    if 0:
        # This does not work as pyinstaller script: sys.executable is wrong so venv is messed up
        print(sys.executable)
        cmd = f"{sys.executable} -m uv venv --prompt TGZR_installer {venv_path}"
        echo(f"EXEC: {cmd}")
        ret = os.system(cmd)
        print("--->", ret)
    elif 0:
        # This does not work as pyinstaller script: sys.executable is wrong so venv is messed up
        import venv

        try:
            venv.main(["--without-pip", "--prompt", "TGZR-Installer", venv_path])
        except Exception:
            raise
    else:
        # This does work as pyinstaller script: we are delegating everything to uv

        # Use this to inspect the content of the pyinstaller archive when
        # we run as a pysintaller script:
        # if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        #     ROOT = sys._MEIPASS
        #     print("FROZEN CONTENT:", os.listdir(ROOT))

        try:
            # NOTE: this also works when we're a pysintaller script thanks to the
            # data arg of the Analysis in the pyinstall spec file:
            # it keeps the uv executable installed in your current venv
            # (it exists because we have uv in the project requirement)
            # and place it in a "bin" folder inside the pysintaller archive.
            # This bin folder is looked up by uv.find_uv_bin() so we're
            # good.
            uv_exe = uv.find_uv_bin()
        except Exception as err:
            # This should not occur ¯\\_(ツ)_/¯
            echo(f"Oops, could not find uv: {err}")
        else:
            cmd = (
                f"{uv_exe} venv -p {python_version} --prompt TGZR-Installer {venv_path}"
            )
            echo(f"EXEC: {cmd}")
            ret = os.system(cmd)
            if ret:
                raise Exception("Error creating venv with cmd: {cmd}")

        default_index_options = ""
        if default_index:
            default_index_options = f"--default-index {default_index}"

        find_links_options = ""
        if find_links:
            find_links_options = f"--find-links {find_links}"

        prerelease_options = ""
        if allow_prerelease:
            prerelease_options = "--prerelease=allow"

        # Install tgzr.shell in the temp venv:
        cmd = f"{uv_exe} pip install {default_index_options} {find_links_options} {prerelease_options} --python {venv_path} tgzr.shell"
        echo(f"EXEC: {cmd}")
        ret = os.system(cmd)
        if ret:
            raise ChildProcessError("Error installing packages in venv with cmd: {cmd}")

        # Use tgzr.cli from the temp venv to create the Studio
        # ! Don't forget to pass the index related options there !
        index_options = ""
        if default_index:
            index_options += f" --default-index {default_index}"
        if find_links:
            index_options += f" --find-links {find_links}"
        if allow_prerelease:
            index_options += " --allow-prerelease"
        if 0:
            # IDKW but this does not work, it runs the orignal tgzr cmd instead of the venv one :[
            cmd = f"{uv_exe} run --python {venv_path} tgzr --home {home} studio create {index_options} {studio_name}"
        else:
            if platform.system() == "Windows":
                tgzr_exe = f"{venv_path}/Scripts/tgzr"
            else:
                tgzr_exe = f"{venv_path}/bin/tgzr"
        cmd = f"{tgzr_exe} --home {home} studio create {index_options}  {studio_name}"
        ret = os.system(cmd)
        echo(f"EXEC: {cmd}")
        if ret:
            raise ChildProcessError(f"Error creating Studio with cmd: {cmd}")
