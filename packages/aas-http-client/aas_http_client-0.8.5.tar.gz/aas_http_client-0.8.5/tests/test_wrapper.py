from http import client
import pytest
from pathlib import Path
from aas_http_client.classes.wrapper.sdk_wrapper import IdEncoding, Level, create_wrapper_by_config, SdkWrapper, create_wrapper_by_dict, create_wrapper_by_url
from basyx.aas import model
import aas_http_client.utilities.model_builder as model_builder
import aas_http_client.utilities.sdk_tools as sdk_tools
from urllib.parse import urlparse
import json
from aas_http_client.utilities import encoder
import random

JAVA_SERVER_PORTS = [8075]
PYTHON_SERVER_PORTS = [5080, 80]
DOTNET_SERVER_PORTS = [5043]

AIMC_SM_ID = "https://fluid40.de/ids/sm/7644_4034_2556_2369"
SM_ID = "fluid40/sm_http_client_unit_tests"
SHELL_ID = "fluid40/aas_http_client_unit_tests"

CONFIG_FILES = [
    "./tests/server_configs/test_java_server_config.yml",
    "./tests/server_configs/test_dotnet_server_config.yml",
    "./tests/server_configs/test_python_server_config.yml"
]

# CONFIG_FILES = [
#     "./tests/server_configs/test_dotnet_server_config_local.json",
# ]

@pytest.fixture(params=CONFIG_FILES, scope="module")
def wrapper(request) -> SdkWrapper:
    try:
        file = Path(request.param).resolve()

        if not file.exists():
            raise FileNotFoundError(f"Configuration file {file} does not exist.")

        wrapper = create_wrapper_by_config(file, basic_auth_password="")

        rand = random.randint(0, 10)
        if (rand % 2) == 0:
            wrapper.set_encoded_ids(IdEncoding.encoded)

        wrapper.set_encoded_ids(IdEncoding.encoded)

    except Exception as e:
        raise RuntimeError("Unable to connect to server.")

    shells = wrapper.get_all_asset_administration_shells()
    if shells is None:
        raise RuntimeError("No shells found on server. Please check the server configuration.")

    return wrapper

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
    submodel = model_builder.create_base_submodel(identifier=SM_ID, id_short="sm_http_client_unit_tests")
    submodel.category = "Unit Test"
    return submodel

@pytest.fixture(scope="module")
def shared_aas(shared_sm: model.Submodel) -> model.AssetAdministrationShell:
    # create an AAS
    aas = model_builder.create_base_ass(identifier=SHELL_ID, id_short="aas_http_client_unit_tests")

    # add Submodel to AAS
    sdk_tools.add_submodel_to_aas(aas, shared_sm)

    return aas

def test_000a_create_wrapper_by_url(wrapper: SdkWrapper):
    base_url: str = wrapper.base_url
    new_client: SdkWrapper = create_wrapper_by_url(base_url=base_url)
    assert new_client is not None

def test_000b_create_wrapper_by_dict(wrapper: SdkWrapper):
    base_url: str = wrapper.base_url

    config_dict: dict = {
        "BaseUrl": base_url
    }

    new_client: SdkWrapper = create_wrapper_by_dict(configuration=config_dict)
    assert new_client is not None

def test_000c_get_client(wrapper: SdkWrapper):
    client = wrapper.get_client()
    assert client is not None
    root = client.get_root()
    assert root is not None

def test_001a_connect(wrapper: SdkWrapper):
    assert wrapper is not None

def test_001b_delete_all_asset_administration_shells(wrapper: SdkWrapper):
    result = wrapper.get_all_asset_administration_shells()
    assert result is not None

    for shell in result.results:
        shell_id = shell.id

        if wrapper.get_encoded_ids() == IdEncoding.encoded:
            shell_id = encoder.decode_base_64(shell_id)

        if shell_id:
            delete_result = wrapper.delete_asset_administration_shell_by_id(shell_id)
            assert delete_result

    shells_result = wrapper.get_all_asset_administration_shells()
    assert len(shells_result.results) == 0

