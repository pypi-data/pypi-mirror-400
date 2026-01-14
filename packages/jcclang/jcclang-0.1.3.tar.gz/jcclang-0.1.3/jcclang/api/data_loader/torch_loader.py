from io import BytesIO

import torch
from torch.utils.data import Dataset as Ds

from jcclang.core.model import VirtualFileParams, Sources
from jcclang.virtualfile.virtual_file import VirtualFile


class Dataset(Ds):
    def __init__(self, sources: Sources, transform=None, decoder=None,
                 virtual_file_params: VirtualFileParams = None):
        if virtual_file_params is None:
            virtual_file_params = VirtualFileParams()
        self.virtual_file_params = virtual_file_params
        self.sources = sources
        self.transform = transform
        self.decoder = decoder or (lambda x: x)

    def __len__(self):
        return len(self.sources.items)

    def __getitem__(self, idx):
        info = self.sources.items[idx]

        # 读取数据
        vf = VirtualFile(info, params=self.virtual_file_params)
        raw = vf.read()
        vf.close()

        # 解码
        sample = self.decoder(raw)

        # transform
        if self.transform:
            sample = self.transform(sample)

        return sample, info.label


class JCWeaverModel:
    """
    通过 JCWeaver VirtualFile 加载模型权重，支持 PyTorch
    """

    def __init__(self, sources: Sources, virtual_file_params: VirtualFileParams = None):
        if virtual_file_params is None:
            virtual_file_params = VirtualFileParams()
        self.virtual_file_params = virtual_file_params
        self.sources = sources

    def load_state_dict(self, model_class, map_location="cpu"):
        """
        从 JCWeaver 读取模型数据，并加载到指定 PyTorch model_class
        """
        vf = VirtualFile(info, params=self.virtual_file_params)
        raw = vf.read()
        vf.close()

        buf = BytesIO(raw)
        state_dict = torch.load(buf, map_location=map_location)
        if isinstance(model_class, type):
            model = model_class()
        else:
            model = model_class
        model.load_state_dict(state_dict)
        return model

    def load_torch_model(self, map_location="cpu"):
        """
        直接读取 PyTorch 完整模型对象
        """
        vf = VirtualFile(info, params=self.virtual_file_params)
        raw = vf.read()
        vf.close()
        buf = BytesIO(raw)
        model = torch.load(buf, map_location=map_location)
        return model
