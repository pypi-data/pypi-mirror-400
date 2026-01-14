import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    handlers: Optional[list] = None,
) -> None:
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    if handlers is None:
        handlers = [logging.StreamHandler(sys.stdout)]
    
    logging.basicConfig(
        level=log_level,
        format=format_string,
        handlers=handlers,
    )


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    return logger


class StructuredLogger:
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = get_logger(name, level)
    
    def log_episode(self, episode_id: str, action: str, success: bool, **kwargs) -> None:
        self.logger.info(
            f"Episode {episode_id}: action={action}, success={success}, extras={kwargs}"
        )
    
    def log_workflow(self, workflow_id: str, status: str, **kwargs) -> None:
        self.logger.info(
            f"Workflow {workflow_id}: status={status}, extras={kwargs}"
        )
    
    def log_evaluation(self, workflow_id: str, reward: float, success: bool, **kwargs) -> None:
        self.logger.info(
            f"Evaluation {workflow_id}: reward={reward:.3f}, success={success}, extras={kwargs}"
        )
    
    def log_insight(self, insight_id: str, insight_type: str, confidence: float, **kwargs) -> None:
        self.logger.info(
            f"Insight {insight_id}: type={insight_type}, confidence={confidence:.3f}, extras={kwargs}"
        )
