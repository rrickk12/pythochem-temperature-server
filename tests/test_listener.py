def test_parse_payload():
    from utils import parser
    sample_payload = {"sensor": "value", "timestamp": "2025-04-14T12:00:00"}
    result = parser.parse_payload(sample_payload)
    assert result == sample_payload, "O parser não retornou o dicionário conforme esperado"
