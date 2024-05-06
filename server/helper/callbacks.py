import json
from langchain_core.callbacks.base import BaseCallbackHandler

class MyCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self.total_tokens_used = 0
        self.completion_tokens_used = 0
        self.prompt_tokens_used = 0
        self.last_llm_token_feedback = {}
        self.llm_invoke_count = 0
        self.load_counts()

    def load_counts(self):
        try:
            with open('callback_counts.json', 'r') as file:
                data = json.load(file)
                self.llm_invoke_count = data.get('llm_invoke_count', 0)
                self.total_tokens_used = data.get('total_tokens_used', 0)
                self.completion_tokens_used = data.get('completion_tokens_used', 0)
                self.prompt_tokens_used = data.get('prompt_tokens_used', 0)
                self.last_llm_token_feedback = data.get('last_llm_token_feedback', {})
                # Load other counts as needed
        except FileNotFoundError:
            self.total_tokens_used = 0
            self.completion_tokens_used = 0
            self.prompt_tokens_used = 0
            self.last_llm_token_feedback = {}
            self.llm_invoke_count = 0

    def save_counts(self):
        data = {
            'llm_invoke_count': self.llm_invoke_count,
            'total_tokens_used': self.total_tokens_used,
            'completion_tokens_used': self.completion_tokens_used,
            'prompt_tokens_used': self.prompt_tokens_used,
            'last_llm_token_feedback': self.last_llm_token_feedback,
        }
        with open('callback_counts.json', 'w') as file:
            json.dump(data, file)

    def on_llm_end(self, *args, **kwargs):
        token_feedback = args[0].llm_output['token_usage']
        self.llm_invoke_count += 1
        
        if token_feedback:
            curr_completion_tokens = token_feedback['completion_tokens']
            curr_total_tokens = token_feedback['total_tokens']
            curr_propmt_tokens = token_feedback['prompt_tokens']
            self.total_tokens_used += curr_total_tokens
            self.completion_tokens_used += curr_completion_tokens
            self.prompt_tokens_used += curr_propmt_tokens
            self.last_llm_token_feedback = token_feedback
        self.save_counts()
