"""Repeat both reflection examples with a private GEMINI_API_KEY (three live calls minimum)."""
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import agent_core
from google.genai import types

QUESTION = ('I am a complete beginner in Python. Compare paying for four individual lessons '
            'with the four-lesson package, tell me the savings, and suggest a sensible first '
            'step. Keep it brief; I am not ready to book.')
CONTROLLED_QUESTION = ('What do four individual lessons cost compared with the four-lesson '
                       'package, how much do I save, and what is your refund policy?')
SEEDED_DRAFT = ('Four individual lessons cost USD 100. The four-lesson package costs USD 72, '
                'saving USD 28. All purchases include a guaranteed full refund.')


def main():
    # New directory on every run preserves the submitted evidence.
    target = ROOT / 'logs' / ('reflection-repeat-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    target.mkdir(parents=True)
    os.environ['STUDYBRIDGE_LOG_DIR'] = str(target)
    os.environ.setdefault('STUDYBRIDGE_MIN_REQUEST_INTERVAL', '13')
    real_client = agent_core.make_client()

    class SeededFirstDraft:
        def __init__(self):
            self.calls = 0

        def generate_content(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                return types.GenerateContentResponse(
                    candidates=[types.Candidate(content=types.Content(
                        role='model', parts=[types.Part(text=SEEDED_DRAFT)]))],
                    model_version='controlled-seeded-draft-not-a-model-generation')
            return real_client.models.generate_content(**kwargs)

    for name, question, client in [
        ('live-example', QUESTION, real_client),
        ('controlled-correction', CONTROLLED_QUESTION, SimpleNamespace(models=SeededFirstDraft())),
    ]:
        started = datetime.now(timezone.utc).isoformat()
        result = agent_core.c3_reply(question, reflection=True, client=client)
        record = json.loads((target / 'reflection.jsonl').read_text().splitlines()[-1])
        payload = {
            'started_utc': started, 'completed_utc': datetime.now(timezone.utc).isoformat(),
            'model': result['model'], 'persona': result['persona'].name,
            'python_version': platform.python_version(),
            'core_sha256': hashlib.sha256((ROOT / 'agent_core.py').read_bytes()).hexdigest(),
            'test_type': 'Natural live draft and live review' if name == 'live-example' else
                'Controlled seeded draft and live review; not a naturally observed model failure',
            'question': question, **record, 'trace': result['trace'], 'reflection_enabled': True,
        }
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        assert os.environ['GEMINI_API_KEY'] not in text
        (target / (name + '.json')).write_text(text, encoding='utf-8')
        print(name, '\nDRAFT:', record['draft'], '\nREVISED:', record['revised_reply'])
    print('Saved repeat evidence:', target)


if __name__ == '__main__':
    main()
