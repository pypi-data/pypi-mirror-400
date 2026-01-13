import os
import platform
from datetime import datetime
from typing import Dict, Any, Optional


def render_instructions(
    template_path: str,
    model: str = "gpt-4o",
    extra_context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Render instructions template with placeholders replaced.

    Placeholders:
        {cwd} - Current working directory
        {is_git_repo} - Whether current dir is a git repo
        {platform} - OS platform (Linux, Darwin, Windows)
        {os_version} - OS version string
        {today} - Current date (YYYY-MM-DD)
        {model} - Model name being used
    """
    with open(template_path, "r") as f:
        content = f.read()

    placeholders = {
        "{cwd}": os.getcwd(),
        "{is_git_repo}": str(os.path.isdir(os.path.join(os.getcwd(), ".git"))),
        "{platform}": platform.system(),
        "{os_version}": platform.release(),
        "{today}": datetime.now().strftime("%Y-%m-%d"),
        "{model}": model,
    }

    if extra_context:
        for key, value in extra_context.items():
            placeholders[f"{{{key}}}"] = str(value)

    for key, value in placeholders.items():
        content = content.replace(key, value)

    return content
