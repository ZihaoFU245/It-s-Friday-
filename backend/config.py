from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from typing import Union

class Config(BaseSettings):
    # Security
    security_key: Union[None, str] = Field(None, env="SECURITY_KEY")
    # Weather
    weather_api_key: Union[None, str] = Field(None, env="WEATHER_API_KEY")
    weather_url: str = Field("http://api.weatherapi.com/v1", env="WEATHER_URL")
    lang: str = Field("en", env="LANG")
    timeout: int = Field(10, env="TIMEOUT")
    temp_unit: str = Field("c", env="TEMP_UNIT")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding='utf-8'
    )

def update_keys(key: str, value: str):
    """
    change the api keys in the .env file
    """
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
        return

    with open(env_path, "r+", encoding="utf-8") as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[idx] = f"{key}={value}\n"
                f.seek(0)
                f.writelines(lines)
                f.truncate()
                return
        # Key not found, append to end, ensuring newline
        if lines and not lines[-1].endswith('\n'):
            f.write('\n')
        f.write(f"{key}={value}\n")

if __name__ == "__main__":
    config = Config()
    print(config.weather_api_key)
    print(config.test_key)
