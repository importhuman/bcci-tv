# Project: bcci.tv MCP server

## Goal
Building an MCP server to interact with bcci.tv and get match information.

## General
- Use python. Write clean code, using constants and classes where applicable, following best practices for python.
- Use uv for managing the project. Do not install packages globally.
- While adding new functions/tests, avoid updating existing functions/tests unless required.
- ALWAYS plan first, then ask for confirmation before implementing.
- Ask for confirmation before updating `pyproject.toml`.
- Document code well

## Code
- Do error handling properly by using try-except blocks.
- Make code async
- Use FastMCP for MCP related code
- Use httpx for HTTP requests
- Avoid unnecessary package or function imports
- Avoid adding unnecessary headers for API calls.

## Structure
- The package should be able to be installed via uv, or referred locally.
- Maintain clean and separate files as per functionality. This includes separate files for calling APIs, API helper functions, MCP functions.

## Testing
- Write unit tests for all functions. For API calls, call a mockserver that provides mock data.
- Write integration tests where possible.