from __future__ import annotations
import argparse
import os
import sys
from dotenv import find_dotenv, load_dotenv
from typing import Optional, List, Dict, Any
from openai import OpenAI

# ResponsesAPI/SimpleClient.py
#
# Simple client for Azure Responses API using the official OpenAI Python SDK.
#
# Prerequisites:
#   pip install --upgrade openai
#
# Required environment variables:
#   AZURE_OPENAI_ENDPOINT       e.g., https://your-resource-name.openai.azure.com
#   AZURE_OPENAI_API_KEY        your Azure OpenAI API key
#   AZURE_OPENAI_DEPLOYMENT     name of your model deployment in Azure OpenAI (e.g., gpt-4o-mini)
#
# Usage examples:
#   python SimpleClient.py --prompt "Say hello from the Azure Responses API."
#   python SimpleClient.py --prompt "Stream this response." --stream
#   python SimpleClient.py --prompt "Custom temp/max tokens" --temperature 0.2 --max-tokens 200




def build_client() -> OpenAI:
    # Load environment variables from .env file
    load_dotenv(find_dotenv())

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY") 

    if not endpoint or not api_key:
        print(
            "Missing required environment variables AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY.",
            file=sys.stderr,
        )
        sys.exit(2)

    return OpenAI(
        base_url=endpoint,
        api_key=api_key,
    )




def build_messages(user_prompt: str, system_prompt: Optional[str]) -> List[Dict[str, Any]]:
    messages: List[Dict[str, Any]] = []
    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": [{"type": "text", "text": system_prompt}],
            }
        )
    messages.append(
        {
            "role": "user",
            "content": [{"type": "text", "text": user_prompt}],
        }
    )
    return messages


def send_request(
    client: OpenAI,
    deployment: str,
    prompt: str,
    stream: bool = False,
    chain: bool = False,
) -> str:
    # Using the Responses API. You can pass a simple string via 'input' or a structured list of messages.
    # We'll pass structured messages to support an optional system prompt.
    #messages = build_messages(prompt, system_prompt)
    messages = prompt
    if stream:
        text_out = []
        # Stream response chunks as they arrive
        with client.responses.stream(
            model=deployment,
            input=messages,  # structured messages
        ) as s:
            for event in s:
                # Accumulate only text deltas for clean output
                if event.type == "response.output_text.delta":
                    delta = event.delta or ""
                    text_out.append(delta)
                    # Echo streaming output to console as it arrives
                    print(delta, end="", flush=True)
                elif event.type == "response.error":
                    print(f"\n[Error] {event.error}", file=sys.stderr)
            # Ensure newline after streaming output
            print()
            # Get the final full response object if needed
            _final = s.get_final_response()
        return "".join(text_out)

    # Non-streaming request
    resp_id = client.responses.create(
        model=deployment,
        input=messages,
    )
    if chain:
        resp_id = client.responses.create(
        model=deployment,
        previous_response_id=resp_id.id,
        input=[{"role": "user", "content": "Explain this at a level that could be understood by a college freshman"}]
        )

    response = client.responses.retrieve(resp_id.id)
    # The SDK aggregates the text for you
    return response.output_text


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Simple Azure Responses API client."
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="User prompt to send to the model.",
    )
    parser.add_argument(
        "--chain",
        action="store_true",
        help="Chain of prompt responses",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream the response.",
    )

    args = parser.parse_args(argv)

    client = build_client()
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    

    try:
        output = send_request(
            client=client,
            deployment=deployment,
            prompt=args.prompt,
            stream=args.stream,
            chain=args.chain,
        )
        if not args.stream:
            print(output)
        return 0
    except KeyboardInterrupt:
        print("\nCanceled.", file=sys.stderr)
        return 130
    except Exception as ex:
        print(f"Request failed: {ex}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())



