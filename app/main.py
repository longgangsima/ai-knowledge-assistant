from fastapi import FastAPI

# 导入 API routes，供主应用统一注册接口
from app.api.routes import router
# 导入配置读取函数，用来拿当前运行配置
from app.core.settings import get_settings
# 导入 logging 初始化函数，启动时配置日志级别
from app.observability.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    # 创建 FastAPI app
    app = FastAPI(
        title="AI Knowledge Assistant",
        version="0.1.0",
        description="Backend-first AI systems scaffold for ingestion, retrieval, and streaming.",
    )

    # 注册 routes
    app.include_router(router)
    return app


app = create_app()
