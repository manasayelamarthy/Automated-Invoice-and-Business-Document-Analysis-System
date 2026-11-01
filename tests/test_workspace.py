from pathlib import Path
import unittest

from app.documents.workspace import UserWorkspace, WorkspaceError


class UserWorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        self.workspace = UserWorkspace(repository_root / "data")

    def test_lists_only_classified_documents_for_user(self) -> None:
        documents = self.workspace.list_documents("user_001")

        self.assertEqual(len(documents), 7)
        self.assertEqual(
            {document.document_type for document in documents},
            {"invoice", "purchase_order", "contract"},
        )
        self.assertTrue(all(document.user_id == "user_001" for document in documents))

    def test_reads_document_from_requested_user_workspace(self) -> None:
        content = self.workspace.read_document("user_001", "invoice_inv_1001.txt")

        self.assertIn("Invoice Number: INV-1001", content)

    def test_rejects_unknown_user(self) -> None:
        with self.assertRaises(WorkspaceError):
            self.workspace.list_documents("user_999")

    def test_rejects_cross_workspace_path(self) -> None:
        with self.assertRaises(WorkspaceError):
            self.workspace.read_document("user_001", "../user_002/invoice_inv_1001.txt")


if __name__ == "__main__":
    unittest.main()
