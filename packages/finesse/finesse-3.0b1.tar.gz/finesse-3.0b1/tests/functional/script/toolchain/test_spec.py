"""KatScript specification tests."""


def test_register_element(spec, fake_element_adapter_factory, fake_element_cls):
    adapter = fake_element_adapter_factory(fake_element_cls)

    assert adapter.full_name not in spec.elements
    spec.register_element(adapter)
    assert adapter.full_name in spec.elements
