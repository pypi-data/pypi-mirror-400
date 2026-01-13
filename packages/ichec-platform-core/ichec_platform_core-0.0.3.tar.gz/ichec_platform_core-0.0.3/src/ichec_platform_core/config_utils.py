from pathlib import Path


def find_config_path(
    candidate: Path | None, app_name: str, filename: str = "config.yaml"
) -> Path | None:

    if candidate:
        return candidate

    user_path = Path.home() / ".config" / app_name / filename
    system_path = Path(f"/etc/{app_name}/{filename}")

    if user_path.exists():
        return user_path
    elif system_path.exists():
        return system_path

    return None
