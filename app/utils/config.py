from pydantic import BaseSettings


class Settings(BaseSettings):

    DATABASE_URI: str
    DEFAULT_PAGE_SIZE: int = 5
    DEFAULT_TENANT_ID: str = "default-tenant"


class DevelopmentConfig(Settings):
    class Config:
        env_file = "./config/dev.env"


configurations = DevelopmentConfig()


if __name__ == "__main__":
    print(configurations)
