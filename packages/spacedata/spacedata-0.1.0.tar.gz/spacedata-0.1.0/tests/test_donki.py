from spacedata.client import SpaceDataClient


async def test_donki_cme(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("donki_cme_200.json")
    respx_mock.get("https://api.nasa.gov/DONKI/CME").respond(
        status_code=200, json=response_data
    )

    cmes = await client.donki.cme(start_date="2022-01-01", end_date="2022-01-02")
    cmes = await cmes.as_list()
    assert len(cmes) == 18


async def test_donki_cme_analysis(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("donki_cme_analysis_200.json")
    respx_mock.get("https://api.nasa.gov/DONKI/CMEAnalysis").respond(
        status_code=200, json=response_data
    )

    cmes = await client.donki.cme_analysis(
        start_date="2022-01-01", end_date="2022-01-02"
    )
    cmes = await cmes.as_list()
    assert len(cmes) == 2


async def test_donki_gst(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("donki_gst_200.json")
    respx_mock.get("https://api.nasa.gov/DONKI/GST").respond(
        status_code=200, json=response_data
    )

    gsts = await client.donki.gst(start_date="2016-01-21", end_date="2016-01-21")
    gsts = await gsts.as_list()
    assert len(gsts) == 1
    assert gsts[0].gst_id == "2016-01-21T03:00:00-GST-001"


async def test_donki_ips(client: SpaceDataClient, respx_mock, load_json):
    # Use a single day to avoid split_weekday_ranges behavior of making multiple calls
    date_str = "2016-01-09"
    response_data = load_json("donki_ips_200.json")
    respx_mock.get("https://api.nasa.gov/DONKI/IPS").respond(
        status_code=200,
        json=[response_data[0]],  # Only the first one matches this date
    )

    ips_list = await client.donki.ips(start_date=date_str, end_date=date_str)
    ips_list = await ips_list.as_list()
    assert len(ips_list) == 1
    assert ips_list[0].activity_id == "2016-01-09T18:00:00-IPS-001"
    assert ips_list[0].location == "STEREO A"


async def test_donki_flr(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("donki_flr_200.json")
    respx_mock.get("https://api.nasa.gov/DONKI/FLR").respond(
        status_code=200, json=response_data
    )

    flares = await client.donki.flr(start_date="2016-01-01", end_date="2016-01-01")
    flares = await flares.as_list()
    assert len(flares) == 2
    assert flares[0].flr_id == "2016-01-01T23:10:00-FLR-001"
    assert flares[0].class_type == "M2.3"
    assert flares[1].flr_id == "2016-01-28T11:48:00-FLR-001"
    assert flares[1].class_type == "C9.6"


async def test_donki_sep(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("donki_sep_200.json")
    respx_mock.get("https://api.nasa.gov/DONKI/SEP").respond(
        status_code=200, json=response_data
    )

    seps = await client.donki.sep(start_date="2016-01-02", end_date="2016-01-02")
    seps = await seps.as_list()
    assert len(seps) == 2
    assert seps[0].sep_id == "2016-01-02T02:48:00-SEP-001"
    assert seps[1].sep_id == "2016-01-02T04:30:00-SEP-001"


async def test_donki_mpc(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("donki_mpc_200.json")
    respx_mock.get("https://api.nasa.gov/DONKI/MPC").respond(
        status_code=200, json=response_data
    )

    mpcs = await client.donki.mpc(start_date="2016-03-06", end_date="2016-03-06")
    mpcs = await mpcs.as_list()
    assert len(mpcs) == 2
    assert mpcs[0].mpc_id == "2016-03-06T16:32:00-MPC-001"
    assert mpcs[1].mpc_id == "2016-03-11T13:00:00-MPC-001"


async def test_donki_rbe(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("donki_rbe_200.json")
    respx_mock.get("https://api.nasa.gov/DONKI/RBE").respond(
        status_code=200, json=response_data
    )

    rbes = await client.donki.rbe(start_date="2016-01-02", end_date="2016-01-02")
    rbes = await rbes.as_list()
    assert len(rbes) == 2
    assert rbes[0].rbe_id == "2016-01-02T12:25:00-RBE-001"
    assert rbes[1].rbe_id == "2016-01-24T15:05:00-RBE-001"


async def test_donki_hss(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("donki_hss_200.json")
    respx_mock.get("https://api.nasa.gov/DONKI/HSS").respond(
        status_code=200, json=response_data
    )

    hss_list = await client.donki.hss(start_date="2016-01-11", end_date="2016-01-11")
    hss_list = await hss_list.as_list()
    assert len(hss_list) == 2
    assert hss_list[0].hss_id == "2016-01-11T12:00:00-HSS-001"
    assert hss_list[1].hss_id == "2016-01-21T10:00:00-HSS-001"


async def test_donki_wsa(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("donki_wsa_200.json")
    respx_mock.get("https://api.nasa.gov/DONKI/WSAEnlilSimulations").respond(
        status_code=200, json=response_data
    )

    wsa_list = await client.donki.wsa(start_date="2016-01-06", end_date="2016-01-06")
    wsa_list = await wsa_list.as_list()
    assert len(wsa_list) == 2
    assert wsa_list[0].simulation_id == "WSA-ENLIL/10003/1"
    assert wsa_list[1].simulation_id == "WSA-ENLIL/10005/1"
    assert len(wsa_list[1].cme_inputs) == 1
    assert wsa_list[1].cme_inputs[0].cmeid == "2016-01-06T14:24:00-CME-001"


async def test_donki_notifications(client: SpaceDataClient, respx_mock, load_json):
    response_data = load_json("donki_notifications_200.json")
    respx_mock.get("https://api.nasa.gov/DONKI/notifications").respond(
        status_code=200, json=response_data
    )

    notifications = await client.donki.notifications(
        start_date="2014-05-08", end_date="2014-05-08"
    )
    notifications = await notifications.as_list()
    assert len(notifications) == 3
    assert notifications[0].message_id == "20140508-AL-002"
    assert notifications[0].message_type == "FLR"
    assert "M5.2 Flare" in notifications[0].message_body
