"""Opt-in live Gemini experiments. Results are generated, never prefilled."""
import argparse
import csv
import json
import os
import time
from dataclasses import asdict
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from agent_core import PERSONAS, ROOT, c4_reply, make_client

CASES = [
    {'id': 'published_price', 'message': 'How much is an individual lesson and the four-lesson package?',
     'required': [], 'forbidden': ['record_customer_interest', 'record_feedback'],
     'check': 'USD 20 / 60 minutes; four individual lessons USD 72.'},
    {'id': 'recommendation', 'message': 'I am new to programming. Which course fits me?',
     'required': ['lookup_courses'], 'forbidden': ['record_customer_interest'],
     'check': 'Recommend Python Starter using catalog; no invented dates or promises.'},
    {'id': 'complete_lead', 'message': 'Please contact me about Python. My name is Alex and my email is alex@example.com.',
     'required': ['record_customer_interest'], 'forbidden': [],
     'check': 'Save exact Alex/alex@example.com; distinguish interest from booking.'},
    {'id': 'missing_email', 'message': 'My name is Alex. I want to enroll in Python tutoring.',
     'required': [], 'forbidden': ['record_customer_interest'],
     'check': 'Ask for email; do not invent contact data or save an incomplete lead.'},
    {'id': 'unknown_policy', 'message': 'Can I get a refund if I cancel a lesson?',
     'required': ['record_feedback'], 'forbidden': ['record_customer_interest'],
     'check': 'Refund policy is absent; log original question and defer to the team.'},
    {'id': 'explicit_feedback', 'message': 'Feedback: the enrollment process was confusing.',
     'required': ['record_feedback'], 'forbidden': ['record_customer_interest'],
     'check': 'Log feedback, acknowledge it, do not fabricate operational changes.'},
    {'id': 'memory', 'message': 'alex@example.com',
     'history': [{'role': 'user', 'content': 'I am Alex and want Python tutoring. Please contact me.'},
                 {'role': 'assistant', 'content': 'Thanks, Alex. What is your email address?'}],
     'required': ['record_customer_interest'], 'forbidden': [],
     'check': 'Use Alex and Python from history and email from current message.'},
]


def setups():
    for name, persona in PERSONAS.items():
        # Each variant changes one prompt factor relative to the baseline.
        for variant, examples, planning, placement in [
            ('baseline', True, False, 'system'),
            ('zero_shot', False, False, 'system'),
            ('planning_cue', True, True, 'system'),
            ('in_message', True, False, 'message')]:
            yield {'id': name + ' / ' + variant, 'persona': name,
                   'persona_config': persona, 'examples': examples,
                   'planning': planning, 'placement': placement, 'instructions_enabled': True}
        yield {'id': name + ' / instructions_ablation', 'persona': name,
               'persona_config': persona, 'examples': False, 'planning': False,
               'placement': 'system', 'instructions_enabled': False,
               'case_ids': ['missing_email', 'unknown_policy']}
        yield {'id': name + ' / two_example_few_shot', 'persona': name,
               'persona_config': persona, 'examples': True, 'planning': False,
               'placement': 'system', 'instructions_enabled': True, 'fewshot_extra': True,
               'case_ids': ['complete_lead', 'unknown_policy']}
        yield {'id': name + ' / stepwise_reasoning', 'persona': name,
               'persona_config': persona, 'examples': True, 'planning': True,
               'placement': 'system', 'instructions_enabled': True, 'stepwise_reasoning': True,
               'case_ids': ['recommendation', 'unknown_policy']}


def balanced_setups():
    """Matched prompt comparisons on three cases, plus baseline functional coverage.

    Both personas use the same recommendation, missing-email and unknown-policy
    cases in every condition. The baseline additionally runs the other four cases.
    One temperature-only control holds the specialist prompt/top-p/top-k fixed.
    """
    common = ['recommendation', 'missing_email', 'unknown_policy']
    for setup in setups():
        variant = setup['id'].split(' / ')[1]
        if variant == 'planning_cue':
            continue  # Explicit stepwise condition covers the reasoning comparison.
        setup = dict(setup)
        if variant == 'baseline':
            setup.pop('case_ids', None)
        else:
            setup['case_ids'] = common
        yield setup
    specialist = PERSONAS['Course Specialist']
    yield {'id': 'Course Specialist / temperature_only_0.7',
           'persona': 'Course Specialist',
           'persona_config': replace(specialist, temperature=0.7),
           'examples': True, 'planning': False, 'placement': 'system',
           'instructions_enabled': True, 'case_ids': common}


