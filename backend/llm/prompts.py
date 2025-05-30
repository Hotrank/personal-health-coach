from datetime import datetime

SYSTEM_PROMPT = f"""You are a helpful assistant that provides information about the current state of the world.
In particular, you ar able to answer health-related questions as a health coach, the current data time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}."""

# For testing only.
USER_MEMORY = """User's name is Hotrank. He was born in 1986. He is a software engineer and has a passion for health and fitness."""
