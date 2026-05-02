---
sidebar_position: 6
---

# Setup Nodes

## Install Debian 13: Trixie

Do a basic installation of Debian 13 - Trixie in the VMs with specs mentioned in [Hardware & Virtualization](./hardware_and_virtualization.mdx).
Enable SSH, assign user and host.

:::tip[Manual Network Setup]
Ensure that you create the interface eth0 or ens using a manual setup.
:::

## Setup Debian trixie VMs

To setup deb-k3s-master and deb-k3s-agent, I have used the following commands for easy access and management:

1. Install sudo

```bash
su -
apt update && apt install sudo
usermod -aG sudo < username >
```
Then exit and relogin with SSH. Now you will be able to use sudo for your commands.

2. Set static IP at /etc/network/interfaces

```bash
sudo nano /etc/network/interfaces
```

Paste the following:

```text
auto ens18
iface ens18 inet static
    address 192.168.0.202 #Provide your IP address outside DHCP range
    netmask 255.255.255.0
    gateway 192.168.0.1
    dns-nameservers 8.8.8.8 1.1.1.1
```

3. Then Restart networking:
```bash
sudo systemctl restart networking
```

4. After setting static IP at /etc/network/interfaces, run -> echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

### Pre-requisites for Raspberry Pi

If you are joining a Raspberry Pi either as a k3s server or a k3s agent, the following needs to be performed:

Standard Raspberry Pi OS installations do not start with cgroups enabled. K3S needs cgroups to start the systemd service. cgroupscan be enabled by appending cgroup_memory=1 cgroup_enable=memory to /boot/firmware/cmdline.txt.
Note: On Debian 11 and older Pi OS releases the cmdline.txt is located at /boot/cmdline.txt.

Example cmdline.txt:

```bash
console=serial0,115200 console=tty1 root=PARTUUID=58b06195-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait cgroup_memory=1 cgroup_enable=memory
```

Just append ```cgroup_memory=1 cgroup_enable=memory``` in the /boot/firmware/cmdline.txt file and you will be good to go.

### Setup VMs / Raspberry Pi to access NFS:

You will need to install a package called ```nfs-common``` in nodes you want to access the NFS file share for. In this case, the Jellyfin server will be installed on the deb-k3s-agent node (without a failover setup and a single replica).

To install and test whether the NFS file share can be mounted on the VMs:

1. Install nfs-common package:
``` bash
sudo apt update
sudo apt install nfs-common
```
2. Create a mount point: 
```bash 
sudo mkdir -p /mnt/shared_files
```
3. Mount it manually to test:
```bash
sudo mount < NFS-SERVER-IP >:/export/media-nfs /mnt/test-nfs
```
Here **media-nfs** needs to be changed to the relative path you have set while creating Shared Folder in OMV.

### Setup UID and GID for the shared folder:

Kubernetes will not be able to perform R/W operations on the /export/< NFS Shared Folder > in the OMV machine because of how the UID and GID are setup on the folder by default. The easiest way for kubernetes to access the folder is to use a common uid and gid for both the jellyfin pods as well as the shared folder.

1. SSH into the OMV node:

```bash
ssh root@< OMV-Node-ID >
```

2. Run

```bash
sudo chown -R 1000:1000 /export/< relative shared folder path >
```

The UID and GID of 1000 will later be passed down to the jellyfin helm values file so that the pod uses a security context with the same UID:GID pair.