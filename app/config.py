from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    ALL_COMMAND_CACHE_MAX_SIZE = int(os.getenv("ALL_COMMAND_CACHE_MAX_SIZE", "1"))
    ALL_COMMAND_CACHE_TTL_IN_SEC = int(os.getenv("ALL_COMMAND_CACHE_TTL_IN_SEC", "180"))
    # Completion script runs on every tab press so it should not stall the prompt.
    COMPLETION_SCRIPT_TIMEOUT_IN_SEC = int(
        os.getenv("COMPLETION_SCRIPT_TIMEOUT_IN_SEC", "2")
    )
