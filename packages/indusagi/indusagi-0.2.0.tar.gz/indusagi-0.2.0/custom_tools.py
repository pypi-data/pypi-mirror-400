"""
Custom Tools Example - User-Defined Tools for indus-agents

This file demonstrates how users can create their own custom tools
and register them with indus-agents.

Usage:
    1. Create your tool function with type hints
    2. Add a clear docstring describing what the tool does
    3. Use @registry.register decorator to register it
    4. The tool becomes immediately available to all agents!

Example:
    from indusagi import registry

    @registry.register
    def my_tool(param: str) -> str:
        '''Description of what my tool does.'''
        return param.upper()
"""

from indusagi import registry
from typing import Optional, List
import random
import os
from datetime import datetime, timedelta


# ============================================================================
# EXAMPLE CUSTOM TOOL 1: Weather Simulator
# ============================================================================

@registry.register
def get_weather(city: str, unit: str = "celsius") -> str:
    """
    Get current weather for a city (simulated data for demo purposes).

    Args:
        city: Name of the city to get weather for
        unit: Temperature unit ('celsius' or 'fahrenheit')

    Returns:
        Weather information as a formatted string
    """
    # Simulate weather data (in real app, would call weather API)
    temperatures = {
        "celsius": random.randint(15, 35),
        "fahrenheit": random.randint(59, 95)
    }

    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Clear"]
    condition = random.choice(conditions)

    temp = temperatures.get(unit.lower(), temperatures["celsius"])
    unit_symbol = "C" if unit.lower() == "celsius" else "F"

    return f"Weather in {city}: {condition}, {temp} degrees {unit_symbol}"


# ============================================================================
# EXAMPLE CUSTOM TOOL 2: File Operations
# ============================================================================

@registry.register
def create_file(filename: str, content: str) -> str:
    """
    Create a text file with the given content.

    Args:
        filename: Name of the file to create (must end with .txt)
        content: Content to write to the file

    Returns:
        Success message with file path
    """
    # Security: Only allow .txt files in current directory
    if not filename.endswith('.txt'):
        return "Error: Only .txt files are allowed for security reasons"

    if '/' in filename or '\\' in filename:
        return "Error: Cannot create files in subdirectories for security reasons"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        full_path = os.path.abspath(filename)
        return f"Successfully created file: {full_path}"

    except Exception as e:
        return f"Error creating file: {str(e)}"


@registry.register
def read_file(filename: str) -> str:
    """
    Read content from a text file.

    Args:
        filename: Name of the file to read

    Returns:
        File content or error message
    """
    try:
        # Security: Only allow reading .txt files in current directory
        if not filename.endswith('.txt'):
            return "Error: Only .txt files are allowed for security reasons"

        if '/' in filename or '\\' in filename:
            return "Error: Cannot read files from subdirectories for security reasons"

        if not os.path.exists(filename):
            return f"Error: File '{filename}' not found"

        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        return f"Content of {filename}:\n{content}"

    except Exception as e:
        return f"Error reading file: {str(e)}"


# ============================================================================
# EXAMPLE CUSTOM TOOL 3: Random Number Generator
# ============================================================================

@registry.register
def random_number(min_value: int = 1, max_value: int = 100) -> str:
    """
    Generate a random number within a specified range.

    Args:
        min_value: Minimum value (inclusive)
        max_value: Maximum value (inclusive)

    Returns:
        Random number as string
    """
    if min_value > max_value:
        return f"Error: min_value ({min_value}) cannot be greater than max_value ({max_value})"

    number = random.randint(min_value, max_value)
    return f"Random number between {min_value} and {max_value}: {number}"


# ============================================================================
# EXAMPLE CUSTOM TOOL 4: Password Generator
# ============================================================================

@registry.register
def generate_password(length: int = 12, include_symbols: bool = True) -> str:
    """
    Generate a secure random password.

    Args:
        length: Length of the password (minimum 8)
        include_symbols: Whether to include special symbols

    Returns:
        Generated password
    """
    if length < 8:
        return "Error: Password length must be at least 8 characters"

    import string

    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += "!@#$%^&*"

    password = ''.join(random.choice(characters) for _ in range(length))
    return f"Generated password: {password}"


