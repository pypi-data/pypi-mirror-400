#  Quapp Platform Project
#  qiskit_device_factory.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk
from quapp_common.factory.device_factory import DeviceFactory
from quapp_common.model.provider.provider import Provider

from ..model.device.ibm_cloud_device import IbmCloudDevice
from ..model.device.ibm_quantum_device import IbmQuantumDevice

from ..model.device.riken_device import RikenDevice
from ..model.device.oqc_cloud_device import OqcCloudDevice
from ..model.device.qapp_qiskit_device import QappQiskitDevice
from quapp_common.config.logging_config import logger


class QiskitDeviceFactory(DeviceFactory):

    @staticmethod
    def create_device(provider: Provider, device_specification: str,
            authentication: dict, sdk: Sdk):
        logger.info("[QiskitDeviceFactory] create_device()")

        provider_type = ProviderTag.resolve(provider.get_provider_type().value)



        if ProviderTag.QUAO_QUANTUM_SIMULATOR.__eq__(
                provider_type) and Sdk.QISKIT.__eq__(sdk):
            logger.info("Created QUAPP_QUANTUM_SIMULATOR device")
            return QappQiskitDevice(provider, device_specification)

        if ProviderTag.IBM_QUANTUM.__eq__(provider_type):
            logger.info("Created IBM_QUANTUM device")
            return IbmQuantumDevice(provider, device_specification)

        if ProviderTag.IBM_CLOUD.__eq__(provider_type):
            logger.info("Created IBM_CLOUD device")
            return IbmCloudDevice(provider, device_specification)

        if ProviderTag.RIKEN.__eq__(provider_type):
            logger.info("Created RIKEN device")
            return RikenDevice(provider, device_specification)

        if ProviderTag.OQC_CLOUD.__eq__(provider_type):
            logger.info("Created OQC_CLOUD device")
            return OqcCloudDevice(provider, device_specification)

        raise Exception("Unsupported device!")
