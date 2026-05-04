
import os
import asyncio
from app.agent import app as adk_app
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService

async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="app", user_id="test_user", session_id="test_session")
    runner = Runner(
        app=adk_app, 
        session_service=session_service, 
        artifact_service=InMemoryArtifactService()
    )
    try:
        from google.genai import types
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session",
            new_message=types.Content(
                role="user", 
                parts=[types.Part.from_text(text="news in London")]
            )
        ):
            print(f"Event: {event}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
