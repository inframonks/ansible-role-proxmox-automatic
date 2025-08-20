# Ansible Role: proxmox_automatic

[![CI](https://github.com/inframonks/ansible-role-proxmox-automatic/workflows/CI/badge.svg)](https://github.com/inframonks/ansible-role-proxmox-automatic/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Ansible Galaxy](https://img.shields.io/badge/ansible--galaxy-proxmox__automatic-blue.svg)](https://galaxy.ansible.com/inframonks/proxmox_automatic)
[![Ansible](https://img.shields.io/badge/ansible-2.14%2B-red.svg)](https://ansible.com)
[![GitHub release](https://img.shields.io/github/release/inframonks/ansible-role-proxmox-automatic.svg)](https://github.com/inframonks/ansible-role-proxmox-automatic/releases)

This role automatically creates virtual machines on a **Proxmox VE Cluster** with individual **Kickstart configurations**. It generates customized ISO files, uploads them to Proxmox, and starts VMs with complex storage and network configurations.

## 🚀 Features

- **Automatic Dependency Installation**: Installs `xorriso` and `syslinux` on various distributions
- **Hierarchical Configuration**: Defaults → group_vars → host_vars → Playbook variables
- **Dynamic Storage Configuration**: Multi-disk support with LVM and flexible sizes
- **Automatic Kickstart Generation**: Individual `.cfg` files per VM
- **ISO Management**: Automatic ISO creation and upload to Proxmox
- **Flexible User Configuration**: Hierarchical user management with SSH keys
- **Multi-Network Support**: Multiple network interfaces with VLAN support
- **Rocky Linux 9 Optimized**: Fixed repository URLs, modern interface names

## 📋 Requirements

### Proxmox VE
- API user with VM management permissions
- Storage for VMs and ISOs

### Ansible Controller Dependencies

**Automatic installation (recommended):**
```yaml
proxmox_automatic_install_dependencies: true
```

**Supported systems:**
- Red Hat family (RHEL, Rocky, CentOS, Fedora)
- Debian family (Debian, Ubuntu)
- macOS (via Homebrew)
- SUSE family (openSUSE, SLES)
- Arch family (Arch, Manjaro)

### Collections

**Required Ansible collections:**
```bash
ansible-galaxy collection install -r collections/requirements.yml
```

**Note:** This role uses the new `community.proxmox` collection, which was split from `community.general` starting with version 11.0.0.

## 🔧 Quick Start

### Prerequisites

**Install required collections:**
```bash
ansible-galaxy collection install -r collections/requirements.yml
```

### Minimal Configuration

```yaml
---
- name: Create virtual machines
  hosts: vm_hosts
  roles:
    - proxmox_automatic
  vars:
    proxmox_automatic_api_host: "pve.example.com"
    proxmox_automatic_api_password: "{{ vault_proxmox_password }}"
    proxmox_automatic_install_dependencies: true
```

### Simple VM Configuration

```yaml
# inventory/host_vars/webserver01.yml
proxmox_automatic_vmid: 101
proxmox_automatic_hypervisor: "pve-node01"
proxmox_automatic_networks:
  - name: net0
    vlanid: 100
    ip: "192.168.1.10"
    netmask: "255.255.255.0"
    gateway: "192.168.1.1"
```

## 💡 Understanding Hierarchical Configuration

The role uses an **intelligent merge system** that combines configurations from different levels:

### 🔄 Merge Order
```
defaults/main.yml → group_vars/ → host_vars/ → Playbook variables
(lowest)                                       (highest priority)
```

### 📝 Practical Example

**1. defaults/main.yml** (Base for all VMs):
```yaml
proxmox_automatic_storage_config_defaults:
  - name: virtio0
    size: "20"
    disk: vda
    bootloader: true
    # Standard LVM configuration
```

**2. group_vars/databases.yml** (All database servers):
```yaml
proxmox_automatic_storage_config_group_vars:
  - name: virtio0
    size: "40"  # Larger system disk for DB servers
  - name: virtio1
    size: "200"  # Additional database disk
    disk: vdb
```

**3. host_vars/db01.yml** (Specific server):
```yaml
proxmox_automatic_storage_config_host_vars:
  - name: virtio1
    size: "500"  # Overrides group_vars: Even larger DB disk
  - name: virtio2
    size: "100"  # Additional backup disk
    disk: vdc
```

**🎯 Final Result for db01:**
```yaml
# The role automatically generates:
storage_final:
  - name: virtio0
    size: "40"        # Taken from group_vars
    disk: vda         # Taken from defaults
    bootloader: true  # Taken from defaults
  - name: virtio1
    size: "500"       # Overridden by host_vars
    disk: vdb         # Taken from group_vars
  - name: virtio2
    size: "100"       # Added by host_vars
    disk: vdc         # Added by host_vars
```

### ✅ Benefits of this System

- **DRY (Don't Repeat Yourself)**: Define common configuration only once
- **Flexibility**: Each level can selectively override or extend
- **Maintainability**: Changes to group standards automatically affect all hosts
- **Scalability**: New VMs automatically inherit sensible defaults

## 🎛️ Configuration

### Important Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `proxmox_automatic_api_host` | Proxmox Host | **required** |
| `proxmox_automatic_api_user` | API User | `svc_ansible_rw@pam` |
| `proxmox_automatic_api_password` | API Password | **required** |
| `proxmox_automatic_install_dependencies` | Auto-install dependencies | `false` |
| `proxmox_automatic_vmid` | VM ID | **required** |
| `proxmox_automatic_hypervisor` | Target hypervisor | **required** |
| `proxmox_automatic_memory` | RAM in MB | `2048` |
| `proxmox_automatic_vcpu` | vCPUs | `2` |

### Storage Configuration

**Hierarchical System:**
The role intelligently combines configurations from different levels:

1. **`defaults/main.yml`** - Base configuration (virtio0 with standard partitioning)
2. **`group_vars/webservers.yml`** - Group-specific additions 
3. **`host_vars/server01.yml`** - Host-specific configuration
4. **Playbook variables** - Highest priority, overrides everything

**Combination Logic:**
```yaml
# defaults/main.yml defines:
proxmox_automatic_storage_config_defaults:
  - name: virtio0
    size: "20"
    disk: vda
    bootloader: true

# group_vars/databases.yml adds:
proxmox_automatic_storage_config_group_vars:
  - name: virtio0
    size: "40"  # Overrides default size
  - name: virtio1
    size: "200"  # New disk for database

# host_vars/db01.yml adds:
proxmox_automatic_storage_config_host_vars:
  - name: virtio2
    size: "100"  # Additional backup disk

# Result: VM gets all 3 disks
# virtio0: 40GB (overridden), virtio1: 200GB, virtio2: 100GB
```

**Basic Example:**
```yaml
proxmox_automatic_storage_config:
  - name: virtio0
    size: "20"
    # More options in complete documentation
```

### Network Configuration

**Hierarchical System:**
Similar to storage, network configurations are also intelligently combined:

```yaml
# defaults/main.yml - No networks (empty)
proxmox_automatic_networks_defaults: []

# group_vars/webservers.yml - Standard management interface
proxmox_automatic_networks_group_vars:
  - name: net0
    vlanid: 100
    bridge: "vmbr1"

# host_vars/webserver01.yml - Host-specific IP + additional interface
proxmox_automatic_networks_host_vars:
  - name: net0
    ip: "192.168.1.10"    # Extends group_vars configuration
    netmask: "255.255.255.0"
    gateway: "192.168.1.1"
  - name: net1            # Additional backup interface
    ip: "10.0.1.10"
    netmask: "255.255.255.0"
    vlanid: 200

# Result: VM gets both interfaces with combined configuration
```

**Multi-Interface Support:**
```yaml
proxmox_automatic_networks:
  - name: net0
    ip: "192.168.1.10"
    netmask: "255.255.255.0"
    gateway: "192.168.1.1"
    vlanid: 100
  - name: net1
    ip: "10.0.1.10"
    netmask: "255.255.255.0"
    vlanid: 200
```

### User Configuration

```yaml
proxmox_automatic_users:
  - name: "admin"
    password: "<filleme>"
    password_encrypted: false  # Set to true if password is already encrypted
    gecos: "Admin User"
    uid: 1000
    gid: 1000
    groups: ["wheel"]
    ssh_key: "<fille with publickey>"
    sudo_commands: "ALL"  # NOPASSWD: ALL, or specific commands like "/bin/systemctl, /usr/bin/docker"
    sudo_nopasswd: true
  - name: "ansible"
    password: "<filleme>"
    password_encrypted: false
    gecos: "Ansible Serviceaccount"
    uid: 1001
    gid: 1001
    groups: []
    ssh_key: "<fille with publickey>"
    sudo_commands: "ALL"
    sudo_nopasswd: true
```

## 🚦 Execution

```bash
# Install collections and dependencies
ansible-galaxy collection install -r collections/requirements.yml
ansible-playbook playbooks/create_vms.yml --tags proxmox_automatic_dependencies

# Create single VM
ansible-playbook playbooks/create_vms.yml -l webserver01

# Create group of VMs
ansible-playbook playbooks/create_vms.yml -l webservers

# Create all VMs
ansible-playbook playbooks/create_vms.yml
```

## 🔍 Debugging

```bash
# Check kickstart files
ls -la playbooks/kickstart-files/
cat playbooks/kickstart-files/ks-hostname.cfg

# Test only template generation
ansible-playbook playbooks/create_vms.yml -l hostname --tags kickstart

# Verbose output
ansible-playbook playbooks/create_vms.yml -l hostname -vvv
```

## 📚 Advanced Examples

<details>
<summary><strong>Multi-Disk Database Server</strong></summary>

```yaml
# inventory/host_vars/database01.yml
proxmox_automatic_storage_config:
  - name: virtio0  # System
    size: 40
    disk: vda
    bootloader: true
    vg:
      - name: system
        lv:
          - name: root
            mount: /
            size: 4096
            fstype: xfs
          - name: swap
            mount: swap
            size: 4096
            fstype: swap
          - name: home
            mount: /home
            size: 1024
            grow: true
            fstype: xfs
            
  - name: virtio1  # Database Storage
    size: 200
    disk: vdb
    vg:
      - name: database
        lv:
          - name: mysql
            mount: /var/lib/mysql
            size: 1024
            grow: true
            fstype: xfs
```
</details>

<details>
<summary><strong>Kubernetes Cluster Node</strong></summary>

```yaml
# inventory/group_vars/kubernetes.yml
proxmox_automatic_packages:
  - docker-ce
  - kubeadm
  - kubelet
  - kubectl

proxmox_automatic_storage_config:
  - name: virtio1  # Container Storage
    size: 100
    disk: vdb
    vg:
      - name: containers
        lv:
          - name: docker
            mount: /var/lib/docker
            size: 1024
            grow: true
            fstype: xfs
```
</details>

<details>
<summary><strong>Monitoring Stack</strong></summary>

```yaml
# inventory/host_vars/monitoring01.yml
proxmox_automatic_storage_config:
  - name: virtio1  # Prometheus Storage
    size: 500
    disk: vdb
    vg:
      - name: monitoring
        lv:
          - name: prometheus
            mount: /var/lib/prometheus
            size: 1024
            grow: true
            fstype: xfs

proxmox_automatic_networks:
  - name: net0  # Management
    vlanid: 100
    ip: "192.168.1.200"
    netmask: "255.255.255.0"
    gateway: "192.168.1.1"
  - name: net1  # Monitoring Network
    vlanid: 150
    ip: "10.0.15.200"
    netmask: "255.255.255.0"
```
</details>

## 🐛 Troubleshooting

### Common Issues

1. **Dependencies missing**
   - **Solution:** Set `proxmox_automatic_install_dependencies: true`

2. **"new lv is too large to fit in free space"**
   - **Problem:** LV sizes exceed available storage
   - **Solution:** Use `grow: true` for only one LV per VG

3. **SSH connection fails**
   - **Problem:** SSH keys or user configuration issues
   - **Solution:** Configure `proxmox_automatic_users` correctly

### Check Logs

```bash
# Follow kickstart installation (in Proxmox Console)
tail -f /root/anaconda-ks-pre.log
tail -f /root/anaconda-ks-post.log

# Ansible logs
export ANSIBLE_LOG_PATH=/tmp/ansible.log
ansible-playbook ... -vvv
```

## 🔒 Security

```yaml
# Recommended vault configuration
ansible-vault create inventory/group_vars/all/vault.yml

# vault.yml content:
vault_admin_password: "secure_password_123"
vault_ansible_password: "service_account_pwd"
vault_proxmox_password: "proxmox_api_password"
```

## 📁 Directory Structure

```
roles/proxmox_automatic/
├── defaults/main.yml           # Default configuration
├── tasks/
│   ├── main.yml               # Main tasks
│   ├── install_dependencies.yml  # Dependency installation
│   ├── create_kickstart.yml   # Kickstart generation
│   └── create_vm.yml          # VM creation
├── templates/
│   └── kickstart.cfg.j2       # Kickstart template
└── README.md                  # This file

playbooks/
├── kickstart-files/          # Generated .cfg files
├── kickstart-isos/           # Generated .iso files  
└── create_vms.yml           # Main playbook
```

## 📖 Complete Documentation

<details>
<summary><strong>All Variables (Click to expand)</strong></summary>

### VM-specific Variables (per host)

| Variable | Description | Default |
|----------|-------------|---------|
| `proxmox_automatic_vmid` | Proxmox VM ID | **required** |
| `proxmox_automatic_hypervisor` | Target hypervisor | **required** |
| `proxmox_automatic_memory` | Memory (MB) | `2048` |
| `proxmox_automatic_vcpu` | vCPUs | `2` |
| `proxmox_automatic_cpu_type` | CPU type | `"x86-64-v3"` |
| `proxmox_automatic_sockets` | CPU sockets | `1` |
| `proxmox_automatic_state` | VM state | `"present"` |
| `proxmox_automatic_kvm` | Enable KVM | `true` |
| `proxmox_automatic_os_type` | OS type | `"l26"` |
| `proxmox_automatic_onboot` | Start VM on boot | `true` |
| `proxmox_automatic_boot_order` | Boot order | `1` |
| `proxmox_automatic_vm_pool` | VM pool | `omit` |

### System Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `proxmox_automatic_timezone` | Timezone | `"Europe/Berlin"` |
| `proxmox_automatic_keyboard_layout` | Keyboard layout | `"de"` |
| `proxmox_automatic_language` | System language | `"en_US.UTF-8"` |
| `proxmox_automatic_selinux_mode` | SELinux mode | `"enforcing"` |
| `proxmox_automatic_firewall_enabled` | Enable firewall | `true` |

### Network Detail Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `vlanid` | VLAN ID | `100` |
| `ip` | IP address | `"192.168.1.10"` |
| `netmask` | Netmask | `"255.255.255.0"` |
| `gateway` | Gateway | `"192.168.1.1"` |
| `bridge` | Proxmox bridge | `"vmbr1"` |
| `model` | NIC model | `"virtio"` |
| `mac` | MAC address | `"02:00:00:aa:bb:cc"` |
| `mtu` | MTU size | `1500` |

### Storage Detail Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `size` | Disk size in GB | `"20"` |
| `disk` | Disk device | `"vda"` |
| `bootloader` | Boot disk | `true` |
| `grow` | LV uses remaining space | `true` |
| `mount` | Mount point | `/`, `/var`, `swap` |
| `fstype` | Filesystem | `xfs`, `ext4`, `swap` |

</details>

<details>
<summary><strong>Repository Configuration</strong></summary>

```yaml
proxmox_automatic_repos:
  - name: "BaseOS"
    mirrorlist: "http://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=BaseOS-$releasever"
  - name: "AppStream"
    mirrorlist: "http://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=AppStream-$releasever"
  - name: "EPEL"
    baseurl: "https://download.fedoraproject.org/pub/epel/9/Everything/x86_64/"
```
</details>

<details>
<summary><strong>Complete Host-Vars Example</strong></summary>

```yaml
# inventory/host_vars/server01.yml
proxmox_automatic_api_host: "192.168.1.100"
proxmox_automatic_vmid: 101
proxmox_automatic_hypervisor: "pve-node01"
proxmox_automatic_memory: 4096
proxmox_automatic_vcpu: 4

proxmox_automatic_storage_config:
  - name: virtio1
    size: "100"
    pve_options:
      iothread: 1
      discard: "on"

proxmox_automatic_networks:
  - name: net0
    vlanid: 100
    ip: "192.168.1.101"
    netmask: "255.255.255.0"
    gateway: "192.168.1.1"
    bridge: "vmbr1"
  - name: net1
    ip: "10.0.1.101"
    netmask: "255.255.255.0"
    vlanid: 200
    bridge: "vmbr1"
    mtu: 9000
```
</details>

## 📞 Support

For questions or issues, please create an issue in the repository.

## 🤝 Contributing

Contributions are welcome! Please create issues and pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

- ✅ **Commercial use** - Use in commercial projects
- ✅ **Modification** - Modify and adapt the code
- ✅ **Distribution** - Distribute copies
- ✅ **Private use** - Use for private projects
- ✅ **Patent use** - Use any patents from contributors
- ❗ **License and copyright notice** - Include license in copies
- ❌ **Liability** - No warranty or liability
- ❌ **Warranty** - No warranty provided
