# RiyadhAI SDK (Python)

Python SDK for building realtime Live Gemini experince with RiyadhAI.

## Install

Core:

```bash
pip install riyadhai
```

All plugins (once published):

```bash
pip install "riyadhai[full]"
```

## Environment variables

- `RIYADHAI_URL`
- `RIYADHAI_API_KEY`
- `RIYADHAI_API_SECRET`
- `GOOGLE_API_KEY`

## Quick start

Create an `agent.py`:

```py
from dotenv import load_dotenv

from riyadhai import agents, rtc
from riyadhai.agents import AgentServer, AgentSession, Agent, room_io
from riyadhai.plugins import (
    google
)

load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")

server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            #Model name
            #Model voice
        )
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
    ),

    await session.generate_reply(
        instructions="Greet the user and offer your assistance. You should start by speaking in English."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
```
Run:

```bash
python agent.py dev
```
