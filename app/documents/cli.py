from __future__ import annotations

import argparse
from pathlib import Path

from app.documents.workspace import UserWorkspace


def main() -> None:
    parser = argparse.ArgumentParser(description="List documents in one user workspace")
    parser.add_argument("user_id", help="User ID from data/users.json")
    args = parser.parse_args()

    repository_root = Path(__file__).resolve().parents[2]
    workspace = UserWorkspace(repository_root / "data")
    for document in workspace.list_documents(args.user_id):
        print(f"{document.document_type}\t{document.filename}\t{document.size_bytes} bytes")


if __name__ == "__main__":
    main()
