from torch.utils.data import Dataset

from jcclang.tests.remotefile.driver import RemoteFile, LocalDriver, HTTPRangeDriver


def choose_driver(url: str):
    if url.startswith("file://"):
        return LocalDriver()
    elif url.startswith("http://") or url.startswith("https://"):
        return HTTPRangeDriver()
    else:
        raise ValueError(f"Unsupported URL: {url}")


class JCWeaverDataset(Dataset):
    def __init__(self, urls, transform=None):
        self.urls = urls
        self.transform = transform

    def __getitem__(self, idx):
        url = self.urls[idx]
        driver = choose_driver(url)
        f = RemoteFile(url, driver)
        raw = f.read()  # 可以顺序读/随机读
        f.close()
        return self.transform(raw) if self.transform else raw

    def __len__(self):
        return len(self.urls)
