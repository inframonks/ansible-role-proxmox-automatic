from ansible.module_utils.basic import AnsibleModule
import requests
import os

DOCUMENTATION = '''
---
module: proxmox_automatic_upload_iso
short_description: Upload an ISO file to a Proxmox storage. The ansible.builtin.uri module doesn't work and locks API access to PVE hosts for the client.
description:
  - Uploads an ISO file to a specified storage on a Proxmox host.
options:
  proxmox_automatic_api_host:
    description: Proxmox host (FQDN or IP) without protocol (e.g. "pve01.id.lenhardt.cc").
    required: true
    type: str
  proxmox_automatic_api_user:
    description: Proxmox username (e.g. "root@pam"). Required if not using API token.
    required: false
    type: str
  proxmox_automatic_api_password:
    description: Proxmox password. Required if not using API token.
    required: false
    type: str
  proxmox_automatic_api_token_id:
    description: API token ID in format "user@realm!tokenname".
    required: false
    type: str
  proxmox_automatic_api_token_secret:
    description: API token secret.
    required: false
    type: str
  proxmox_automatic_storage:
    description: Target storage where ISO should be uploaded.
    required: true
    type: str
  proxmox_automatic_hypervisor:
    description: Proxmox node where the storage is located.
    required: true
    type: str
  proxmox_automatic_iso_path:
    description: Path to the local ISO file to upload.
    required: true
    type: str
  proxmox_automatic_iso_name:
    description: Name of the ISO file on Proxmox (e.g., "custom.iso").
    required: true
    type: str
'''


def upload_iso(module, api_host, node, storage, iso_path, iso_name, headers):
    url = f"https://{api_host}:8006/api2/json/nodes/{node}/storage/{storage}/upload"
    files = {
        'content': (None, 'iso'),
        'filename': (iso_name, open(iso_path, 'rb'), 'application/octet-stream')
    }

    response = requests.post(url, headers=headers, files=files, verify=False)

    if response.status_code == 200:
        return {'changed': True, 'msg': 'ISO upload successful', 'response': response.json()}
    else:
        module.fail_json(msg=f"Failed to upload ISO. Response: {response.text}", status=response.status_code)


def main():
    module_args = {
        'proxmox_automatic_api_host': {'type': 'str', 'required': True},
        'proxmox_automatic_api_user': {'type': 'str', 'required': False},
        'proxmox_automatic_api_password': {'type': 'str', 'required': False, 'no_log': True},
        'proxmox_automatic_api_token_id': {'type': 'str', 'required': False},
        'proxmox_automatic_api_token_secret': {'type': 'str', 'required': False, 'no_log': True},
        'proxmox_automatic_storage': {'type': 'str', 'required': True},
        'proxmox_automatic_hypervisor': {'type': 'str', 'required': True},
        'proxmox_automatic_iso_path': {'type': 'str', 'required': True},
        'proxmox_automatic_iso_name': {'type': 'str', 'required': True},
    }

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    api_host = module.params['proxmox_automatic_api_host']
    node = module.params['proxmox_automatic_hypervisor']
    storage = module.params['proxmox_automatic_storage']
    iso_path = module.params['proxmox_automatic_iso_path']
    iso_name = module.params['proxmox_automatic_iso_name']

    if not os.path.isfile(iso_path):
        module.fail_json(msg=f"ISO file not found: {iso_path}")

    headers = {}
    if module.params['proxmox_automatic_api_token_id'] and module.params['proxmox_automatic_api_token_secret']:
        headers['Authorization'] = f"PVEAPIToken={module.params['proxmox_automatic_api_token_id']}={module.params['proxmox_automatic_api_token_secret']}"
    elif module.params['proxmox_automatic_api_user'] and module.params['proxmox_automatic_api_password']:
        auth_url = f"https://{api_host}:8006/api2/json/access/ticket"
        auth_data = {'username': module.params['proxmox_automatic_api_user'], 'password': module.params['proxmox_automatic_api_password']}
        response = requests.post(auth_url, data=auth_data, verify=False)
        if response.status_code != 200:
            module.fail_json(msg="Failed to authenticate with Proxmox API", response=response.text)
        token = response.json()['data']['ticket']
        headers['Authorization'] = f"PVEAuthCookie={token}"
    else:
        module.fail_json(msg="Either API token or username/password must be provided.")

    result = upload_iso(module, api_host, node, storage, iso_path, iso_name, headers)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