def test_001c_delete_all_submodels(wrapper: SdkWrapper):
    result = wrapper.get_all_submodels()
    assert result is not None

    for submodel in result.results:
        submodel_id = submodel.id

        if wrapper.get_encoded_ids() == IdEncoding.encoded:
            submodel_id = encoder.decode_base_64(submodel_id)

        if submodel_id:
            delete_result = wrapper.delete_submodel_by_id(submodel_id)
            assert delete_result

    submodels_result = wrapper.get_all_submodels()
    assert len(submodels_result.results) == 0

def test_002_get_all_asset_administration_shells(wrapper: SdkWrapper):
    shells = wrapper.get_all_asset_administration_shells()
    assert shells is not None
    assert len(shells.results) == 0

def test_003_post_asset_administration_shell(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell):
    shell = wrapper.post_asset_administration_shell(shared_aas)

    assert shell is not None
    assert shell.id == SHELL_ID
    assert shell.id_short == shared_aas.id_short

    shells = wrapper.get_all_asset_administration_shells()
    assert shells is not None
    assert len(shells.results) == 1
    assert shells.results[0].id_short == shared_aas.id_short
    assert shells.results[0].id == SHELL_ID

def test_004a_get_asset_administration_shell_by_id(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell):
    shell_id = SHELL_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        shell_id = encoder.decode_base_64(shell_id)

    shell = wrapper.get_asset_administration_shell_by_id(shell_id)

    assert shell is not None
    assert shell.id_short == shared_aas.id_short
    assert shell.id == SHELL_ID

def test_004b_get_asset_administration_shell_by_id(wrapper: SdkWrapper):
    shell = wrapper.get_asset_administration_shell_by_id("non_existent_id")

    assert shell is None

def test_005a_put_asset_administration_shell_by_id(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell):
    aas = model.AssetAdministrationShell(id_=shared_aas.asset_information.global_asset_id, asset_information=shared_aas.asset_information)
    aas.id_short = shared_aas.id_short

    description_text = "Put description for unit tests"
    aas.description = model.MultiLanguageTextType({"en": description_text})
    aas.submodel = shared_aas.submodel  # Keep existing submodels

    shell_id = SHELL_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        shell_id = encoder.decode_base_64(shell_id)

    result = wrapper.put_asset_administration_shell_by_id(shell_id, aas)

    assert result

    shell = wrapper.get_asset_administration_shell_by_id(shell_id)

    assert shell is not None
    assert shell.id_short == shared_aas.id_short
    assert shell.id == SHELL_ID
    # description must have changed
    assert shell.description.get("en", "") == description_text
    assert shell.description.get("en", "") != shared_aas.description.get("en", "")
    # submodels must be retained
    assert len(shell.submodel) == len(shared_aas.submodel)

    # The display name must be empty
    # currently not working in dotnet
    # assert len(get_result.get("displayName", {})) == 0

    # # restore to its original state
    wrapper.put_asset_administration_shell_by_id(shell_id, shared_aas)  # Restore original submodel

def test_005b_put_asset_administration_shell_by_id(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell):
    # put with other ID
    id_short = "put_short_id"
    identifier = f"fluid40/{id_short}"
    asset_info = model_builder.create_base_asset_information(identifier)
    aas = model.AssetAdministrationShell(id_=asset_info.global_asset_id, asset_information=asset_info)
    aas.id_short = id_short

    description_text = {"en": "Updated description for unit tests"}
    aas.description = model.MultiLanguageTextType(description_text)

    shell_id = SHELL_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        shell_id = encoder.decode_base_64(SHELL_ID)

    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: Python server crashes by this test
        result = False
    else:
        result = wrapper.put_asset_administration_shell_by_id(shell_id, aas)

    assert not result

    shell = wrapper.get_asset_administration_shell_by_id(shell_id)
    assert shell.description.get("en", "") != description_text
    assert shell.description.get("en", "") == shared_aas.description.get("en", "")

