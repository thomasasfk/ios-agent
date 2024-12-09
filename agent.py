import textwrap
from dataclasses import dataclass

import logfire
from typing import Optional, Union, Tuple
from pydantic import BaseModel
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from typing import Literal

from notes import NotesDB

logfire.configure()
load_dotenv()

CopyToClipboard = Literal["Copy to Clipboard"]
OpeniPhoneApp = Literal["Open iPhone App"]
ShowResponse = Literal["Show Response"]
ActionType = CopyToClipboard | OpeniPhoneApp | ShowResponse
IPhoneApp = Literal["Amazon", "Anki", "Arnold Clark", "Asda Rewards", "Authenticator", "Authy", "BS Companion",
                    "Bambu Handy", "Bitwarden", "BroadLink", "Calculator", "Calendar", "ChatGPT", "Claude", "Clock",
                    "Compass", "Connect", "Contacts", "Discord", "FaceTime", "Files", "Find My", "Fitness",
                    "Google Translate", "HMRC", "Health", "Home Assistant", "Insta360", "JD Gyms", "Just Eat", "Lens",
                    "LinkedIn", "Magnifier", "Mail", "Maps", "Measure", "Messages", "Messenger", "Meta Horizon",
                    "Notes", "Passwords", "PayPal", "Phone", "Photos", "Plex", "RVNC Viewer", "Reminders", "Revolut",
                    "Safari", "Shortcuts", "Snapchat", "Spotify", "Steam", "Steam Chat", "TSB", "Teams", "Telegram",
                    "Three", "Three+", "TikTok", "Translate", "Tuya Smart", "Twitch", "Weather", "WhatsApp", "YouTube",
                    "YouTube Music"]

class BaseResponse(BaseModel):
    action: ActionType
    success: bool

class CopyResponse(BaseResponse):
    action: CopyToClipboard = "Copy to Clipboard"
    clipboard_text: str

class IPhoneAppResponse(BaseResponse):
    action: OpeniPhoneApp = "Open iPhone App"
    app_name: IPhoneApp

class ShowResponse(BaseResponse):
    action: ShowResponse = "Show Response"
    response_text: str

ResponseType = CopyResponse | IPhoneAppResponse | ShowResponse

@dataclass
class Dependencies:
    notes_db: NotesDB = NotesDB()

SYSTEM_PROMPT = """
You are a personal assistant that manages notes and handles various actions. You can:
1. Create new notes
2. Update the current working note
3. View today's notes
4. Handle other actions like copying to clipboard or opening iPhone apps

For note management:
- When asked to create a new note, use create_note()
- When asked to update the current note, use update_current_note()
- Always include any existing note content when updating
- Return appropriate ShowResponse for note operations

For other actions:
- Return CopyResponse for clipboard operations
- Return IPhoneAppResponse for app opening requests
- Return ShowResponse for general questions or ambiguous requests
- When returning ShowResponse, don't return markdown, plaintext only
"""

agent = Agent(
    "openai:gpt-4o-mini",
    deps_type=Dependencies,
    result_type=ResponseType,
    system_prompt=textwrap.dedent(SYSTEM_PROMPT),
    result_retries=3,
    retries=3,
)

@agent.tool
def create_note(ctx: RunContext[Dependencies], initial_content: str = "") -> int:
    """Creates a new note and makes it the current note. Returns the note ID."""
    return ctx.deps.notes_db.create_note(initial_content)

@agent.tool
def get_current_note(ctx: RunContext[Dependencies]) -> Optional[Tuple[int, str, str, str]]:
    """Gets the current note's details (id, content, created_at, updated_at)"""
    return ctx.deps.notes_db.get_current_note()

@agent.tool
def update_current_note(ctx: RunContext[Dependencies], new_content: str) -> Optional[int]:
    """Updates the current note with new content. Returns the note ID or None if no current note."""
    return ctx.deps.notes_db.update_current_note(new_content)

def run_agent(transcription: str) -> str:
    """Runs the agent with the given transcription and returns the response as JSON"""
    run_result = agent.run_sync(transcription, deps=Dependencies())
    return run_result.data.model_dump_json()