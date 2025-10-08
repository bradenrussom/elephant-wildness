"""
Utilities - Shared helper functions and configuration loading
"""

import yaml
import os
from typing import Dict, Any, List
import re


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config.yaml
    
    Returns:
        Dictionary with configuration
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_module_config(module_name: str, config: Dict = None) -> Dict[str, Any]:
    """
    Get configuration for a specific module
    
    Args:
        module_name: Name of module (e.g., 'communications_standards')
        config: Full config dict (will load if None)
    
    Returns:
        Module configuration dictionary
    """
    if config is None:
        config = load_config()
    
    return config.get(module_name, {})


def is_check_enabled(check_config: Dict) -> bool:
    """
    Check if a specific check is enabled
    
    Args:
        check_config: Configuration dict for the check
    
    Returns:
        True if enabled, False otherwise
    """
    # If there's an 'enabled' key, use it
    if 'enabled' in check_config:
        return check_config['enabled']
    
    # If there's a 'check' key with value 'auto', it's enabled
    if check_config.get('check') == 'auto':
        return True
    
    # Otherwise default to False (manual checks)
    return False


def format_phone_number(phone: str, config: Dict = None) -> str:
    """
    Format phone number according to MVP standards
    
    Args:
        phone: Phone number string
        config: Phone number config (optional)
    
    Returns:
        Formatted phone number
    """
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Standard format: no spaces, dashes, or parentheses
    if len(digits) == 10:
        return digits
    elif len(digits) == 11 and digits[0] == '1':
        # Toll-free with prefix
        return f"1-{digits[1:]}"
    
    return phone  # Return original if can't parse


def format_time(time_str: str) -> str:
    """
    Format time according to MVP standards
    - Lowercase am/pm
    - No spaces
    - No periods
    - Remove :00
    
    Args:
        time_str: Time string (e.g., "3:00 PM", "9:30 am")
    
    Returns:
        Formatted time string (e.g., "3 pm", "9:30 am")
    """
    # Remove :00
    time_str = re.sub(r':00\b', '', time_str)
    
    # Lowercase and remove spaces/periods from AM/PM
    time_str = re.sub(r'\s*(A\.?M\.?|P\.?M\.?)\b', 
                     lambda m: ' ' + m.group(1).replace('.', '').lower(), 
                     time_str, flags=re.IGNORECASE)
    
    return time_str.strip()


def format_time_range(time_range: str) -> str:
    """
    Format time range with en dash, no spaces
    
    Args:
        time_range: Time range string (e.g., "8:00 AM - 5:00 PM")
    
    Returns:
        Formatted range (e.g., "8 am–5 pm")
    """
    # Split on various dash types and 'to'
    parts = re.split(r'\s*[-–—]\s*|\s+to\s+', time_range, flags=re.IGNORECASE)
    
    if len(parts) == 2:
        start = format_time(parts[0])
        end = format_time(parts[1])
        return f"{start}–{end}"
    
    return time_range


def spell_out_number(num: int) -> str:
    """
    Spell out single-digit numbers (1-9)
    
    Args:
        num: Number to spell out
    
    Returns:
        Spelled out number or original if > 9
    """
    number_words = {
        1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
        6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'
    }
    
    return number_words.get(num, str(num))


def add_commas_to_number(num_str: str) -> str:
    """
    Add commas to numbers >= 1000
    
    Args:
        num_str: Number string
    
    Returns:
        Number with commas
    """
    # Check if it's a valid number
    try:
        num = int(num_str.replace(',', ''))
        if num >= 1000:
            return f"{num:,}"
        return num_str
    except ValueError:
        return num_str


def clean_double_spaces(text: str) -> str:
    """
    Replace double spaces with single spaces
    
    Args:
        text: Text to clean
    
    Returns:
        Text with single spaces
    """
    return re.sub(r'  +', ' ', text)


def get_heading_level(style_name: str) -> int:
    """
    Extract heading level from style name
    
    Args:
        style_name: Style name (e.g., "Heading 1", "Heading 2")
    
    Returns:
        Heading level (1-5) or 0 if not a heading
    """
    match = re.search(r'Heading (\d)', style_name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0


def should_be_title_case(heading_level: int) -> bool:
    """
    Determine if heading should be title case (H1, H2) or sentence case (H3+)
    
    Args:
        heading_level: Heading level (1-5)
    
    Returns:
        True if should be title case, False for sentence case
    """
    return heading_level in [1, 2]


def to_title_case(text: str) -> str:
    """
    Convert text to title case
    
    Args:
        text: Text to convert
    
    Returns:
        Title cased text
    """
    # Simple title case - capitalize first letter of each major word
    small_words = ['a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 
                   'of', 'on', 'or', 'the', 'to', 'up', 'via']
    
    words = text.split()
    result = []
    
    for i, word in enumerate(words):
        # Always capitalize first and last word
        if i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        # Small words stay lowercase (unless they start a sentence)
        elif word.lower() in small_words:
            result.append(word.lower())
        # Everything else gets capitalized
        else:
            result.append(word.capitalize())
    
    return ' '.join(result)


def to_sentence_case(text: str) -> str:
    """
    Convert text to sentence case
    
    Args:
        text: Text to convert
    
    Returns:
        Sentence cased text
    """
    # Capitalize first letter only
    if not text:
        return text
    return text[0].upper() + text[1:].lower()


def extract_links_from_text(text: str) -> List[Dict[str, str]]:
    """
    Extract links formatted like: ~anchor text~ [url]
    
    Args:
        text: Text containing formatted links
    
    Returns:
        List of dicts with 'anchor' and 'url' keys
    """
    # Pattern: ~text~ [url]
    pattern = r'~([^~]+)~\s*\[([^\]]+)\]'
    matches = re.finditer(pattern, text)
    
    links = []
    for match in matches:
        links.append({
            'anchor': match.group(1).strip(),
            'url': match.group(2).strip()
        })
    
    return links


def is_url(text: str) -> bool:
    """
    Check if text is a URL
    
    Args:
        text: Text to check
    
    Returns:
        True if text appears to be a URL
    """
    url_pattern = r'^(https?://|www\.)'
    return bool(re.match(url_pattern, text.lower()))


def create_correction_log_entry(rule_name: str, original: str, corrected: str, 
                                location: str = '') -> Dict[str, str]:
    """
    Create a standardized correction log entry
    
    Args:
        rule_name: Name of the rule applied
        original: Original text
        corrected: Corrected text
        location: Location in document (optional)
    
    Returns:
        Dictionary with correction details
    """
    return {
        'rule': rule_name,
        'original': original,
        'corrected': corrected,
        'location': location
    }


# Example usage
if __name__ == '__main__':
    # Load config
    config = load_config()
    print("Config loaded successfully")
    
    # Get module config
    comms_config = get_module_config('communications_standards', config)
    print(f"Communications standards config: {list(comms_config.keys())}")
    
    # Test utilities
    print(f"\nTime formatting:")
    print(f"  '3:00 PM' -> '{format_time('3:00 PM')}'")
    print(f"  '8:00 AM - 5:00 PM' -> '{format_time_range('8:00 AM - 5:00 PM')}'")
    
    print(f"\nNumber formatting:")
    print(f"  5 -> '{spell_out_number(5)}'")
    print(f"  '1500' -> '{add_commas_to_number('1500')}'")
    
    print(f"\nHeading cases:")
    print(f"  'hello world' (H1) -> '{to_title_case('hello world')}'")
    print(f"  'HELLO WORLD' (H3) -> '{to_sentence_case('HELLO WORLD')}'")