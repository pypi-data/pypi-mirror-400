from spacedata.client import SpaceDataClient


async def test_neo_feed(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("neo_feed_200.json")
    respx_mock.get("https://api.nasa.gov/neo/rest/v1/feed").respond(
        status_code=200, json=response_data
    )

    neos = await client.neo.feed(start_date="2022-01-01", end_date="2022-01-02")
    assert len(await neos.as_list()) == 27


async def test_neo_browse(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("neo_browse_200.json")
    respx_mock.get("https://api.nasa.gov/neo/rest/v1/neo/browse").respond(
        status_code=200, json=response_data
    )

    neos = await client.neo.browse(limit=27)
    neos = await neos.as_list()
    assert len(neos) == 27


async def test_neo_lookup(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("neo_lookup_200.json")
    respx_mock.get("https://api.nasa.gov/neo/rest/v1/neo/3542519").respond(
        status_code=200, json=response_data
    )

    neo = await client.neo.lookup(asteroid_ids=[3542519])
    neo = await neo.as_list()
    assert neo[0].id == "3542519"
