# Project: bcci.tv MCP server

## Goal
Building an MCP server to interact with bcci.tv and get match information.

## General
- Use python.
- Use uv for managing the project. Do not install packages globally.
- Document code well
- Make code async
- Use FastMCP for MCP related code
- Use httpx for HTTP requests
- Avoid unnecessary package or function imports

## Structure
- The package should be able to be installed via uv, or referred locally.
- Maintain clean and separate files as per functionality. This includes separate files for calling APIs, API helper functions, MCP functions.

## Testing
- Write unit tests for all functions. For API calls, call a mockserver that provides mock data.
- Write integration tests where possible.