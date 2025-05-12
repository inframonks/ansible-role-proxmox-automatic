# Ansible Role: proxmox-automatic

Diese Rolle automatisiert das Deployment von virtuellen Maschinen auf Proxmox mittels **Kickstart für Rocky Linux**.

## 📌 **Funktionen**
- Erstellung von **Kickstart-ISO-Dateien** für Proxmox.
- Hochladen der ISOs auf das Proxmox-Storage.
- Automatische Provisionierung von VMs mit:
  - Definierten Ressourcen (CPU, RAM, Disks).
  - Netzwerkkonfiguration (VLAN, MTU, MAC).
  - Cloud-Init oder Kickstart für Betriebssysteme.

---

# Prerequirements

## 🔹 Debian / Ubuntu

Erforderliche Pakete:
* xorriso
* isolinux (für /usr/share/syslinux/isohdpfx.bin)


```bash
sudo apt update
sudo apt install -y xorriso isolinux syslinux
```

## 🔹 Red Hat / Rocky Linux / AlmaLinux

Erforderliche Pakete:
* xorriso
* syslinux (für isohdpfx.bin)

```bash
sudo dnf install -y xorriso syslinux
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

---

## 📌 Create SSH-Key

Damit auf den Zielsystem ohen Passworteingabe zugegriffen werden kann, sollte ein Key generiert und der Public Key mit im kickstart file hinterlegt sein.

Ein vordefinirter Key befindet sich im files Ordner dieser Rolle.

```bash
ssh-keygen -t ed25519 -C "svc_ansible_rw@local" -N ""
```

Über die Ansible config Datei im Hauptordner kann dann dieser Key referenziert werden.

Beispiel SSH Clientkonfiguration, damit der richtige Key und User verwendet werden kann.

```bash
# Für alle 10.10.*.* und *.hw.local Hosts
Host 10.10.*.* *.hw.local
    User svc_ansible_rw
    IdentityFile ~/.ssh/id_ansible_ed25519
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
```

## 🏗 **Setup & Verwendung**
### 1️⃣ **Inventar Datei (`hosts.yml`) anpassen**

Das Inventar enthält nicht nur die Informationen, die für das Kickstart file notwendig sind, sondern auch direkt jene, die dann für die Grundkonfiguration wie mehrere NICS, Disks, LVM's und Monitoring Informationen notwendig sind.

```yaml
all:
  children:
    proxmox_hosts:
      hosts:
        srv-hyp-01.hw.local:
        srv-hyp-01.hw.local:
        srv-hyp-01.hw.local:
        srv-hyp-02.hw.local:
        srv-hyp-02.hw.local:
        srv-hyp-02.hw.local:
    helper:
      hosts:
        shell01.vm.local:
          {
            vm_host: srv-hyp-01.hw.local, os: rocky9, vmid: 3101,
            cpu: 4, memory: 4096, boot_order: 2, state: present,
            disks:   [{ name: virtio1, size: "30", partitions: [{ partition: 1, size: "28", mountpoints: "/opt" }] }],
            network: [{ name: net0, vlanid: 1001, ip: 10.10.1.101, netmask: 255.255.255.0, gateway: 10.10.1.1 }],
            monitoring: true, datacenter: glasbox, system: helper, function: shell
          }
```

### 2️⃣ Variablen in group_vars/all.yml

```yaml
proxmox_api_user: "root@pam"
proxmox_api_password: "DeinPasswort"
proxmox_api_token_id: "root@pam!ansible"
proxmox_api_token_secret: "xxxxxxxxxxxxxxxx"
proxmox_iso_storage: "cephfs"
proxmox_vm_storage: "lvolumes"
proxmox_vm_first_disk_size: "20G"
```

### 3️⃣ Playbook ausführen

```bash
ansible-playbook -i hosts.yml playbook.yml
```
