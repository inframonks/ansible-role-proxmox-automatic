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

**Note:** This role uses the new `community.proxmox` collection.

## 📚 Quick Start

### Minimal Configuration

```yaml
# playbook.yml
- hosts: proxmox_vms
  roles:
    - inframonks.proxmox_automatic
  vars:
    proxmox_automatic_api_host: "pve.example.com"
    proxmox_automatic_api_password: "your-api-password"
    proxmox_automatic_hypervisor: "pve-node1"
```

```ini
# inventory
[proxmox_vms]
web01 proxmox_automatic_vmid=101 ansible_host=10.1.1.10
db01 proxmox_automatic_vmid=102 ansible_host=10.1.1.20
```

## 🎯 Understanding Hierarchical Configuration

This role uses an intelligent merge system that combines configurations from different levels:

**Priority Order (highest to lowest):**
```
Playbook variables → host_vars/ → group_vars/ → defaults/main.yml
```

### Storage Configuration Hierarchy

The role supports three levels of storage configuration:

- `proxmox_automatic_storage_config_defaults` - Base configuration
- `proxmox_automatic_storage_config_group_vars` - Group-specific additions
- `proxmox_automatic_storage_config_host_vars` - Host-specific configuration

**Example:**

```yaml
# defaults/main.yml - All VMs get this base disk
proxmox_automatic_storage_config_defaults:
  - name: virtio0
    size: "20"
    disk: vda
    bootloader: true

# group_vars/databases.yml - Database servers get additional storage
proxmox_automatic_storage_config_group_vars:
  - name: virtio0
    size: "40"  # Override base size
  - name: virtio1
    size: "200"  # Additional data disk

# host_vars/db01.yml - Specific host gets backup disk
proxmox_automatic_storage_config_host_vars:
  - name: virtio2
    size: "100"  # Backup storage
```

**Result:** `db01` will have 3 disks: 40GB system, 200GB data, 100GB backup.

### User Configuration Hierarchy

Similar hierarchical approach for users:

```yaml
# defaults/main.yml - Standard admin user
proxmox_automatic_users_defaults:
  root:
    password: "$6$encrypted_password"
    ssh_key: "ssh-rsa AAAA..."

# group_vars/webservers.yml - Web-specific service user
proxmox_automatic_users_group_vars:
  nginx:
    shell: "/bin/false"
    home: "/var/www"

# host_vars/web01.yml - Host-specific developer access
proxmox_automatic_users_host_vars:
  developer:
    password: "$6$dev_password"
    groups: ["wheel"]
```

### Network Configuration Hierarchy

```yaml
# defaults/main.yml - Standard network
proxmox_automatic_networks_defaults:
  - name: net0
    bridge: vmbr0

# group_vars/databases.yml - Database VLAN
proxmox_automatic_networks_group_vars:
  - name: net1
    bridge: vmbr1
    vlanid: 200

# host_vars/db01.yml - Additional management interface
proxmox_automatic_networks_host_vars:
  - name: net2
    bridge: vmbr2
    vlanid: 100
```

## 🛠️ Variables Reference

### Core Configuration

##### `proxmox_automatic_install_dependencies`
**Default:** `false`  
**Description:** Automatically install dependencies (xorriso, syslinux) on Ansible Controller

**Example:**
```yaml
proxmox_automatic_install_dependencies: true
```

##### `proxmox_automatic_files_dir`
**Default:** `"kickstart-files"`  
**Description:** Path for Kickstart files

**Example:**
```yaml
proxmox_automatic_files_dir: "/tmp/ks-files"
```

##### `proxmox_automatic_iso_dir`
**Default:** `"kickstart-isos"`  
**Description:** Path for generated ISO files

**Example:**
```yaml
proxmox_automatic_iso_dir: "/var/lib/isos"
```

##### `proxmox_automatic_iso_name`
**Default:** `"rocky9.6-ks"`  
**Description:** Name of the Kickstart ISO file (without .iso)

**Example:**
```yaml
proxmox_automatic_iso_name: "rocky9-custom"
```

### Proxmox API Configuration

##### `proxmox_automatic_api_host`
**Default:** *required*  
**Description:** FQDN or IP of the Proxmox API host

