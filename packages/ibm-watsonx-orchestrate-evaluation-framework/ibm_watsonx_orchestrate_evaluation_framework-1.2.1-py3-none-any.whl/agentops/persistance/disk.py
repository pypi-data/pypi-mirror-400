from agentops.evaluation_package import EvaluationResult
from agentops.persistance.persistance_base import PersistanceBase


class DiskPersistance(PersistanceBase):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)

    def persist(self, evaluation_results: EvaluationResult):
        pass

    def clean(self):
        pass
