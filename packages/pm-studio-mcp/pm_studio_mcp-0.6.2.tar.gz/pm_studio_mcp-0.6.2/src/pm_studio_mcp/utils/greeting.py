from pm_studio_mcp.config import config
from pm_studio_mcp.internal_prompt.pm_studio_prompt import get_pm_studio_prompt

class GreetingUtils:
    @staticmethod
    def get_pm_studio_guide(name: str, intent: str = "default"):
        """
        Respond to a greeting or ask for help message with the PM Studio prompt content.
        
        Args:
            name (str): User's name for personalization
            intent (str): Specific intent to customize the prompt for.
                         Options: "feedback_analysis", "competitor_analysis", "data_analysis", "mission_review", "default"
        """
        try:
            # Get the appropriate prompt based on intent
            prompt_content = get_pm_studio_prompt(intent)
            
            # Return the content with a personalized greeting
            return f"Use the chat: run prompt tool to run prompt from {prompt_content}"
                
        except Exception as e:
            # Fallback to the original greeting if there's any error
            return f"Hello {name}! {config.GREETING_TEMPLATE.format(name=name)} (Error loading full guide: {str(e)})"