from specific_ai import OpenAI


def classification_example():
    """Example of using the specific_ai SDK for text classification."""

    # This is an example of how to use the specific_ai SDK.
    # As default (use_specific_ai_inference=False), it sends requests to the OpenAI API, and only traces the results via SpecificAI platform.
    # If you want to inference the SpecificAI models, you need to set use_specific_ai_inference=True.
    # Make sure to set the task_name and project_name in the specific_ai parameters and deploy the model through the SpecificAI platform.

    # For example, let's write a prompt for classification of a question to one of two categories:
    PROMPT_TEMPLATE = """
given the example, classify the reviews to one of two options according to their content, the optional categories are: 
Label 0: Negative 
Label 1: Positive 

always return only the numerical value for each review, meaning you will return a number either 0 or 1. 
for example: 0, another example: 1. no other talks.
example:
{{example}}
"""
    example = "This movie was terrible!"
    prompt = PROMPT_TEMPLATE.replace("{{example}}", example)

    # Initialize the OpenAI client with SpecificAI integration
    client = OpenAI(
        specific_ai_url="<your-specific-ai-service-URL>",
        api_key="<your-openai-api-key>",  # Optional, only if you want to use the OpenAI API directly (for collecting data for your task) or for fallback in case the SpecificAI model is not available.
        use_specific_ai_inference=True,  # Set to true once you successfully deployed the model through the SpecificAI platform
    )

    # Sends a request through the specific_ai SDK.
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=1,
        specific_ai={  # SpecificAI's parameters
            "task_name": "classification-task-example",  # choose the deployed Task name in the SpecificAI platform
            "project_name": "classification-project-example",  # choose the deployed Project name in the SpecificAI platform
        },
    )

    # And that's it!
    print(f"Classification result: {response.choices[0].message.content}")


if __name__ == "__main__":
    classification_example()
