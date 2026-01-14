from dataclasses import dataclass

@dataclass
class RikenEndpoint:
  submit_job: str
  job_status: str
  job_cancel: str
  job_delete: str
  job_list: str

@dataclass
class RikenConfig:
  endpoints: RikenEndpoint
  client_id: str
  client_secret: str
  token_endpoint: str
  qc_token: str
