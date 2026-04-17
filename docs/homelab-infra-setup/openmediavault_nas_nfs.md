---
sidebar_position : 3
---

# NAS & NFS - OpenMediaVault

A persistent NFS file share is essential for storing and streaming media content through servers such as Jellyfin or Plex Media Server. While physical storage devices (USB drives, SSDs, or HDDs) can be directly passed through to virtual machines in Proxmox, this approach introduces limitations.

Direct passthrough makes it difficult to transfer media files across the network, as access becomes tightly coupled to a specific VM. Additionally, workloads running outside that VM—such as Kubernetes pods on a Raspberry Pi—cannot access the storage if it is locally attached within Proxmox.

To address these challenges, a dedicated NAS solution is recommended. Platforms like OpenMediaVault or TrueNAS provide a centralized and network-accessible storage layer. These open-source systems allow you to expose storage using standard protocols such as NFS, SMB, and FTP, ensuring seamless access across multiple machines, virtual environments, and containerized workloads.

## Setup OpenMediaVault NAS Server

To setup OpenMediaVault (OMV) NAS server, assign the USB as a SATA passthrough in proxmox and to use the USB as a NFS file share for storing movies and other media, first we need to spin up a VM in proxmox with the specifications mentioned in the previous page.
nas
## Download OMV OS ISO

Download the ISO file for the OMV OS prior to spinning up the VM from [OpenMediaVault ISO Download](https://www.openmediavault.org/download.html). Store it proxmox local by uploading the ISO.

## USB passthrough

Follow these steps to do a device passthrough of the storage media you want to use as a NFS file share:
1. Go to proxmox VM (usually named pve) and go to Disks.
2. Select and wipe the USB drive or any other external storage device and not the main installation media. Usually the main installation media of Proxmox is assigned to the device **sda** with it's partitions. Also be careful and take backup of the storage data already present in USB.
3. Go to the proxmox pve console:
- Run ```bash lsblk ``` to check the disks and partitions. You should see all the devices including your external disk as devices named sda, sdb, ... with their respective partitions. You'll also see the external device currently doesnt have any partitions.
- Run ```bash cfdisk /dev/<device letter>``` to create a partition.
- Select gpt
- Firstly create a **New** partition. You will see a partUUID generated.
- Then select **Write** to write the partition out.
- Select **Quit**.
- Copy the Device partuuid of the external drive by running ```bash blkid``` command.

4. Passthrough the newly partitioned external device using the following:

```bash
qm set < VM ID of omv nas server > -sata1 /dev/disk/by-partuuid/< partuuid copied for the device >
```

:::tip[Note]

Since the default storage of the OMV NAS is ```sata 0```, we have assigned the external storage to ```sata 1```. If you are using multiple devices, use ```sata 2, sata 3,...sata n``` in the command along with their respective partUUIDs.

:::


## Access OMV

Follow these steps to setup and access OMV:
1. Install OMV in the VM in proxmox, mostly with the default settings available.
2. Assign static IP either in the VM or through DCHP reservation in your router. DHCP reservation is used here for assigning a static IP handed out by the DHCP server of the router.
3. Login to OMV using http://< OMV IP > in browser and with initial credentials as:

```
Username: admin
Password: openmediavault

```

## Create NFS file share

Follow these steps to setup NFS file share:

1. Go to **Storage -> Disks** and then check whether your external storage is being picked up by OMV.
2. Next we need to create a File System: 

- **Go to File Systems** and select **plus icon**.
- Select on the preferred file system. For this project, **EXT4 is chosen** and then the storage that will be used as NFS was selected.
- **Wait for completion** as it will take time based on the size of the disk.

3. Create a Shared Folder next: 

- **Go to Shared Folders** and then click on **plus icon**.
- Provide a **name** and a **replative path**. 
- Select the file system formatted storage created above.

4. Create a NFS file share:
- First go to **Services -> NFS -> Settings** and select on Enable.
- **Go to Shares** under NFS. Click on plus icon and then **select the shared folder** created above.
- **Provide Client CIDR range** - Usually it should be your DHCP CIDR range (e.g. 192.168.0.0/24) so that all devices in your nextwork can access this NFS share. You can also specifically set a CIDR range for one device like 192.168.0.203/24.
- Make sure the **permission is selected as Read/Write**.
- Paste these Extra Options keeping kubernetes compatibility in mind - ```insecure,rw,async,no_subtree_check,no_root_squash```
- Type in a Tag if required.
- Create the NFS file share.