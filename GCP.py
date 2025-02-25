from dataclasses import asdict, dataclass
from typing import Optional
from google.cloud import firestore
from datetime import datetime, timezone
import os


@dataclass
class Data:
    url: str
    updateAt: Optional[datetime]

    def __post_init__(self):
        if self.updateAt is None:
            print("Note: updateAt has value 'None'.")
            return

        if self.updateAt.tzinfo is None or self.updateAt.tzinfo.utcoffset(self.updateAt) is None:
            raise ValueError(
                "Error: 'updateAt' must be in UTC (timezone-aware)")


def GCP_Credentials() -> bool:
    keywords = ["google", "gcp"]
    if (os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is not None):
        return True

    json_file = [f for f in os.listdir(".") if f.endswith(".json")]
    filtered_json = [f for f in json_file if any(
        keyword in f.lower() for keyword in keywords)]

    # Error checking
    if len(filtered_json) > 0 and len(filtered_json) == 1:
        print(f"Found {filtered_json[0]}.")
        creds_path = os.path.abspath(filtered_json[0])
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        return True
    elif len(filtered_json) > 1:
        print(f"{"_"*40}\n")

        print(f"Error: Found multiple candidate for 'GOOGLE_APPLICATION_CREDENTIALS'.")
        print(
            f"Please check the file name not containing the following keywords {keywords}.")
        print(f"Note: This function only check for file extension '.json'")
        return False
    else:
        print(f"{"_"*40}\n")

        print(f"Error: Could not found candidate for 'GOOGLE_APPLICATION_CREDENTIALS'.")
        print(
            f"Please check if file contain the following keywords {keywords}.")
        return False


class database:
    def __init__(self, collection: str = None):
        if os.getenv("PROJECT_ID") is None or os.getenv("DATABASE_NAME") is None:
            print("Error: Please check your '.env' file.")
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
            doc_dict = doc.to_dict()
            temp[doc.id] = asdict(
                Data(doc_dict.get("url"), doc_dict.get("updateAt")))
            result.append(temp)
        return result

    def update(self, data: dict, document_id: str, collection: str = None):
        doc_ref = self._db.collection(
            self._collection if not collection else collection
        ).document(document_id)
        doc_ref.update(data)
        return
