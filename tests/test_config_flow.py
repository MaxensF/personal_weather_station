"""Config and options flows, and removing a station."""

import pathlib

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr
from homeassistant.setup import async_setup_component

from custom_components.personal_weather_station import (
    async_ensure_views,
    async_remove_config_entry_device,
    config_flow,
)
from custom_components.personal_weather_station.const import (
    CONF_AVAILABILITY_TIMEOUT,
    CONF_WIND_OFFSETS,
    DOMAIN,
    IMAGES_URL,
)

from .conftest import WSLINK_ENDPOINT, device_for, state_of

DEVICE_ID = "wsabcde123"


def test_every_walkthrough_step_has_its_screenshot():
    """
    A missing file would leave a broken image in the wizard and nothing else.

    Nothing at runtime notices: the static route just answers 404, the flow
    still works, and the user sees an empty box where the screen they are
    looking for should be.
    """

    images = pathlib.Path(config_flow.__file__).parent / "images"

    missing = [
        name
        for name in config_flow.WALKTHROUGH.values()
        if not (images / name).is_file()
    ]

    assert not missing, missing


async def _walk_to_the_wait(hass, client_factory, password="s3cr3t", upload=None):
    """Drive the wizard from the first screen to the point where it waits."""

    assert await async_setup_component(hass, "http", {})

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_PASSWORD: password} if password else {}
    )

    for step in ("station", "settings", "server", "form", "confirm"):
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == step

        # Every walkthrough screen carries its screenshot.
        assert IMAGES_URL in result["description_placeholders"]["image"]

        if upload is not None and step == upload:
            client = await client_factory()
            assert (
                await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&wspw={password}")
            ).status == 200

        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})

    return result


async def test_the_wizard_waits_for_the_first_upload(
    hass, hass_client_no_auth, monkeypatch
):
    """The whole point of the walkthrough: end it by seeing the station arrive."""

    result = await _walk_to_the_wait(hass, hass_client_no_auth)

    assert result["type"] == FlowResultType.SHOW_PROGRESS
    assert result["progress_action"] == "waiting_for_station"

    client = await hass_client_no_auth()
    response = await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&wspw=s3cr3t")

    # Answered 200 even though no entry exists yet: a station told the upload
    # failed may stop trying.
    assert response.status == 200

    await hass.async_block_till_done()

    result = await hass.config_entries.flow.async_configure(result["flow_id"])
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "received"
    assert result["description_placeholders"]["station"] == DEVICE_ID

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_PASSWORD: "s3cr3t"}


async def test_a_station_configured_early_is_not_missed(hass, hass_client_no_auth):
    """
    These stations drop off Wi-Fi if you dawdle, so users configure them fast.

    The endpoints are live from the first screen of the wizard, not from the
    wait, so an upload that lands while the user is still reading still counts.
    """

    result = await _walk_to_the_wait(hass, hass_client_no_auth, upload="settings")

    # The sighting was already recorded, so the wait is over before it starts.
    while result["type"] == FlowResultType.SHOW_PROGRESS:
        await hass.async_block_till_done()
        result = await hass.config_entries.flow.async_configure(result["flow_id"])

    assert result["step_id"] == "received"


async def test_the_wizard_gives_up_and_still_keeps_the_setup(
    hass, hass_client_no_auth, monkeypatch
):
    """A timeout must not throw away everything the user typed."""

    monkeypatch.setattr(config_flow, "STATION_WAIT_TIMEOUT", 0)

    result = await _walk_to_the_wait(hass, hass_client_no_auth)

    while result["type"] == FlowResultType.SHOW_PROGRESS:
        await hass.async_block_till_done()
        result = await hass.config_entries.flow.async_configure(result["flow_id"])

    assert result["step_id"] == "timeout"
    assert result["description_placeholders"]["key_hint_extra"] == ""

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_PASSWORD: "s3cr3t"}


async def test_a_wrong_key_during_the_wizard_is_named(
    hass, hass_client_no_auth, monkeypatch
):
    """A silent timeout hides the single most common setup mistake."""

    monkeypatch.setattr(config_flow, "STATION_WAIT_TIMEOUT", 0)

    assert await async_setup_component(hass, "http", {})

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_PASSWORD: "s3cr3t"}
    )

    client = await hass_client_no_auth()
    response = await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&wspw=wrong")

    assert response.status == 401

    for _ in range(5):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})

    while result["type"] == FlowResultType.SHOW_PROGRESS:
        await hass.async_block_till_done()
        result = await hass.config_entries.flow.async_configure(result["flow_id"])

    assert result["step_id"] == "timeout"
    assert "does not match" in result["description_placeholders"]["key_hint_extra"]


