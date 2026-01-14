import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lindormmemobase import LindormMemobase, Config
from lindormmemobase.models.blob import ChatBlob, BlobType, OpenAICompatibleMessage

async def ingest_chat_dataset(
    config_path: str = "config.yaml",
    chat_path: str = "datasets/chat.json",
    project_id: Optional[str] = "test_project_1",
) -> None:
    # 1. Load config.yaml and initialize LindormMemobase (this also initializes storage & buffer tables)
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    config = Config.from_yaml_file(str(config_file))
    memobase = LindormMemobase(config)

    # 2. Load chat.json (contains user_id and messages)
    chat_file = Path(chat_path)
    if not chat_file.exists():
        raise FileNotFoundError(f"Chat dataset not found: {chat_file}")

    with chat_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    user_id = data["user_id"]
    messages = data.get("messages", [])
    total = len(messages)

    print(f"Loaded {total} messages from {chat_file} for user_id={user_id}")
    if project_id:
        print(f"Using project_id={project_id}")
    print()

    processed_batches = 0

    # 3. Insert messages one by one into buffer, and after each insert:
    #    - detect buffer full
    #    - if full, trigger process_buffer()
    for idx, msg in enumerate(messages, start=1):
        # Build OpenAICompatibleMessage from each entry
        chat_message = OpenAICompatibleMessage(
            role=msg["role"],
            content=msg["content"],
            created_at=msg.get("created_at"),
        )

        # Optionally map created_at to the blob-level timestamp
        created_at_dt: Optional[datetime] = None
        created_at_str = msg.get("created_at")
        if created_at_str:
            try:
                created_at_dt = datetime.fromisoformat(created_at_str)
            except ValueError:
                # If parsing fails, just leave created_at as None
                created_at_dt = None

        # Each message becomes a single ChatBlob
        blob = ChatBlob(
            messages=[chat_message],
            type=BlobType.chat,
            created_at=created_at_dt,
        )

        # Insert into buffer
        blob_id = await memobase.add_blob_to_buffer(
            user_id=user_id,
            blob=blob,
            project_id=project_id,
        )
        print(f"[{idx}/{total}] Inserted blob_id={blob_id}")

        # Detect whether buffer is full after this insert
        status = await memobase.detect_buffer_full_or_not(
            user_id=user_id,
            blob_type=BlobType.chat,
            project_id=project_id,
        )

        if status["is_full"]:
            buffer_ids = status["buffer_full_ids"]
            print(
                f"  Buffer is full: {len(buffer_ids)} blobs (type={status['blob_type']}). "
                f"Triggering process_buffer()..."
            )
            result = await memobase.process_buffer(
                user_id=user_id,
                blob_type=BlobType.chat,
                project_id=project_id,
            )
            processed_batches += 1

            if result:
                print(
                    f"  Batch #{processed_batches} processed: "
                    f"event_id={result.event_id}, "
                    f"add_profiles={len(result.add_profiles)}, "
                    f"update_profiles={len(result.update_profiles)}"
                )
            else:
                print(f"  Batch #{processed_batches} processed: no result returned")
            print()

    # 4. After all messages inserted, flush any remaining blobs in buffer
    print("All messages inserted. Running final process_buffer() to flush remaining blobs...")
    final_result = await memobase.process_buffer(
        user_id=user_id,
        blob_type=BlobType.chat,
        project_id=project_id,
    )

    if final_result:
        print(
            "Final processing done: "
            f"event_id={final_result.event_id}, "
            f"add_profiles={len(final_result.add_profiles)}, "
            f"update_profiles={len(final_result.update_profiles)}"
        )
    else:
        print("Final processing: no remaining blobs to process.")
    print("Ingestion finished.")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Ingest chat.json messages into buffer and trigger extraction."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml)",
    )
    parser.add_argument(
        "--input",
        type=str,
        default="datasets/chat.json",
        help="Path to chat.json (default: datasets/chat.json)",
    )
    parser.add_argument(
        "--project-id",
        type=str,
        default=None,
        help="Optional project_id for multi-tenancy",
    )

    args = parser.parse_args()

    asyncio.run(
        ingest_chat_dataset(
            config_path=args.config,
            chat_path=args.input,
            project_id=args.project_id,
        )
    )


if __name__ == "__main__":
    main()