**Example:**
```yaml
proxmox_automatic_api_host: "pve.example.com"
```

##### `proxmox_automatic_api_user`
**Default:** `"svc_ansible_rw@pam"`  
**Description:** Username for Proxmox API

**Example:**
```yaml
proxmox_automatic_api_user: "ansible@pve"
```

##### `proxmox_automatic_api_password`
**Default:** *required*  
**Description:** Password for Proxmox API

**Example:**
```yaml
proxmox_automatic_api_password: "{{ vault_proxmox_password }}"
```

### VM Configuration

##### `proxmox_automatic_vmid`
**Default:** *optional*  
**Description:** Proxmox VM ID

**Example:**
```yaml
proxmox_automatic_vmid: 101
```

##### `proxmox_automatic_hypervisor`
**Default:** *required*  
**Description:** Proxmox Node (e.g. srv-hyp-01.local)

**Example:**
```yaml
proxmox_automatic_hypervisor: "pve-node1"
```

##### `proxmox_automatic_memory`
**Default:** `2048`  
**Description:** VM RAM in MB

**Example:**
```yaml
proxmox_automatic_memory: 4096
```

##### `proxmox_automatic_vcpu`
**Default:** `2`  
**Description:** Number of vCPUs

**Example:**
```yaml
proxmox_automatic_vcpu: 4
```

##### `proxmox_automatic_cpu_type`
**Default:** `"x86-64-v3"`  
**Description:** CPU type

**Example:**
```yaml
proxmox_automatic_cpu_type: "host"
```

##### `proxmox_automatic_sockets`
**Default:** `1`  
**Description:** Number of CPU sockets

**Example:**
```yaml
proxmox_automatic_sockets: 2
```

##### `proxmox_automatic_state`
**Default:** `"present"`  
**Description:** VM state

**Choices:** `["present", "absent"]`

**Example:**
```yaml
proxmox_automatic_state: "absent"  # To delete VM
```

##### `proxmox_automatic_kvm`
**Default:** `true`  
**Description:** Enable KVM

**Example:**
```yaml
proxmox_automatic_kvm: false  # For nested virtualization issues
```

##### `proxmox_automatic_os_type`
**Default:** `"l26"`  
**Description:** Operating system type

**Example:**
```yaml
proxmox_automatic_os_type: "l26"  # Linux 2.6+ kernel
```

##### `proxmox_automatic_onboot`
**Default:** `true`  
**Description:** Enable autostart

**Example:**
```yaml
proxmox_automatic_onboot: false
```

##### `proxmox_automatic_scsi_hw`
**Default:** `"virtio-scsi-single"`  
**Description:** SCSI controller type

**Example:**
```yaml
proxmox_automatic_scsi_hw: "virtio-scsi-pci"
```

##### `proxmox_automatic_machine`
**Default:** `"q35"`  
**Description:** Machine type

**Example:**
```yaml
proxmox_automatic_machine: "pc-i440fx-8.0"
```

##### `proxmox_automatic_hotplug`
**Default:** `"disk"`  
**Description:** Hotplug configuration

**Example:**
```yaml
proxmox_automatic_hotplug: "disk,network,usb"
```

### Storage Configuration

##### `proxmox_automatic_storage`
**Default:** *optional*  
**Description:** Optional: Override storage for VM and ISO

**Example:**
```yaml
proxmox_automatic_storage: "local-lvm"
```

##### `proxmox_automatic_pve_iso_storage`
**Default:** `"cephfs"`  
**Description:** Proxmox storage for ISOs

**Example:**
```yaml
proxmox_automatic_pve_iso_storage: "local"
```

##### `proxmox_automatic_pve_vm_storage`
**Default:** `"volumes"`  
**Description:** Proxmox storage for VM disks

**Example:**
```yaml
proxmox_automatic_pve_vm_storage: "ceph-rbd"
```

##### `proxmox_automatic_first_disk_size`
**Default:** `"20"`  
**Description:** Size of first disk in GB (number only)

**Example:**
```yaml
proxmox_automatic_first_disk_size: "50"
```

##### `proxmox_automatic_storage_config_defaults`
**Default:** `[]`  
**Description:** Default storage configuration for disks

