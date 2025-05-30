from datetime import datetime

SYSTEM_PROMPT = (
    f"You are a helpful assistant that provides information about the current state "
    f"of the world. In particular, you are able to answer health-related questions "
    f"as a health coach, the current date time is "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
)

USER_MEMORY_PROMPT = (
    "Here is what we know about the user:\n\n"
    "{user_memory}\n"
)

MEMORY_SUMMARIZE_PROMPT = (
    "Summarize the following conversation in terms of new facts learned about the "
    "user, return empty string if nothing worth memorizing:\n\n"
    "{messages}\n"
)

MEMORY_CONSOLIDATE_PROMPT = (
    "Compare the following two pieces of user memory and determine if the new memory "
    "should replace the existing one. If so, return the new memory as short bullet "
    "points, otherwise return an empty string.\n"
    "Existing Memory:\n{existing_memory}\n"
    "New Memory:\n{new_memory}]\n"
)
