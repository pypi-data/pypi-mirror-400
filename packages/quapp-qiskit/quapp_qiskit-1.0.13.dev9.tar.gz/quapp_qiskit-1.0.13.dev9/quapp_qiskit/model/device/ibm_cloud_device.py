"""
    QApp Platform Project ibm_cloud_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  ibm_cloud_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from qiskit_ibm_runtime import SamplerV2 as Sampler
from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from qiskit import transpile
import time


from .qiskit_device import QiskitDevice


class IbmCloudDevice(QiskitDevice):
    def _is_simulator(self) -> bool:
        self.logger.debug('Checking if simulator')
        simulator = self.device.configuration().simulator
        self.logger.debug(f'Simulator: {simulator}')
        return True

    def _create_job(self, circuit, options: CircuitRunningOption):
        self.logger.debug(f"Creating job with {options.shots} shots")

        transpiled_circuit = transpile(circuits=circuit, backend=self.device)
        self.logger.debug('Transpiled circuit created successfully')

        sampler = Sampler(self.device)
        self.logger.debug('Sampler created successfully')

        job = sampler.run([transpiled_circuit], shots=options.shots)
        self.logger.info('Job submitted successfully')

        while True:
            current_status = job.status()
            if current_status != "ERROR" and current_status != "DONE" and current_status != "CANCELLED":
                self.logger.info(f"Job status: {current_status}. Waiting for completion...")
                time.sleep(5)
            else:
                self.logger.info(
                    f"Job ended, status: {current_status}.")
                break

        self.execution_time = job.usage()  # Seconds

        return job
    def _get_job_status(self, job) -> str:
        return "DONE"

    def _calculate_execution_time(self, job_result):
        # calculate execution time is done in _create_job for IBM Cloud
        pass