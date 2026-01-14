import json
import sys
from skills.registry import get_registry

def read_payload(path=None):
    if path:
        data = open(path, 'r', encoding='utf-8').read()
    else:
        data = sys.stdin.read()
    if not data.strip():
        raise ValueError('empty input')
    return json.loads(data)

def emit(phase, payload):
    print(json.dumps({**{'phase': phase}, **payload}, ensure_ascii=True))

def main():
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    input_path = None
    if '--input' in args:
        idx = args.index('--input')
        if idx + 1 < len(args):
            input_path = args[idx + 1]
    payload = read_payload(input_path)
    emit('PLAN', {'steps': ['execute skill', 'verify output', 'commit result']})
    if dry_run:
        emit('STATUS', {'status': 'FAILURE', 'reason': 'dry_run_no_change'})
        return 2
    registry = get_registry()
    result = registry.execute_skill('dialogue/answering-core', payload, context=None)
    emit('EXECUTE', {'skill_id': 'dialogue/answering-core', 'success': result.success})
    emit('VERIFY', {'success': bool(result.success)})
    emit('COMMIT', {'record': {'skill_id': 'dialogue/answering-core', 'success': result.success}})
    if result.success:
        emit('STATUS', {'status': 'SUCCESS'})
        return 0
    emit('STATUS', {'status': 'FAILURE', 'reason': result.error or 'skill_failed'})
    return 3

if __name__ == '__main__':
    raise SystemExit(main())
