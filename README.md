# Ansible Role: proxmox_automatic

Diese Rolle erstellt automatisiert virtuelle Maschinen auf einem **Proxmox VE Cluster** mit individuellen **Kickstart-Konfigurationen**. Sie generiert maßgeschneiderte ISO-Dateien, lädt sie auf Proxmox hoch und startet die VMs mit komplexen Storage- und Netzwerkkonfigurationen.

## 🚀 Features

- **Hierarchische Konfiguration**: Defaults → group_vars → host_vars → Playbook-Variablen
- **Dynamische Storage-Konfiguration**: Multi-Disk Support mit LVM und flexiblen Größen
- **Automatische Kickstart-Generierung**: Individuelle `.cfg` Dateien pro VM
- **ISO-Management**: Automatische ISO-Erstellung und Upload nach Proxmox
- **Flexible Benutzer-Konfiguration**: Hierarchisches User-Management mit SSH-Keys
- **Multi-Network Support**: Mehrere Netzwerkkarten mit VLAN-Support
- **Rocky Linux 9 Optimiert**: Feste Repository-URLs, moderne Interface-Namen

## 📋 Anforderungen

### Auf dem Ansible Controller
```bash
# Rocky Linux / RHEL / CentOS
sudo dnf install genisoimage

# Ubuntu / Debian  
sudo apt-get install genisoimage
```

### Proxmox VE
- API-Benutzer mit VM-Verwaltungsrechten
- Storage für VMs und ISOs

## 🔧 Verwendung

### Basis-Playbook

```yaml
---
- name: Create virtual machines
  hosts: vm_hosts
  roles:
    - proxmox_automatic
  vars:
    proxmox_automatic_api_host: "pve.example.com"
    proxmox_automatic_api_password: "{{ vault_proxmox_password }}"
```

### Einfache VM mit Standard-Konfiguration

```yaml
# inventory/host_vars/webserver01.yml
proxmox_automatic_networks:
  - name: net0
    vlanid: 100
    ip: "192.168.1.10"
    netmask: "255.255.255.0"
    gateway: "192.168.1.1"
```

### Erweiterte Multi-Disk VM

```yaml
# inventory/host_vars/database01.yml
proxmox_automatic_networks:
  - name: net0
    vlanid: 200
    ip: "10.0.1.50"
    netmask: "255.255.255.0"
    gateway: "10.0.1.1"
  - name: net1  # Backup-Netz
    vlanid: 201
    ip: "10.0.2.50"
    netmask: "255.255.255.0"

proxmox_automatic_storage_config:
  - name: virtio0  # System-Disk
    size: 40  # 40GB für System
    disk: vda
    bootloader: true
    partitions:
      - name: efi
        mount: /boot/efi
        size: 1024
        fstype: efi
        primary: true
      - name: boot
        mount: /boot
        size: 1024
        fstype: ext4
        primary: true
      - name: pv.root
        size: 1024
        grow: true
        primary: true
        type: pv
    vg:
      - name: system
        lv:
          - name: root
            mount: /
            size: 4096
            fstype: xfs
          - name: var
            mount: /var
            size: 8192
            fstype: xfs
          - name: log
            mount: /var/log
            size: 4096
            fstype: xfs
          - name: swap
            mount: swap
            size: 4096
            fstype: swap
          - name: tmp
            mount: /tmp
            size: 2048
            fstype: xfs
          - name: home
            mount: /home
            size: 1024
            grow: true  # Nimmt verbleibenden Platz
            fstype: xfs
            
  - name: virtio1  # Datenbank-Storage
    size: 200  # 200GB für Datenbank
    disk: vdb
    partitions:
      - name: pv.data
        size: 1024
        grow: true
        primary: true
        type: pv
    vg:
      - name: database
        lv:
          - name: mysql
            mount: /var/lib/mysql
            size: 1024
            grow: true  # Nutzt gesamte Disk
            fstype: xfs
```

