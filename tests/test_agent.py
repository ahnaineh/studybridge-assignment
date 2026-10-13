"""Offline regression checks with real SDK objects and scripted model outputs."""
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from google.genai import types
import agent_core as core


def answer(text):
    return types.Content(role='model', parts=[types.Part.from_text(text=text)])


def action(name, args):
    return types.Content(role='model', parts=[types.Part(
        function_call=types.FunctionCall(name=name, args=args, id='test-call'),
        thought_signature=b'scripted-signature')])


class FakeClient:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.requests = []
        self.models = self

    def generate_content(self, **request):
        self.requests.append(request)
        result = next(self.replies)
        if isinstance(result, Exception):
            raise result
        return SimpleNamespace(candidates=[SimpleNamespace(content=result)])


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.previous = os.environ.get('STUDYBRIDGE_LOG_DIR')
        os.environ['STUDYBRIDGE_LOG_DIR'] = self.directory.name

    def tearDown(self):
        if self.previous is None:
            os.environ.pop('STUDYBRIDGE_LOG_DIR', None)
        else:
            os.environ['STUDYBRIDGE_LOG_DIR'] = self.previous
        self.directory.cleanup()

    def test_router_three_intents_and_followup(self):
        self.assertEqual(core.route_message('What subjects do you offer?'), 'general')
        self.assertEqual(core.route_message('I want to enroll'), 'lead')
        self.assertEqual(core.route_message('Feedback: confusing signup'), 'feedback')
        self.assertEqual(core.route_message('Alex', [{'role': 'assistant', 'content': 'What is your name?'}]), 'lead')

    def test_invalid_lead_is_not_persisted(self):
        result = core.record_customer_interest('invalid', 'Alex', 'Python')
        self.assertEqual(result['status'], 'error')
        self.assertFalse((Path(self.directory.name) / 'leads.jsonl').exists())

    def test_c3_feedback_call_returns_observation(self):
        client = FakeClient([action('record_feedback', {'question': 'Refund policy?'}), answer('The team must confirm.')])
        state = core.c3_reply('Refund policy?', client=client)
        self.assertEqual(state['turns'], 2)
        self.assertEqual(client.requests[1]['contents'][-1].role, 'user')
        self.assertEqual(client.requests[1]['contents'][-1].parts[0].function_response.response['status'], 'ok')

    def test_c4_native_action_and_signature_survive(self):
        client = FakeClient([action('record_customer_interest', {'email': 'alex@example.com',
                            'name': 'Alex', 'message': 'Python follow-up'}), answer('Interest recorded.')])
        result = core.c4_reply('Contact me about Python. Alex, alex@example.com.', client=client)
        self.assertEqual(result['answer'], 'Interest recorded.')
        self.assertEqual(result['trace'][1]['tool_names'], ['record_customer_interest'])
        self.assertEqual(client.requests[1]['contents'][-2].parts[0].thought_signature, b'scripted-signature')
        self.assertTrue(client.requests[0]['config'].automatic_function_calling.disable)

    def test_multi_tool_calls_all_receive_responses(self):
        content = types.Content(role='model', parts=[
            action('lookup_courses', {'query': 'Python'}).parts[0],
            action('record_feedback', {'question': 'Refund policy?'}).parts[0]])
        client = FakeClient([content, answer('Python Starter; refunds need confirmation.')])
        core.c4_reply('Which Python course? What is your refund policy?', client=client)
        self.assertEqual(len(client.requests[1]['contents'][-1].parts), 2)

    def test_loop_limit_does_not_return_draft(self):
        client = FakeClient([action('lookup_courses', {'query': 'Python'})] * core.MAX_MODEL_TURNS)
        result = core.c4_reply('Python options?', client=client)
        self.assertIn('tool limit', result['answer'])
        self.assertEqual(len(client.requests), core.MAX_MODEL_TURNS)

    def test_repeat_action_is_saved_once_per_turn(self):
        call = action('record_feedback', {'question': 'Refund policy?'})
        client = FakeClient([call, call, answer('Logged.')])
        core.c4_reply('Refund policy?', client=client)
        self.assertEqual(len((Path(self.directory.name) / 'feedback.jsonl').read_text().splitlines()), 1)

    def test_history_and_in_message_placement(self):
        client = FakeClient([answer('Please provide an email.')])
        core.c4_reply('I am Alex.', [{'role': 'user', 'content': 'Please contact me about Python.'}],
                      client=client, placement='message', examples=False, planning=True)
        self.assertIsNone(client.requests[0]['config'].system_instruction)
        self.assertIn('Please contact me about Python.', client.requests[0]['contents'][0].parts[0].text)
        self.assertNotIn('Worked example inside', client.requests[0]['contents'][-1].parts[0].text)

    def test_unknown_tool_becomes_error_observation(self):
        client = FakeClient([action('invented_tool', {}), answer('Unable to perform that action.')])
        result = core.c4_reply('Do something.', client=client)
        self.assertEqual(result['trace'][2]['observation']['status'], 'error')

    def test_transient_generation_retry_does_not_repeat_saved_tool(self):
        failure = RuntimeError('temporary generation failure')
        failure.code = 503
        client = FakeClient([action('record_feedback', {'question': 'Refund policy?'}),
                             failure, answer('Logged for confirmation.')])
        result = core.c4_reply('Refund policy?', client=client)
        self.assertEqual(len(client.requests), 3)
        self.assertEqual(len((Path(self.directory.name) / 'feedback.jsonl').read_text().splitlines()), 1)
        self.assertEqual(result['answer'], 'Logged for confirmation.')
        self.assertEqual(sum(e['event'] == 'api_retry' for e in result['trace']), 1)

    def test_example_email_cannot_be_used_for_missing_contact(self):
        for message in ('My name is Alex. I want Python tutoring.', 'Contact me: alex@example.com'):
            with self.subTest(message=message):
                client = FakeClient([action('record_customer_interest', {'email': 'alex@example.com',
                                    'name': 'Alex', 'message': 'Python'}), answer('Please provide the missing detail.')])
                result = core.c4_reply(message, client=client, placement='message')
                self.assertEqual(result['trace'][2]['observation']['status'], 'error')
                self.assertFalse((Path(self.directory.name) / 'leads.jsonl').exists())


if __name__ == '__main__':
    unittest.main()
