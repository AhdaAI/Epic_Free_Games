from dataclasses import asdict, dataclass
from google.cloud import firestore
from datetime import datetime, timezone
import os


@dataclass
class DocumentData:
    id: str
    url: str

    def to_dict(self):
        return asdict(self)


class database:
    def __init__(self, collection: str = None):
        if not os.getenv("PROJECT_ID"):
            print(f"[!] Database cannot be use [!]")
            print(f"{" PROJECT_ID not found ":=^40}")
            return None
        self._db = firestore.Client(
            project=os.getenv("PROJECT_ID"),
            database=os.getenv('DATABASE_NAME'))
        self._collection = collection

    def read(self, collection: str = None) -> list[dict]:
        if not collection:
            collection = self._collection
        docs = self._db.collection(collection).stream()
        result = []
        for doc in docs:
            temp = {}
            temp[doc.id] = doc.to_dict()
            result.append(temp)
        return result

    def update(self, data: dict, document_id: str, collection: str = None):
        doc_ref = self._db.collection(
            self._collection if not collection else collection
        ).document(document_id)
        doc_ref.update(data)
        return

    def fetch_webhook(self) -> list[DocumentData]:
        if not self._collection:
            print("Error: Collection is not defined.")
            return

        docs = self._db.collection(self._collection).stream()
        result = []
        for doc in docs:
            data = doc.to_dict()
            if not data.get('update_on') or data.get('update_on') <= datetime.now(timezone.utc):
                result.append(DocumentData(doc.id, data.get('url')).to_dict())
                continue

        return result
