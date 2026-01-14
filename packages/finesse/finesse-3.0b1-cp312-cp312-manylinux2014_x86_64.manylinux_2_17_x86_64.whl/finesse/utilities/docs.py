from importlib.metadata import metadata

import finesse


def class_to_url(cls: type) -> str:
    """Get the api page for a finesse class. Always points to the latest release
    version

    Parameters
    ----------
    cls : type
        A class defined in |Finesse|

    Returns
    -------
    str
        The url to the api documentation page
    """
    modules = cls.__module__.split(".")
    if modules[0] != "finesse":
        raise ValueError(f"Class {cls} is not a finesse cls")
    folder = "/".join(modules[1:])
    name = cls.__module__ + "." + cls.__name__
    if ".dev" in finesse.__version__:
        version = "develop"
    else:
        version = finesse.__version__
    base = f"{get_docs_url()}{version}/api/"
    url = base + folder + "/" + name + ".html"
    return url


def get_docs_url() -> str:
    """Retrieves the documentation URL from the Finesse package metadata

    Returns
    -------
    str
        documentation url
    """
    # unfortunately stored as a list
    project_urls = metadata("finesse").json["project_url"]
    docs_url = None
    for url in project_urls:
        if "documentation" in url.lower():
            docs_url = url
    if docs_url is None:
        raise ValueError("Documentation url not found")
    docs_url = docs_url.split()[-1]
    if docs_url.endswith("/"):
        return docs_url
    else:
        return docs_url + "/"
