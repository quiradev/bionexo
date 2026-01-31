
def create_n_run_app():
    from bionexo.application.webapp.app import MainApp
    main_app = MainApp()
    main_app.run()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv(os.getenv("ENV_FILE"))
    create_n_run_app()