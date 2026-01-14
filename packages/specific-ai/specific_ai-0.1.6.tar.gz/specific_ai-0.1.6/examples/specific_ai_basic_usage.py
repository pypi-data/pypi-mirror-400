from specific_ai import SpecificAIClient


def specific_ai_example():
    """Example of using SpecificAIClient for direct inference on SpecificAI models."""

    # This is an example of how to use the SpecificAIClient for direct inference.
    # Unlike the OpenAI and Anthropic wrappers, this client communicates directly with
    # SpecificAI deployed models without any fallback to third-party LLM providers.
    # Use this when you have a trained and deployed model on the SpecificAI platform.

    # For example, let's write a prompt for classification of a review:
    PROMPT_TEMPLATE = """
given the example, classify the reviews to one of two options according to their content, the optional categories are: 
Label 0: Negative 
Label 1: Positive 

always return only the numerical value for each review, meaning you will return a number either 0 or 1. 
for example: 0, another example: 1. no other talks.
example:
{example}
"""
    example = "This movie was terrible!"
    prompt = PROMPT_TEMPLATE.format(example=example)

    # Initialize the SpecificAI client
    client = SpecificAIClient(
        url="<your-specific-ai-service-URL>",  # Your SpecificAI service URL
    )

    # Make a direct inference request to the deployed SpecificAI model
    # The response type depends on your task type (classification, NER, etc.)
    response = client.create(
        message=prompt,
        task_name="<your-task-name>",  # The deployed Task name in the SpecificAI platform
        project_name="<your-project-name>",  # The deployed Project name in the SpecificAI platform
    )

    # For classification tasks, response is a ClassificationResponse with a 'labels' field
    print(f"Classification result: {response.labels}")


if __name__ == "__main__":
    specific_ai_example()
