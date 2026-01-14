from torch.utils.data import DataLoader

from jcweaver_dataset import JCWeaverDataset


def decode_text(raw: bytes):
    return raw.decode("utf-8")


# 用户只要传 URL，不关心底层是本地还是 HTTP
urls = [
    # "file://D:\Work\Codes\workspace\JCWeaver\doc\发布流程.md",
    "http://121.36.5.116:32010/object/download?userID=5&objectID=157109"
]

dataset = JCWeaverDataset(urls, transform=decode_text)
loader = DataLoader(dataset, batch_size=1)


def test_pt_demo():
    for batch in loader:
        print("Got batch:", batch)
