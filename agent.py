import textwrap
import logfire
from typing import Optional, Union
from pydantic import BaseModel
from dotenv import load_dotenv
from pydantic_ai import Agent
from typing import Literal

logfire.configure()
load_dotenv()


ActionType = Literal["copy_to_clipboard", "open_iphone_app", "unknown_action"]
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
    action: Literal["copy_to_clipboard"]
    clipboard_text: str

class IPhoneAppResponse(BaseResponse):
    action: Literal["open_iphone_app"]
    app_name: IPhoneApp

class UnknownResponse(BaseResponse):
    action: Literal["unknown_action"]
    error_message: Optional[str] = None


ResponseType = Union[CopyResponse, IPhoneAppResponse, UnknownResponse]


class Dependencies: ...

agent = Agent(
    "openai:gpt-4o-mini",
    deps_type=Dependencies,
    result_type=ResponseType,
    system_prompt=textwrap.dedent("""
        Route user requests to supported actions. 
        Map to appropriate response types and validate data.
        For unsupported requests, return UnknownResponse with available actions. 
        If you find an action, respond with the appropriate ResponseType.
        Handle common variations in user phrasing.
    """)
)

# @agent.tool
# def copy_to_clipboard(ctx: RunContext[Dependencies], text: str) -> ResponseType:
#     return ctx.deps.copy_to_clipboard(text)

def run_agent(transcription: str) -> str:
    run_result = agent.run_sync(transcription, deps=Dependencies())
    return run_result.data.model_dump_json()