### Benutzer-Konfiguration

```yaml
# inventory/group_vars/webservers.yml
proxmox_automatic_users:
  - name: admin
    password: "{{ vault_admin_password }}"
    password_encrypted: false
    gecos: "System Administrator"
    uid: 1000
    gid: 1000
    groups: ["wheel", "docker"]
    ssh_key: "ssh-rsa AAAAB3NzaC1yc2E... admin@example.com"
    sudo_commands: "ALL"
    sudo_nopasswd: true
    
  - name: webadmin
    password: "{{ vault_webadmin_password }}"
    password_encrypted: false
    gecos: "Web Administrator"
    uid: 1001
    gid: 1001
    groups: ["wheel"]
    ssh_key: "ssh-rsa AAAAB3NzaC1yc2E... webadmin@example.com"
    sudo_commands: "/bin/systemctl, /usr/bin/docker"
    sudo_nopasswd: false
    
  - name: ansible
    password: "{{ vault_ansible_password }}"
    password_encrypted: false
    gecos: "Ansible Service Account"
    uid: 1002
    gid: 1002
    groups: []
    ssh_key: "{{ ansible_ssh_key }}"
    sudo_commands: "ALL"
    sudo_nopasswd: true
```

### Entwicklungsumgebung mit minimaler Konfiguration

```yaml
# inventory/host_vars/dev01.yml
proxmox_automatic_networks:
  - name: net0
    vlanid: 300
    ip: "172.16.1.100"
    netmask: "255.255.255.0"
    gateway: "172.16.1.1"

# Nur System-Disk, ohne zusätzlichen Storage
proxmox_automatic_storage_config:
  - name: virtio0
    size: 25
    disk: vda
    bootloader: true
    # Partitions werden von defaults übernommen
    vg:
      - name: system
        lv:
          - name: root
            mount: /
            size: 1024
            grow: true  # Nimmt gesamten verfügbaren Platz
            fstype: xfs
          - name: swap
            mount: swap
            size: 2048
            fstype: swap

# Entwickler-spezifische Pakete
proxmox_automatic_packages:
  - qemu-guest-agent
  - vim
  - git
  - docker-ce
  - nodejs
  - python3-pip
  - code-server
```

## 📁 Verzeichnisstruktur

```
roles/proxmox_automatic/
├── defaults/main.yml           # Standard-Konfiguration
├── tasks/main.yml             # Haupttasks
├── templates/
│   └── kickstart.cfg.j2       # Kickstart-Template
├── README.md                  # Diese Datei
└── meta/main.yml             # Role-Metadaten

playbooks/
├── kickstart-files/          # Generierte .cfg Dateien
├── kickstart-isos/           # Generierte .iso Dateien  
└── create_vms.yml           # Hauptplaybook

inventory/
├── hosts.yml               # Inventory-Datei
├── group_vars/
│   ├── all.yml
│   ├── webservers.yml
│   └── databases.yml
└── host_vars/
    ├── webserver01.yml
    ├── database01.yml
    └── dev01.yml
```

## 🔧 Wichtige Variablen

### Storage-Konfiguration

| Variable | Beschreibung | Beispiel |
|----------|--------------|----------|
| `size` | Disk-Größe in GB | `40` |
| `grow: true` | LV nutzt verbleibenden Platz | `true/false` |
| `mount` | Mount-Point | `/`, `/var/log`, `swap` |
| `fstype` | Dateisystem | `xfs`, `ext4`, `swap` |

### Netzwerk-Konfiguration

| Variable | Beschreibung | Beispiel |
|----------|--------------|----------|
| `vlanid` | VLAN-ID | `100` |
| `ip` | IP-Adresse | `192.168.1.10` |
| `netmask` | Netzmaske | `255.255.255.0` |
| `gateway` | Gateway (optional) | `192.168.1.1` |

### API-Konfiguration