**Supports hierarchical configuration:** This variable works together with `proxmox_automatic_storage_config_group_vars` and `proxmox_automatic_storage_config_host_vars` to create a complete storage layout.

**Example:**
```yaml
# Standard system disk for all VMs
proxmox_automatic_storage_config_defaults:
  - name: virtio0
    size: "20"
    disk: vda
    bootloader: true
    vg:
      - name: system
        lv:
          - name: root
            mount: /
            size: 8192
            fstype: xfs
          - name: swap
            mount: swap
            size: 2048
            fstype: swap
          - name: home
            mount: /home
            size: 1024
            grow: true
            fstype: xfs
```

**Group-specific storage additions:**
```yaml
# group_vars/databases.yml
proxmox_automatic_storage_config_group_vars:
  - name: virtio1
    size: "100"
    disk: vdb
    vg:
      - name: data
        lv:
          - name: mysql
            mount: /var/lib/mysql
            size: 1024
            grow: true
            fstype: xfs
```

**Host-specific storage:**
```yaml
# host_vars/db-master.yml
proxmox_automatic_storage_config_host_vars:
  - name: virtio2
    size: "200"
    disk: vdc
    vg:
      - name: backup
        lv:
          - name: backups
            mount: /backups
            size: 1024
            grow: true
            fstype: xfs
```

##### `proxmox_automatic_disks`
**Default:** `[]`  
**Description:** List of additional disks (name, size, storage)

**Example:**
```yaml
proxmox_automatic_disks:
  - name: virtio1
    size: "100"
    storage: "ceph-rbd"
  - name: virtio2
    size: "50"
    storage: "local-lvm"
```

### Network Configuration

##### `proxmox_automatic_defaultbridge`
**Default:** `"vmbr1"`  
**Description:** Default bridge for network cards

**Example:**
```yaml
proxmox_automatic_defaultbridge: "vmbr0"
```

##### `proxmox_automatic_networks`
**Default:** `[]`  
**Description:** List of additional network cards (bridge, vlanid, mtu, mac, model)

**Example:**
```yaml
proxmox_automatic_networks:
  - name: net0
    bridge: vmbr0
    vlanid: 100
    mtu: 1500
  - name: net1
    bridge: vmbr1
    vlanid: 200
    model: "virtio"
```

**Supports hierarchical configuration:**
```yaml
# defaults/main.yml
proxmox_automatic_networks_defaults:
  - name: net0
    bridge: vmbr0

# group_vars/webservers.yml
proxmox_automatic_networks_group_vars:
  - name: net1
    bridge: vmbr1
    vlanid: 100  # Web VLAN

# host_vars/web01.yml
proxmox_automatic_networks_host_vars:
  - name: net2
    bridge: vmbr2
    vlanid: 999  # Management VLAN
```

##### `proxmox_automatic_dhcp_enabled`
**Default:** `false`  
**Description:** Enable DHCP for network configuration. When true, static IPs are ignored.

**Example:**
```yaml
proxmox_automatic_dhcp_enabled: true
```

##### `proxmox_automatic_dns_servers`
**Default:** `["1.0.0.1", "1.1.1.1"]`  
**Description:** List of DNS servers

**Example:**
```yaml
proxmox_automatic_dns_servers:
  - "8.8.8.8"
  - "8.8.4.4"
  - "1.1.1.1"
```

### Boot Configuration

##### `proxmox_automatic_boot_order`
**Default:** `1`  
**Description:** Boot order

**Example:**
```yaml
proxmox_automatic_boot_order: 2
```

##### `proxmox_automatic_boot_order_up_wait`
**Default:** `3`  
**Description:** Wait time after start (seconds)

**Example:**
```yaml
proxmox_automatic_boot_order_up_wait: 10
```

##### `proxmox_automatic_boot_order_down_wait`
**Default:** `3`  
**Description:** Wait time after shutdown (seconds)

**Example:**
```yaml
proxmox_automatic_boot_order_down_wait: 5
```

### System Configuration

##### `proxmox_automatic_timezone`
**Default:** `"Europe/Berlin"`  
**Description:** VM timezone