def test_006_get_asset_administration_shell_by_id_reference_aas_repository(wrapper: SdkWrapper):
    shell_id = SHELL_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        shell_id = encoder.decode_base_64(SHELL_ID)

    reference = wrapper.get_asset_administration_shell_by_id_reference_aas_repository(shell_id)

    assert reference is not None
    assert len(reference.key) == 1
    assert reference.key[0].value == SHELL_ID

def test_007_get_submodel_by_id_aas_repository(wrapper: SdkWrapper, shared_sm: model.Submodel):
    shell_id = SHELL_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        shell_id = encoder.decode_base_64(SHELL_ID)

    submodel = wrapper.get_submodel_by_id_aas_repository(shell_id, shared_sm.id)

    assert submodel is None

def test_008_get_all_submodels(wrapper: SdkWrapper):
    submodels = wrapper.get_all_submodels()
    assert submodels is not None
    assert len(submodels.results) == 0

def test_009a_post_submodel(wrapper: SdkWrapper, shared_sm: model.Submodel):
    submodel = wrapper.post_submodel(shared_sm)

    assert submodel is not None
    assert submodel.id == SM_ID
    assert submodel.id_short == shared_sm.id_short

    submodels = wrapper.get_all_submodels()
    assert submodels is not None
    assert len(submodels.results) == 1
    assert submodels.results[0].id_short == shared_sm.id_short
    assert submodels.results[0].id == SM_ID

def test_009b_post_submodel(wrapper: SdkWrapper):
    sm_template_file = Path(f"./tests/test_data/aimc.json").resolve()

    with Path.open(sm_template_file, "r", encoding="utf-8") as f:
        sm_data = json.load(f)

    submodel = sdk_tools.convert_to_object(sm_data)

    result = wrapper.post_submodel(submodel)

    assert result is not None
    assert result.id == AIMC_SM_ID

    get_result = wrapper.get_all_submodels()
    assert get_result is not None
    submodels = get_result.results
    assert len(submodels) == 2

def test_010_get_submodel_by_id_aas_repository(wrapper: SdkWrapper, shared_sm: model.Submodel):
    shell_id = SHELL_ID
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        shell_id = encoder.decode_base_64(SHELL_ID)
        sm_id = encoder.decode_base_64(SM_ID)

    submodel = wrapper.get_submodel_by_id_aas_repository(shell_id, sm_id)

    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS:
        # Basyx java server do not provide this endpoint
        assert submodel is None
    else:
        assert submodel is not None
        assert submodel.id_short == shared_sm.id_short
        assert submodel.id == SM_ID

def test_011a_get_submodel_by_id(wrapper: SdkWrapper, shared_sm: model.Submodel):
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    submodel = wrapper.get_submodel_by_id(sm_id)

    assert submodel is not None
    assert submodel.id_short == shared_sm.id_short
    assert submodel.id == SM_ID

def test_011b_get_submodel_by_id(wrapper: SdkWrapper):
    result = wrapper.get_submodel_by_id("non_existent_id")

    assert result is None

def test_011c_get_submodel_by_id(wrapper: SdkWrapper):
    sm_id = AIMC_SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(AIMC_SM_ID)

    result = wrapper.get_submodel_by_id(sm_id)

    assert result is not None
    assert result.id == AIMC_SM_ID

def test_011d_get_submodel_by_id(wrapper: SdkWrapper):
    sm_id = AIMC_SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(AIMC_SM_ID)

    result = wrapper.get_submodel_by_id(sm_id, level=Level.core)

    assert result is not None
    assert result.id == AIMC_SM_ID
    # assert "submodelElements" not in result