| Variable | Beschreibung | Standard |
|----------|--------------|----------|
| `proxmox_automatic_api_host` | Proxmox Host | **erforderlich** |
| `proxmox_automatic_api_user` | API-Benutzer | `svc_ansible_rw@pam` |
| `proxmox_automatic_api_password` | API-Passwort | **erforderlich** |

## 💡 Hierarchische Konfiguration

Die Role unterstützt ein mächtiges hierarchisches Konfigurationssystem:

1. **defaults/main.yml** - Basis-Konfiguration
2. **group_vars/** - Gruppen-spezifische Überschreibungen  
3. **host_vars/** - Host-spezifische Konfiguration
4. **Playbook-Variablen** - Höchste Priorität

```yaml
# Beispiel: Storage wird hierarchisch gemergt
# defaults/main.yml definiert virtio0 + virtio1
# group_vars/databases.yml überschreibt virtio0 Größe  
# host_vars/db01.yml fügt virtio2 hinzu
# Resultat: VM bekommt alle drei Disks mit finaler Konfiguration
```

## 🔒 Sicherheit

```yaml
# Empfohlene Passwort-Verschlüsselung
ansible-vault create inventory/group_vars/all/vault.yml

# vault.yml Inhalt:
vault_admin_password: "secure_password_123"
vault_ansible_password: "service_account_pwd"
vault_proxmox_password: "proxmox_api_password"
```

## 🚦 Ausführung

```bash
# Einzelne VM erstellen
ansible-playbook playbooks/create_vms.yml -i inventory/hosts.yml -l webserver01

# Gruppe von VMs erstellen  
ansible-playbook playbooks/create_vms.yml -i inventory/hosts.yml -l webservers

# Alle VMs erstellen
ansible-playbook playbooks/create_vms.yml -i inventory/hosts.yml

# Mit Vault-Passwort
ansible-playbook playbooks/create_vms.yml -i inventory/hosts.yml --ask-vault-pass
```

## 🔍 Debugging

```bash
# Generierte Kickstart-Datei überprüfen
ls -la playbooks/kickstart-files/
cat playbooks/kickstart-files/ks-webserver01.example.com.cfg

# Template-Generierung testen (ohne VM-Erstellung)
ansible-playbook playbooks/create_vms.yml -i inventory/hosts.yml -l webserver01 --tags kickstart

# Verbose Output
ansible-playbook playbooks/create_vms.yml -i inventory/hosts.yml -l webserver01 -vvv
```

## 📚 Erweiterte Beispiele

### Kubernetes-Cluster

```yaml
# inventory/group_vars/kubernetes.yml
proxmox_automatic_storage_config:
  - name: virtio0
    size: 30
    # Standard-Partitionierung
  - name: virtio1  # Container-Storage
    size: 100
    disk: vdb
    partitions:
      - name: pv.containers
        size: 1024
        grow: true
        primary: true
        type: pv
    vg:
      - name: containers
        lv:
          - name: docker
            mount: /var/lib/docker
            size: 1024
            grow: true
            fstype: xfs

proxmox_automatic_packages:
  - docker-ce
  - kubeadm
  - kubelet
  - kubectl

# host_vars/k8s-master01.yml
proxmox_automatic_networks:
  - name: net0
    vlanid: 400
    ip: "10.0.4.10"
    netmask: "255.255.255.0"
    gateway: "10.0.4.1"

# host_vars/k8s-worker01.yml  
proxmox_automatic_networks:
  - name: net0
    vlanid: 400
    ip: "10.0.4.20"
    netmask: "255.255.255.0"
    gateway: "10.0.4.1"
```

### Monitoring-Stack

```yaml
# inventory/host_vars/monitoring01.yml
proxmox_automatic_storage_config:
  - name: virtio0
    size: 40
    # System-Disk
  - name: virtio1  # Prometheus-Storage
    size: 500
    disk: vdb
    partitions:
      - name: pv.monitoring
        size: 1024
        grow: true
        primary: true
        type: pv
    vg:
      - name: monitoring
        lv:
          - name: prometheus
            mount: /var/lib/prometheus
            size: 1024
            grow: true
            fstype: xfs
  - name: virtio2  # Grafana + Logs
    size: 100  
    disk: vdc
    partitions:
      - name: pv.data
        size: 1024
        grow: true
        primary: true
        type: pv
    vg:
      - name: data
        lv:
          - name: grafana
            mount: /var/lib/grafana
            size: 10240  # 10GB
            fstype: xfs
          - name: logs
            mount: /var/log/monitoring
            size: 1024
            grow: true  # Rest der Disk
            fstype: xfs

proxmox_automatic_networks:
  - name: net0  # Management
    vlanid: 100
    ip: "192.168.1.200"
    netmask: "255.255.255.0"
    gateway: "192.168.1.1"
  - name: net1  # Monitoring-Netz
    vlanid: 150
    ip: "10.0.15.200"
    netmask: "255.255.255.0"
```

## 🐛 Fehlerbehebung

### Häufige Probleme

1. **"Unable to detect release version"**
   - Problem: Repository-URLs mit Variablen
   - Lösung: Feste Rocky Linux 9 URLs werden verwendet

2. **"new lv is too large to fit in free space"** 
   - Problem: LV-Größen überschreiten verfügbaren Speicher
   - Lösung: `grow: true` für ein LV pro VG verwenden

3. **"Request boot drive 'vda' doesn't exist"**
   - Problem: Mehrfache ignoredisk-Befehle  
   - Lösung: Globale Disk-Konfiguration wird verwendet

4. **SSH-Verbindung schlägt fehl**
   - Problem: SSH-Keys oder Benutzer-Konfiguration
   - Lösung: `proxmox_automatic_users` korrekt konfigurieren

### Logs überprüfen

```bash
# Kickstart-Installation verfolgen
# In Proxmox Console:
tail -f /root/anaconda-ks-pre.log
tail -f /root/anaconda-ks-post.log

# Ansible-Logs
export ANSIBLE_LOG_PATH=/tmp/ansible.log
ansible-playbook ... -vvv
```

## 📝 Lizenz

[Hier Lizenz einfügen]

## 🤝 Beiträge

Beiträge sind willkommen! Bitte erstellen Sie Issues und Pull Requests.

## 📞 Support

Bei Fragen oder Problemen erstellen Sie bitte ein Issue im Repository.
| `proxmox_automatic_url_mirrorlist`       | Mirrorlist für Rocky-Install alternativ zu vorheriger Var. | Rocky Mirror URL                         |
| `proxmox_automatic_repos`                | Zusätzliche Repository-Konfiguration                       | Siehe YAML-Beispiel                      |

## 🧩 VM-spezifische Variablen (pro Host)

| Variable                                 | Beschreibung                                               | Standardwert                             |
|------------------------------------------|------------------------------------------------------------|------------------------------------------|
| `proxmox_automatic_vmid`                 | Proxmox VM-ID                                              | **erforderlich**                         |
| `proxmox_automatic_hypervisor`           | Ziel-Hypervisor (Hostname/FQDN)                            | **erforderlich**                         |
| `proxmox_automatic_memory`               | Arbeitsspeicher (MB)                                       | `2048`                                   |
| `proxmox_automatic_vcpu`                 | vCPUs                                                      | `2`                                      |
| `proxmox_automatic_cpu_type`             | CPU-Typ (QEMU)                                             | `"x86-64-v3"`                        |
| `proxmox_automatic_sockets`              | CPU-Sockelanzahl                                           | `1`                                      |
| `proxmox_automatic_state`                | VM-Zustand (`present` / `absent`)                          | `"present"`                              |
| `proxmox_automatic_storage`              | Manuelles Override des Storage                             | *(leer)*                                 |
| `proxmox_automatic_kvm`                  | KVM aktivieren                                             | `true`                                   |
| `proxmox_automatic_os_type`              | OS-Typ (`l26`, `win10`, etc.)                              | `"l26"`                                  |
| `proxmox_automatic_onboot`               | VM beim Boot starten                                       | `true`                                   |
| `proxmox_automatic_scsi_hw`              | SCSI-Controller                                            | `"virtio-scsi-single"`                   |
| `proxmox_automatic_machine`              | QEMU-Maschine                                              | `"q35"`                                  |
| `proxmox_automatic_hotplug`              | Hotplug-Funktion                                           | `"disk"`                                 |
| `proxmox_automatic_boot_order`           | Boot-Reihenfolge                                           | `1`                                      |
| `proxmox_automatic_boot_order_up_wait`   | Warten nach Start (s)                                      | `3`                                      |
| `proxmox_automatic_boot_order_down_wait` | Warten nach Shutdown (s)                                   | `3`                                      |
| `proxmox_automatic_storage_config`       | Storage-Konfiguration (siehe Beispiele)                    | `[]`                                     |
| `proxmox_automatic_dhcp_enabled`         | Aktiviert DHCP für die Netzwerkkonfiguration               | `false`                                  |
| `proxmox_automatic_networks`             | Liste zusätzlicher NICs (siehe Beispiele)                  | `[]`                                     |
| `proxmox_automatic_use_traditional_interface_names` | Verwendet eth0, eth1 statt enp6s18, enp6s19      | `true`                                   |
| `proxmox_automatic_interface_prefix`     | Interface-Präfix für traditionelle Namen                   | `"eth"`                                  |
| `proxmox_automatic_vm_pool`              | Pool in dem die VM eingetragen wird                        | `omit`                                   |

## Interface-Namen Konfiguration

**Rocky Linux 9** verwendet standardmäßig "predictable network interface names" wie `enp6s18`, `enp6s19`, etc. Für automatisierte Deployments sind die traditionellen Namen `eth0`, `eth1` oft praktischer.

```yaml
# Standard: Traditionelle Namen (empfohlen für Automation)
proxmox_automatic_use_traditional_interface_names: true
proxmox_automatic_interface_prefix: "eth"

# Alternativ: Moderne predictable Namen
proxmox_automatic_use_traditional_interface_names: false
# Interface-Namen werden automatisch als enp6s18, enp6s19, etc. generiert
```

## Beispiel für Storage-Konfiguration

Die Storage-Konfiguration wird in einem hierarchischen System verwaltet. Alle Disks werden direkt bei der VM-Erstellung hinzugefügt:

- `proxmox_automatic_storage_config_defaults` - Standard-Konfiguration in defaults/main.yml
- `proxmox_automatic_storage_config_group_vars` - Gruppen-spezifische Konfiguration
- `proxmox_automatic_storage_config_host_vars` - Host-spezifische Konfiguration 
- `proxmox_automatic_storage_config` - Playbook-Level Konfiguration (überschreibt alle anderen)

```yaml
proxmox_automatic_storage_config:
  - name: virtio0  # Boot-Disk (immer erforderlich)
    size: "20"
    pve_options:
      cache: "writeback"
      iothread: 1
      discard: "on"
  - name: virtio1  # Zusätzliche Disk
    size: "100"
    pve_options:
      cache: "none"
      iothread: 1
      ssd: 1
      backup: 0
  - name: virtio2
    size: "50"
```

## Beispiel für weitere Netzwerkkarten

Die Netzwerkkonfiguration wird nun in einem hierarchischen System verwaltet, ähnlich der Storage-Konfiguration. Die Konfiguration kann auf verschiedenen Ebenen definiert werden:

- `proxmox_automatic_networks_defaults` - Standard-Konfiguration in defaults/main.yml
- `proxmox_automatic_networks_group_vars` - Gruppen-spezifische Konfiguration
- `proxmox_automatic_networks_host_vars` - Host-spezifische Konfiguration 
- `proxmox_automatic_networks` - Playbook-Level Konfiguration (überschreibt alle anderen)

Alle Netzwerkinterfaces werden sowohl in der VM-Konfiguration als auch im Kickstart-Template konfiguriert.

```yaml
proxmox_automatic_networks:
  - name: net0
    ip: "192.168.1.10"
    netmask: "255.255.255.0"
    gateway: "192.168.1.1"
    bridge: vmbr1
    vlanid: 30
    model: virtio
    mac: "02:00:00:aa:bb:cc"
  - name: net1
    ip: "192.168.2.10"
    netmask: "255.255.255.0"
    bridge: vmbr1
    vlanid: 40
    mtu: 9000
    model: virtio
```

**Wichtig:** Das erste Interface (net0) sollte immer das Management-Interface mit Gateway sein. Zusätzliche Interfaces können optionale Gateway-Konfiguration haben.

## Beispiel für Repositories

```yaml
proxmox_automatic_repos:
  - name: "BaseOS"
    mirrorlist: "http://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=BaseOS-$releasever"
    cost: 0
  - name: "AppStream"
    mirrorlist: "http://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=AppStream-$releasever"
    cost: 0
  - name: "Extras"
    mirrorlist: "http://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=extras-$releasever"
    cost: 0
  - name: "CRB"+
    mirrorlist: "https://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=CRB-$releasever$rltype"
    cost: 0
  - name: "EPEL"
    baseurl: "https://download.fedoraproject.org/pub/epel/9/Everything/x86_64/"
    cost: 0
```

---

## 2️⃣ Variablen in group_vars/all.yml

```yaml
proxmox_api_user: "root@pam"
proxmox_api_password: "DeinPasswort"
proxmox_api_token_id: "root@pam!ansible"
proxmox_api_token_secret: "xxxxxxxxxxxxxxxx"
proxmox_iso_storage: "cephfs"
proxmox_vm_storage: "lvolumes"
proxmox_vm_first_disk_size: "20G"
```

---

## Beispiel: Host-Vars

Der proxmox_automatic_hypervisor ist der Hostname des Proxmox-Servers, auf dem die VM erstellt werden soll. Die VM-ID muss eindeutig sein.

Der proxmox_automatic_api_host gegen den sich Ansible verbindet. Hier kann auch eine IP-Adresse angegeben werden.

```yaml
proxmox_automatic_api_host: 192.168.178.12
proxmox_automatic_vmid: 17812
proxmox_automatic_hypervisor: srv-hyp-01
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
    vlanid: 178
    ip: "10.10.1.101"
    netmask: "255.255.255.0"
    gateway: "10.10.1.1"
    bridge: "vmbr1"
  - name: net1
    ip: "10.10.2.101"
    netmask: "255.255.255.0"
    vlanid: 300
    bridge: "vmbr1"
    mtu: 9000
```

---

# Prerequirements

Die folgenden Abhängigkeiten sind notwendig, um die ISO zu erstellen. Diese Rolle ist nicht für die Installation von Rocky Linux verantwortlich, sondern nur für die Erstellung der ISO.
Die Rolle ist so konzipiert, dass sie auf einem Linux-Host ausgeführt wird, der Zugriff auf den Proxmox-Cluster hat.

## 🔹 Red Hat / Rocky Linux / AlmaLinux

Erforderliche Pakete:
* xorriso
* syslinux (für isohdpfx.bin)

```bash
sudo dnf install -y xorriso syslinux
```

## 🔹 Debian / Ubuntu

Erforderliche Pakete:
* xorriso
* isolinux (für /usr/share/syslinux/isohdpfx.bin)


```bash
sudo apt update
sudo apt install -y xorriso isolinux syslinux
```

## 🔹 macOS

Unter macOS empfiehlt sich zur einfachen Installation das Paketmanagement mit Homebrew.

Installation (Homebrew erforderlich):

```bash
brew install xorriso syslinux
```
# Basis ISO erstellen

## 📌 Schritt 1: Original ISO herunterladen und entpacken

```bash

curl -LO https://download.rockylinux.org/pub/rocky/9/isos/x86_64/Rocky-9.6-x86_64-boot.iso

sudo mkdir /mnt/iso
sudo mount -o loop Rocky-9.6-x86_64-boot.iso /mnt/iso

mkdir ~/rocky_custom_iso
sudo rsync -a /mnt/iso/ ~/rocky_custom_iso/

sudo umount /mnt/iso
```

## 📌 Schritt 2: Anpassung der Boot-Konfiguration (wichtig!)

### BIOS (Legacy) – isolinux/isolinux.cfg:

Bearbeiten der Datei:

```bash
vim ~/rocky_custom_iso/isolinux/isolinux.cfg
```

Ersetze die Zeile mit append initrd= durch:
```bash
label linux
  menu label ^Install Rocky Linux 9.5 via Kickstart (2. CDROM)
  kernel vmlinuz
  append initrd=initrd.img inst.stage2=hd:LABEL=Rocky9 inst.ks=hd:/dev/sr1:/ks.cfg quiet
```

### EFI (UEFI) – EFI/BOOT/grub.cfg:

Bearbeiten der Datei:
```bash
vim ~/rocky_custom_iso/EFI/BOOT/grub.cfg
```

Füge exakt folgenden Eintrag hinzu oder passe den bestehenden an:
```bash
set default=0
set timeout=5

menuentry 'Install Rocky Linux 9.5 via Kickstart (2. CDROM)' --class fedora --class gnu-linux --class os {
    linuxefi /images/pxeboot/vmlinuz inst.stage2=hd:LABEL=Rocky9 inst.ks=hd:/dev/sr1:/ks.cfg quiet
    initrdefi /images/pxeboot/initrd.img
}
```
**Wichtig:** Die Label-Bezeichnung (Rocky9) muss exakt mit dem ISO-Label (nächster Schritt) übereinstimmen.

## 📌 Schritt 3: ISO sauber erstellen (vollständig kompatibel mit BIOS + EFI)

```bash
cd ~/rocky_custom_iso

sudo xorriso -as mkisofs \
  -V 'Rocky9' \
  -o ../rocky9-ks.iso \
  -isohybrid-mbr /usr/share/syslinux/isohdpfx.bin \
  -c isolinux/boot.cat \
  -b isolinux/isolinux.bin \
    -no-emul-boot -boot-load-size 4 -boot-info-table \
  -eltorito-alt-boot \
  -e images/efiboot.img \
    -no-emul-boot -isohybrid-gpt-basdat \
  .
```

## 📌 Schritt 4: Erstelle ein zweites ISO für Kickstart

Kickstart-ISO erzeugen (enthält nur die ks.cfg) und wird generell von Ansible erledigt:
```bash
mkdir ~/ks_iso
cp ks.cfg ~/ks_iso/

xorriso -as mkisofs \
  -V "KS_ISO" \
  -J -R \
  -o ~/ks.iso \
  ~/ks_iso
```

## 📌 Schritt 5: Nutzung in Proxmox (Wichtig!)

VM-Konfiguration:
	•	BIOS: OVMF (UEFI) oder SeaBIOS (Legacy)
	•	CD-ROM 1 (ide2): rocky9-ks.iso
	•	CD-ROM 2 (ide3): ks.iso (Kickstart-Datei)

Bootreihenfolge:
	1.	Erste CD-ROM (rocky9-ks.iso)
	2.	Zweite CD-ROM (ks.iso)

Rocky sucht dank des Parameters inst.ks=hd:/dev/sr1:/ks.cfg explizit auf der zweiten CD-ROM nach der Kickstart-Datei.
