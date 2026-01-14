#  Quapp Platform Project
#  qiskit_provider_factory.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk
from quapp_common.factory.provider_factory import ProviderFactory

from ..model.provider.riken_provider import RikenProvider
from ..model.provider.data import RikenConfig, RikenEndpoint
from ..model.provider.ibm_cloud_provider import IbmCloudProvider
from ..model.provider.ibm_quantum_provider import IbmQuantumProvider
from ..model.provider.oqc_cloud_provider import OqcCloudProvider
from ..model.provider.qapp_qiskit_provider import QappQiskitProvider


class QiskitProviderFactory(ProviderFactory):

    @staticmethod
    def create_provider(provider_type: ProviderTag, sdk: Sdk,
            authentication: dict):
        logger.debug("Create Qiskit Provider")

        if ProviderTag.QUAO_QUANTUM_SIMULATOR.__eq__(
                provider_type) and Sdk.QISKIT.__eq__(sdk):
            logger.debug("Create Qiskit Qapp Qiskit Provider")
            return QappQiskitProvider()

        if ProviderTag.IBM_QUANTUM.__eq__(provider_type):
            logger.debug("Create IBM Quantum Provider")
            return IbmQuantumProvider(authentication.get("token"))

        if ProviderTag.IBM_CLOUD.__eq__(provider_type):
            logger.debug("Create IBM Cloud Provider")
            return IbmCloudProvider(authentication.get("token"),
                    authentication.get("crn"))

        if ProviderTag.OQC_CLOUD.__eq__(provider_type):
            logger.debug("Create OQC Cloud Provider")
            return OqcCloudProvider(authentication.get("url"),
                    authentication.get("accessToken"))

        if ProviderTag.RIKEN.__eq__(provider_type):
            return RikenProvider(config=RikenConfig(
                    client_id=authentication.get("clientId"),
                    client_secret=authentication.get("clientSecret"),
                    token_endpoint=authentication.get("tokenEndpoint"),
                    qc_token=authentication.get("qcToken"),
                    endpoints=RikenEndpoint(
                        submit_job=authentication.get("endpoints").get("submitJob"),
                        job_list=authentication.get("endpoints").get("jobList"),
                        job_status=authentication.get("endpoints").get("jobStatus"),
                        job_cancel=authentication.get("endpoints").get("jobCancel"),
                        job_delete=authentication.get("endpoints").get("jobDelete"),
                    ))
                , qc_type=authentication.get("metadata").get("qc_type")
            )
        raise Exception("Unsupported provider!")