def run_experiments(repeats=1, smoke=False, setup_ids=None, case_pairs=None, balanced=False):
    client = make_client()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run_dir = ROOT / 'results' / stamp
    run_dir.mkdir(parents=True)
    old_logs = os.environ.get('STUDYBRIDGE_LOG_DIR')
    os.environ['STUDYBRIDGE_LOG_DIR'] = str(run_dir / 'synthetic_logs')
    fields = ['setup', 'case', 'repeat', 'model_requested', 'model_versions', 'temperature', 'top_p', 'top_k',
              'max_output_tokens', 'examples', 'planning', 'placement', 'latency_seconds', 'api_latency_seconds',
              'instructions_enabled', 'example_count', 'stepwise_reasoning', 'model_turns', 'api_retries',
              'successful_tools', 'tool_check', 'answer', 'error', 'error_detail',
              'grounded_0_2', 'helpful_0_2', 'natural_0_2', 'instruction_following_0_2', 'notes']
    selected_setups = list(balanced_setups()) if balanced else list(setups())
    if smoke:
        selected_setups = selected_setups[:1]
    if setup_ids is not None:
        selected_setups = [s for s in selected_setups if s['id'] in setup_ids]
    selected_cases = CASES[:2] if smoke else CASES
    (run_dir / 'cases.json').write_text(json.dumps(CASES, indent=2), encoding='utf-8')
    (run_dir / 'configurations.json').write_text(json.dumps([
        {**s, 'persona_config': asdict(s['persona_config'])} for s in selected_setups], indent=2), encoding='utf-8')
    try:
        with (run_dir / 'comparison.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for setup in selected_setups:
                for repeat in range(1, repeats + 1):
                    for case in selected_cases:
                        if setup.get('case_ids') and case['id'] not in setup['case_ids']:
                            continue
                        if case_pairs is not None and (setup['id'], case['id']) not in case_pairs:
                            continue
                        start = time.perf_counter()
                        result = None
                        row = dict.fromkeys(fields, '')
                        config = setup['persona_config']
                        row.update(setup=setup['id'], case=case['id'], repeat=repeat,
                                   model_requested=os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite'),
                                   temperature=config.temperature, top_p=config.top_p,
                                   top_k=config.top_k, max_output_tokens=config.max_output_tokens,
                                   examples=setup['examples'], planning=setup['planning'], placement=setup['placement'],
                                   instructions_enabled=setup['instructions_enabled'])
                        row['example_count'] = (2 if setup.get('fewshot_extra') else 1) if setup['examples'] else 0
                        row['stepwise_reasoning'] = setup.get('stepwise_reasoning', False)
                        try:
                            result = c4_reply(case['message'], case.get('history'), client=client,
                                              **{k: v for k, v in setup.items() if k not in ('id', 'case_ids')})
                            events = [e for e in result['trace'] if e['event'] == 'action_observation']
                            names = [e['name'] for e in events if e['observation'].get('status') == 'ok']
                            passes = (all(n in names for n in case['required']) and
                                      not any(n in [e['name'] for e in events] for n in case['forbidden']))
                            row.update(answer=result['answer'], model_turns=result['turns'],
                                       api_retries=sum(e['event'] == 'api_retry' for e in result['trace']),
                                       successful_tools=json.dumps(names), tool_check=int(passes),
                                       api_latency_seconds=round(sum(e.get('api_latency_seconds', 0)
                                           for e in result['trace']), 3),
                                       model_versions=json.dumps(sorted({e['model_version'] for e in result['trace']
                                           if e.get('model_version')})))
                        except Exception as error:
                            # Errors stay visible in the results rather than becoming fake scores.
                            row.update(error=f'{type(error).__name__}: {getattr(error, "code", "")}', tool_check=0,
                                       error_detail=str(error).replace(os.getenv('GEMINI_API_KEY', 'UNSET_KEY'), '[REDACTED]'))
                        row['latency_seconds'] = round(time.perf_counter() - start, 3)
                        writer.writerow(row)
                        stream.flush()
                        with (run_dir / 'case_results.jsonl').open('a', encoding='utf-8') as evidence:
                            evidence.write(json.dumps({'setup': setup['id'], 'case': case['id'],
                                'message': case['message'], 'history': case.get('history', []),
                                'row': row, 'trace': result['trace'] if result else []}, ensure_ascii=False) + '\n')
                        print(setup['id'], case['id'], 'tool_check=', row['tool_check'])
                        time.sleep(1)  # Basic pacing; adjust for your account quota.
    finally:
        if old_logs is None:
            os.environ.pop('STUDYBRIDGE_LOG_DIR', None)
        else:
            os.environ['STUDYBRIDGE_LOG_DIR'] = old_logs
    print('Results:', run_dir)
    return run_dir


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repeats', type=int, default=1)
    parser.add_argument('--smoke', action='store_true', help='Only baseline + two cases.')
    parser.add_argument('--balanced', action='store_true', help='Matched final-code study (47 conversations).')
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error('--repeats must be positive')
    run_experiments(args.repeats, args.smoke, balanced=args.balanced)
