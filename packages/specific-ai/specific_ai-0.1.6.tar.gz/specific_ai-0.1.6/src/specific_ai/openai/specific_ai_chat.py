from openai.resources.chat import Chat
from specific_ai.openai.specific_ai_completions import SpecificAICompletions


class SpecificAIChat(Chat):
    """Enhanced chat interface with SpecificAI capabilities."""

    completions: SpecificAICompletions

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completions = SpecificAICompletions(client=self._client)
