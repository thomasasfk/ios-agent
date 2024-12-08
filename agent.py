import textwrap
import logfire
from typing import Optional, Union
from pydantic import BaseModel
from dotenv import load_dotenv
from pydantic_ai import Agent
from typing import Literal

logfire.configure()
load_dotenv()


ActionType = Literal["copy_to_clipboard", "open_iphone_app", "show_response", "unknown_action"]
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

class ShowResponse(BaseResponse):
    action: Literal["show_response"]
    response_text: str

class UnknownResponse(BaseResponse):
    action: Literal["unknown_action"]
    error_message: Optional[str] = None


ResponseType = Union[CopyResponse, IPhoneAppResponse, ShowResponse, UnknownResponse]


class Dependencies: ...

agent = Agent(
    "openai:gpt-4o-mini",
    deps_type=Dependencies,
    result_type=ResponseType,
    system_prompt=textwrap.dedent("""
        Route user requests to supported actions or show responses for questions.
        Return ShowResponse for general questions, use appropriate action responses
        for commands, and UnknownResponse only for ambiguous requests.
    """)
)

def run_agent(transcription: str) -> str:
    run_result = agent.run_sync(transcription, deps=Dependencies())
    return run_result.data.model_dump_json()