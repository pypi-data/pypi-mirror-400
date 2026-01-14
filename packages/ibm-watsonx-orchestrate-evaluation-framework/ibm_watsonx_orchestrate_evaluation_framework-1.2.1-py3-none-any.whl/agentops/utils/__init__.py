import json
import os
import tempfile
from pathlib import Path

from agentops.utils.langfuse_utils import sync as sync_langfuse_dataset
from agentops.utils.open_ai_tool_extractor import ToolExtractionOpenAIFormat
from agentops.utils.parsers import ReferencelessEvalParser
from agentops.utils.utils import (
    N_A,
    TestCaseResources,
    add_line_seperator,
    list_run_files,
    load_run_metrics,
)


def json_dump(output_path, obj):
    """
    Atomically dump JSON to `output_path`.

    - Writes to a temporary file first
    - Then atomically replaces the target file
    - Prevents corrupted/half-written JSON if process is interrupted
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        dir=output_path.parent,
        prefix=output_path.stem,
        suffix=".tmp",
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, output_path)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise
