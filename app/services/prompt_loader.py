"""
Simple prompt management service for loading and managing system prompts.
"""

class PromptManager:
    """Manages system prompts for various agent nodes."""
    
    def __init__(self):
        self.prompts = {
            "ticket_analysis": """
You are a helpful assistant who is an expert at classifying and analyzing customer support tickets.
Your task is to:
1. Analyze the content of the email/ticket
2. Classify it into the appropriate category
3. Provide clear reasoning for your classification
4. Assess confidence level in your classification

Be thorough but concise in your analysis.
""",
            "email_classification": """
You are a helpful assistant who is an expert at classifying emails into one of the following categories:
- SPAM: Unsolicited commercial emails, promotional content, or junk mail
- MESSAGE: Personal or business correspondence requiring attention
- RESUME: Job applications, CVs, or recruitment-related content
- OTHER: Emails that don't fit the above categories

Analyze the email content and provide accurate classification.
""",
        }
    
    def get_prompt(self, prompt_name: str) -> str:
        """
        Retrieve a prompt by name.
        
        Args:
            prompt_name: The name/key of the prompt to retrieve
            
        Returns:
            The prompt string, or a default prompt if not found
        """
        return self.prompts.get(
            prompt_name, 
            "You are a helpful AI assistant. Please analyze the provided content and respond appropriately."
        )
    
    def add_prompt(self, prompt_name: str, prompt_text: str) -> None:
        """
        Add a new prompt to the manager.
        
        Args:
            prompt_name: The name/key for the prompt
            prompt_text: The prompt text to store
        """
        self.prompts[prompt_name] = prompt_text