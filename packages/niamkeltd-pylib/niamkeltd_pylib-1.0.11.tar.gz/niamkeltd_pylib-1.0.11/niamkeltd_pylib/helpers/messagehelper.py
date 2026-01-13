import re

def get_id(message: str) -> int:
    numbers = list(map(int, re.findall(r'\d+', message)))
    return 0 if numbers.__len__() == 0 else numbers[0]

def get_flag(message: str) -> bool:
    """Convert a string to a boolean.
    Any values that are not 'true', 'yes' or '1' will return false.
    This means that an explicit check for 'false', 'no' or '0' is not required."""
    return message.strip().lower() in ['true', 'yes', '1']

def trim_and_close_html_tags(s: str, max_length: int) -> str:
    """Trim a string to max_length, ensuring HTML tags like <i> and <b> are properly closed."""
    trimmed = s[:max_length]
    open_tags = []

    # Parse and track unclosed tags
    i = 0
    while i < len(trimmed):
        if trimmed[i] == "<":
            # Look for opening or closing tags
            end = trimmed.find(">", i)
            if end == -1:
                break  # Malformed tag, exit parsing
            tag = trimmed[i + 1:end].strip()
            if not tag.startswith("/"):  # Opening tag
                open_tags.append(tag)
            elif open_tags and open_tags[-1] == tag[1:]:  # Closing tag
                open_tags.pop()
            i = end
        i += 1

    # Append closing tags for any unclosed tags
    for tag in reversed(open_tags):
        trimmed += f"</{tag}>"

    return trimmed