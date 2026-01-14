import pytest
from pathlib import Path
from aas_http_client.classes.client.aas_client import create_client_by_config, AasHttpClient, create_client_by_dict, create_client_by_url
from basyx.aas import model
import aas_http_client.utilities.model_builder as model_builder
import aas_http_client.utilities.sdk_tools as sdk_tools
import json
import basyx.aas.adapter.json
from urllib.parse import urlparse
import logging
from aas_http_client.demo.logging_handler import initialize_logging
from aas_http_client.utilities import encoder
import random

logger = logging.getLogger(__name__)

JAVA_SERVER_PORTS = [8075]
PYTHON_SERVER_PORTS = [5080, 80]

AIMC_SM_ID = "https://fluid40.de/ids/sm/7644_4034_2556_2369"
SM_ID = "fluid40/sm_http_client_unit_tests"
SHELL_ID = "fluid40/aas_http_client_unit_tests"

CONFIG_FILES = [
    "./tests/server_configs/test_java_server_config.yml",
    "./tests/server_configs/test_dotnet_server_config.yml",
    "./tests/server_configs/test_python_server_config.yml"
]

# CONFIG_FILES = [
#     "./tests/server_configs/test_dotnet_server_config_local.yml",
# ]

@pytest.fixture(params=CONFIG_FILES, scope="module")
def client(request) -> AasHttpClient:
    try:
        initialize_logging()
        file = Path(request.param).resolve()

        if not file.exists():
            raise FileNotFoundError(f"Configuration file {file} does not exist.")

        client = create_client_by_config(file)

        # Randomly set encoded_ids to True or False for testing both scenarios
        rand = random.randint(0, 10)
        if (rand % 2) == 0:
            client.encoded_ids = True

    except Exception as e:
        raise RuntimeError("Unable to connect to server.")

    shells = client.shell.get_all_asset_administration_shells()
    if shells is None:
        raise RuntimeError("No shells found on server. Please check the server configuration.")

    return client

@pytest.fixture(scope="module")
def shared_sme_string() -> model.Property:
    # create a Submodel
    return model_builder.create_base_submodel_element_property("sme_property_string", model.datatypes.String, "Sample String Value")

@pytest.fixture(scope="module")
def shared_sme_bool() -> model.Property:
    # create a Submodel
    return model_builder.create_base_submodel_element_property("sme_property_bool", model.datatypes.Boolean, True)

@pytest.fixture(scope="module")
def shared_sme_int() -> model.Property:
    # create a Submodel
    return model_builder.create_base_submodel_element_property("sme_property_int", model.datatypes.Integer, 262)

@pytest.fixture(scope="module")
def shared_sme_float() -> model.Property:
    # create a Submodel
    return model_builder.create_base_submodel_element_property("sme_property_float", model.datatypes.Float, 262.3)

@pytest.fixture(scope="module")
def shared_sm() -> model.Submodel:
    # create a Submodel
    return model_builder.create_base_submodel(identifier=SM_ID, id_short="sm_http_client_unit_tests")

@pytest.fixture(scope="module")
def shared_aas(shared_sm: model.Submodel) -> model.AssetAdministrationShell:
    # create an AAS
    aas = model_builder.create_base_ass(identifier=SHELL_ID, id_short="aas_http_client_unit_tests")

    # add Submodel to AAS
    sdk_tools.add_submodel_to_aas(aas, shared_sm)

    return aas

def test_000a_create_client_by_url(client: AasHttpClient):
    base_url: str = client.base_url
    new_client: AasHttpClient = create_client_by_url(base_url=base_url)
    assert new_client is not None

def test_000b_create_client_by_dict(client: AasHttpClient):
    base_url: str = client.base_url

    config_dict: dict = {
        "BaseUrl": base_url
    }

    new_client: AasHttpClient = create_client_by_dict(configuration=config_dict)
    assert new_client is not None

def test_001a_connect(client: AasHttpClient):
    assert client is not None

def test_001b_delete_all_asset_administration_shells(client: AasHttpClient):
    result = client.shell.get_all_asset_administration_shells()
    assert result is not None
    shells = result.get("result", [])

    for shell in shells:
        shell_id = shell.get("id", "")

        if client.encoded_ids:
            shell_id = encoder.decode_base_64(shell_id)

        if shell_id:
            delete_result = client.shell.delete_asset_administration_shell_by_id(shell_id)
            assert delete_result

    shells_result = client.shell.get_all_asset_administration_shells()
    shells = shells_result.get("result", [])
    assert len(shells) == 0

