"""
Gradio Chat Interface for Retail Agent

Multi-workflow retail agent with automatic intent detection.
Supports: returns, order status, and profile inquiries.
"""

import os
import sys
import uuid

import gradio as gr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processor import RetailAgentProcessor

processor = RetailAgentProcessor()


def respond(message: str, history: list, thread_state: str):
    """Process user message through the retail agent."""
    if thread_state is None:
        thread_state = f"retail_{uuid.uuid4().hex[:8]}"

    try:
        response = processor.process_message(
            thread_id=thread_state,
            user_message=message,
            history=history  # Pass history for intent detection
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        response = f"Error: {str(e)}"

    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": response}
    ]

    # Check if async pending to show/hide buttons
    is_pending = processor.is_async_pending(thread_state)

    return "", history, thread_state, gr.update(visible=is_pending), gr.update(visible=is_pending)


def approve_validation(history: list, thread_state: str):
    """Simulate async validation completing with approval."""
    if thread_state and processor.is_async_pending(thread_state):
        response = processor.complete_async(thread_state, True)
        history = history + [
            {"role": "assistant", "content": "Validation approved."},
            {"role": "assistant", "content": response}
        ]
    return history, gr.update(visible=False), gr.update(visible=False)


def reject_validation(history: list, thread_state: str):
    """Simulate async validation completing with rejection."""
    if thread_state and processor.is_async_pending(thread_state):
        response = processor.complete_async(thread_state, False)
        history = history + [
            {"role": "assistant", "content": "Validation rejected."},
            {"role": "assistant", "content": response}
        ]
    return history, gr.update(visible=False), gr.update(visible=False)


def new_conversation(history: list, thread_state: str):
    """Start a new conversation."""
    if thread_state:
        processor.reset_workflow(thread_state)
    return [], None, gr.update(visible=False), gr.update(visible=False)


with gr.Blocks(title="Retail Agent") as demo:
    gr.Markdown("""
    # Retail Agent
    I can help you with:
    - **Returns & Refunds** - Process returns for your orders
    - **Order Status** - Check tracking and delivery info
    - **Profile** - View your account and loyalty info
    """)

    thread_state = gr.State(None)
    chatbot = gr.Chatbot(type="messages", height=450)

    with gr.Row():
        msg = gr.Textbox(
            placeholder="How can I help you today?",
            show_label=False,
            scale=4
        )

    # Async callback simulation buttons (hidden by default)
    with gr.Row():
        approve_btn = gr.Button("Approve Validation", variant="primary", visible=False)
        reject_btn = gr.Button("Reject Validation", variant="stop", visible=False)

    with gr.Row():
        new_btn = gr.Button("New Conversation", variant="secondary")

    msg.submit(
        respond,
        [msg, chatbot, thread_state],
        [msg, chatbot, thread_state, approve_btn, reject_btn]
    )

    approve_btn.click(
        approve_validation,
        [chatbot, thread_state],
        [chatbot, approve_btn, reject_btn]
    )

    reject_btn.click(
        reject_validation,
        [chatbot, thread_state],
        [chatbot, approve_btn, reject_btn]
    )

    new_btn.click(
        new_conversation,
        [chatbot, thread_state],
        [chatbot, thread_state, approve_btn, reject_btn]
    )


if __name__ == "__main__":
    demo.launch()
