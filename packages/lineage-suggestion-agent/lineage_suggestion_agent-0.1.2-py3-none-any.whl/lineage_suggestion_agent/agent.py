from sfn_blueprint import SFNAIHandler
from .config import LineageConfig
from .models import LineageSuggestion
from .constants import format_prompt
from typing import Any, Dict, Tuple, Optional
import logging

class LineageSuggestionAgent:
    def __init__(self, config: LineageConfig | None = None):
        self.config = config or LineageConfig()
        self.ai_handler = SFNAIHandler()
        self.logger = logging.getLogger(__name__)

    def execute_task(self, task: Dict[str, Any]) -> Tuple[LineageSuggestion, Dict[str, Any]]:
        context = task["context"]
        system_prompt, user_prompt = format_prompt(context)
        response, cost = self.llm_call(system_prompt, user_prompt)
        return response, cost

    def __call__(self, *args, **kwds):
        return self.execute_task(*args, **kwds)
    

    def llm_call(self, system_prompt, user_prompt):

        response, cost = self.ai_handler.route_to(
            llm_provider=self.config.lineage_ai_provider,
            configuration={
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": self.config.lineage_temperature,
                "max_tokens": self.config.lineage_max_tokens,
                "text_format": LineageSuggestion
            },
            model=self.config.lineage_model,
        )

        return response, cost
