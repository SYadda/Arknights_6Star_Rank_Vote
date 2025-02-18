from litestar.plugins.problem_details import ProblemDetailsPlugin
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin
from litestar.plugins.structlog import StructlogPlugin
from litestar_granian import GranianPlugin
from litestar_saq import SAQPlugin

from app.config import app as app_config
from app.db.model import sqlalchemy_config

structlog = StructlogPlugin(config=app_config.log)
saq = SAQPlugin(config=app_config.saq)
granian = GranianPlugin()
problem_details = ProblemDetailsPlugin(config=app_config.problem_details)
sqlalchemy_plugin = SQLAlchemyPlugin(config=sqlalchemy_config)
