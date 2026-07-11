from backend.models import PortfolioModel


def test_portfolio_schema_keys():
    schema = PortfolioModel.get_schema()

    assert "education" in schema
    assert "experiences" in schema
    assert isinstance(schema["education"]["fields"], list)
