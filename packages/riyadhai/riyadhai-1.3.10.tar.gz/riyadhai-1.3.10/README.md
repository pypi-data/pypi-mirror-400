# RiyadhAI

RiyadhAI LLC publishes the `riyadhai` Python package.

It provides:
- `riyadhai.agents`: RiyadhAI Agents runtime + tooling
- `riyadhai.plugins.google.realtime`: Gemini Realtime integration

## Env Vars

Required (Server):
- `RIYADAI_URL`
- `RIYADAI_API_KEY`
- `RIYADAI_API_SECRET`

Required (Gemini):
- `GOOGLE_API_KEY` (or set Vertex AI auth envs)

## Install

- Install (dev): `pip install -e .`

## Usage

Write your own agent using `riyadhai.agents.AgentServer` + `riyadhai.plugins.google.realtime.RealtimeModel`.
