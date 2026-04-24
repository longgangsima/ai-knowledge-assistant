from functools import lru_cache

# 导入 Pydantic settings 基类和配置规则对象，用来管理环境变量配置
from pydantic_settings import BaseSettings, SettingsConfigDict


# 把配置集中放这里，
# 不然后面 log_level、API key 这些会散在各个文件里，不好找也不好改。
# 定义项目的集中配置对象
class Settings(BaseSettings):
    # 表示当前应用运行环境
    app_env: str = "development"
    # 控制 logging 输出级别
    log_level: str = "INFO"
    # 为后续接入 OpenAI provider 预留 API key 配置
    openai_api_key: str | None = None

    # 定义读取配置时的规则，比如环境变量前缀和多余配置怎么处理。 
    model_config = SettingsConfigDict(env_prefix="AI_KA_", extra="ignore")


# 用 lru_cache 缓存 settings，避免重复创建同一份配置对象
@lru_cache
def get_settings() -> Settings:
    # 返回当前应用使用的 settings 实例
    return Settings()