**Example:**
```yaml
proxmox_automatic_timezone: "America/New_York"
```

##### `proxmox_automatic_language`
**Default:** `"en_US.UTF-8"`  
**Description:** System language

**Example:**
```yaml
proxmox_automatic_language: "de_DE.UTF-8"
```

##### `proxmox_automatic_keyboard_layout`
**Default:** `"de"`  
**Description:** Keyboard layout

**Example:**
```yaml
proxmox_automatic_keyboard_layout: "us"
```

##### `proxmox_automatic_keyboard_variants`
**Default:** `"de (nodeadkeys),us"`  
**Description:** Keyboard variants

**Example:**
```yaml
proxmox_automatic_keyboard_variants: "us,de"
```

##### `proxmox_automatic_ntp_servers`
**Default:** `["time.cloudflare.com"]`  
**Description:** List of NTP servers

**Example:**
```yaml
proxmox_automatic_ntp_servers:
  - "pool.ntp.org"
  - "time.google.com"
```

##### `proxmox_automatic_selinux_mode`
**Default:** `"enforcing"`  
**Description:** SELinux mode

**Choices:** `["enforcing", "permissive", "disabled"]`

**Example:**
```yaml
proxmox_automatic_selinux_mode: "permissive"
```

### Security Configuration

##### `proxmox_automatic_firewall_enabled`
**Default:** `true`  
**Description:** Enable firewall

**Example:**
```yaml
proxmox_automatic_firewall_enabled: false
```

##### `proxmox_automatic_firewall_services`
**Default:** `["ssh"]`  
**Description:** Firewall services to allow

**Example:**
```yaml
proxmox_automatic_firewall_services:
  - "ssh"
  - "http"
  - "https"
  - "mysql"
```

##### `proxmox_automatic_ssh_port`
**Default:** `22`  
**Description:** SSH port for the VM

**Example:**
```yaml
proxmox_automatic_ssh_port: 2222
```

### User Management

##### `proxmox_automatic_users`
**Default:** `[]`  
**Description:** List of users to be created during installation

**Supports hierarchical configuration:** This variable works together with `proxmox_automatic_users_defaults`, `proxmox_automatic_users_group_vars`, and `proxmox_automatic_users_host_vars`.

**Example:**
```yaml
# Standard users for all VMs
proxmox_automatic_users_defaults:
  root:
    password: "$6$rounds=656000$salt$hash"
    ssh_key: "ssh-rsa AAAA..."

# Group-specific users
proxmox_automatic_users_group_vars:
  webadmin:
    password: "$6$rounds=656000$salt$hash"
    groups: ["wheel", "apache"]
    shell: "/bin/bash"
    home: "/home/webadmin"

# Host-specific users
proxmox_automatic_users_host_vars:
  developer:
    password: "$6$rounds=656000$salt$hash"
    groups: ["wheel"]
    ssh_key: "ssh-rsa AAAA...developer-key"
```

##### `proxmox_automatic_service_user`
**Default:** `"ansible"`  
**Description:** Ansible service account created in the target system

**Example:**
```yaml
proxmox_automatic_service_user: "automation"
```

##### `proxmox_automatic_service_password`
**Default:** `""`  
**Description:** Password for the Ansible service account

**Example:**
```yaml
proxmox_automatic_service_password: "{{ vault_service_password }}"
```

##### `proxmox_automatic_service_ssh_key`
**Default:** `""`  
**Description:** SSH public key for the Ansible service account

**Example:**
```yaml
proxmox_automatic_service_ssh_key: "ssh-rsa AAAA...ansible-controller-key"
```

##### `proxmox_automatic_service_gecos`
**Default:** `"Ansible Serviceaccount"`  
**Description:** Comment/GECOS for the Ansible service account

**Example:**
```yaml
proxmox_automatic_service_gecos: "Automation Service Account"
```

### Host Management

##### `proxmox_automatic_host_description`
**Default:** `"Managed by Ansible"`  
**Description:** Host description

**Example:**
```yaml
proxmox_automatic_host_description: "Web Server - Production"
```

##### `proxmox_automatic_host_responsible`
**Default:** `"admin@example.com"`  
**Description:** Person responsible for the host