def test_012_patch_submodel_by_id(wrapper: SdkWrapper, shared_sm: model.Submodel):
    sm = model.Submodel(shared_sm.id_short)
    sm.id_short = shared_sm.id_short

    description_text = "Patched description for unit tests"
    sm.description = model.MultiLanguageTextType({"en": description_text})

    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    result = wrapper.patch_submodel_by_id(sm_id, sm)

    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS or int(parsed.port) in PYTHON_SERVER_PORTS:
        # Basyx java server do not provide this endpoint
        assert not result
    else:
        assert result

        submodel = wrapper.get_submodel_by_id(sm_id)
        assert submodel is not None
        assert submodel.id_short == shared_sm.id_short
        assert submodel.id == SM_ID
        # Only the description may change in patch.
        assert submodel.description.get("en", "") == description_text
        assert submodel.description.get("en", "") != shared_sm.description.get("en", "")
        # The display name must remain the same.
        assert submodel.display_name == shared_sm.display_name
        assert len(submodel.submodel_element) == len(shared_sm.submodel_element)

def test_013_put_submodel_by_id_aas_repository(wrapper: SdkWrapper, shared_sm: model.Submodel):
    sm = model.Submodel(SM_ID)
    sm.id_short = shared_sm.id_short

    description_text = "Put via shell description for unit tests"
    sm.description = model.MultiLanguageTextType({"en": description_text})
    sm.display_name = shared_sm.display_name  # Keep existing display name because of problems with empty lists

    shell_id = SHELL_ID
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        shell_id = encoder.decode_base_64(SHELL_ID)
        sm_id = encoder.decode_base_64(SM_ID)

    result = wrapper.put_submodel_by_id_aas_repository(shell_id, sm_id, sm)

    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS:
        # Basyx java server do not provide this endpoint
        assert not result
    else:
        assert result

        submodel = wrapper.get_submodel_by_id_aas_repository(shell_id, sm_id)
        assert submodel is not None
        assert submodel.id_short == shared_sm.id_short
        assert submodel.id == SM_ID
        # description must have changed
        assert submodel.description.get("en", "") == description_text
        assert submodel.description.get("en", "") != shared_sm.description.get("en", "")
        # display name stays
        assert submodel.display_name == shared_sm.display_name
        # category was not set an must be empty
        assert submodel.category is None
        assert len(submodel.submodel_element) == 0

        # restore to its original state
        wrapper.put_submodel_by_id_aas_repository(shell_id, sm_id, shared_sm)  # Restore original submodel

def test_014_put_submodels_by_id(wrapper: SdkWrapper, shared_sm: model.Submodel):
    sm = model.Submodel(shared_sm.id)
    sm.id_short = shared_sm.id_short

    description_text = "Put description for unit tests"
    sm.description = model.MultiLanguageTextType({"en": description_text})
    sm.display_name = shared_sm.display_name  # Keep existing display name because of problems with empty lists

    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    result = wrapper.put_submodels_by_id(sm_id, sm)

    assert result

    submodel = wrapper.get_submodel_by_id(sm_id)
    assert submodel is not None
    assert submodel.id_short == shared_sm.id_short
    assert submodel.id == SM_ID
    # description must have changed
    assert submodel.description.get("en", "") == description_text
    assert submodel.description.get("en", "") != shared_sm.description.get("en", "")
    # display name stays
    # assert submodel.display_name == shared_sm.display_name
    # category was not set an must be empty
    assert submodel.category is None
    assert len(submodel.submodel_element) == 0

    # restore to its original state
    wrapper.put_submodels_by_id(sm_id, shared_sm)  # Restore original submodel

def test_015_get_all_submodel_elements_submodel_repository(wrapper: SdkWrapper):
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    submodel_elements = wrapper.get_all_submodel_elements_submodel_repository(sm_id)

    assert submodel_elements is not None
    assert len(submodel_elements.results) == 0

