import os
from uuid import UUID

import requests


class Data:
    payload: dict[str, str | int | None]
    meaningful_params: list[str]
    id_harvest: int | UUID
    bbox: list[list[float]] | None

    def __init__(
        self, id_harvest: None | int | UUID,
        payload: dict[str, str | int | None],
        meaningful_params: list[str],
        bbox: list[list[float]] | None = None
    ):
        self.payload = payload
        self.meaningful_params = meaningful_params
        self.id_harvest = id_harvest
        self.bbox = bbox

    def __repr__(self):
        """
        >>> Data(id_harvest=1, payload={"key":"payload"}, meaningful_params=["key"], bbox=[0,0,1,1])
        Data(id_harvest=1, payload="{'key': 'payload'}", bbox=[0, 0, 1, 1])
        """
        return f'Data(id_harvest={self.id_harvest}, payload="{ self.payload }", bbox={self.bbox})'

    @classmethod
    def dicts_to_datas(cls, datas: list[dict]) -> list["Data"]:
        return [cls(payload=data) if isinstance(data, str) else cls(**data) for data in datas]

    def to_dict(self):
        return self.__dict__


class OnegeoChatClient:
    def __init__(self, url: str, auth: tuple[str, str], csrf_cookie_name="onegeo-csrftokenchat"):
        self.url: str = url
        self.auth: tuple[str, str] = auth
        self.csrf_cookie_name = csrf_cookie_name
        self._set_csrf()

    def _set_csrf(self):
        self.session = requests.Session()
        complete_url = self.url + "/chat/api/connect/"

        # CSRF
        connect_resp = self.session.get(complete_url, auth=self.auth)
        connect_resp.raise_for_status()

        self.session.headers.update(
            {"Referer": self.url + "/chat/app", "X-CSRFToken": connect_resp.cookies[self.csrf_cookie_name]}
        )

    def delete_source(self, source_name: str, ignore_missing=True):
        path = "chat/api/document_source/"

        resp = self.session.get(os.path.join(self.url, path.lstrip("/")))
        resp.raise_for_status()

        sources = resp.json()

        source_id = None

        for source in sources:
            if source["name"] == source_name:
                source_id = source["id"]

        if source_id:
            resp = self.session.delete(os.path.join(self.url, path.lstrip("/"), str(source_id)))
            resp.raise_for_status()

    def delete_document(self, id_harvest: str, source_name: str):
        path = "chat/api/document/"

        resp = self.session.get(
            os.path.join(self.url, path.lstrip("/")), params={"source__name": source_name, "id_harvest": id_harvest}
        )

        resp.raise_for_status()
        documents = resp.json()

        for doc in documents:
            django_id = doc["id"]

            resp = self.session.delete(os.path.join(self.url, path.lstrip("/"), f"{django_id}/"))
            resp.raise_for_status()

    def load_bulk(self, datas: list[Data], append: bool = True, source_name=None, chunk_size=1024):
        """
        Inject several data with the semantic vector in Onegeo Chat database
        """
        path = "chat/api/load_docs/"

        for offset, chunk_i in ((i, datas[i : i + chunk_size]) for i in range(0, len(datas), chunk_size)):
            docs = {
                "data": [doc.to_dict() for doc in chunk_i],
                "append": append if offset == 0 else True,  # apply append value once, the other iterations must append
            }

            if source_name:
                docs["source_name"] = source_name

            resp = self.session.post(
                os.path.join(self.url, path.lstrip("/")),
                json=docs,
            )

            resp.raise_for_status()

    def bbox_to_wkt(self, bbox: list[list[float]]) -> str | None:
        """
        Convert bbox [[xmin,ymin],[xmin,ymax],[xmax,ymax],[xmax,ymin],[xmin,ymin]] into WKT POLYGON
        """
        if bbox:
            points_str = ", ".join(f"{x} {y}" for x, y in bbox)
            return f"POLYGON(({points_str}))"
        return None

    def load(self,
        doc: str,
        id: int | UUID,
        meaningful_params: list[str],
        bbox: list[list[float]] | None = None,
        append: bool = True,
        source_name=None
    ):
        """
        Inject single data with the semantic vector in Onegeo Chat database
        """
        path = "chat/api/load_docs/"

        docs = {
            "data": [
                {
                    "id": id,
                    "doc": doc,
                    "meaningful_params": meaningful_params,
                    "bbox": self.bbox_to_wkt(bbox)
                }
            ],
            "append": append
        }

        if source_name:
            docs["source_name"] = source_name

        resp = self.session.post(
            os.path.join(self.url, path.lstrip("/")),
            json=docs,
        )

        resp.raise_for_status()

    def get_documents(self, source_name: str=None):
            path = "chat/api/document/"

            resp = self.session.get(os.path.join(self.url, path.lstrip("/")))
            resp.raise_for_status()

            documents = resp.json()

            if source_name:
                return [doc for doc in documents if doc.get("source") == source_name]
            else:
                return documents