async def test_uploads_are_refused_when_no_wizard_is_running(hass, hass_client_no_auth):
    """Outside onboarding, an upload with no entry is still a 503."""

    assert await async_setup_component(hass, "http", {})
    async_ensure_views(hass)

    client = await hass_client_no_auth()
    response = await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}")

    assert response.status == 503


async def test_only_one_entry_is_allowed(hass, setup_pws):
    """One HTTP server, one station key, any number of stations."""

    await setup_pws()

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_options_flow_defaults(hass, setup_pws):
    entry, _ = await setup_pws(password="s3cr3t")

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.MENU
    assert set(result["menu_options"]) == {"options", "instructions"}

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "options"}
    )
    assert result["type"] == FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_PASSWORD: "s3cr3t",
            CONF_AVAILABILITY_TIMEOUT: 45,
            "debug": True,
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_AVAILABILITY_TIMEOUT] == 45
    assert entry.options["debug"] is True


async def test_station_can_be_removed(hass, setup_pws):
    """
    Devices show up on their own, so a typo in the sender ID would otherwise
    leave a ghost station behind for good.
    """

    entry, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=237&t1tem=21")
    await hass.async_block_till_done()

    await hass.services.async_call(
        "button",
        "press",
        {
            "entity_id": hass.states.async_entity_ids("button")[0],
        },
        blocking=True,
    )
    await hass.async_block_till_done()
    assert entry.options[CONF_WIND_OFFSETS] == {DEVICE_ID: 123}

    device_entry = device_for(hass, entry, DEVICE_ID)
    assert device_entry is not None

    assert await async_remove_config_entry_device(hass, entry, device_entry)
    await hass.async_block_till_done()

    runtime = hass.data[DOMAIN]
    assert DEVICE_ID not in runtime.devices

    # Its calibration is dropped along with it.
    assert entry.options[CONF_WIND_OFFSETS] == {}


async def test_removed_station_reappears_when_it_posts_again(hass, setup_pws):
    entry, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21")
    await hass.async_block_till_done()

    device_entry = device_for(hass, entry, DEVICE_ID)
    await async_remove_config_entry_device(hass, entry, device_entry)
    dr.async_get(hass).async_remove_device(device_entry.id)
    await hass.async_block_till_done()

    response = await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=24")
    assert response.status == 200
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == "24"


async def test_onboarding_repair_waits_for_the_first_upload(hass, setup_pws):
    """
    The integration has no "add device" button, so it says what to do and then
    watches for the station instead of leaving the user on an empty page.
    """

    from homeassistant.helpers import issue_registry as ir

    from custom_components.personal_weather_station.const import ISSUE_NO_STATION_YET
    from custom_components.personal_weather_station.repairs import (
        async_create_fix_flow,
    )

    entry, client = await setup_pws()

    issue = ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_NO_STATION_YET)
    assert issue is not None
    assert issue.is_fixable
    assert "urls" in issue.translation_placeholders

    flow = await async_create_fix_flow(
        hass, ISSUE_NO_STATION_YET, {"entry_id": entry.entry_id}
    )
    flow.hass = hass

    # The instructions, then the wait starts.
    form = await flow.async_step_confirm()
    assert form["step_id"] == "confirm"

    progress = await flow.async_step_confirm({})
    assert progress["type"] == FlowResultType.SHOW_PROGRESS
    assert progress["progress_action"] == "waiting_for_station"

    # The station finally posts.
    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5")
    await hass.async_block_till_done()

    await flow._task
    done = await flow.async_step_wait()
    assert done["type"] == FlowResultType.SHOW_PROGRESS_DONE
    assert done["step_id"] == "received"

    received = await flow.async_step_received()
    assert received["description_placeholders"]["station"] == DEVICE_ID

    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_NO_STATION_YET) is None


async def test_onboarding_repair_clears_itself_without_the_flow(hass, setup_pws):
    """A station showing up on its own must dismiss the prompt."""

    from homeassistant.helpers import issue_registry as ir

    from custom_components.personal_weather_station.const import ISSUE_NO_STATION_YET

    _, client = await setup_pws()

    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_NO_STATION_YET)

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5")
    await hass.async_block_till_done()

    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_NO_STATION_YET) is None


