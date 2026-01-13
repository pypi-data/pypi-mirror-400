"""Interactive setup wizard for TrendMiner MCP Server."""

import random
import sys
from pathlib import Path
from typing import Optional

# Example channel names (planets, dwarf planets, and their moons)
EXAMPLE_CHANNEL_NAMES = [
    # Major planets
    "tm-mcp-mercury",
    "tm-mcp-venus",
    "tm-mcp-earth",
    "tm-mcp-mars",
    "tm-mcp-jupiter",
    "tm-mcp-saturn",
    "tm-mcp-uranus",
    "tm-mcp-neptune",
    # Earth's moon
    "tm-mcp-moon",
    # Mars moons
    "tm-mcp-phobos",
    "tm-mcp-deimos",
    # Jupiter moons
    "tm-mcp-io",
    "tm-mcp-europa",
    "tm-mcp-ganymede",
    "tm-mcp-callisto",
    "tm-mcp-amalthea",
    "tm-mcp-adrastea",
    "tm-mcp-metis",
    "tm-mcp-thebe",
    "tm-mcp-himalia",
    "tm-mcp-elara",
    # Saturn moons
    "tm-mcp-titan",
    "tm-mcp-enceladus",
    "tm-mcp-rhea",
    "tm-mcp-iapetus",
    "tm-mcp-dione",
    "tm-mcp-tethys",
    "tm-mcp-mimas",
    "tm-mcp-phoebe",
    "tm-mcp-hyperion",
    "tm-mcp-pandora",
    "tm-mcp-prometheus",
    # Uranus moons
    "tm-mcp-miranda",
    "tm-mcp-ariel",
    "tm-mcp-umbriel",
    "tm-mcp-titania",
    "tm-mcp-oberon",
    "tm-mcp-puck",
    "tm-mcp-cordelia",
    "tm-mcp-ophelia",
    "tm-mcp-bianca",
    "tm-mcp-cressida",
    "tm-mcp-desdemona",
    "tm-mcp-juliet",
    "tm-mcp-portia",
    "tm-mcp-rosalind",
    "tm-mcp-belinda",
    "tm-mcp-perdita",
    # Neptune moons
    "tm-mcp-triton",
    "tm-mcp-nereid",
    "tm-mcp-proteus",
    "tm-mcp-naiad",
    "tm-mcp-thalassa",
    "tm-mcp-despina",
    "tm-mcp-galatea",
    "tm-mcp-larissa",
    "tm-mcp-hippocamp",
    # Dwarf planets
    "tm-mcp-ceres",
    "tm-mcp-pluto",
    "tm-mcp-haumea",
    "tm-mcp-makemake",
    "tm-mcp-eris",
    # Dwarf planet moons
    "tm-mcp-charon",
    "tm-mcp-styx",
    "tm-mcp-nix",
    "tm-mcp-kerberos",
    "tm-mcp-hydra",
    "tm-mcp-hiiaka",
    "tm-mcp-namaka",
    "tm-mcp-mk2",
    "tm-mcp-dysnomia",
]

EXAMPLE_CHANNEL_CODES = [
    "8908DC9F",
    "A7B3E2D1",
    "F4C9B6E8",
    "D2A8F1C5",
    "E6B9D3A2",
    "C5F8A1D7",
    "B9E4C7F2",
    "A3D6E9B4",
    "F1C8D5A6",
    "E7A2B9F3",
]


def prompt(message: str, default: Optional[str] = None, min_length: Optional[int] = None,
           exact_length: Optional[int] = None) -> str:
    """Prompt user for input with optional default value and validation."""
    while True:
        if default:
            result = input(f"{message} [{default}]: ").strip()
            result = result if result else default
        else:
            result = input(f"{message}: ").strip()
            if not result:
                print("  This field is required. Please enter a value.")
                continue

        # Validate exact length if specified
        if exact_length and len(result) != exact_length:
            print(f"  Value must be exactly {exact_length} characters long. Please try again.")
            continue

        # Validate minimum length if specified
        if min_length and len(result) < min_length:
            print(f"  Value must be at least {min_length} characters long. Please try again.")
            continue

        return result


def prompt_yes_no(message: str, default: bool = False) -> bool:
    """Prompt user for yes/no answer."""
    default_str = "Y/n" if default else "y/N"
    while True:
        result = input(f"{message} [{default_str}]: ").strip().lower()
        if not result:
            return default
        if result in ('y', 'yes'):
            return True
        if result in ('n', 'no'):
            return False
        print("  Please answer 'y' or 'n'")


