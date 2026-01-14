import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.response_state_visualizer import ResponseStateVisualizer

viz = ResponseStateVisualizer()
if not viz.enabled(verbose=True):
    print("Set GPIA_RESPONSE_PREVIEW=1 to enable preview output")
else:
    viz.emit("Intent", "explain | general | low")
    viz.emit_list("Keywords", ["preview", "response", "state"])
    viz.emit_list("Skills", ["answering-core", "dynamic-budget-orchestrator"])
    viz.emit("Draft", "Answer: This is a short draft preview.")
    viz.emit("Final", "Ready (see output below)")