async def test_onboarding_repair_reports_a_failure_after_the_wait(
    hass, setup_pws, monkeypatch
):
    """
    Nothing arriving is the case worth handling well.

    The user is told what to check, the prompt stays so they can come back, and
    the wait can be started again.
    """

    from homeassistant.helpers import issue_registry as ir

    from custom_components.personal_weather_station import repairs
    from custom_components.personal_weather_station.const import ISSUE_NO_STATION_YET

    monkeypatch.setattr(repairs, "STATION_WAIT_TIMEOUT", 0)

    entry, _ = await setup_pws()

    flow = await repairs.async_create_fix_flow(
        hass, ISSUE_NO_STATION_YET, {"entry_id": entry.entry_id}
    )
    flow.hass = hass

    await flow.async_step_confirm()
    result = await flow.async_step_confirm({})

    if result["type"] == FlowResultType.SHOW_PROGRESS:
        await flow._task
        result = await flow.async_step_wait()

    assert result["type"] == FlowResultType.SHOW_PROGRESS_DONE
    assert result["step_id"] == "timeout"

    failure = await flow.async_step_timeout()
    assert failure["step_id"] == "timeout"
    # It says how long it waited, where to point the station and what the key is.
    assert {"minutes", "urls", "key_hint"} <= failure["description_placeholders"].keys()

    # Closing it must abort, not succeed. RepairsFlowManager.async_finish_flow
    # deletes the issue for every result type except ABORT, so ending any other
    # way would mark a failed wait as resolved and make the prompt vanish.
    closed = await flow.async_step_timeout({})
    assert closed["type"] == FlowResultType.ABORT
    assert closed["reason"] == "not_received"
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_NO_STATION_YET) is not None


async def test_the_walkthrough_is_reachable_from_the_options(hass, setup_pws):
    """
    The onboarding repair goes away once a station has posted.

    Someone adding a second station months later needs the same five screens as
    the first one, so the options walk them too, ending without touching
    anything the user has configured.
    """

    entry, client = await setup_pws(options={CONF_AVAILABILITY_TIMEOUT: 42})

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5")
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "instructions"}
    )

    for step in ("station", "settings", "server", "form", "confirm"):
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == step

        placeholders = result["description_placeholders"]
        assert IMAGES_URL in placeholders["image"]
        assert {"urls", "key_hint", "endpoints"} <= placeholders.keys()

        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {}
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Walking the instructions is not a settings change.
    assert entry.options[CONF_AVAILABILITY_TIMEOUT] == 42


async def test_failed_wait_does_not_resolve_the_repair(hass, setup_pws, monkeypatch):
    """
    Driven through the real repairs manager, which is where the rule lives.

    RepairsFlowManager.async_finish_flow deletes the issue for every result
    type except ABORT. Ending the failed wait any other way marked it as fixed
    and made the prompt disappear, while its own text promised the opposite.
    """

    import asyncio

    from homeassistant.helpers import issue_registry as ir
    from homeassistant.setup import async_setup_component

    from custom_components.personal_weather_station import repairs
    from custom_components.personal_weather_station.const import ISSUE_NO_STATION_YET

    monkeypatch.setattr(repairs, "STATION_WAIT_TIMEOUT", 2)

    assert await async_setup_component(hass, "repairs", {})
    await setup_pws()

    manager = hass.data["repairs"]["flow_manager"]

    result = await manager.async_init(
        DOMAIN, data={"handler": DOMAIN, "issue_id": ISSUE_NO_STATION_YET}
    )
    assert result["step_id"] == "confirm"

    flow_id = result["flow_id"]
    result = await manager.async_configure(flow_id, {})
    assert result["type"] == FlowResultType.SHOW_PROGRESS

    for _ in range(6):
        if result["type"] != FlowResultType.SHOW_PROGRESS:
            break
        await asyncio.sleep(1)
        result = await manager.async_configure(flow_id)

    assert result["step_id"] == "timeout"

    result = await manager.async_configure(flow_id, {})
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "not_received"

    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_NO_STATION_YET) is not None


async def test_successful_wait_resolves_the_repair(hass, setup_pws, monkeypatch):
    """The other half: a station arriving must clear the prompt for good."""

    import asyncio

    from homeassistant.helpers import issue_registry as ir
    from homeassistant.setup import async_setup_component

    from custom_components.personal_weather_station import repairs
    from custom_components.personal_weather_station.const import ISSUE_NO_STATION_YET

    monkeypatch.setattr(repairs, "STATION_WAIT_TIMEOUT", 10)

    assert await async_setup_component(hass, "repairs", {})
    _, client = await setup_pws()

    manager = hass.data["repairs"]["flow_manager"]

    result = await manager.async_init(
        DOMAIN, data={"handler": DOMAIN, "issue_id": ISSUE_NO_STATION_YET}
    )
    flow_id = result["flow_id"]
    result = await manager.async_configure(flow_id, {})
    assert result["type"] == FlowResultType.SHOW_PROGRESS

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21.5")
    await hass.async_block_till_done()

    for _ in range(6):
        if result["type"] != FlowResultType.SHOW_PROGRESS:
            break
        await asyncio.sleep(1)
        result = await manager.async_configure(flow_id)

    assert result["step_id"] == "received"
    assert result["description_placeholders"]["station"] == DEVICE_ID

    result = await manager.async_configure(flow_id, {})
    assert result["type"] == FlowResultType.CREATE_ENTRY

    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_NO_STATION_YET) is None
