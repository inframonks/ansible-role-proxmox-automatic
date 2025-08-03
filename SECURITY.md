# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | -------------------- |
| 1.x.x   | :white_check_mark:   |
| < 1.0   | :x:                  |

## Reporting Security Vulnerabilities

If you find a security vulnerability in this project, please **do not report it via public issues**.

Instead:

1. **Send email** to: [security@inframonks.de] (if available)
2. **Or**: Create a private Security Advisory via GitHub
3. **Or**: Contact the maintainers directly

### What to Include in the Report

- **Description** of the security vulnerability
- **Steps to reproduce**
- **Potential impact**
- **Proposed solution** (if available)
- **Your contact details** for follow-up questions

### What Happens Next?

1. **Confirmation** within 48 hours
2. **Initial assessment** within 7 days
3. **Develop fix** depending on severity
4. **Coordinated release** of the fix
5. **Credit** for the reporter (if desired)

## Security Best Practices

### For Role Users

```yaml
# ✅ Secure configuration
- name: Secure VM creation
  vars:
    # Use Ansible Vault for sensitive data
    proxmox_automatic_api_password: "{{ vault_proxmox_password }}"
    
    # Enable firewall
    proxmox_automatic_firewall_enabled: true
    
    # Keep SELinux enabled
    proxmox_automatic_selinux_mode: "enforcing"
    
    # Strong SSH configuration
    proxmox_automatic_users:
      - name: admin
        password: "{{ vault_admin_password }}"
        ssh_key: "{{ vault_admin_ssh_key }}"
        sudo_nopasswd: false  # Require password for sudo
```

### Sensitive Data

**❌ Never in plaintext:**
```yaml
# WRONG - passwords in plaintext
proxmox_automatic_api_password: "my-password"
proxmox_automatic_users:
  - name: admin
    password: "admin123"
```

**✅ Use Ansible Vault:**
```bash
# Create vault file
ansible-vault create group_vars/all/vault.yml

# Content of vault.yml:
vault_proxmox_password: "secure-password"
vault_admin_password: "$6$rounds=656000$..."  # mkpasswd --method=sha-512
```

### API Security

- Create **dedicated API users** with minimal rights
- Use **token-based authentication** when possible
- **Network restrictions** for API access
- **Regular rotation** of API credentials

### VM Security

```yaml
# Recommended security settings
proxmox_automatic_firewall_enabled: true
proxmox_automatic_selinux_mode: "enforcing"
proxmox_automatic_firewall_services:
  - "ssh"
  # Only open required services

# Secure SSH configuration
proxmox_automatic_users:
  - name: ansible
    ssh_key: "{{ vault_ansible_ssh_key }}"
    sudo_nopasswd: true   # Only for service accounts
  - name: admin
    ssh_key: "{{ vault_admin_ssh_key }}"
    sudo_nopasswd: false  # Humans need password
```

## Known Security Considerations

### Kickstart Files

- Kickstart files may contain sensitive information
- Temporarily stored on the Ansible Controller
- Automatic cleanup after VM creation recommended

### ISO Files

- Contain kickstart configuration
- Uploaded to Proxmox storage
- Should be deleted after installation

### Network Security

```yaml
# Example: Isolated networks
proxmox_automatic_networks:
  - name: net0  # Management (restricted access)
    vlanid: 100
    ip: "192.168.100.10"
    
  - name: net1  # Production (isolated)
    vlanid: 200
    ip: "10.0.200.10"
```

## Compliance

This role supports the following security standards:

- **CIS Benchmarks** - Secure basic configuration
- **NIST Cybersecurity Framework** - Through configurable security settings
- **BSI IT-Grundschutz** - German security standards

## Updates and Patches

- **Critical security vulnerabilities**: Patch within 24-48h
- **Important security vulnerabilities**: Patch within 7 days
- **Low security vulnerabilities**: With next regular release

## Contact

- **Security issues**: [security@inframonks.de] (if available)
- **General questions**: GitHub Issues
- **Discussions**: GitHub Discussions
