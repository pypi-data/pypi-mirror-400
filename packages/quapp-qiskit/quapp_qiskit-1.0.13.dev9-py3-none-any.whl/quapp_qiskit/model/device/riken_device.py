"""
    QApp Platform Project ibm_cloud_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  ibm_cloud_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

import time
from qiskit import qasm2
import base64

from quapp_common.data.device.circuit_running_option import CircuitRunningOption


from .qiskit_device import QiskitDevice


class RikenDevice(QiskitDevice):
    def _is_simulator(self) -> bool:
        return True

    def _create_job(self, circuit, options: CircuitRunningOption):

        qasm = qasm2.dumps(circuit)
        riken_response = self.device.submit_job(qasm,options.shots)

        job_id = riken_response.get("jobId")

        while True:
            status_response = self.device.get_job_status(job_id)
            current_status = status_response.get("status")

            if current_status != 4 and current_status != 5 and current_status != 6:
                self.logger.info(f"Job status: {current_status}. Waiting for completion...")
                time.sleep(5)
            else:
                self.logger.info(
                    f"Job ended, status: {current_status}.")
                return status_response



    def _get_job_status(self, job) -> str:
        return "DONE"

    def _calculate_execution_time(self, job_result):
        # not implemented
        pass

    def _produce_histogram_data(self, job_result) -> dict | None:
        return None

    def _get_provider_job_id(self, job) -> str:
        self.logger.debug('Get provider job id')
        return job.get("qcJobId")


    def _get_job_result(self, job):
        return job.get("result")

    def _get_shots(self, job_result) -> int | None:
        return None
