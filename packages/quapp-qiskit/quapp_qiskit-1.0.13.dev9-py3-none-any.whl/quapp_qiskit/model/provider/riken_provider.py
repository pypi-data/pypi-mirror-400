"""
    QApp Platform Project ibm_cloud_provider.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  ibm_cloud_provider.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime.accounts import ChannelType

from quapp_common.config.logging_config import job_logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider
import requests
from requests.auth import HTTPBasicAuth
from .data import RikenConfig

logger = job_logger('RikenProvider')


class RikenProvider(Provider):

    def collect_provider(self):
        #Not applicable for RikenProvider
        pass

    def __init__(self, config: RikenConfig, qc_type: int):
        super().__init__(ProviderTag.RIKEN)
        self.config = config
        self.qc_type = qc_type

    def get_backend(self, device_specification: str):
        logger.debug('Get backend from Riken')



        return RikenBackend(
            config= self.config,
            device_specification=device_specification,
            qc_type=self.qc_type
        )

class RikenBackend:
    def __init__(self,
        config: RikenConfig,
        device_specification: str = None,
        qc_type: int = 99999):
        self.config = config
        self.device_specification = device_specification
        self.qc_type = qc_type

    def get_token(self):
        data = {
            'grant_type': 'client_credentials',
            'scope': 'apiauth/read'
        }

        # 2. Gọi API Token Endpoint
        try:
            auth = HTTPBasicAuth(self.config.client_id, self.config.client_secret)

            response = requests.post(
                self.config.token_endpoint,
                data=data,
                auth=auth,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )

            response.raise_for_status()

            # 3. Parse kết quả
            token_data = response.json()

            # Lấy access_token
            access_token = token_data.get('access_token')

            if not access_token:
                raise ValueError("No access_token")

            return access_token

        except requests.exceptions.RequestException as e:
            logger.error(e)
            raise e

    def submit_job(self, qasm_base64: str,
        shots: int,
        priority: int = 1):

        payload = {
            "token": self.config.qc_token,
            "priority": priority,
            "qasm": qasm_base64,
            "shots": shots,
            "qc_type": self.qc_type
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_token()}"
        }

        try:
            response = requests.post(self.config.endpoints.submit_job, json=payload, headers=headers,
                                     timeout=30)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(e)

    def get_job_status(self, job_id: str):

        payload = {
            "token": self.config.qc_token,
            "job_id": job_id
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_token()}"
        }

        try:
            response = requests.post(self.config.endpoints.job_status, json=payload, headers=headers,
                                     timeout=30)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(e)