def test_016a_post_submodel_element_submodel_repo(wrapper: SdkWrapper, shared_sme_string: model.Property):
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    submodel_element = wrapper.post_submodel_element_submodel_repo(sm_id, shared_sme_string)

    assert submodel_element is not None

    assert isinstance(submodel_element, model.Property)
    property: model.Property = submodel_element
    assert property.value == shared_sme_string.value

    assert submodel_element.id_short == shared_sme_string.id_short
    assert submodel_element.description.get("en", "") == shared_sme_string.description.get("en", "")
    assert submodel_element.display_name.get("en", "") == shared_sme_string.display_name.get("en", "")
    assert submodel_element.value == shared_sme_string.value

    submodel_elements = wrapper.get_all_submodel_elements_submodel_repository(sm_id)

    assert submodel_elements is not None
    assert len(submodel_elements.results) == 1

def test_016b_post_submodel_element_submodel_repo(wrapper: SdkWrapper, shared_sme_bool: model.Property):
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    submodel_element = wrapper.post_submodel_element_submodel_repo(sm_id, shared_sme_bool)

    assert submodel_element is not None

    assert isinstance(submodel_element, model.Property)
    property: model.Property = submodel_element
    assert property.value == shared_sme_bool.value

    assert submodel_element.id_short == shared_sme_bool.id_short
    assert submodel_element.description.get("en", "") == shared_sme_bool.description.get("en", "")
    assert submodel_element.display_name.get("en", "") == shared_sme_bool.display_name.get("en", "")
    assert submodel_element.value == shared_sme_bool.value

    submodel_elements = wrapper.get_all_submodel_elements_submodel_repository(sm_id)

    assert submodel_elements is not None
    assert len(submodel_elements.results) == 2

def test_016c_post_submodel_element_submodel_repo(wrapper: SdkWrapper, shared_sme_int: model.Property):
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    submodel_element = wrapper.post_submodel_element_submodel_repo(sm_id, shared_sme_int)

    assert submodel_element is not None

    assert isinstance(submodel_element, model.Property)
    property: model.Property = submodel_element
    assert property.value == shared_sme_int.value

    assert submodel_element.id_short == shared_sme_int.id_short
    assert submodel_element.description.get("en", "") == shared_sme_int.description.get("en", "")
    assert submodel_element.display_name.get("en", "") == shared_sme_int.display_name.get("en", "")
    assert submodel_element.value == shared_sme_int.value

    submodel_elements = wrapper.get_all_submodel_elements_submodel_repository(sm_id)

    assert submodel_elements is not None
    assert len(submodel_elements.results) == 3

def test_016d_post_submodel_element_submodel_repo(wrapper: SdkWrapper, shared_sme_float: model.Property):
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    submodel_element = wrapper.post_submodel_element_submodel_repo(sm_id, shared_sme_float)

    assert submodel_element is not None

    assert isinstance(submodel_element, model.Property)
    property: model.Property = submodel_element
    assert property.value == shared_sme_float.value

    assert submodel_element.id_short == shared_sme_float.id_short
    assert submodel_element.description.get("en", "") == shared_sme_float.description.get("en", "")
    assert submodel_element.display_name.get("en", "") == shared_sme_float.display_name.get("en", "")
    assert submodel_element.value == shared_sme_float.value

    submodel_elements = wrapper.get_all_submodel_elements_submodel_repository(sm_id)

    assert submodel_elements is not None
    assert len(submodel_elements.results) == 4

def test_017a_get_submodel_element_by_path_submodel_repo(wrapper: SdkWrapper, shared_sme_string: model.Property):
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    submodel_element = wrapper.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_string.id_short)

    assert submodel_element is not None

    assert isinstance(submodel_element, model.Property)

    assert submodel_element.id_short == shared_sme_string.id_short
    assert submodel_element.description.get("en", "") == shared_sme_string.description.get("en", "")
    assert submodel_element.display_name.get("en", "") == shared_sme_string.display_name.get("en", "")
    assert submodel_element.value == shared_sme_string.value

