from pathlib import Path
import sys
import os

if __name__ == '__main__':
    sys.path.append(str(Path(__file__).parents[2] / "src"))
    os.chdir(Path(__file__).parents[2])
    from bionexo.application.webapp.main import create_n_run_app
    create_n_run_app()