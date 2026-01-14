import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to Python path to import lindormmemobase
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lindormmemobase import LindormMemobase, Config


async def get_all_profiles(
    config_path: str = "config.yaml",
    user_id: str = None,
    project_id: Optional[str] = None,
    output_path: Optional[str] = None,
) -> None:
    """
    Retrieve all user profiles for a given user_id.
    
    Args:
        config_path: Path to config.yaml file
        user_id: User ID to retrieve profiles for
        project_id: Optional project ID for multi-tenancy filtering
        output_path: Optional path to save profiles as JSON file
    """
    # Load config and initialize LindormMemobase
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    config = Config.from_yaml_file(str(config_file))
    memobase = LindormMemobase(config)

    # Retrieve all user profiles
    print(f"Retrieving profiles for user_id={user_id}")
    if project_id:
        print(f"Filtering by project_id={project_id}")
    print()

    profiles = await memobase.get_user_profiles(
        user_id=user_id,
        project_id=project_id
    )

    print(f"✓ Retrieved {len(profiles)} profile topics\n")
    print("=" * 80)

    # Display profiles
    for idx, profile in enumerate(profiles, start=1):
        print(f"\n[Topic {idx}] {profile.topic}")
        print("-" * 80)
        
        for subtopic_name, entry in profile.subtopics.items():
            print(f"\n  Subtopic: {subtopic_name}")
            print(f"  Content: {entry.content}")
            
            # Display metadata if available
            if hasattr(entry, 'created_at') and entry.created_at:
                print(f"  Created: {entry.created_at}")
            if hasattr(entry, 'updated_at') and entry.updated_at:
                print(f"  Updated: {entry.updated_at}")
            if hasattr(entry, 'update_hits') and entry.update_hits:
                print(f"  Update hits: {entry.update_hits}")
    
    print("\n" + "=" * 80)

    # Save to JSON file if output path is specified
    if output_path:
        output_data = []
        for profile in profiles:
            topic_data = {
                "topic": profile.topic,
                "subtopics": {}
            }
            
            for subtopic_name, entry in profile.subtopics.items():
                topic_data["subtopics"][subtopic_name] = {
                    "content": entry.content,
                    "created_at": entry.created_at.isoformat() if hasattr(entry, 'created_at') and entry.created_at else None,
                    "updated_at": entry.updated_at.isoformat() if hasattr(entry, 'updated_at') and entry.updated_at else None,
                    "update_hits": entry.update_hits if hasattr(entry, 'update_hits') else 0,
                }
            
            output_data.append(topic_data)
        
        output_file = Path(output_path)
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Profiles saved to {output_path}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Retrieve all user profiles from LindormMemobase."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml)",
    )
    parser.add_argument(
        "--user-id",
        type=str,
        required=True,
        help="User ID to retrieve profiles for (required)",
    )
    parser.add_argument(
        "--project-id",
        type=str,
        default=None,
        help="Optional project ID for filtering (default: None, retrieves all projects)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional output path to save profiles as JSON (default: None, display only)",
    )

    args = parser.parse_args()

    asyncio.run(
        get_all_profiles(
            config_path=args.config,
            user_id=args.user_id,
            project_id=args.project_id,
            output_path=args.output,
        )
    )


if __name__ == "__main__":
    main()