def test_017b_get_submodel_element_by_path_submodel_repo(wrapper: SdkWrapper, shared_sme_bool: model.Property):
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    submodel_element = wrapper.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_bool.id_short)

    assert submodel_element is not None

    assert isinstance(submodel_element, model.Property)

    assert submodel_element.id_short == shared_sme_bool.id_short
    assert submodel_element.description.get("en", "") == shared_sme_bool.description.get("en", "")
    assert submodel_element.display_name.get("en", "") == shared_sme_bool.display_name.get("en", "")
    assert submodel_element.value == shared_sme_bool.value

def test_017c_get_submodel_element_by_path_submodel_repo(wrapper: SdkWrapper, shared_sme_int: model.Property):
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    submodel_element = wrapper.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_int.id_short)

    assert submodel_element is not None

    assert isinstance(submodel_element, model.Property)

    assert submodel_element.id_short == shared_sme_int.id_short
    assert submodel_element.description.get("en", "") == shared_sme_int.description.get("en", "")
    assert submodel_element.display_name.get("en", "") == shared_sme_int.display_name.get("en", "")
    assert submodel_element.value == shared_sme_int.value

def test_017d_get_submodel_element_by_path_submodel_repo(wrapper: SdkWrapper, shared_sme_float: model.Property):
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    submodel_element = wrapper.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_float.id_short)

    assert submodel_element is not None

    assert isinstance(submodel_element, model.Property)

    assert submodel_element.id_short == shared_sme_float.id_short
    assert submodel_element.description.get("en", "") == shared_sme_float.description.get("en", "")
    assert submodel_element.display_name.get("en", "") == shared_sme_float.display_name.get("en", "")
    assert submodel_element.value == shared_sme_float.value

def test_018a_patch_submodel_element_by_path_value_only_submodel_repo(wrapper: SdkWrapper, shared_sme_string: model.Property):
    new_value = "Patched String Value"

    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    result = wrapper.patch_submodel_element_by_path_value_only_submodel_repo(sm_id, shared_sme_string.id_short, new_value)

    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server do not provide this endpoint
        assert result is False
    else:
        assert result is True

        submodel_element = wrapper.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_string.id_short)

        assert submodel_element is not None
        assert submodel_element.id_short == shared_sme_string.id_short
        assert submodel_element.description.get("en", "") == shared_sme_string.description.get("en", "")
        assert submodel_element.display_name.get("en", "") == shared_sme_string.display_name.get("en", "")

        assert isinstance(submodel_element, model.Property)
        property: model.Property = submodel_element
        assert property.value == new_value

def test_018b_patch_submodel_element_by_path_value_only_submodel_repo(wrapper: SdkWrapper, shared_sme_bool: model.Property):
    new_value = "false"

    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    result = wrapper.patch_submodel_element_by_path_value_only_submodel_repo(sm_id, shared_sme_bool.id_short, new_value)

    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server do not provide this endpoint
        assert result is False
    else:
        assert result is True

        submodel_element = wrapper.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_bool.id_short)

        assert submodel_element is not None
        assert submodel_element.id_short == shared_sme_bool.id_short
        assert submodel_element.description.get("en", "") == shared_sme_bool.description.get("en", "")
        assert submodel_element.display_name.get("en", "") == shared_sme_bool.display_name.get("en", "")

        assert isinstance(submodel_element, model.Property)
        property: model.Property = submodel_element
        assert property.value == json.loads(new_value)

def test_018c_patch_submodel_element_by_path_value_only_submodel_repo(wrapper: SdkWrapper, shared_sme_int: model.Property):
    new_value = "263"

    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    result = wrapper.patch_submodel_element_by_path_value_only_submodel_repo(sm_id, shared_sme_int.id_short, new_value)

    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server do not provide this endpoint
        assert result is False
    else:
        assert result is True

        submodel_element = wrapper.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_int.id_short)

        assert submodel_element is not None
        assert submodel_element.id_short == shared_sme_int.id_short
        assert submodel_element.description.get("en", "") == shared_sme_int.description.get("en", "")
        assert submodel_element.display_name.get("en", "") == shared_sme_int.display_name.get("en", "")

        assert isinstance(submodel_element, model.Property)
        property: model.Property = submodel_element
        assert property.value == int(new_value)

