from google.cloud import firestore
import os


class database:
    def __init__(self, collection: str = None):
        if not os.getenv("PROJECT_ID"):
            print(f"[!] Database cannot be use [!]")
            print(f"{" PROJECT_ID not found ":=^40}")
            return
        self._db = firestore.Client(
            project=os.getenv("PROJECT_ID"),
            database=os.getenv('DATABASE_NAME'))
        self._collection = collection

    def read(self, collection: str = None) -> list:
        if not collection:
            collection = self._collection
        docs = self._db.collection(collection).stream()
        result = []
        for doc in docs:
            temp = {}
            temp[doc.id] = doc.to_dict()
            result.append(temp)
        return result

    def update(self, data: dict, document_id: str):
        doc_ref = self._db.collection(self._collection).document(document_id)
        doc_ref.update(data)
        return
