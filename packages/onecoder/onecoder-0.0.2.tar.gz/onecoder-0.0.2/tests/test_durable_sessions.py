import asyncio
import os
import shutil
import pytest
from pathlib import Path
from onecoder.sessions import DurableSessionService
from google.adk.events.event import Event, EventActions
from google.adk.sessions.state import State

@pytest.mark.async_io
async def test_durable_session_persistence():
    storage_dir = "test_sessions_storage"
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)
        
    service = DurableSessionService(storage_dir=storage_dir)
    app_name = "test_app"
    user_id = "user_1"
    session_id = "session_1"
    
    # 1. Create session
    session = await service.create_session(
        app_name=app_name, 
        user_id=user_id, 
        session_id=session_id,
        state={"initial": "value"}
    )
    
    assert session.id == session_id
    assert session.state["initial"] == "value"
    
    # 2. Append event with state delta
    event = Event(
        author="test_author",
        timestamp=123.456,
        actions=EventActions(
            state_delta={"new_key": "new_value", "initial": "updated"}
        )
    )
    await service.append_event(session, event)
    
    # 3. Reload service and session
    new_service = DurableSessionService(storage_dir=storage_dir)
    loaded_session = await new_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    assert loaded_session is not None
    assert loaded_session.id == session_id
    assert loaded_session.state["new_key"] == "new_value"
    assert loaded_session.state["initial"] == "updated"
    assert len(loaded_session.events) == 1
    assert loaded_session.events[0].timestamp == 123.456
    
    # Clean up
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)

if __name__ == "__main__":
    asyncio.run(test_durable_session_persistence())
    print("Verification test passed!")
