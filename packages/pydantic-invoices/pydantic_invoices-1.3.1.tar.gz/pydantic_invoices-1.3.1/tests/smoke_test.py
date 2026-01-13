from pydantic_invoices import __version__

def test_import():
    assert __version__ is not None
    print(f"pydantic_invoices version: {__version__}")

if __name__ == "__main__":
    test_import()
