from spacedata.client import SpaceDataClient


async def test_apod(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("planetary_apod_200.json")

    respx_mock.get("https://api.nasa.gov/planetary/apod").respond(
        status_code=200, json=response_data
    )
    apods = await client.planetary.apod()
    assert len(await apods.as_list()) == 1