def test_018d_patch_submodel_element_by_path_value_only_submodel_repo(wrapper: SdkWrapper, shared_sme_float: model.Property):
    new_value = "262.1"

    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    result = wrapper.patch_submodel_element_by_path_value_only_submodel_repo(sm_id, shared_sme_float.id_short, new_value)

    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server do not provide this endpoint
        assert result is False
    else:
        assert result is True

        submodel_element = wrapper.get_submodel_element_by_path_submodel_repo(sm_id, shared_sme_float.id_short)

        assert submodel_element is not None
        assert submodel_element.id_short == shared_sme_float.id_short
        assert submodel_element.description.get("en", "") == shared_sme_float.description.get("en", "")
        assert submodel_element.display_name.get("en", "") == shared_sme_float.display_name.get("en", "")

        assert isinstance(submodel_element, model.Property)
        property: model.Property = submodel_element
        assert property.value == float(new_value)

def test_020a_encoded_ids(wrapper: SdkWrapper):
    base_url: str = wrapper.base_url
    new_wrapper: SdkWrapper = create_wrapper_by_url(base_url=base_url)
    assert new_wrapper is not None

    sm = new_wrapper.get_submodel_by_id(AIMC_SM_ID)
    assert sm is None

    encoded_id = encoder.decode_base_64(AIMC_SM_ID)
    encoded_sm = new_wrapper.get_submodel_by_id(encoded_id)
    assert encoded_sm is not None
    assert encoded_sm.id == AIMC_SM_ID

def test_020b_encoded_ids(wrapper: SdkWrapper):
    base_url: str = wrapper.base_url
    new_wrapper: SdkWrapper = create_wrapper_by_url(base_url=base_url)
    assert new_wrapper is not None

    sm = new_wrapper.get_asset_administration_shell_by_id(SHELL_ID)
    assert sm is None

    encoded_id = encoder.decode_base_64(SHELL_ID)
    encoded_sm = new_wrapper.get_asset_administration_shell_by_id(encoded_id)
    assert encoded_sm is not None
    assert encoded_sm.id == SHELL_ID

def test_021_post_file_by_path_submodel_repo(wrapper: SdkWrapper):
    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS or int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        # NOTE: Basyx java server do not provide this endpoint
        return

    file_sme = model.File("file_sme", content_type="application/pdf")

    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    file_post_result = wrapper.post_submodel_element_submodel_repo(sm_id, file_sme)
    assert file_post_result is not None

    filename = "https.pdf"
    file = Path(f"./tests/test_data/{filename}").resolve()
    result = wrapper.experimental_post_file_by_path_submodel_repo(sm_id, file_sme.id_short, file)
    assert result is True

    result_sme = wrapper.get_submodel_element_by_path_submodel_repo(sm_id, file_sme.id_short)

    assert result_sme is not None
    assert result_sme.id_short == file_sme.id_short

    assert result_sme.content_type == file_sme.content_type
    assert result_sme.value == f"/{filename}"

def test_022_get_file_content_by_path_submodel_repo(wrapper: SdkWrapper):
    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS or int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        # NOTE: Basyx java server do not provide this endpoint
        return

    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    attachment = wrapper.experimental_get_file_by_path_submodel_repo(sm_id, "file_sme")
    assert attachment is not None
    assert attachment.content_type == "application/pdf"
    assert isinstance(attachment.content, bytes)
    assert len(attachment.content) > 0
    assert attachment.content.startswith(b"%PDF-1.7")
    assert attachment.filename == "/https.pdf"

