import os
from datetime import timedelta

db_username = os.getenv("MONGO_INITDB_ROOT_USERNAME", None)
db_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD", None)
db_name = os.getenv("MONGO_INITDB_DATABASE", None)
db_host = os.getenv("DB_HOST", "localhost")
db_port = int(os.getenv("DB_PORT", 27017))
db_collection = "secrets_collection"

fernet_key = os.getenv("FERNET_KEY", None)

secret_ttl = int(
    timedelta(weeks=1, days=0, hours=0, minutes=0).total_seconds()
)