def generate_env_file(config: dict) -> str:
    """Generate .env file content from configuration."""
    lines = [
        "# ------------------------------------------------------------------------------",
        "# TrendMiner Server Configuration",
        "# ------------------------------------------------------------------------------",
        f"TM_SERVER_URL={config['tm_server_url']}",
        "",
        "# ------------------------------------------------------------------------------",
        "# OAuth Authentication",
        "# ------------------------------------------------------------------------------",
        f"TM_MCP_AUTHORIZATION_SERVER={config['authorization_server']}",
        f"TM_MCP_RESOURCE_SERVER={config['resource_server']}",
        f"# TM_MCP_RESOURCE_SERVER=http://localhost:8765 # FastMCP",
        f"# TM_MCP_RESOURCE_SERVER=http://localhost:6080 # Inspectr Local",
    ]

    # Add credentials if provided
    if config.get('use_credentials'):
        lines.extend([
            "",
            "# ------------------------------------------------------------------------------",
            "# Credentials Mode (Optional - for local development without OAuth)",
            "# ------------------------------------------------------------------------------",
            f"TM_CLIENT_ID={config.get('tm_client_id', '')}",
            f"TM_CLIENT_SECRET={config.get('tm_client_secret', '')}",
            f"TM_USERNAME={config.get('tm_username', '')}",
            f"TM_PASSWORD={config.get('tm_password', '')}",
        ])

    return "\n".join(lines) + "\n"


def generate_inspectr_yaml(config: dict) -> str:
    """Generate .inspectr.yaml file content."""
    return f"""# Local Service Port
listen: ":6080"
# Fast MCP server
backend: "http://localhost:8765"
# Ingress Channel
expose: true
channel: "{config['channel_name']}"
channelCode: "{config['channel_code']}"
# App
appPort: 4567
# Command
command: uvx
commandArgs:
  - tm-mcp-server-preview
commandLogFile: log-mcp-sessions/tm-mcp-server-process.log
# Export
export: true
exportDir: log-mcp-sessions
"""


def run_setup() -> bool:
    """
    Run the interactive setup wizard.

    Returns True if setup completed successfully, False if cancelled.
    """
    print("\n" + "=" * 70)
    print("🚀 TrendMiner MCP Server - First-Time Setup")
    print("=" * 70)
    print("\nThis wizard will help you configure your TrendMiner MCP Server.")
    print("You can re-run this setup anytime with: uvx tm-mcp-server-preview --setup\n")

    config = {}

    # 1. TrendMiner Server URL
    print("\n📡 TrendMiner Server Configuration")
    print("-" * 70)
    config['tm_server_url'] = prompt(
        "TrendMiner Server URL",
        default="https://cs.trendminer.net"
    )

    # 2. Inspectr Configuration
    print("\n🌐 Inspectr Configuration")
    print("-" * 70)
    print("Inspectr provides a public URL for your MCP server.")
    print("Choose a unique channel name (min 8 characters, e.g., 'tm-mcp-saturn').")

    config['channel_name'] = prompt(
        "Channel name",
        default=random.choice(EXAMPLE_CHANNEL_NAMES),
        min_length=8
    )

    config['channel_code'] = prompt(
        "Channel code (exactly 8 characters)",
        default=random.choice(EXAMPLE_CHANNEL_CODES),
        exact_length=8
    )

    # 3. OAuth Configuration (auto-configured)
    # Use TrendMiner Server URL as Authorization Server (typically the same)
    config['authorization_server'] = config['tm_server_url']

    # Use channel name to construct resource server URL automatically
    config['resource_server'] = f"https://{config['channel_name']}.in-spectr.dev"

    # 4. Review and Confirm
    print("\n" + "=" * 70)
    print("📋 Configuration Summary")
    print("=" * 70)
    print(f"TrendMiner Server:     {config['tm_server_url']}")
    print(f"Authorization Server:  {config['authorization_server']}")
    print(f"Resource Server:       {config['resource_server']}")
    print(f"Inspectr Channel:      {config['channel_name']}")
    print(f"Inspectr Channel Code: {config['channel_code']}")
    print("=" * 70)

    if not prompt_yes_no("\nSave this configuration?", default=True):
        print("\n❌ Setup cancelled.")
        return False

    # 6. Write configuration files
    try:
        # Create .env file
        env_content = generate_env_file(config)
        Path(".env").write_text(env_content, encoding="utf-8")
        print("\n✅ Created .env file")

        # Create .inspectr.yaml file
        yaml_content = generate_inspectr_yaml(config)
        Path(".inspectr.yaml").write_text(yaml_content, encoding="utf-8")
        print("✅ Created .inspectr.yaml file")

        # Create log directory
        Path("log-mcp-sessions").mkdir(exist_ok=True)
        print("✅ Created log-mcp-sessions directory")

        print("\n" + "=" * 70)
        print("🎉 Setup Complete!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Run: npx @inspectr/inspectr")
        print("  2. Copy the config below to your Claude Desktop config file")
        print("\nClaude Desktop config snippet:")
        print("-" * 70)
        print(f"""{{
  "mcpServers": {{
    "trendminer": {{
      "command": "npx",
      "args": [
        "mcp-remote@0.1.37",
        "{config['resource_server']}/mcp",
        "--debug",
        "--static-oauth-client-info",
        "{{\\"client_id\\":\\"publicmcppreview\\"}}"
      ]
    }}
  }}
}}""")
        print("-" * 70)
        print("\nConfig file location:")
        print("  macOS/Linux: ~/Library/Application Support/Claude/claude_desktop_config.json")
        print("  Windows: %APPDATA%/Claude/claude_desktop_config.json")
        print("\nFor more information, see the README.md\n")

        return True

    except Exception as e:
        print(f"\n❌ Error writing configuration files: {e}")
        return False


def setup_cli():
    """CLI entry point for standalone setup command."""
    success = run_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    setup_cli()
