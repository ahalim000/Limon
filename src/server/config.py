import os


class Config:
    def __init__(self):
        self.algorithm: str = os.environ.get("RECIPE_ALGORITHM", "HS256")
        self.secret_key: str = os.environ["RECIPE_SECRET_KEY"]
        self.database_url: str = os.environ["RECIPE_DATABASE_URL"]
        self.access_token_expire_minutes: int = int(
            os.environ.get("RECIPE_ACCESS_TOKEN_EXPIRE_MINUTES", "300")
        )
        self.bootstrap_admin_password: str = os.environ[
            "RECIPE_BOOTSTRAP_ADMIN_PASSWORD"
        ]


CONFIG = Config()
