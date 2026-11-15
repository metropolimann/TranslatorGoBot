# src/pdfbot/config.py
from pathlib import Path
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from platformdirs import user_data_dir

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # 1. Paths
    data_dir: Optional[Path] = None
    log_dir: Optional[Path] = None

    # 2. PDF splitting
    pack_size: int = 25

    # 3. Browser & translation
    brave_path: Optional[Path] = None
    browser_profile_dir: Optional[Path] = None
    headless: bool = False
    browser_timeout: int = 30
    translator_backend: Literal["browser", "deep", "cloud"] = "browser"
    default_src_lang: str = "en"
    default_tgt_lang: str = "fr"
    translate_delay_seconds: float = 5.0
    translate_chunk_chars: int = 4500

    # 4. Databases
    sqlite_url: Optional[str] = None
    postgres_dsn: Optional[str] = None

    # 5. Sync worker
    sync_interval_seconds: int = 60
    sync_max_backoff_seconds: int = 300

    # 6. Logging
    log_level: str = "INFO"
    log_rotate_bytes: int = 10 * 1024 * 1024
    log_backup_count: int = 5

    # 7. Operator
    operator_name: Optional[str] = None

    # 8. Google Cloud
    google_api_key: Optional[str] = None
    google_cloud_project: Optional[str] = None

    def model_post_init(self, __context) -> None:
        """Resolve dynamic paths after loading from .env."""
        if self.data_dir is None:
            self.data_dir = Path(user_data_dir("pdfbot"))
            
        if self.log_dir is None:
            self.log_dir = self.data_dir / "logs"
            
        if self.browser_profile_dir is None:
            self.browser_profile_dir = self.data_dir / "browser_profile"
            
        if self.sqlite_url is None:
            self.sqlite_url = f"sqlite:///{self.data_dir}/history.db"

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

# Global instance for the app to import
settings = Settings()