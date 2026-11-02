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

    ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg"}

    def __init__(self, data_root: Path) -> None:
        self.data_root = data_root.resolve()
        self.users_file = self.data_root / "users.json"

    def list_documents(self, user_id: str) -> list[DocumentMetadata]:
        workspace = self.get_user_workspace(user_id)
        documents: list[DocumentMetadata] = []

        for path in sorted(workspace.iterdir()):
            if not self.is_document_file(path):
                continue

            document_type = self.classify_document(path)
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
        workspace = self.get_user_workspace(user_id)
        path = self.get_document_path(workspace, filename)
        return path.read_text(encoding="utf-8")

    def get_user_workspace(self, user_id: str) -> Path:
        """Return the directory assigned to one user."""
        if not user_id or Path(user_id).name != user_id:
            raise WorkspaceError("Invalid user ID")

        user = self.find_user(user_id)
        if user is None:
            raise WorkspaceError(f"Unknown user: {user_id}")

        workspace = self.build_workspace_path(user["workspace"])
        if not workspace.is_dir():
            raise WorkspaceError(f"Workspace does not exist: {user_id}")
        return workspace

    def find_user(self, user_id: str) -> dict[str, str] | None:
        """Find a user in the registry."""
        try:
            users = json.loads(self.users_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise WorkspaceError("User registry is unavailable or invalid") from error

        return next((user for user in users if user.get("user_id") == user_id), None)

    def build_workspace_path(self, configured_path: str) -> Path:
        """Build a safe path inside data/users."""
        workspace = (self.data_root.parent / configured_path).resolve()
        users_directory = (self.data_root / "users").resolve()
        if workspace.parent != users_directory:
            raise WorkspaceError("User workspace is outside the configured users directory")
        return workspace

    def get_document_path(self, workspace: Path, filename: str) -> Path:
        """Return a valid document path inside a user workspace."""
        path = (workspace / filename).resolve()
        if path.parent != workspace:
            raise WorkspaceError("Document must be directly inside the user workspace")
        if not self.is_document_file(path):
            raise WorkspaceError(f"Unsupported or missing document: {filename}")
        if self.classify_document(path) is None:
            raise WorkspaceError(f"Unable to classify document: {filename}")
        return path

    @classmethod
    def is_document_file(cls, path: Path) -> bool:
        """Check whether a path is a supported file."""
        return path.is_file() and path.suffix.lower() in cls.ALLOWED_EXTENSIONS

    @staticmethod
    def classify_document(path: Path) -> str | None:
        """Classify a document using its first non-empty line."""
        try:
            first_line = next(
                line.strip().upper()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        except (OSError, UnicodeDecodeError, StopIteration):
            return None

        if first_line == "INVOICE":
            return "invoice"
        if first_line == "PURCHASE ORDER":
            return "purchase_order"
        if first_line == "SERVICE AND SUPPLY AGREEMENT":
            return "contract"
        return None