**Example:**
```yaml
proxmox_automatic_host_responsible: "webteam@company.com"
```

##### `proxmox_automatic_additional_hosts`
**Default:** `[]`  
**Description:** Additional hosts entries for /etc/hosts

**Example:**
```yaml
proxmox_automatic_additional_hosts:
  - ip: "10.1.1.50"
    hostname: "db.internal.com"
    aliases: ["database", "mysql"]
  - ip: "10.1.1.60"
    hostname: "cache.internal.com"
```

### SMTP Configuration

##### `proxmox_automatic_smtp_host`
**Default:** `"smtp.example.com"`  
**Description:** SMTP server for email delivery

**Example:**
```yaml
proxmox_automatic_smtp_host: "mail.company.com"
```

##### `proxmox_automatic_smtp_port`
**Default:** `587`  
**Description:** SMTP port

**Example:**
```yaml
proxmox_automatic_smtp_port: 25
```

##### `proxmox_automatic_smtp_from`
**Default:** `"noreply@example.com"`  
**Description:** Sender email address

**Example:**
```yaml
proxmox_automatic_smtp_from: "system@company.com"
```

##### `proxmox_automatic_smtp_user`
**Default:** `"<fillme>"`  
**Description:** SMTP username

**Example:**
```yaml
proxmox_automatic_smtp_user: "{{ vault_smtp_user }}"
```

##### `proxmox_automatic_smtp_password`
**Default:** `"<fillme>"`  
**Description:** SMTP password

**Example:**
```yaml
proxmox_automatic_smtp_password: "{{ vault_smtp_password }}"
```

##### `proxmox_automatic_smtp_root`
**Default:** `"<fillme>"`  
**Description:** Email address for root notifications

**Example:**
```yaml
proxmox_automatic_smtp_root: "sysadmin@company.com"
```

### Services Configuration

##### `proxmox_automatic_enabled_services`
**Default:** `["sshd", "rsyslog", "chronyd", "NetworkManager"]`  
**Description:** Services to enable at boot

**Example:**
```yaml
proxmox_automatic_enabled_services:
  - "sshd"
  - "httpd"
  - "mysqld"
  - "chronyd"
```

##### `proxmox_automatic_disabled_services`
**Default:** `[]`  
**Description:** Services to disable

**Example:**
```yaml
proxmox_automatic_disabled_services:
  - "postfix"
  - "cups"
  - "bluetooth"
```

### Package Management

##### `proxmox_automatic_packages`
**Default:** `[]`  
**Description:** List of packages to install in Kickstart

**Example:**
```yaml
proxmox_automatic_packages:
  - "vim"
  - "htop"
  - "git"
  - "curl"
  - "wget"
```

##### `proxmox_automatic_package_retries`
**Default:** `5`  
**Description:** Number of retries for package installation

**Example:**
```yaml
proxmox_automatic_package_retries: 3
```

##### `proxmox_automatic_package_timeout`
**Default:** `20`  
**Description:** Timeout for package installation (seconds)

**Example:**
```yaml
proxmox_automatic_package_timeout: 60
```

##### `proxmox_automatic_minimal_environment`
**Default:** `"@^minimal-environment"`  
**Description:** Minimal environment for installation

**Example:**
```yaml
proxmox_automatic_minimal_environment: "@^server-product-environment"
```

##### `proxmox_automatic_install_languages`
**Default:** `"en"`  
**Description:** Installed language packages

**Example:**
```yaml
proxmox_automatic_install_languages: "en de fr"
```

### Repository Configuration

##### `proxmox_automatic_repos`
**Default:** `[]`  
**Description:** List of additional repositories

**Example:**
```yaml
proxmox_automatic_repos:
  - name: "epel"
    baseurl: "https://download.fedoraproject.org/pub/epel/9/Everything/$basearch/"
    gpgcheck: true
    gpgkey: "https://download.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-9"
```

