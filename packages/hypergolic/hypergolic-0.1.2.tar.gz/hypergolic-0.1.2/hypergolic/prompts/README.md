# System Prompts

This directory contains system prompts used by the AI coding assistant.

## Files

- **system_prompt.txt**: The main system prompt that defines the AI assistant's behavior, capabilities, and guidelines.

## Usage

The system prompt is automatically loaded by `llm/api.py` when making API calls to the language model. It sets the context and behavior for how the assistant should respond to user requests.

## Modifying the System Prompt

To modify the assistant's behavior:

1. Edit `system_prompt.txt` with your desired changes
2. The changes will take effect immediately on the next API call
3. No code changes are needed - the prompt is loaded dynamically

## Structure

The system prompt includes:
- **Core Capabilities**: Description of available tools
- **Guidelines**: Behavioral principles for the assistant
- **Best Practices**: Specific recommendations for effective assistance

Keep the prompt clear, focused, and actionable to ensure the best assistant behavior.
