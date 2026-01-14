import json
import sys



def _read_payload() -> tuple[str, dict]:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    return payload.get('task', ''), payload.get('context', {})

if __name__ == '__main__':
    task, context = _read_payload()
    result = solve(task, context)
    try:
        print(json.dumps(result))
    except TypeError:
        print(str(result))
