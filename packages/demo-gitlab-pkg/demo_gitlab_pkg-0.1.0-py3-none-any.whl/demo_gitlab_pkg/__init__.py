"""
Demo GitLab Package.
"""

def hello(name: str = "World") -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

def main() -> None:
    """Entry point for the application."""
    print(hello("GitLab"))

if __name__ == "__main__":
    main()
