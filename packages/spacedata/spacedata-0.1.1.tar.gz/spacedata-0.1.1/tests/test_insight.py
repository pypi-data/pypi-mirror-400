from spacedata.client import SpaceDataClient


async def test_insight_mars_weather(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("insight_mars_weather_200.json")

    respx_mock.get("https://api.nasa.gov/insight_weather/").respond(
        status_code=200, json=response_data
    )

    result = await client.insight.mars_weather()
    items = await result.as_list()
    weather = items[0]

    assert weather is not None
    assert "675" in weather.sol_keys
    assert weather.get_sol("675").season == "fall"
    assert weather.validity_checks.sol_hours_required == 18
