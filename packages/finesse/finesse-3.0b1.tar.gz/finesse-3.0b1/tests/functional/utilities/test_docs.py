import pytest

from finesse.utilities.docs import class_to_url, get_docs_url
from finesse.components import Mirror


def test_get_docs_url():
    assert get_docs_url() == "https://finesse.ifosim.org/docs/"


def test_class_to_url():
    import finesse

    if ".dev" in finesse.__version__:
        version = "develop"
    else:
        version = finesse.__version__
    assert (
        class_to_url(Mirror)
        == f"https://finesse.ifosim.org/docs/{version}/api/components/mirror/finesse.components.mirror.Mirror.html"
    )


def test_class_to_url_no_finesse_class():
    with pytest.raises(ValueError):
        class_to_url(int)
