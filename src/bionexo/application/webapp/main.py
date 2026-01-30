
import os
from dotenv import load_dotenv


def create_n_run_app():
    load_dotenv(os.getenv("ENV_FILE"))

    from bionexo.application.webapp.app import MainApp
    main_app = MainApp()
    main_app.run()


if __name__ == "__main__":
    create_n_run_app()