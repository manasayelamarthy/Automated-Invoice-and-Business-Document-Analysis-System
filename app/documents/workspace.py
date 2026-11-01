from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


class WorkspaceError(ValueError):
    """Raised when a user workspace cannot be resolved safely."""


@dataclass(frozen=True)
class DocumentMetadata:
    document_id: str
    filename: str
    document_type: str
    user_id: str
    path: Path
    size_bytes: int


class UserWorkspace:
    """Read-only access to one user's document workspace."""

    SUPPORTED_DOCUMENT_TYPES = frozenset({"invoice", "purchase_order", "contract"})
    DOCUMENT_EXTENSIONS = frozenset({".txt", ".pdf", ".png", ".jpg", ".jpeg"})

    def __init__(self, data_root: Path) -> None:
        self.data_root = data_root.resolve()
        self.users_file = self.data_root / "users.json"

    def list_documents(self, user_id: str) -> list[DocumentMetadata]:
        workspace = self._resolve_workspace(user_id)
        documents: list[DocumentMetadata] = []

        for path in sorted(workspace.iterdir()):
            if not path.is_file() or path.suffix.lower() not in self.DOCUMENT_EXTENSIONS:
                continue

            document_type = self._classify_document(path)
            if document_type is None:
                continue

            documents.append(
                DocumentMetadata(
                    document_id=path.stem,
                    filename=path.name,
                    document_type=document_type,
                    user_id=user_id,
                    path=path,
                    size_bytes=path.stat().st_size,
                )
            )

        return documents

    def read_document(self, user_id: str, filename: str) -> str:
        workspace = self._resolve_workspace(user_id)
        path = (workspace / filename).resolve()
        if path.parent != workspace:
            raise WorkspaceError("Document must be directly inside the user workspace")
        if not path.is_file() or path.suffix.lower() not in self.DOCUMENT_EXTENSIONS:
            raise WorkspaceError(f"Unsupported or missing document: {filename}")
        if self._classify_document(path) is None:
            raise WorkspaceError(f"Unable to classify document: {filename}")
        return path.read_text(encoding="utf-8")

    def _resolve_workspace(self, user_id: str) -> Path:
        if not user_id or Path(user_id).name != user_id:
            raise WorkspaceError("Invalid user ID")

        try:
            users = json.loads(self.users_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise WorkspaceError("User registry is unavailable or invalid") from error

        user = next((entry for entry in users if entry.get("user_id") == user_id), None)
        if user is None:
            raise WorkspaceError(f"Unknown user: {user_id}")

        configured_path = Path(user["workspace"])
        workspace = (self.data_root.parent / configured_path).resolve()
        if workspace.parent != (self.data_root / "users").resolve():
            raise WorkspaceError("User workspace is outside the configured users directory")
        if not workspace.is_dir():
            raise WorkspaceError(f"Workspace does not exist: {user_id}")
        return workspace

    def _classify_document(self, path: Path) -> str | None:
        try:
            first_line = path.read_text(encoding="utf-8").splitlines()[0].strip().upper()
        except (OSError, UnicodeDecodeError, IndexError):
            return None

        if first_line == "INVOICE":
            return "invoice"
        if first_line == "PURCHASE ORDER":
            return "purchase_order"
        if first_line == "SERVICE AND SUPPLY AGREEMENT":
            return "contract"
        return None
