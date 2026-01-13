from datetime import datetime

def set_now_time_to_string(content: str) -> str:
    """
    Enriches the content with the datetime it is generated.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f" [{now_str}] {content}"