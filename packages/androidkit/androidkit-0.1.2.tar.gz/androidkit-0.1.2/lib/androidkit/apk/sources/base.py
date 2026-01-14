from abc import ABCMeta, abstractmethod


class Source(metaclass=ABCMeta):
    @abstractmethod
    def get_download_url(self, package_name: str, version: str) -> str:
        ...

    @abstractmethod
    def search(self, keyword: str, limit: int) -> list[dict]:
        ...