##### `proxmox_automatic_url_baseurl`
**Default:** `""`  
**Description:** Base URL for Rocky Linux (e.g. http://mirror.example.com/rocky/9/updates/x86_64/Packages/)

**Example:**
```yaml
proxmox_automatic_url_baseurl: "http://mirror.local.com/rocky/9/"
```

##### `proxmox_automatic_url_baseos`
**Default:** `""`  
**Description:** BaseOS URL (optional)

**Example:**
```yaml
proxmox_automatic_url_baseos: "http://mirror.local.com/rocky/9/BaseOS/"
```

##### `proxmox_automatic_url_mirrorlist`
**Default:** `"http://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=BaseOS-$releasever"`  
**Description:** Mirrorlist URL for Rocky Linux BaseOS

**Example:**
```yaml
proxmox_automatic_url_mirrorlist: "http://internal-mirror.com/rocky/mirrorlist"
```

### System Tuning

##### `proxmox_automatic_sysctl_settings`
**Default:** `{}`  
**Description:** Sysctl settings for better network performance

**Example:**
```yaml
proxmox_automatic_sysctl_settings:
  "net.ipv4.tcp_congestion_control": "bbr"
  "net.core.rmem_max": "16777216"
  "net.core.wmem_max": "16777216"
  "vm.swappiness": "10"
```

### Pool Management

##### `proxmox_automatic_vm_pool`
**Default:** `"omit"`  
**Description:** Optional pool where the VM will be registered. Only used if specified.

**Example:**
```yaml
proxmox_automatic_vm_pool: "production"
```

### Performance Tuning

##### `proxmox_automatic_create_vm_throttle`
**Default:** `3`  
**Description:** Number of concurrent VM creations

**Example:**
```yaml
proxmox_automatic_create_vm_throttle: 5
```

##### `proxmox_automatic_create_vm_retries`
**Default:** `3`  
**Description:** Retries for VM creation

**Example:**
```yaml
proxmox_automatic_create_vm_retries: 5
```

##### `proxmox_automatic_create_vm_retry_delay`
**Default:** `5`  
**Description:** Delay between retries (seconds)

**Example:**
```yaml
proxmox_automatic_create_vm_retry_delay: 10
```

##### `proxmox_automatic_create_vm_pause`
**Default:** `3`  
**Description:** Pause after VM creation (seconds)

**Example:**
```yaml
proxmox_automatic_create_vm_pause: 5
```

##### `proxmox_automatic_start_vm_throttle`
**Default:** `3`  
**Description:** Number of concurrent VM starts

**Example:**
```yaml
proxmox_automatic_start_vm_throttle: 2
```

##### `proxmox_automatic_start_vm_retries`
**Default:** `3`  
**Description:** Retries for VM start

**Example:**
```yaml
proxmox_automatic_start_vm_retries: 5
```

##### `proxmox_automatic_start_vm_retry_delay`
**Default:** `3`  
**Description:** Delay between start retries (seconds)

**Example:**
```yaml
proxmox_automatic_start_vm_retry_delay: 5
```

##### `proxmox_automatic_start_vm_pause`
**Default:** `5`  
**Description:** Pause after VM start (seconds)

**Example:**
```yaml
proxmox_automatic_start_vm_pause: 10
```

## 📚 Examples

### Database Server with Multiple Disks

```yaml
# host_vars/db01.yml
proxmox_automatic_memory: 8192
proxmox_automatic_vcpu: 4

# Storage hierarchy example
proxmox_automatic_storage_config_host_vars:
  - name: virtio0  # System disk
    size: "40"
    disk: vda
    bootloader: true
    vg:
      - name: system
        lv:
          - name: root
            mount: /
            size: 8192
            fstype: xfs
          - name: swap
            mount: swap
            size: 4096
            fstype: swap
          - name: var
            mount: /var
            size: 4096
            fstype: xfs
          - name: tmp
            mount: /tmp
            size: 2048
            fstype: xfs
            
  - name: virtio1  # Database storage
    size: "200"
    disk: vdb
    vg:
      - name: database
        lv:
          - name: mysql
            mount: /var/lib/mysql
            size: 1024
            grow: true
            fstype: xfs
            
  - name: virtio2  # Log storage
    size: "50"
    disk: vdc
    vg:
      - name: logs
        lv:
          - name: mysqllogs
            mount: /var/log/mysql
            size: 1024
            grow: true
            fstype: xfs

# Network configuration
proxmox_automatic_networks_host_vars:
  - name: net1
    bridge: vmbr1
    vlanid: 200  # Database VLAN

# Database-specific packages
proxmox_automatic_packages:
  - "mariadb-server"
  - "mariadb-client"
  - "python3-pymysql"
```

### Web Server Cluster

```yaml
# group_vars/webservers.yml
proxmox_automatic_memory: 4096
proxmox_automatic_vcpu: 2

# Web servers get additional storage for content
proxmox_automatic_storage_config_group_vars:
  - name: virtio1
    size: "100"
    disk: vdb
    vg:
      - name: web
        lv:
          - name: www
            mount: /var/www
            size: 1024
            grow: true
            fstype: xfs

# Web VLAN
proxmox_automatic_networks_group_vars:
  - name: net1
    bridge: vmbr1
    vlanid: 100

# Web-specific packages
proxmox_automatic_packages:
  - "httpd"
  - "php"
  - "php-mysqlnd"

# Web admin user
proxmox_automatic_users_group_vars:
  webadmin:
    password: "$6$rounds=656000$YourSaltHere$YourHashHere"
    groups: ["wheel", "apache"]
    shell: "/bin/bash"
```

### Development Environment

```yaml
# group_vars/development.yml
proxmox_automatic_selinux_mode: "permissive"
proxmox_automatic_firewall_enabled: false

# Development packages
proxmox_automatic_packages:
  - "git"
  - "vim"
  - "htop"
  - "nodejs"
  - "npm"
  - "python3-pip"
  - "docker-ce"

# Developer users with sudo access
proxmox_automatic_users_group_vars:
  developer:
    password: "$6$rounds=656000$DevSalt$DevHash"
    groups: ["wheel", "docker"]
    ssh_key: "ssh-rsa AAAA...developer-key"

# Additional development repositories
proxmox_automatic_repos:
  - name: "docker-ce"
    baseurl: "https://download.docker.com/linux/centos/9/$basearch/stable"
    gpgcheck: true
    gpgkey: "https://download.docker.com/linux/centos/gpg"
```

## 🚀 Advanced Usage

### Custom Kickstart Templates

You can extend the role by providing custom kickstart templates:

```yaml
# Create custom template in templates/
# templates/custom-kickstart.cfg.j2

# Use custom template
proxmox_automatic_kickstart_template: "custom-kickstart.cfg.j2"
```

### Integration with Ansible Vault

```yaml
# group_vars/all/vault.yml (encrypted with ansible-vault)
vault_proxmox_password: "super-secret-password"
vault_smtp_password: "email-password"

# group_vars/all/main.yml
proxmox_automatic_api_password: "{{ vault_proxmox_password }}"
proxmox_automatic_smtp_password: "{{ vault_smtp_password }}"
```

### Conditional VM Creation

```yaml
# Create VMs only in production
- hosts: all
  roles:
    - role: inframonks.proxmox_automatic
      when: environment == "production"
```

## 🔧 Troubleshooting

### Common Issues

1. **ISO Creation Fails**
   ```bash
   # Check dependencies
   proxmox_automatic_install_dependencies: true
   ```

2. **VM Creation Timeout**
   ```yaml
   # Increase timeouts
   proxmox_automatic_create_vm_retries: 5
   proxmox_automatic_create_vm_retry_delay: 10
   ```

3. **Network Issues**
   ```yaml
   # Use DHCP for testing
   proxmox_automatic_dhcp_enabled: true
   ```

### Debug Mode

```bash
# Run with increased verbosity
ansible-playbook -vvv playbook.yml
```

### Log Locations

- **Kickstart Files:** `{{ proxmox_automatic_files_dir }}/`
- **ISO Files:** `{{ proxmox_automatic_iso_dir }}/`
- **VM Console:** Proxmox VE web interface → VM → Console

## 📄 License

MIT

## 👥 Author Information

This role was created by [InfraMonks](https://github.com/inframonks).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- [GitHub Issues](https://github.com/inframonks/ansible-role-proxmox-automatic/issues)
- [Ansible Galaxy](https://galaxy.ansible.com/inframonks/proxmox_automatic)
