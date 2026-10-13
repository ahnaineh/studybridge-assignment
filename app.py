"""Run python app.py after setting GEMINI_API_KEY. C3 and C4 in one interface."""
import gradio as gr
from agent_core import c3_reply, c4_reply, PERSONAS


def respond(message, history, assignment, persona, reflection):
    try:
        result = (c3_reply(message, history, persona, reflection=reflection)
                  if assignment == 'C3' else c4_reply(message, history, persona))
        return result['answer']
    except Exception as error:
        # Do not expose keys or provider exception payloads in a public interface.
        print(f'[APP ERROR] {type(error).__name__}')
        if getattr(error, 'code', None) == 429:
            return ('The assistant has reached its current request limit. Please try again later. '
                    'An earlier action may already have been recorded.')
        return ('I could not complete this request right now. Please try again in a moment. '
                'An earlier action may already have been recorded.')


def create_demo():
    with gr.Blocks(title='StudyBridge | Agentic Systems') as demo:
        gr.Markdown('# StudyBridge\nA fictional tutoring assistant for C3 and C4. '
                    'Use fake contact details in demos. Interest logging does not book a lesson.')
        with gr.Row():
            assignment = gr.Dropdown(['C3', 'C4'], value='C3', label='Assignment')
            persona = gr.Dropdown(list(PERSONAS), value='Friendly Advisor', label='Persona')
            reflection = gr.Checkbox(value=False, label='C3 reflection bonus (extra API call)')
        gr.ChatInterface(respond, additional_inputs=[assignment, persona, reflection],
                         examples=[['What subjects do you offer?', 'C3', 'Friendly Advisor', False],
                                   ['What is your refund policy?', 'C3', 'Friendly Advisor', False],
                                   ['Contact me about Python. I am Alex, alex@example.com.',
                                    'C4', 'Course Specialist', False]])
    return demo


if __name__ == '__main__':
    create_demo().launch()
