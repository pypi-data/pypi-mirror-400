import asyncio
import os
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

load_dotenv()


async def test_openrouter():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("FAIL: OPENROUTER_API_KEY not found")
        return False

    model = LiteLlm(
        model="openrouter/xiaomi/mimo-v2-flash:free",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    try:
        # Simple completion test
        response = await model.generate_content_async("Say 'Hello World'")
        if response and hasattr(response, "text"):
            print(f"SUCCESS: OpenRouter connection works. Response: {response.text}")
            return True
        else:
            print("FAIL: No valid response from OpenRouter")
            return False
    except Exception as e:
        print(f"FAIL: Error connecting to OpenRouter: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_openrouter())
    exit(0 if result else 1)
