from typing import List, Any
from interfaces.i_pipeline_step import IPipelineStep

class Pipeline:
    def __init__(self, steps: List[IPipelineStep]):
        self.steps = steps

    def execute(self, initial_data: Any) -> Any:
        data = initial_data
        for step in self.steps:
            data = step.process(data)
        return data