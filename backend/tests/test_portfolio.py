from backend.models import PortfolioModel


def test_portfolio_schema_keys():
    schema = PortfolioModel.get_schema()

    assert "experiences" in schema
    assert "education" not in schema
    assert "achievements" not in schema
    assert isinstance(schema["experiences"]["fields"], list)
