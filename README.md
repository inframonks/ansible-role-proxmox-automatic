# Ansible Role: `inframonks.proxmox_automatic`

Diese Rolle erstellt automatisiert virtuelle Maschinen auf einem **Proxmox VE Cluster**, generiert individuelle **Kickstart-ISOs**, lädt sie hoch und startet die VM. Unterstützt werden außerdem **zusätzliche Disks** und **Netzwerkgeräte**.

Im unteren Abschnitt befindet sich die Abhängigkeiten zu den benötigten Paketen, die für die Erstellung der ISO notwendig sind.

Es wird ein eigenes Plugin für den Upload der ISO-Dateien auf den Proxmox-Server verwendet. Dieses Plugin befindet sich im Plugin-Ordner der Collection. Das eigene Ansible module `ansible.builtin.uri` kann an dieser Stelle nicht verwendet werden, da mit diesem der Proxmox Host den hochladenen blockiert.

---

## Rollenfunktionen

- Erzeugung individueller Kickstart-Dateien (`.cfg`)
- Erstellung einer ISO mit Kickstart-Config pro VM
- Upload der ISO auf das Proxmox-Storage
- Provisionierung der VM mit:
  - Basis-Hardwareparametern
  - UEFI + TPM
  - zusätzlichem Storage
  - mehreren Netzwerkkarten (inkl. VLAN, MTU, MAC)
- Start der VM nach Erstellung

---

## Variablen

| Variable                                 | Beschreibung                                               | Standardwert                             |
|------------------------------------------|------------------------------------------------------------|------------------------------------------|
| `proxmox_automatic_files_dir`            | Verzeichnis für Kickstart-Dateien                          | `"kickstart-files"`                      |
| `proxmox_automatic_iso_dir`              | Verzeichnis für erzeugte ISO-Dateien                       | `"kickstart-isos"`                       |
| `proxmox_automatic_os`                   | Zielbetriebssystem                                         | `"rocky9"`                               |
| `proxmox_automatic_first_disk_size`      | Größe der ersten Festplatte (in GB)                        | `"20G"`                                  |
| `proxmox_automatic_storage`              | Standard-Storage (für VM & ISO)                            | `proxmox_automatic_pve_vm_storage`       |
| `proxmox_automatic_pve_iso_storage`      | Storage für ISOs in Proxmox                                | `"cephfs"`                               |
| `proxmox_automatic_pve_vm_storage`       | Storage für VMs in Proxmox                                 | `"volumes"`                              |
| `proxmox_automatic_defaultbridge`        | Standard-Bridge für Netzwerk                               | `"vmbr1"`                                |
| `proxmox_automatic_api_host`             | API-Zielhost (FQDN oder IP)                                | **erforderlich**                         |
| `proxmox_automatic_api_user`             | Benutzername für die API                                   | `"svc_ansible_rw@pam"`                   |
| `proxmox_automatic_api_password`         | Passwort für API-Zugang                                    | **erforderlich**                         |
| `proxmox_automatic_timezone`             | Zeitzone der VM                                            | `"Europe/Berlin"`                        |
| `proxmox_automatic_ntp_servers`          | Liste von NTP-Servern                                      | `["ntp.cloudflare.com"]`                 |
| `proxmox_automatic_dns_servers`          | Liste von DNS-Servern                                      | `["1.1.1.1", "1.0.0.1"]`                 |
| `proxmox_automatic_admin_user`           | Admin-Benutzer im Zielsystem                               | `"admin"`                                |
| `proxmox_automatic_admin_password`       | Passwort für Admin-Benutzer                                | **erforderlich**                         |
| `proxmox_automatic_admin_ssh_key`        | SSH Public Key für Admin                                   | **erforderlich**                         |
| `proxmox_automatic_admin_gecos`          | GECOS-Feld / Beschreibung                                  | `"Admin user"`                           |
| `proxmox_automatic_service_user`         | Ansible Serviceaccount                                     | `"ansible"`                              |
| `proxmox_automatic_service_password`     | Passwort für Ansible Serviceaccount                        | **erforderlich**                         |
| `proxmox_automatic_service_ssh_key`      | SSH Public Key für Ansible Serviceaccount                  | **erforderlich**                         |
| `proxmox_automatic_url_baseos`           | BaseOS URL für Rocky-Install                               | Rocky BaseOS URL                         |
| `proxmox_automatic_url_mirrorlist`       | Mirrorlist für Rocky-Install alternativ zu vorheriger Var. | Rocky Mirror URL                         |
| `proxmox_automatic_repos`                | Zusätzliche Repository-Konfiguration                       | Siehe YAML-Beispiel                      |

## 🧩 VM-spezifische Variablen (pro Host)

| Variable                                 | Beschreibung                                               | Standardwert                             |
|------------------------------------------|------------------------------------------------------------|------------------------------------------|
| `proxmox_automatic_vmid`                 | Proxmox VM-ID                                              | **erforderlich**                         |
| `proxmox_automatic_hypervisor`           | Ziel-Hypervisor (Hostname/FQDN)                            | **erforderlich**                         |
| `proxmox_automatic_memory`               | Arbeitsspeicher (MB)                                       | `2048`                                   |
| `proxmox_automatic_vcpu`                 | vCPUs                                                      | `2`                                      |
| `proxmox_automatic_cpu_type`             | CPU-Typ (QEMU)                                             | `"x86-64-v2-AES"`                        |
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
| `proxmox_automatic_disks`                | Liste zusätzlicher Festplatten (siehe Beispiele)           | `[]`                                     |
| `proxmox_automatic_dhcp_enabled`         | Aktiviert DHCP für die Netzwerkkonfiguration               | `false`                                  |
| `proxmox_automatic_networks`             | Liste zusätzlicher NICs (siehe Beispiele)                  | `[]`                                     |
| `proxmox_automatic_vm_pool`              | Pool in dem die VM eingetragen wird                        | `omit`                                   |

## Bespiel für weitere Disks

virtio0 ist immer belegt für die erste Disk (root). Weitere Disks werden in der Liste `proxmox_automatic_disks` definiert.

```yaml
proxmox_automatic_disks:
  - name: virtio1
    size: "100"
    storage: "volumes"
  - name: virtio2
    size: "50"
```

## Beispiel für weitere Netzwerkkarten

Die MAC-Adresse wird automatisch generiert, wenn nicht angegeben. Die Bridge ist immer `{{ proxmox_automatic_defaultbridge }}`, wenn nicht anders angegeben.

```yaml
proxmox_automatic_networks:
  - name: net1
    bridge: vmbr1
    vlanid: 30
    mtu: 9000
    model: virtio
    mac: "02:00:00:aa:bb:cc"
  - name: net2
    vlanid: 40
    model: virtio
```
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
proxmox_automatic_disks:
  - name: virtio1
    size: 100G
proxmox_automatic_networks:
  - name: net0
    vlanid: 178
    ip: 10.10.1.101
    netmask: 255.255.255.0
    gateway: 10.10.1.1
  - name: net2
    vlanid: 300
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

curl -LO https://download.rockylinux.org/pub/rocky/9/isos/x86_64/Rocky-9.5-x86_64-boot.iso

sudo mkdir /mnt/iso
sudo mount -o loop Rocky-9.5-x86_64-boot.iso /mnt/iso

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
