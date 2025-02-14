from dataclasses import asdict, dataclass
from google.cloud import firestore
from datetime import datetime, timezone
import os


@dataclass
class Data:
    url: str
    updateAt: datetime

    def __post_init__(self):
        if self.updateAt.tzinfo is None or self.updateAt.tzinfo.utcoffset(self.updateAt) is None:
            raise ValueError(
                "Error: 'updateAt' must be in UTC (timezone-aware)")


def GCP_Credentials() -> bool:
    keywords = ["google", "gcp"]
    print("Checking Google Credentials...")
    if (os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is not None):
        return True

    print("Checking current directory.")
    print(f"Checking keywords {keywords}")
    json_file = [f for f in os.listdir(".") if f.endswith(".json")]
    filtered_json = [f for f in json_file if any(
        keyword in f.lower() for keyword in keywords)]

    if len(filtered_json) > 0 and len(filtered_json) == 1:
        print(f"Found {filtered_json[0]}.")
        creds_path = os.path.abspath(filtered_json[0])
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        return True
    elif len(filtered_json) > 1:
        print(f"Error: Found multiple candidate for 'GOOGLE_APPLICATION_CREDENTIALS'.")
        print(
            f"Please check the file name not containing the following keywords {keywords}.")
        print(f"Note: This function only check for file extension '.json'")
        return False
    else:
        print(f"Error: Could not found candidate for 'GOOGLE_APPLICATION_CREDENTIALS'.")
        return False


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

    def fetch_webhook(self) -> list[dict]:
        if not self._collection:
            print("Error: Collection is not defined.")
            return

        docs = self._db.collection(self._collection).stream()
        result = []
        for doc in docs:
            data = doc.to_dict()
            if not data.get('updateAt') or data.get('updateAt') <= datetime.now(timezone.utc):
                result.append({"id": doc.id, "url": data.get('url')})
                continue

        return result
