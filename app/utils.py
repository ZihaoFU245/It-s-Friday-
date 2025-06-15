from pathlib import Path

def update_keys(key: str, value: str):
    """
    change the api keys in the .env file
    """
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
        return

    with open(env_path, "r+", encoding="utf-8") as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[idx] = f"{key}={value}\n"
                f.seek(0)
                f.writelines(lines)
                f.truncate()
                return
        # Key not found, append to end, ensuring newline
        if lines and not lines[-1].endswith('\n'):
            f.write('\n')
        f.write(f"{key}={value}\n")