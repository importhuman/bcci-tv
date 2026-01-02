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

## Precision & Non-Interference
- **Fresh State Check:** Always call `read_file` immediately before making any modification to ensure you are working with the latest version of the code, including any manual edits made by the user.
- **Surgical Edits:** Favor the `replace` tool over `write_file` for existing files. Keep the `old_string` as specific as possible to target only the intended logic.
- **Scope Discipline:** Do not refactor, "clean up," or modify code that is outside the direct scope of the current task. If a task is to add Function B, do not touch Function A.
- **Context Preservation:** When using `replace`, ensure at least 3 lines of unchanged context are included in both `old_string` and `new_string` to anchor the change correctly without drifting.
- **No Unsolicited Rewrites:** Never rewrite a function to "improve" it unless explicitly asked to refactor. Maintain the user's manual implementation details (comments, variable naming) exactly as they are.

## Structure
- The package should be able to be installed via uv, or referred locally.
- Maintain clean and separate files as per functionality. This includes separate files for calling APIs, API helper functions, MCP functions.

## Testing
- Write unit tests for all functions. For API calls, call a mockserver that provides mock data.
- Write integration tests where possible.