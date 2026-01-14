from typing import Callable, List
from openai import OpenAI as OriginOpenAI
from specific_ai.openai.specific_ai_chat import SpecificAIChat
from specific_ai.common.lm_response_types import LMResponse

def default_parse_specific_ai_response(response: List[LMResponse]) -> str:
    return ';'.join(response[0].labels)


class OpenAI(OriginOpenAI):
    """SpecificAI enhanced OpenAI client.
    
    This client extends the original OpenAI client to add automatic request logging
    and model optimization capabilities.
    
    Args:
        specific_ai_url (str): The URL of the SpecificAI server
        api_key (str): our OpenAI API key
        use_specific_ai_inference (bool): Whether to use SpecificAI's optimized models
        parse_specific_ai_response (Callable[[List[LMResponse]], str]): Function to parse responses from a list of LMResponse types to the original response format
    """

    chat: SpecificAIChat
    
    def __init__(
        self,
        api_key: str,
        specific_ai_url: str,
        use_specific_ai_inference: bool = False,
        parse_specific_ai_response: Callable[[List[LMResponse]], str] = default_parse_specific_ai_response,
        **kwargs
    ):
        super().__init__(api_key=api_key, **kwargs)
        self._specific_ai_url = specific_ai_url
        self._use_specific_ai_inference = use_specific_ai_inference
        self._parse_specific_ai_response = parse_specific_ai_response
        
        # Initialize chat interface with SpecificAI enhancements
        self.chat = SpecificAIChat(client=self)
    
    def __del__(self):
        """Cleanup if needed."""
        try:
            self.chat.completions._shutdown()
        except Exception:
            pass