def test_001c_delete_all_submodels(client: AasHttpClient):
    result = client.submodel.get_all_submodels()
    assert result is not None
    submodels = result.get("result", [])

    for submodel in submodels:
        submodel_id = submodel.get("id", "")

        if client.encoded_ids:
            submodel_id = encoder.decode_base_64(submodel_id)

        if submodel_id:
            delete_result = client.submodel.delete_submodel_by_id(submodel_id)
            assert delete_result

    submodels_result = client.submodel.get_all_submodels()
    submodels = submodels_result.get("result", [])
    assert len(submodels) == 0

def test_002_get_all_asset_administration_shells(client: AasHttpClient):
    result = client.shell.get_all_asset_administration_shells()
    assert result is not None
    shells = result.get("result", [])
    assert len(shells) == 0

def test_003_post_asset_administration_shell(client: AasHttpClient, shared_aas: model.AssetAdministrationShell):
    aas_data_string = json.dumps(shared_aas, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    aas_data = json.loads(aas_data_string)
    result = client.shell.post_asset_administration_shell(aas_data)

    assert result is not None
    assert result.get("idShort", "") == shared_aas.id_short
    assert result.get("id", "") == SHELL_ID

    get_result = client.shell.get_all_asset_administration_shells()
    assert get_result is not None
    shells = get_result.get("result", [])
    assert len(shells) == 1
    assert shells[0].get("idShort", "") == shared_aas.id_short
    assert shells[0].get("id", "") == SHELL_ID

def test_004a_get_asset_administration_shell_by_id(client: AasHttpClient, shared_aas: model.AssetAdministrationShell):
    shell_id = SHELL_ID

    if client.encoded_ids:
        shell_id = encoder.decode_base_64(SHELL_ID)

    result = client.shell.get_asset_administration_shell_by_id(shell_id)

    assert result is not None
    assert result.get("idShort", "") == shared_aas.id_short
    assert result.get("id", "") == SHELL_ID

def test_004b_get_asset_administration_shell_by_id(client: AasHttpClient):
    result = client.shell.get_asset_administration_shell_by_id("non_existent_id")

    assert result is None

def test_005a_put_asset_administration_shell_by_id(client: AasHttpClient, shared_aas: model.AssetAdministrationShell):
    aas = model.AssetAdministrationShell(id_=shared_aas.asset_information.global_asset_id, asset_information=shared_aas.asset_information)
    aas.id_short = shared_aas.id_short

    description_text = "Put description for unit tests"
    aas.description = model.MultiLanguageTextType({"en": description_text})
    aas.submodel = shared_aas.submodel  # Keep existing submodels

    aas_data_string = json.dumps(aas, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    aas_data = json.loads(aas_data_string)

    shell_id = SHELL_ID

    if client.encoded_ids:
        shell_id = encoder.decode_base_64(SHELL_ID)

    result = client.shell.put_asset_administration_shell_by_id(shell_id, aas_data)
    assert result

    get_result = client.shell.get_asset_administration_shell_by_id(shell_id)
    assert get_result
    assert get_result.get("idShort", "") == shared_aas.id_short
    assert get_result.get("id", "") == SHELL_ID
    # description must have changed
    assert get_result.get("description", {})[0].get("text", "") == description_text
    assert get_result.get("description", {})[0].get("text", "") != shared_aas.description.get("en", "")
    # submodels must be retained
    assert len(get_result.get("submodels", [])) == len(shared_aas.submodel)

    # The display name must be empty
    # NOTE: currently not working in dotnet
    # assert len(get_result.get("displayName", {})) == 0

    # restore to its original state
    sm_data_string = json.dumps(shared_aas, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)
    client.shell.put_asset_administration_shell_by_id(shell_id, sm_data)  # Restore original submodel

def test_005b_put_asset_administration_shell_by_id(client: AasHttpClient, shared_aas: model.AssetAdministrationShell):
    # put with other ID
    id_short = "put_short_id"
    identifier = f"fluid40/{id_short}"
    asset_info = model_builder.create_base_asset_information(identifier)
    aas = model.AssetAdministrationShell(id_=asset_info.global_asset_id, asset_information=asset_info)
    aas.id_short = id_short

    description_text = {"en": "Updated description for unit tests"}
    aas.description = model.MultiLanguageTextType(description_text)

    aas_data_string = json.dumps(aas, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    aas_data = json.loads(aas_data_string)

    shell_id = SHELL_ID

    if client.encoded_ids:
        shell_id = encoder.decode_base_64(SHELL_ID)

    parsed = urlparse(client.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: Python server crashes by this test
        result = False
    else:
        result = client.shell.put_asset_administration_shell_by_id(shell_id, aas_data)

    assert not result

    get_result = client.shell.get_asset_administration_shell_by_id(shell_id)

    assert get_result.get("description", {})[0].get("text", "") != description_text
    assert get_result.get("description", {})[0].get("text", "") == shared_aas.description.get("en", "")

def test_006_get_asset_administration_shell_by_id_reference_aas_repository(client: AasHttpClient):
    shell_id = SHELL_ID

    if client.encoded_ids:
        shell_id = encoder.decode_base_64(SHELL_ID)

    result = client.shell.get_asset_administration_shell_by_id_reference_aas_repository(shell_id)

    parsed = urlparse(client.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS:
        # NOTE: Basyx java server do not provide this endpoint
        assert result is None
    else:
        assert result is not None
        keys = result.get("keys", [])
        assert len(keys) == 1
        assert keys[0].get("value", "") == SHELL_ID

def test_007_get_submodel_by_id_aas_repository(client: AasHttpClient):
    shell_id = SHELL_ID
    sm_id = SM_ID

    if client.encoded_ids:
        shell_id = encoder.decode_base_64(SHELL_ID)
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.shell.get_submodel_by_id_aas_repository(shell_id, sm_id)

    assert result is None

def test_008_get_all_submodels(client: AasHttpClient):
    result = client.submodel.get_all_submodels()
    assert result is not None
    submodels = result.get("result", [])
    assert len(submodels) == 0

def test_009a_post_submodel(client: AasHttpClient, shared_sm: model.Submodel):
    sm_data_string = json.dumps(shared_sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)

    result = client.submodel.post_submodel(sm_data)

    assert result is not None
    result_id_short = result.get("idShort", "")
    assert result_id_short == shared_sm.id_short

    get_result = client.submodel.get_all_submodels()
    assert get_result is not None
    submodels = get_result.get("result", [])
    assert len(submodels) == 1
    assert submodels[0].get("idShort", "") == shared_sm.id_short

def test_009b_post_submodel(client: AasHttpClient):
    sm_template_file = Path(f"./tests/test_data/aimc.json").resolve()

    with Path.open(sm_template_file, "r", encoding="utf-8") as f:
        sm_data = json.load(f)

    result = client.submodel.post_submodel(sm_data)

    assert result is not None
    result_id = result.get("id", "")
    assert result_id == AIMC_SM_ID

    get_result = client.submodel.get_all_submodels()
    assert get_result is not None
    submodels = get_result.get("result", [])
    assert len(submodels) == 2

def test_010_get_submodel_by_id_aas_repository(client: AasHttpClient, shared_sm: model.Submodel):
    shell_id = SHELL_ID
    sm_id = SM_ID

    if client.encoded_ids:
        shell_id = encoder.decode_base_64(SHELL_ID)
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.shell.get_submodel_by_id_aas_repository(shell_id, sm_id)

    parsed = urlparse(client.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS:
        # NOTE: Basyx java server do not provide this endpoint
        assert result is None
    else:
        assert result is not None
        result_id_short = result.get("idShort", "")
        assert result_id_short == shared_sm.id_short

def test_011a_get_submodel_by_id(client: AasHttpClient, shared_sm: model.Submodel):
    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.get_submodel_by_id(sm_id)

    assert result is not None
    result_id_short = result.get("idShort", "")
    assert result_id_short == shared_sm.id_short

def test_011b_get_submodel_by_id(client: AasHttpClient):
    result = client.submodel.get_submodel_by_id("non_existent_id")

    assert result is None

def test_011c_get_submodel_by_id(client: AasHttpClient):
    sm_id = AIMC_SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(AIMC_SM_ID)

    result = client.submodel.get_submodel_by_id(sm_id)

    assert result is not None
    result_id = result.get("id", "")
    assert result_id == AIMC_SM_ID

def test_011d_get_submodel_by_id(client: AasHttpClient):
    sm_id = AIMC_SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(AIMC_SM_ID)

    result = client.submodel.get_submodel_by_id(sm_id, level="core")

    assert result is not None
    result_id = result.get("id", "")
    assert result_id == AIMC_SM_ID
    #assert "submodelElements" not in result

def test_012_patch_submodel_by_id(client: AasHttpClient, shared_sm: model.Submodel):
    sm = model.Submodel(shared_sm.id_short)
    sm.id_short = shared_sm.id_short

    description_text = "Patched description for unit tests"
    sm.description = model.MultiLanguageTextType({"en": description_text})

    sm_data_string = json.dumps(sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.patch_submodel_by_id(sm_id, sm_data)

    parsed = urlparse(client.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS or int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: Basyx java and python server do not provide this endpoint
        assert not result
    else:
        assert result is True

        get_result = client.submodel.get_submodel_by_id(sm_id)
        assert get_result is not None
        assert get_result.get("idShort", "") == shared_sm.id_short
        assert get_result.get("id", "") == SM_ID
        # Only the description may change in patch.
        assert get_result.get("description", {})[0].get("text", "") == description_text
        assert get_result.get("description", {})[0].get("text", "") != shared_sm.description.get("en", "")
        # The display name must remain the same.
        assert get_result.get("displayName", {})[0].get("text", "") == shared_sm.display_name.get("en", "")

def test_013_put_submodel_by_id_aas_repository(client: AasHttpClient, shared_sm: model.Submodel):
    sm = model.Submodel(SM_ID)
    sm.id_short = shared_sm.id_short

    description_text = "Put via shell description for unit tests"
    sm.description = model.MultiLanguageTextType({"en": description_text})

    sm_data_string = json.dumps(sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)

    shell_id = SHELL_ID
    sm_id = SM_ID

    if client.encoded_ids:
        shell_id = encoder.decode_base_64(SHELL_ID)
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.shell.put_submodel_by_id_aas_repository(shell_id, sm_id, sm_data)

    parsed = urlparse(client.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS:
        # NOTE: Basyx java server do not provide this endpoint
        assert not result
    else:
        assert result

        get_result = client.shell.get_submodel_by_id_aas_repository(shell_id, sm_id)
        assert get_result is not None
        assert get_result.get("idShort", "") == shared_sm.id_short
        assert get_result.get("id", "") == SM_ID
        # description must have changed
        assert get_result.get("description", {})[0].get("text", "") == description_text
        assert get_result.get("description", {})[0].get("text", "") != shared_sm.description.get("en", "")
        assert len(get_result.get("displayName", {})) == 0

    # restore to its original state
    sm_data_string = json.dumps(shared_sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)
    client.shell.put_submodel_by_id_aas_repository(shell_id, sm_id, sm_data)  # Restore original submodel

def test_014_put_submodels_by_id(client: AasHttpClient, shared_sm: model.Submodel):
    sm = model.Submodel(SM_ID)
    sm.id_short = shared_sm.id_short

    description_text = "Put description for unit tests"
    sm.description = model.MultiLanguageTextType({"en": description_text})

    sm_data_string = json.dumps(sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.put_submodels_by_id(sm_id, sm_data)

    assert result is True

    get_result = client.submodel.get_submodel_by_id(sm_id)
    assert get_result is not None
    assert get_result.get("idShort", "") == shared_sm.id_short
    assert get_result.get("id", "") == SM_ID
    # description must have changed
    assert get_result.get("description", {})[0].get("text", "") == description_text
    assert get_result.get("description", {})[0].get("text", "") != shared_sm.description.get("en", "")
    assert len(get_result.get("displayName", {})) == 0

    # restore to its original state
    sm_data_string = json.dumps(shared_sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)
    client.submodel.put_submodels_by_id(SM_ID, sm_data)  # Restore original submodel

def test_015_get_all_submodel_elements_submodel_repository(client: AasHttpClient, shared_sm: model.Submodel):
    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    submodel_elements = client.submodel.get_all_submodel_elements_submodel_repository(sm_id)

    assert submodel_elements is not None
    assert len(submodel_elements.get("result", [])) == 0

def test_016a_post_submodel_element_submodel_repo(client: AasHttpClient, shared_sme_string: model.Property):
    sme_data_string = json.dumps(shared_sme_string, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sme_data = json.loads(sme_data_string)

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.post_submodel_element_submodel_repo(sm_id, sme_data)

    assert result is not None
    assert result.get("idShort", "") == shared_sme_string.id_short
    assert result.get("description", {})[0].get("text", "") == shared_sme_string.description.get("en", "")
    assert result.get("displayName", {})[0].get("text", "") == shared_sme_string.display_name.get("en", "")
    assert result.get("value", "") == shared_sme_string.value

    get_result = client.submodel.get_all_submodel_elements_submodel_repository(sm_id)

    assert len(get_result.get("result", [])) == 1

def test_016b_post_submodel_element_submodel_repo(client: AasHttpClient, shared_sme_bool: model.Property):
    sme_data_string = json.dumps(shared_sme_bool, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sme_data = json.loads(sme_data_string)

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.post_submodel_element_submodel_repo(sm_id, sme_data)

    assert result is not None
    assert result.get("idShort", "") == shared_sme_bool.id_short
    assert result.get("description", {})[0].get("text", "") == shared_sme_bool.description.get("en", "")
    assert result.get("displayName", {})[0].get("text", "") == shared_sme_bool.display_name.get("en", "")
    assert json.loads(result.get("value", "").lower()) == shared_sme_bool.value

    get_result = client.submodel.get_all_submodel_elements_submodel_repository(sm_id)

    assert len(get_result.get("result", [])) == 2

def test_016c_post_submodel_element_submodel_repo(client: AasHttpClient, shared_sme_int: model.Property):
    sme_data_string = json.dumps(shared_sme_int, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sme_data = json.loads(sme_data_string)

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.post_submodel_element_submodel_repo(sm_id, sme_data)

    assert result is not None
    assert result.get("idShort", "") == shared_sme_int.id_short
    assert result.get("description", {})[0].get("text", "") == shared_sme_int.description.get("en", "")
    assert result.get("displayName", {})[0].get("text", "") == shared_sme_int.display_name.get("en", "")
    assert int(result.get("value", "")) == shared_sme_int.value

    get_result = client.submodel.get_all_submodel_elements_submodel_repository(sm_id)

    assert len(get_result.get("result", [])) == 3

def test_016d_post_submodel_element_submodel_repo(client: AasHttpClient, shared_sme_float: model.Property):
    sme_data_string = json.dumps(shared_sme_float, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sme_data = json.loads(sme_data_string)

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.post_submodel_element_submodel_repo(sm_id, sme_data)

    assert result is not None
    assert result.get("idShort", "") == shared_sme_float.id_short
    assert result.get("description", {})[0].get("text", "") == shared_sme_float.description.get("en", "")
    assert result.get("displayName", {})[0].get("text", "") == shared_sme_float.display_name.get("en", "")
    assert float(result.get("value", "")) == shared_sme_float.value

    get_result = client.submodel.get_all_submodel_elements_submodel_repository(sm_id)

    assert len(get_result.get("result", [])) == 4

def test_017a_get_submodel_element_by_path_submodel_repo(client: AasHttpClient, shared_sme_string: model.Property):
    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_string.id_short)

    assert result is not None
    assert result.get("idShort", "") == shared_sme_string.id_short
    assert result.get("description", {})[0].get("text", "") == shared_sme_string.description.get("en", "")
    assert result.get("displayName", {})[0].get("text", "") == shared_sme_string.display_name.get("en", "")
    assert result.get("value", "") == shared_sme_string.value

def test_017b_get_submodel_element_by_path_submodel_repo(client: AasHttpClient, shared_sme_bool: model.Property):
    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_bool.id_short)

    assert result is not None
    assert result.get("idShort", "") == shared_sme_bool.id_short
    assert result.get("description", {})[0].get("text", "") == shared_sme_bool.description.get("en", "")
    assert result.get("displayName", {})[0].get("text", "") == shared_sme_bool.display_name.get("en", "")
    assert json.loads(result.get("value", "").lower()) == shared_sme_bool.value

def test_017c_get_submodel_element_by_path_submodel_repo(client: AasHttpClient, shared_sme_int: model.Property):
    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_int.id_short)

    assert result is not None
    assert result.get("idShort", "") == shared_sme_int.id_short
    assert result.get("description", {})[0].get("text", "") == shared_sme_int.description.get("en", "")
    assert result.get("displayName", {})[0].get("text", "") == shared_sme_int.display_name.get("en", "")
    assert int(result.get("value", "")) == shared_sme_int.value

def test_017d_get_submodel_element_by_path_submodel_repo(client: AasHttpClient, shared_sme_float: model.Property):
    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_float.id_short)

    assert result is not None
    assert result.get("idShort", "") == shared_sme_float.id_short
    assert result.get("description", {})[0].get("text", "") == shared_sme_float.description.get("en", "")
    assert result.get("displayName", {})[0].get("text", "") == shared_sme_float.display_name.get("en", "")
    assert float(result.get("value", "")) == shared_sme_float.value

def test_018a_patch_submodel_element_by_path_value_only_submodel_repo(client: AasHttpClient, shared_sme_string: model.Property):
    new_value = "Patched String Value"

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.patch_submodel_element_by_path_value_only_submodel_repo(sm_id, shared_sme_string.id_short, new_value)

    parsed = urlparse(client.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server do not provide this endpoint
        assert result is False
    else:
        assert result is True

        get_result = client.submodel.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_string.id_short)

        assert get_result is not None
        assert get_result.get("idShort", "") == shared_sme_string.id_short
        assert get_result.get("value", "") == new_value
        assert get_result.get("description", {})[0].get("text", "") == shared_sme_string.description.get("en", "")
        assert get_result.get("displayName", {})[0].get("text", "") == shared_sme_string.display_name.get("en", "")

def test_018b_patch_submodel_element_by_path_value_only_submodel_repo(client: AasHttpClient, shared_sme_bool: model.Property):
    new_value = "false"

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.patch_submodel_element_by_path_value_only_submodel_repo(sm_id, shared_sme_bool.id_short, new_value)

    parsed = urlparse(client.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server do not provide this endpoint
        assert result is False
    else:
        assert result is True

        get_result = client.submodel.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_bool.id_short)

        assert get_result is not None
        assert get_result.get("idShort", "") == shared_sme_bool.id_short
        assert json.loads(get_result.get("value", "").lower()) == json.loads(new_value)
        assert get_result.get("description", {})[0].get("text", "") == shared_sme_bool.description.get("en", "")
        assert get_result.get("displayName", {})[0].get("text", "") == shared_sme_bool.display_name.get("en", "")

def test_018c_patch_submodel_element_by_path_value_only_submodel_repo(client: AasHttpClient, shared_sme_int: model.Property):
    new_value = "263"

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.patch_submodel_element_by_path_value_only_submodel_repo(sm_id, shared_sme_int.id_short, new_value)

    parsed = urlparse(client.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server do not provide this endpoint
        assert result is False
    else:
        assert result is True

        get_result = client.submodel.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_int.id_short)

        assert get_result is not None
        assert get_result.get("idShort", "") == shared_sme_int.id_short
        assert int(get_result.get("value", "")) == int(new_value)
        assert get_result.get("description", {})[0].get("text", "") == shared_sme_int.description.get("en", "")
        assert get_result.get("displayName", {})[0].get("text", "") == shared_sme_int.display_name.get("en", "")

def test_018d_patch_submodel_element_by_path_value_only_submodel_repo(client: AasHttpClient, shared_sme_float: model.Property):
    new_value = "262.1"

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.patch_submodel_element_by_path_value_only_submodel_repo(sm_id, shared_sme_float.id_short, new_value)

    parsed = urlparse(client.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server do not provide this endpoint
        assert result is False
    else:
        assert result is True

        get_result = client.submodel.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_float.id_short)

        assert get_result is not None
        assert get_result.get("idShort", "") == shared_sme_float.id_short
        assert float(get_result.get("value", "")) == float(new_value)
        assert get_result.get("description", {})[0].get("text", "") == shared_sme_float.description.get("en", "")
        assert get_result.get("displayName", {})[0].get("text", "") == shared_sme_float.display_name.get("en", "")

def test_019a_post_submodel_element_by_path_submodel_repo(client: AasHttpClient):
    submodel_element_list = model.SubmodelElementList(id_short="sme_list_1", type_value_list_element=model.Property, value_type_list_element=model.datatypes.String)
    submodel_element_list_dict = sdk_tools.convert_to_dict(submodel_element_list)

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    first_result = client.submodel.post_submodel_element_submodel_repo(sm_id, submodel_element_list_dict)

    assert first_result is not None

    property = model_builder.create_base_submodel_element_property("sme_property_in_list", model.datatypes.String, "Value in List")
    property_dict = sdk_tools.convert_to_dict(property)
    del property_dict["idShort"]

    result = client.submodel.post_submodel_element_by_path_submodel_repo(sm_id, submodel_element_list.id_short, property_dict)

    assert result is not None
    assert "idShort" not in result  # idShort was deleted

    submodel = client.submodel.get_submodel_by_id(sm_id)

    assert submodel is not None
    elements = submodel.get("submodelElements", [])
    assert len(elements) == 5  # 4 previous properties + 1 list
    assert elements[4].get("idShort", "") == submodel_element_list.id_short
    list_elements = elements[4].get("value", [])
    assert len(list_elements) == 1
    assert list_elements[0].get("idShort", "") == ""
    assert list_elements[0].get("value", "") == property.value


def test_019b_post_submodel_element_by_path_submodel_repo(client: AasHttpClient):
    submodel_element_collection = model.SubmodelElementCollection(id_short="sme_collection_1")
    submodel_element_collection_dict = sdk_tools.convert_to_dict(submodel_element_collection)

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    first_result = client.submodel.post_submodel_element_submodel_repo(sm_id, submodel_element_collection_dict)

    assert first_result is not None

    property = model_builder.create_base_submodel_element_property("sme_property_in_collection", model.datatypes.String, "Value in List")
    property_dict = sdk_tools.convert_to_dict(property)

    result = client.submodel.post_submodel_element_by_path_submodel_repo(sm_id, submodel_element_collection.id_short, property_dict)

    assert result is not None
    assert result["idShort"] == property.id_short

    submodel = client.submodel.get_submodel_by_id(sm_id)

    assert submodel is not None
    elements = submodel.get("submodelElements", [])
    assert len(elements) == 6
    assert elements[5].get("idShort", "") == submodel_element_collection.id_short
    list_elements = elements[5].get("value", [])
    assert len(list_elements) == 1
    assert list_elements[0].get("idShort", "") == property.id_short
    assert list_elements[0].get("value", "") == property.value

    base_url: str = client.base_url
    new_client: AasHttpClient = create_client_by_url(base_url=base_url)
    assert new_client is not None

    sm = new_client.submodel.get_submodel_by_id(AIMC_SM_ID)
    assert sm is None

    decoded_id = encoder.decode_base_64(AIMC_SM_ID)
    decoded_sm = new_client.submodel.get_submodel_by_id(decoded_id)
    assert decoded_sm is not None
    assert decoded_sm.get("id", "") == AIMC_SM_ID

def test_020b_encoded_ids(client: AasHttpClient):
    base_url: str = client.base_url
    new_client: AasHttpClient = create_client_by_url(base_url=base_url)
    assert new_client is not None

    sm = new_client.shell.get_asset_administration_shell_by_id(SHELL_ID)
    assert sm is None

    decoded_id = encoder.decode_base_64(SHELL_ID)
    decoded_sm = new_client.shell.get_asset_administration_shell_by_id(decoded_id)
    assert decoded_sm is not None
    assert decoded_sm.get("id", "") == SHELL_ID

def test_021_post_file_by_path_submodel_repo(client: AasHttpClient):
    parsed = urlparse(client.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS or int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        # NOTE: Basyx java server do not provide this endpoint
        return

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    file_sme = model.File("file_sme", content_type="application/pdf")
    file_post_result = client.submodel.post_submodel_element_submodel_repo(sm_id, sdk_tools.convert_to_dict(file_sme))
    assert file_post_result is not None

    filename = "https.pdf"
    file = Path(f"./tests/test_data/{filename}").resolve()
    result = client.experimental.post_file_by_path_submodel_repo(sm_id, file_sme.id_short, file)
    assert result is True

    result_sme = client.submodel.get_submodel_element_by_path_submodel_repo(sm_id, file_sme.id_short)

    assert result_sme is not None
    assert result_sme.get("idShort", "") == file_sme.id_short
    assert result_sme.get("contentType", "") == file_sme.content_type
    assert "value" in result_sme
    assert result_sme.get("value", "") == f"/{filename}"

def test_022_get_file_content_by_path_submodel_repo(client: AasHttpClient):
    parsed = urlparse(client.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS or int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        # NOTE: Basyx java server do not provide this endpoint
        return

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.experimental.get_file_by_path_submodel_repo(sm_id, "file_sme")
    assert result is not None
    assert len(result) > 0
    assert result.startswith(b"%PDF-1.7")

def test_023_put_file_content_by_path_submodel_repo(client: AasHttpClient):
    parsed = urlparse(client.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS or int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        # NOTE: Basyx java server do not provide this endpoint
        return

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    filename = "aimc.json"
    file = Path(f"./tests/test_data/{filename}").resolve()
    result = client.experimental.put_file_by_path_submodel_repo(sm_id, "file_sme", file)
    assert result is True

    get_result = client.experimental.get_file_by_path_submodel_repo(sm_id, "file_sme")
    assert get_result is not None
    assert len(get_result) > 0
    assert get_result.startswith(b"{\n")

    result_sme = client.submodel.get_submodel_element_by_path_submodel_repo(sm_id, "file_sme")
    assert result_sme is not None
    assert "value" in result_sme
    assert result_sme.get("value", "") == f"/{filename}"

def test_024_delete_file_content_by_path_submodel_repo(client: AasHttpClient):
    parsed = urlparse(client.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS or int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server do not provide this endpoint
        return

    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.experimental.delete_file_by_path_submodel_repo(sm_id, "file_sme")
    assert result is True

    get_result = client.experimental.get_file_by_path_submodel_repo(sm_id, "file_sme")
    assert get_result is None

    result_sme = client.submodel.get_submodel_element_by_path_submodel_repo(sm_id, "file_sme")
    assert result_sme is not None
    assert "value" in result_sme
    assert result_sme.get("value", "") == None

def test_025_get_thumbnail_aas_repository(client: AasHttpClient):
    parsed = urlparse(client.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        return

    shell_id = SHELL_ID

    if client.encoded_ids:
        shell_id = encoder.decode_base_64(SHELL_ID)

    result = client.shell.get_thumbnail_aas_repository(shell_id)
    assert result is None

def test_026_put_thumbnail_aas_repository(client: AasHttpClient):
    parsed = urlparse(client.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        return

    shell_id = SHELL_ID

    if client.encoded_ids:
        shell_id = encoder.decode_base_64(SHELL_ID)

    filename = "Pen_Machine.png"
    file = Path(f"./tests/test_data/{filename}").resolve()

    result = client.shell.put_thumbnail_aas_repository(shell_id, file.name, file)
    assert result is True

def test_027_get_thumbnail_aas_repository(client: AasHttpClient):
    parsed = urlparse(client.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        return

    shell_id = SHELL_ID

    if client.encoded_ids:
        shell_id = encoder.decode_base_64(SHELL_ID)

    result = client.shell.get_thumbnail_aas_repository(shell_id)
    assert result is not None
    assert len(result) > 0
    assert result.startswith(b"\x89PNG\r\n\x1a\n")

def test_028_delete_thumbnail_aas_repository(client: AasHttpClient):
    parsed = urlparse(client.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server do not provide this endpoint
        return

    shell_id = SHELL_ID

    if client.encoded_ids:
        shell_id = encoder.decode_base_64(SHELL_ID)

    result = client.shell.delete_thumbnail_aas_repository(shell_id)
    assert result is True

    get_result = client.shell.get_thumbnail_aas_repository(shell_id)
    assert get_result is None

def test_098_delete_asset_administration_shell_by_id(client: AasHttpClient):
    shell_id = SHELL_ID

    if client.encoded_ids:
        shell_id = encoder.decode_base_64(SHELL_ID)

    result = client.shell.delete_asset_administration_shell_by_id(shell_id)

    assert result is True

    get_result = client.shell.get_all_asset_administration_shells()
    assert get_result is not None
    shells = get_result.get("result", [])
    assert len(shells) == 0

def test_099a_delete_submodel_by_id(client: AasHttpClient):
    sm_id = SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(SM_ID)

    result = client.submodel.delete_submodel_by_id(sm_id)

    assert result is True

    get_result = client.submodel.get_all_submodels()
    assert get_result is not None
    submodels = get_result.get("result", [])
    assert len(submodels) == 1

def test_099b_delete_submodel_by_id(client: AasHttpClient):
    sm_id = AIMC_SM_ID

    if client.encoded_ids:
        sm_id = encoder.decode_base_64(AIMC_SM_ID)

    result = client.submodel.delete_submodel_by_id(sm_id)

    assert result is True

    get_result = client.submodel.get_all_submodels()
    assert get_result is not None
    submodels = get_result.get("result", [])
    assert len(submodels) == 0
