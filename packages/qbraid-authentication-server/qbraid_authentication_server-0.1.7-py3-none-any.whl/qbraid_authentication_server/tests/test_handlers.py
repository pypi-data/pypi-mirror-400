import json


async def test_get_config(jp_fetch):
    """Test the get config endpoint"""
    response = await jp_fetch("qbraid-authentication-server", "qbraid-config")

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "apiKey": None,
        "url": None
    }
