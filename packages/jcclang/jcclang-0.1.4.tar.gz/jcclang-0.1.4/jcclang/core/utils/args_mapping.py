def param_mapping(key: str) -> str:
    if key == "package_name":
        return "PackageName"
    elif key == "output":
        return "Output"
    elif key == "platform":
        return "ClusterID"

    return key
