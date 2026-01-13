import requests
from requests.auth import HTTPBasicAuth
from typing import Dict
import os

from loguru import logger


class WOS:
    def __init__(self, bucket: str, app_id: str, secret_id: str):
        super().__init__()
        self.bucket = bucket
        self.app_id = app_id
        self.secret_id = secret_id
        self.upload_url = f"http://wosin14.58corp.com/{self.app_id}/{self.bucket}"
        self.base_url = f"http://wosin14.58corp.com/{self.app_id}/{self.bucket}"

    def get_token(self, file_name: str) -> str:
        token_server = "http://token.wos.58dns.org"
        auth = HTTPBasicAuth(self.app_id, self.secret_id)
        headers = {
            "host": "token.wos.58dns.org",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"bucket": self.bucket, "filename": file_name}
        res = requests.get(
            url=token_server + "/get_token", headers=headers, auth=auth, params=data
        )
        return res.json()["data"]

    def upload_slice_init(self, filename: str, file_path: str) -> Dict[str, str]:
        token = self.get_token(filename)
        headers = {"Authorization": token}
        filesize = os.path.getsize(file_path)
        data = {
            "op": "upload_slice_init",
            "filesize": filesize,
            "slice_size": 4194304,
        }
        res = requests.post(
            url=self.base_url + f"/{filename}",
            data=data,
            headers=headers,
        )
        res = res.json()
        if "data" not in res:
            raise Exception(f"upload failed: {res['message']}")
        return res["data"]

    def upload_slice_data(
        self, filename: str, file_path: str, slice_config: Dict
    ) -> Dict[str, str]:
        token = self.get_token(filename)
        headers = {"Authorization": token}
        filesize = os.path.getsize(file_path)
        session = slice_config["session"]
        slice_size = int(slice_config["slice_size"])
        with open(file_path, mode="rb") as f:
            offset = 0
            while offset < filesize:
                f.seek(offset)
                chunk = f.read(slice_size)
                if not chunk:
                    break

                files = {"filecontent": (filename, chunk, "application/octet-stream")}
                data = {
                    "op": "upload_slice_data",
                    "session": session,
                    "offset": offset,
                }

                res = requests.post(
                    url=self.base_url + f"/{filename}",
                    data=data,
                    files=files,
                    headers=headers,
                )
                res = res.json()
                if "data" not in res:
                    raise Exception(f"upload failed: {res['message']}")
                offset += slice_size
        return

    def upload_slice_finish(
        self, filename: str, file_path: str, slice_config: Dict
    ) -> Dict[str, str]:
        token = self.get_token(filename)
        headers = {"Authorization": token}
        filesize = os.path.getsize(file_path)
        session = slice_config["session"]

        data = {
            "op": "upload_slice_finish",
            "session": session,
            "filesize": filesize,
        }

        res = requests.post(
            url=self.base_url + f"/{filename}",
            data=data,
            headers=headers,
        )
        res = res.json()
        if "data" not in res:
            raise Exception(f"upload failed: {res['message']}")
        return res["data"]

    def upload_large_file(self, filename: str, file_path: str) -> Dict[str, str]:
        slice_cfg = self.upload_slice_init(filename, file_path)
        res = self.upload_slice_data(filename, file_path, slice_cfg)
        res = self.upload_slice_finish(filename, file_path, slice_cfg)
        return res

    def upload(self, filename: str, file_path: str) -> Dict[str, str]:
        token = self.get_token(filename)
        headers = {"Authorization": token}
        with open(file_path, mode="rb") as f:
            files = {"filecontent": (filename, f, "application/octet-stream")}
            data = {"op": "upload"}
            res = requests.post(
                url=self.base_url + f"/{filename}",
                data=data,
                files=files,
                headers=headers,
            )
            res = res.json()
            if "data" not in res:
                raise Exception(f"upload failed: {res['message']}")
        return res["data"]

    def delete(self, filename: str):
        token = self.get_token(filename)
        headers = {"Authorization": token}
        res = requests.post(
            url=self.base_url + f"/{filename}?op=delete&cdn=del",
            headers=headers,
        )
        res = res.json()
        if res["code"] != 0:
            raise Exception(f"delete failed: {res['message']}")
        logger.info(f"delete {filename} success")