# ============================================================================
# EXAMPLE CUSTOM TOOL 5: Text Statistics
# ============================================================================

@registry.register
def text_stats(text: str) -> str:
    """
    Get detailed statistics about a text string.

    Args:
        text: Text to analyze

    Returns:
        Formatted statistics about the text
    """
    char_count = len(text)
    word_count = len(text.split())
    line_count = text.count('\n') + 1
    alpha_count = sum(c.isalpha() for c in text)
    digit_count = sum(c.isdigit() for c in text)
    space_count = sum(c.isspace() for c in text)

    stats = f"""Text Statistics:
- Characters: {char_count}
- Words: {word_count}
- Lines: {line_count}
- Letters: {alpha_count}
- Digits: {digit_count}
- Spaces: {space_count}"""

    return stats


# ============================================================================
# EXAMPLE CUSTOM TOOL 6: Date Calculator
# ============================================================================

@registry.register
def date_calculator(days_from_now: int) -> str:
    """
    Calculate a date by adding or subtracting days from today.

    Args:
        days_from_now: Number of days to add (positive) or subtract (negative)

    Returns:
        The calculated date in YYYY-MM-DD format
    """
    target_date = datetime.now() + timedelta(days=days_from_now)
    formatted_date = target_date.strftime("%Y-%m-%d")

    if days_from_now > 0:
        return f"{days_from_now} days from now will be: {formatted_date}"
    elif days_from_now < 0:
        return f"{abs(days_from_now)} days ago was: {formatted_date}"
    else:
        return f"Today's date is: {formatted_date}"


# ============================================================================
# EXAMPLE CUSTOM TOOL 7: List Operations
# ============================================================================

@registry.register
def pick_random_item(items: str, separator: str = ",") -> str:
    """
    Pick a random item from a list of items.

    Args:
        items: Items separated by the separator (e.g., "apple,banana,orange")
        separator: Character/string that separates items (default: comma)

    Returns:
        Randomly selected item
    """
    item_list = [item.strip() for item in items.split(separator) if item.strip()]

    if not item_list:
        return "Error: No items provided"

    if len(item_list) == 1:
        return f"Only one item available: {item_list[0]}"

    selected = random.choice(item_list)
    return f"Randomly selected from {len(item_list)} items: {selected}"


# ============================================================================
# EXAMPLE CUSTOM TOOL 8: URL Builder
# ============================================================================

@registry.register
def build_search_url(query: str, search_engine: str = "google") -> str:
    """
    Build a search URL for popular search engines.

    Args:
        query: Search query
        search_engine: Search engine to use (google, bing, duckduckgo)

    Returns:
        Complete search URL
    """
    import urllib.parse

    encoded_query = urllib.parse.quote(query)

    urls = {
        "google": f"https://www.google.com/search?q={encoded_query}",
        "bing": f"https://www.bing.com/search?q={encoded_query}",
        "duckduckgo": f"https://duckduckgo.com/?q={encoded_query}"
    }

    url = urls.get(search_engine.lower())

    if not url:
        available = ", ".join(urls.keys())
        return f"Error: Unknown search engine. Available: {available}"

    return f"Search URL for '{query}' on {search_engine}: {url}"


# ============================================================================
# Print confirmation when module is loaded
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CUSTOM TOOLS LOADED SUCCESSFULLY")
    print("=" * 70)
    print(f"\nTotal custom tools registered: 8")
    print("\nAvailable custom tools:")
    print("  1. get_weather - Get weather for a city")
    print("  2. create_file - Create a text file")
    print("  3. read_file - Read a text file")
    print("  4. random_number - Generate random number")
    print("  5. generate_password - Generate secure password")
    print("  6. text_stats - Get text statistics")
    print("  7. date_calculator - Calculate dates")
    print("  8. pick_random_item - Pick random item from list")
    print("  9. build_search_url - Build search URLs")
    print("\nThese tools are now available in the registry!")
    print("=" * 70)
