import os
from pathlib import Path
import sys

if __name__ == '__main__':
    from streamlit.web import bootstrap
    import streamlit.config as _config

    os.environ["ENV_FILE"] = str(Path(__file__).parents[1] / ".env")

    from bionexo.application.webapp import main

    _config.set_option("browser.gatherUsageStats", False)
    _config.set_option("server.headless", True)
    sys.path.append(str(Path(__file__).parents[2] / "src"))

    app_path = main.__file__

    bootstrap.run(app_path, False, [], flag_options={})
