from .modelarts import ModelArtsAdapter
from .octopus import OctopusAdapter
from .openi import OpenIAdapter
from ..core.const import Platform
from ..core.logger import jcwLogger


def get_adapter(platform: str):
    platform = platform.lower()
    if platform == Platform.MODELARTS:
        return ModelArtsAdapter()
    elif platform == Platform.OPENI:
        return OpenIAdapter()
    elif platform == Platform.OCTOPUS:
        return OctopusAdapter()
    jcwLogger.error(f"Unsupported platform: {platform}")
    return None
