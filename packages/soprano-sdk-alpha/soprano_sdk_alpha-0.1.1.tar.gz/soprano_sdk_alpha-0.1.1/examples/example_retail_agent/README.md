# Retail Return Agent Example

This example demonstrates a complete return processing workflow using the Soprano SDK.

## Features

1. **Structured Output Extraction**: When users say "I want to return order #12345 because it's damaged", the processor automatically extracts:
   - `order_id`: 12345
   - `return_reason`: damaged

2. **Interactive Workflow**: The workflow guides users through:
   - Order ID collection (if not provided)
   - Eligibility check
   - Return reason collection (if not provided)
   - Reason validation
   - Return processing

3. **Interrupt Handling**: The processor manages workflow interrupts, allowing multi-turn conversations.

## Running the Example

```bash
cd examples/example_retail_agent
python ui.py
```

Then open http://localhost:7860 in your browser.

## File Structure

| File | Description |
|------|-------------|
| `return_workflow.yaml` | Workflow definition with steps and transitions |
| `return_functions.py` | Mock business logic (eligibility, validation, processing) |
| `processor.py` | Main processor with LLM context extraction |
| `ui.py` | Gradio chat interface |

## Testing Different Scenarios

| User Message | Expected Behavior |
|-------------|-------------------|
| "I want to return" | Asks for order ID |
| "Return order #12345" | Extracts order_id, asks for reason |
| "Return #12345, it's damaged" | Extracts both, processes if eligible |
| "Return order #12340" | Ineligible (ends in 0) |
| "Return #123, just because" | Invalid reason (blocked phrase) |

## Architecture

```
User Message
    │
    ▼
┌─────────────────────────────────┐
│ Structured Output Extraction    │
│ (LLM extracts order_id, reason) │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ WorkflowTool.execute()          │
│ (pass initial_context)          │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Workflow Steps                  │
│ - Skip pre-filled steps         │
│ - Collect missing info          │
│ - Run business logic            │
└─────────────────────────────────┘
    │
    ▼
Response (prompt or outcome)
```

## Workflow Steps

1. **collect_order_id** - Agent collects order ID from user
2. **check_eligibility** - Function checks if order can be returned
3. **collect_reason** - Agent collects return reason
4. **check_validity** - Function validates the reason
5. **process_return** - Function processes the return request

## Mock Logic

- **Eligibility**: Orders ending in `0` are ineligible (for testing)
- **Reason Validation**: Phrases like "just because", "no reason" are rejected
- **Processing**: Always succeeds if previous steps pass

## Customization

To use real business logic, replace the functions in `return_functions.py`:

```python
def check_eligibility(state: dict) -> bool:
    order_id = state.get('order_id')
    # Query your database
    order = db.get_order(order_id)
    return order.is_returnable()
```
