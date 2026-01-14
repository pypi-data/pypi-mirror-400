"""Main process for the demo."""

import json
import logging
from pathlib import Path

from basyx.aas import model

from aas_http_client.classes.client import aas_client
from aas_http_client.classes.wrapper import sdk_wrapper
from aas_http_client.utilities import encoder, model_builder, sdk_tools

logger = logging.getLogger(__name__)


def start() -> None:
    """Start the demo process."""
    # create a submodel element
    wrapper = sdk_wrapper.create_wrapper_by_url(base_url="http://javaaasserver:8075", encoded_ids=False)
    client = wrapper.get_client()
    # client = aas_client.create_client_by_url(base_url="http://pythonaasserver:80/", encoded_ids=False)
    client_shell_reg = aas_client.create_client_by_url(base_url="http://aas-registry:8080", encoded_ids=False)

    sm = model_builder.create_base_submodel("TestSubmodel", "TestSM")
    shell = model_builder.create_base_ass("TestAAS", "TestAAS")
    sdk_tools.add_submodel_to_aas(shell, sm)

    client.shell.delete_asset_administration_shell_by_id(shell.id)
    client.submodel.delete_submodel_by_id(sm.id)

    shell_data = sdk_tools.convert_to_dict(shell)
    sm_data = sdk_tools.convert_to_dict(sm)

    result = client.submodel.post_submodel(sm_data)
    result = client.shell.post_asset_administration_shell(shell_data)

    descriptors = client_shell_reg.shell_registry.get_all_asset_administration_shell_descriptors()
    descriptor = sdk_tools.convert_to_object(descriptors.get("result", [])[0])

    file_sme = model.File("file_sme", content_type="application/pdf")
    file_post_result = client.submodel.post_submodel_element_submodel_repo(sm.id, sdk_tools.convert_to_dict(file_sme))

    file_get_result = wrapper.get_submodel_element_by_path_submodel_repo(sm.id, file_sme.id_short)

    file = Path(f"./tests/test_data/https.pdf").resolve()
    tmp = client.experimental.post_file_by_path_submodel_repo(sm.id, file_sme.id_short, file)

    file_get_result = client.submodel.get_submodel_element_by_path_submodel_repo(sm.id, file_sme.id_short)

    attachment = client.experimental.get_file_by_path_submodel_repo(sm.id, file_sme.id_short)

    attachment_2 = wrapper.experimental_get_file_by_path_submodel_repo(sm.id, file_sme.id_short)

    file = Path(f"./tests/test_data/aimc.json").resolve()
    tmp = client.experimental.put_file_by_path_submodel_repo(sm.id, file_sme.id_short, file)

    attachment = client.experimental.get_file_by_path_submodel_repo(sm.id, file_sme.id_short)

    delete_result = client.experimental.delete_file_by_path_submodel_repo(sm.id, file_sme.id_short)

    attachment = client.experimental.get_file_by_path_submodel_repo(sm.id, file_sme.id_short)

    print(attachment)
