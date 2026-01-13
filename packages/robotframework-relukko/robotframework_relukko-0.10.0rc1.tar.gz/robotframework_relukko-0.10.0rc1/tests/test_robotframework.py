import platform
from pathlib import Path

from robot import run as rf_run
from robot import version

from Relukko import Relukko

SCRIPT_DIR = Path(__file__).parent.absolute()
ROBOT_FILE = SCRIPT_DIR / "relukko.robot"


def test_relukko_robot(relukko_backend):
    relukko, _ = relukko_backend
    base_url = relukko.client.base_url
    api_key = relukko.client.api_key
    ver_str=f"py_{platform.python_version()}-rf_{version.VERSION}"

    exit_code = rf_run(
        ROBOT_FILE,
        variable=[
            f"BASE_URL:{base_url}",
            f"API_KEY:{api_key}",
            f"VER_STR:{ver_str}",
        ],
        name=f"Relukko-{ver_str}",
        outputdir=SCRIPT_DIR.parent,
        log=f"log-{ver_str}.html",
        output=f"output-{ver_str}.xml",
        xunit=f"xunit-{ver_str}.xml",
        report="None",
    )
    assert exit_code == 0


def test_relukko_with_skip_robot(mock_env_relukko_skip):
    assert mock_env_relukko_skip is None
    relukko = Relukko(base_url="http://relukko", api_key="abcd")
    base_url = relukko.client.base_url
    api_key = relukko.client.api_key
    ver_str=f"py_{platform.python_version()}-rf_{version.VERSION}-skip"

    exit_code = rf_run(
        ROBOT_FILE,
        variable=[
            f"BASE_URL:{base_url}",
            f"API_KEY:{api_key}",
            f"VER_STR:{ver_str}",
        ],
        name=f"Relukko-{ver_str}",
        outputdir=SCRIPT_DIR.parent,
        log=f"log-{ver_str}.html",
        output=f"output-{ver_str}.xml",
        xunit=f"xunit-{ver_str}.xml",
        report="None",
        test="RelukkoLifeCycle",
    )
    assert exit_code == 0
