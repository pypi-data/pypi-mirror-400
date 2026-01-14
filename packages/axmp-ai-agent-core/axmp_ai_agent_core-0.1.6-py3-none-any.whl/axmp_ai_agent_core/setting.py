"""Base settings for AI Agent Studio."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class AIServiceKeySettings(BaseSettings):
    """Settings for AIServiceKey."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", extra="ignore"
    )
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None


ai_service_key_settings = AIServiceKeySettings()


class CoreSettings(BaseSettings):
    """Settings for AI Agent Core."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="CORE_", env_file=".env", extra="ignore"
    )

    domain: str = "0.0.0.0"
    api_endpoint: str
    web_endpoint: str
    default_model: str = "openai/gpt-4.1-mini"
    default_model_max_tokens: int = 5000
    recursion_limit: int = 30
    stream_mode: Literal["messages", "values", "updates"] = "messages"
    temperature: float = 0
    csrf_safe_methods: str = "GET;HEAD;OPTIONS;TRACE;POST;PUT;DELETE;PATCH"
    python_path: str = "/application/.venv/bin/python"
    mcp_connection_timeout: float = 30.0
    image_max_size_mb: int = 3
    pdf_max_size_mb: int = 10
    image_path: str = "/application/public/images"
    default_image_path: str = "/application/public/default-images"
    image_server_endpoint: str = "http://0.0.0.0:7700/images"
    agent_icon_path: str = "/agent/agent.png"
    mcp_server_icon_path: str = "/mcp-server/mcp.png"
    axmp_provision_target_label: str = "platform.axmp/target=instance"
    mcp_server_separator: str = "---"
    agent_cache_ttl: int = 3600
    agent_cache_max_size: int = 100
    agent_cache_cleanup_interval: int = 60


core_settings = CoreSettings()


class MongoDBSettings(BaseSettings):
    """Settings for MongoDB."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="MONGODB_", env_file=".env", extra="ignore"
    )

    hostname: str
    port: int
    username: str
    password: str
    database: str
    connection_timeout_ms: int = 5000

    # Collection names
    collection_llm_model: str = "llm_model"
    collection_kubernetes_config: str = "kubernetes_config"
    collection_backend_server: str = "backend_server"
    collection_mcp_server_profile: str = "mcp_server_profile"
    collection_agent_profile: str = "agent_profile"
    collection_agent_catalog: str = "agent_catalog"
    collection_mcp_server_profile_history: str = "mcp_server_profile_history"
    collection_mcp_server: str = "mcp_server"
    collection_internal_server_history: str = "internal_server_history"
    collection_mcp_registry: str = "mcp_registry"
    collection_chat_file: str = "chat_file"
    collection_llm_provider: str = "llm_provider"
    collection_agent_trigger: str = "agent_trigger"
    collection_user_credential: str = "user_credential"
    collection_chat_memory: str = "chat_memory"
    collection_idp_provider: str = "idp_provider"
    collection_agent_profile_history: str = "agent_profile_history"
    collection_group: str = "groups"
    collection_user: str = "oauth_user"
    collection_role: str = "roles"
    collection_conversation: str = "chat_conversation"

    @property
    def uri(self) -> str:
        """Get MongoDB connection URI."""
        return f"mongodb://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}"


mongodb_settings = MongoDBSettings()


class S3Settings(BaseSettings):
    """Settings for AWS S3."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="AWS_", env_file=".env", extra="ignore"
    )
    access_key_id: str
    secret_access_key: str
    default_region: str
    s3_bucket_name: str
    s3_bucket_root: str


s3_settings = S3Settings()


class PostgreSQLSettings(BaseSettings):
    """Settings for PostgreSQL."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="POSTGRESQL_", env_file=".env", extra="ignore"
    )

    hostname: str
    port: int
    username: str
    password: str
    database: str
    # Connection timeout settings
    connect_timeout: int = 10
    # TCP keepalive settings
    tcp_keepalives_idle: int = 600  # 10 minutes
    tcp_keepalives_interval: int = 30  # 30 seconds
    tcp_keepalives_count: int = 3
    # SSL settings
    sslmode: str = "prefer"
    # Application name for connection identification
    application_name: str = "axmp-ai-agent-core"

    @property
    def db_uri(self) -> str:
        """Return the connection string for the PostgreSQL database."""
        return f"postgresql://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}"

    @property
    def db_uri_with_params(self) -> str:
        """Return the connection string with additional parameters for connection stability."""
        params = [
            f"connect_timeout={self.connect_timeout}",
            f"sslmode={self.sslmode}",
            f"application_name={self.application_name}",
            f"keepalives_idle={self.tcp_keepalives_idle}",
            f"keepalives_interval={self.tcp_keepalives_interval}",
            f"keepalives_count={self.tcp_keepalives_count}",
        ]

        param_string = "&".join(params)
        return f"{self.db_uri}?{param_string}"


postgresql_settings = PostgreSQLSettings()