def test_023_put_file_content_by_path_submodel_repo(wrapper: SdkWrapper):
    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS or int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        # NOTE: Basyx java server do not provide this endpoint
        return

    filename = "aimc.json"
    file = Path(f"./tests/test_data/{filename}").resolve()

    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    result = wrapper.experimental_put_file_by_path_submodel_repo(sm_id, "file_sme", file)
    assert result is True

    get_result = wrapper.experimental_get_file_by_path_submodel_repo(sm_id, "file_sme")
    assert get_result is not None
    assert len(get_result.content) > 0
    assert get_result.content.startswith(b"{\n")
    assert get_result.filename == f"/{filename}"
    assert get_result.content_type == "application/json"

    result_sme = wrapper.get_submodel_element_by_path_submodel_repo(sm_id, "file_sme")
    assert result_sme is not None
    assert result_sme.value == f"/{filename}"

def test_024_delete_file_content_by_path_submodel_repo(wrapper: SdkWrapper):
    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in JAVA_SERVER_PORTS or int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        # NOTE: Basyx java server do not provide this endpoint
        return

    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    result = wrapper.experimental_delete_file_by_path_submodel_repo(sm_id, "file_sme")
    assert result is True

    get_result = wrapper.experimental_get_file_by_path_submodel_repo(sm_id, "file_sme")
    assert get_result is None

    result_sme = wrapper.get_submodel_element_by_path_submodel_repo(sm_id, "file_sme")
    assert result_sme is not None
    assert result_sme.value == None

def test_025_get_thumbnail_aas_repository(wrapper: SdkWrapper):
    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        return

    shell_id = SHELL_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        shell_id = encoder.decode_base_64(SHELL_ID)

    result = wrapper.get_thumbnail_aas_repository(shell_id)
    assert result is None

def test_026_put_thumbnail_aas_repository(wrapper: SdkWrapper):
    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        return

    shell_id = SHELL_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        shell_id = encoder.decode_base_64(SHELL_ID)

    filename = "Pen_Machine.png"
    file = Path(f"./tests/test_data/{filename}").resolve()

    result = wrapper.put_thumbnail_aas_repository(shell_id, file.name, file)
    assert result is True

def test_027_get_thumbnail_aas_repository(wrapper: SdkWrapper):
    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server implementation differs
        return

    shell_id = SHELL_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        shell_id = encoder.decode_base_64(SHELL_ID)

    result = wrapper.get_thumbnail_aas_repository(shell_id)
    assert result is not None

    assert len(result.content) > 0
    assert result.content.startswith(b"\x89PNG\r\n\x1a\n")
    assert result.filename == "thumbnail"
    assert result.content_type == "image/png"

def test_028_delete_thumbnail_aas_repository(wrapper: SdkWrapper):
    parsed = urlparse(wrapper.base_url)
    if int(parsed.port) in PYTHON_SERVER_PORTS:
        # NOTE: python server do not provide this endpoint
        return

    shell_id = SHELL_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        shell_id = encoder.decode_base_64(SHELL_ID)

    result = wrapper.delete_thumbnail_aas_repository(shell_id)
    assert result is True

    get_result = wrapper.get_thumbnail_aas_repository(shell_id)
    assert get_result is None

def test_098_delete_asset_administration_shell_by_id(wrapper: SdkWrapper):
    shell_id = SHELL_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        shell_id = encoder.decode_base_64(SHELL_ID)

    result = wrapper.delete_asset_administration_shell_by_id(shell_id)

    assert result

    shells = wrapper.get_all_asset_administration_shells()
    assert shells is not None
    assert len(shells.results) == 0

def test_099a_delete_submodel_by_id(wrapper: SdkWrapper):
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(SM_ID)

    result = wrapper.delete_submodel_by_id(sm_id)

    assert result

    submodels = wrapper.get_all_submodels()
    assert submodels is not None
    assert len(submodels.results) == 1

def test_099b_delete_submodel_by_id(wrapper: SdkWrapper):
    sm_id = SM_ID

    if wrapper.get_encoded_ids() == IdEncoding.encoded:
        sm_id = encoder.decode_base_64(AIMC_SM_ID)

    result = wrapper.delete_submodel_by_id(sm_id)

    assert result

    submodels = wrapper.get_all_submodels()
    assert submodels is not None
    assert len(submodels.results) == 0
