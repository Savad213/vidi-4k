import json, os

brain = r'C:\Users\SM.DESKTOP-P1R0508.000\.gemini\antigravity-cli\brain'
cid = '90a8fc0b-828a-4a2e-8620-1f849840ce43'
p = os.path.join(brain, cid, '.system_generated', 'logs', 'transcript.jsonl')

with open(p, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if line.strip():
            obj = json.loads(line)
            if obj.get('type') == 'USER_INPUT':
                print(f"[{idx}] USER: {obj.get('content')}")
            elif obj.get('type') == 'PLANNER_RESPONSE' and obj.get('content'):
                print(f"[{idx}] ASSISTANT: {obj.get('content')[:300]}")
