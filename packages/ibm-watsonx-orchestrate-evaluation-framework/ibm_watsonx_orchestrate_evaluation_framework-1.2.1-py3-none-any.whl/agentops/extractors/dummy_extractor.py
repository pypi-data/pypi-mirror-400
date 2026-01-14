from agentops.extractors.extractor_base import Extractor
from agentops.metrics.metrics import ExtractorData


class DummyExtractor(Extractor):
    """Example purpose only"""

    def __init__(self, config=None):
        super().__init__(config)

    def do_extract(
        self,
        messages,
        ground_truth,
        extracted_context={},
        **kwargs,
    ):

        return ExtractorData(
            field_name="dummy_extractor",
            value=1234,
        )
