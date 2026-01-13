from mark2pdf.postprocess.compile_overview import process


def test_compile_overview_basic():
    content = '<div className="overview">content</div>'
    expected = ":::{#overview}content:::"
    assert process(content) == expected


def test_compile_overview_mixed_divs():
    content = '<div className="overview"><div>inner</div></div>'
    expected = ":::{#overview}<div>inner</div>:::"
    assert process(content) == expected


def test_compile_overview_attribute_order():
    # This currently fails with the old regex
    content = '<div id="foo" className="overview">content</div>'
    expected = ":::{#overview}content:::"
    assert process(content) == expected


def test_compile_overview_spacing():
    content = '<div   className="overview"  >content</div>'
    expected = ":::{#overview}content:::"
    assert process(content) == expected


def test_compile_overview_nested_overview():
    content = '<div className="overview"><div className="overview">inner</div></div>'
    # Stack logic should handle this, though Pandoc might not like nested same-id divs.
    # The tool just converts syntax.
    expected = ":::{#overview}:::{#overview}inner::::::"
    assert process(content) == expected
