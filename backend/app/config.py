import os

class Settings:
    PROJECT_NAME: str = "TexStyle CRM API"
    API_V1_STR: str = "/api/v1"
    
    # Security
    # JWT Secret Key - real sharoitda buni environment variable orqali o'rnatish lozim
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-texstyle-crm-1234567890-abcdef")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 soatlik sessiya
    
    # Database
    # Agar environmentda DATABASE_URL berilsa shuni oladi, aks holda local SQLite ishlatiladi
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./texstyle_crm.db"
    )

settings = Settings()
