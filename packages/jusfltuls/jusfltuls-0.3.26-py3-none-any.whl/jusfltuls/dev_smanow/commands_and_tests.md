# 1. Find disks NVME or SATA/SCSI



## Test disks present on the system

COMMAND : `lsblk -d -n -o NAME,TRAN,TYPE -e 7`

### Output on 'diskos'
```
sda     sata   disk
sdb     sata   disk
sdc     sata   disk
sdd     sata   disk
nvme0n1 nvme   disk
```

### Output on 'gigajm'
```
sda  sata   disk
sdb  usb    disk
```

### Output on 'core6a'
```
sda sata   disk
```
### Output on 'super'
```
sda     sata   disk
sdb     sata   disk
nvme0n1 nvme   disk
```

### Output on 'gigavg'
```
sda  sata   disk
```


# 2. Find partitions with btrfs
`lsblk -ln -o NAME,FSTYPE | awk '$2=="btrfs"{print "/dev/"$1}' `

## Outputs
### Output on 'diskos'
```
/dev/sda1
/dev/sdd1
/dev/nvme0n1p6
```
### Output on gigajm'
```
/dev/sda3
```
### Output on 'core6a'
```
/dev/sda5
```
### Output on 'super'
```
/dev/sda3
/dev/sdb1
/dev/nvme0n1p4
```


# 2. Find btrfs disks

## Test btrfs partitions/disks present on the system

COMMAND : `lsblk -ln -o NAME,FSTYPE | awk '$2=="btrfs"{print "/dev/"$1}' `

### Output on 'diskos'
```
/dev/sda1
/dev/sdd1
/dev/nvme0n1p6
```

### Output on 'core6a'
```
/dev/sda5
```

### Output on 'gigavg' is none
```
```




# 3. Find which btrfs partition is in btrfs RAID (must detect even in unmounted state)

## Test btrfs partitions/disks present on the system

COMMAND: `sudo btrfs inspect-internal dump-super -f "/dev/sdXX" `

OBSERVATION: if no raid, "SYSTEM|DUP" is seen,
if RAID1, "SYSTEM|RAID1" is seen.

### Output on 'diskos' (RAID from sdd1 and sda1)
```
 sudo btrfs inspect-internal dump-super -f "/dev/sdd1"                                                                                                  [14:23:36]
superblock: bytenr=65536, device=/dev/sdd1
---------------------------------------------------------
csum_type		0 (crc32c)
csum_size		4
csum			0x51915620 [match]
bytenr			65536
flags			0x1
			( WRITTEN )
magic			_BHRfS_M [match]
fsid			ec7022d8-04a6-46f5-b285-35bc7df2e0cb
metadata_uuid		00000000-0000-0000-0000-000000000000
label			t21ab_array
generation		9024
root			5435653079040
sys_array_size		129
chunk_root_generation	8290
root_level		0
chunk_root		23543808
chunk_root_level	1
log_root		0
log_root_transid (deprecated)	0
log_root_level		0
total_bytes		48000550305792
bytes_used		6428089077760
sectorsize		4096
nodesize		16384
leafsize (deprecated)	16384
stripesize		4096
root_dir		6
num_devices		2
compat_flags		0x0
compat_ro_flags		0x3
			( FREE_SPACE_TREE |
			 FREE_SPACE_TREE_VALID )
incompat_flags		0x361
			( MIXED_BACKREF |
			 BIG_METADATA |
			 EXTENDED_IREF |
			 SKINNY_METADATA |
			 NO_HOLES )
cache_generation	0
uuid_tree_generation	9024
dev_item.uuid		26dd9ee8-4180-487b-9a74-b1be3d640bb2
dev_item.fsid		ec7022d8-04a6-46f5-b285-35bc7df2e0cb [match]
dev_item.type		0
dev_item.total_bytes	24000275152896
dev_item.bytes_used	6432795656192
dev_item.io_align	4096
dev_item.io_width	4096
dev_item.sector_size	4096
dev_item.devid		2
dev_item.dev_group	0
dev_item.seek_speed	0
dev_item.bandwidth	0
dev_item.generation	0
sys_chunk_array[2048]:
	item 0 key (FIRST_CHUNK_TREE CHUNK_ITEM 22020096)
		length 8388608 owner 2 stripe_len 65536 type SYSTEM|RAID1
		io_align 65536 io_width 65536 sector_size 4096
		num_stripes 2 sub_stripes 1
			stripe 0 devid 1 offset 22020096
			dev_uuid 4f6ad6ca-962d-4f6f-9e45-f28a4b43dcac
			stripe 1 devid 2 offset 1048576
			dev_uuid 26dd9ee8-4180-487b-9a74-b1be3d640bb2
backup_roots[4]:
...
```

### Output on gigajm' (no RAID)
```
sudo btrfs inspect-internal dump-super -f "/dev/sda3"                                                                                                  [14:23:49]
superblock: bytenr=65536, device=/dev/sda3
---------------------------------------------------------
csum_type		0 (crc32c)
csum_size		4
csum			0x842141f7 [match]
bytenr			65536
flags			0x1
			( WRITTEN )
magic			_BHRfS_M [match]
fsid			57acd985-f1b4-4736-bfb0-c4cf19184ff4
metadata_uuid		57acd985-f1b4-4736-bfb0-c4cf19184ff4
label
generation		902499
root			105922560
sys_array_size		129
chunk_root_generation	757420
root_level		1
chunk_root		61401481216
chunk_root_level	0
log_root		0
log_root_transid	0
log_root_level		0
total_bytes		179502579712
bytes_used		58631864320
sectorsize		4096
nodesize		16384
leafsize (deprecated)	16384
stripesize		4096
root_dir		6
num_devices		1
compat_flags		0x0
compat_ro_flags		0x3
			( FREE_SPACE_TREE |
			 FREE_SPACE_TREE_VALID )
incompat_flags		0x361
			( MIXED_BACKREF |
			 BIG_METADATA |
			 EXTENDED_IREF |
			 SKINNY_METADATA |
			 NO_HOLES )
cache_generation	0
uuid_tree_generation	902499
dev_item.uuid		dadf9e0a-9d34-4802-ad74-18673e65d924
dev_item.fsid		57acd985-f1b4-4736-bfb0-c4cf19184ff4 [match]
dev_item.type		0
dev_item.total_bytes	179502579712
dev_item.bytes_used	62352523264
dev_item.io_align	4096
dev_item.io_width	4096
dev_item.sector_size	4096
dev_item.devid		1
dev_item.dev_group	0
dev_item.seek_speed	0
dev_item.bandwidth	0
dev_item.generation	0
sys_chunk_array[2048]:
	item 0 key (FIRST_CHUNK_TREE CHUNK_ITEM 61401464832)
		length 33554432 owner 2 stripe_len 65536 type SYSTEM|DUP
		io_align 65536 io_width 65536 sector_size 4096
		num_stripes 2 sub_stripes 1
			stripe 0 devid 1 offset 62382931968
			dev_uuid dadf9e0a-9d34-4802-ad74-18673e65d924
			stripe 1 devid 1 offset 62416486400
			dev_uuid dadf9e0a-9d34-4802-ad74-18673e65d924
backup_roots[4]:
...
```

### Output on 'core6a' (no RAID)
```
 sudo btrfs inspect-internal dump-super -f "/dev/sda5"                                         [14:24:01]
superblock: bytenr=65536, device=/dev/sda5
---------------------------------------------------------
csum_type		0 (crc32c)
csum_size		4
csum			0x9c40266b [match]
bytenr			65536
flags			0x1
			( WRITTEN )
magic			_BHRfS_M [match]
fsid			b327ec08-5f72-478a-a256-3e0be82e7857
metadata_uuid		00000000-0000-0000-0000-000000000000
label
generation		2673111
root			1036677251072
sys_array_size		258
chunk_root_generation	2670025
root_level		1
chunk_root		1055115968512
chunk_root_level	1
log_root		1036671877120
log_root_transid (deprecated)	0
log_root_level		0
total_bytes		907704008704
bytes_used		596972621824
sectorsize		4096
nodesize		16384
leafsize (deprecated)	16384
stripesize		4096
root_dir		6
num_devices		1
compat_flags		0x0
compat_ro_flags		0x7
			( FREE_SPACE_TREE |
			 FREE_SPACE_TREE_VALID )
incompat_flags		0x361
			( MIXED_BACKREF |
			 BIG_METADATA |
			 EXTENDED_IREF |
			 SKINNY_METADATA |
			 NO_HOLES )
cache_generation	0
uuid_tree_generation	2673111
dev_item.uuid		43d14a54-ce5f-477a-b5f6-773a9cfddbf8
dev_item.fsid		b327ec08-5f72-478a-a256-3e0be82e7857 [match]
dev_item.type		0
dev_item.total_bytes	907704008704
dev_item.bytes_used	666885947392
dev_item.io_align	4096
dev_item.io_width	4096
dev_item.sector_size	4096
dev_item.devid		1
dev_item.dev_group	0
dev_item.seek_speed	0
dev_item.bandwidth	0
dev_item.generation	0
sys_chunk_array[2048]:
	item 0 key (FIRST_CHUNK_TREE CHUNK_ITEM 22020096)
		length 8388608 owner 2 stripe_len 65536 type SYSTEM|DUP
		io_align 65536 io_width 65536 sector_size 4096
		num_stripes 2 sub_stripes 1
			stripe 0 devid 1 offset 22020096
			dev_uuid 43d14a54-ce5f-477a-b5f6-773a9cfddbf8
			stripe 1 devid 1 offset 30408704
			dev_uuid 43d14a54-ce5f-477a-b5f6-773a9cfddbf8
	item 1 key (FIRST_CHUNK_TREE CHUNK_ITEM 1055115968512)
		length 33554432 owner 2 stripe_len 65536 type SYSTEM|DUP
		io_align 65536 io_width 65536 sector_size 4096
		num_stripes 2 sub_stripes 1
			stripe 0 devid 1 offset 9702473728
			dev_uuid 43d14a54-ce5f-477a-b5f6-773a9cfddbf8
			stripe 1 devid 1 offset 9736028160
			dev_uuid 43d14a54-ce5f-477a-b5f6-773a9cfddbf8
backup_roots[4]:
...
```

### Output on 'super'
```
sudo btrfs inspect-internal dump-super -f "/dev/sdb1"                                                                                                   [14:24:08]
superblock: bytenr=65536, device=/dev/sdb1
---------------------------------------------------------
csum_type		0 (crc32c)
csum_size		4
csum			0x6c2f3697 [match]
bytenr			65536
flags			0x1
			( WRITTEN )
magic			_BHRfS_M [match]
fsid			58ea3039-157d-461b-93c1-ca40bf1df844
metadata_uuid		58ea3039-157d-461b-93c1-ca40bf1df844
label			btr8
generation		3779
root			1525972762624
sys_array_size		129
chunk_root_generation	3777
root_level		0
chunk_root		243919749120
chunk_root_level	1
log_root		0
log_root_transid	0
log_root_level		0
total_bytes		8001561821184
bytes_used		1748960927744
sectorsize		4096
nodesize		16384
leafsize (deprecated)	16384
stripesize		4096
root_dir		6
num_devices		1
compat_flags		0x0
compat_ro_flags		0x3
			( FREE_SPACE_TREE |
			 FREE_SPACE_TREE_VALID )
incompat_flags		0x361
			( MIXED_BACKREF |
			 BIG_METADATA |
			 EXTENDED_IREF |
			 SKINNY_METADATA |
			 NO_HOLES )
cache_generation	0
uuid_tree_generation	3779
dev_item.uuid		b0e466da-a14f-4e07-ad27-3f42b0bf5d52
dev_item.fsid		58ea3039-157d-461b-93c1-ca40bf1df844 [match]
dev_item.type		0
dev_item.total_bytes	8001561821184
dev_item.bytes_used	1765307056128
dev_item.io_align	4096
dev_item.io_width	4096
dev_item.sector_size	4096
dev_item.devid		1
dev_item.dev_group	0
dev_item.seek_speed	0
dev_item.bandwidth	0
dev_item.generation	0
sys_chunk_array[2048]:
	item 0 key (FIRST_CHUNK_TREE CHUNK_ITEM 243904020480)
		length 33554432 owner 2 stripe_len 65536 type SYSTEM|DUP
		io_align 65536 io_width 65536 sector_size 4096
		num_stripes 2 sub_stripes 1
			stripe 0 devid 1 offset 2186280960
			dev_uuid b0e466da-a14f-4e07-ad27-3f42b0bf5d52
			stripe 1 devid 1 offset 2219835392
			dev_uuid b0e466da-a14f-4e07-ad27-3f42b0bf5d52
backup_roots[4]:
...
```

### No btrfs on gigavg


# 4. Mountpoints

## See mount points

COMMAND: `lsblk -p -P -o NAME,TYPE,MOUNTPOINT | awk -F'"' '/TYPE="part"/{m=$6; if(m=="") m="not_mounted"; print $2 "\t" m}'`


### Output on 'diskos'
```
/dev/sda1	/mnt/raid24
/dev/sdb1	not_mounted
/dev/sdc1	not_mounted
/dev/sdd1	not_mounted
/dev/nvme0n1p1	/boot/efi
/dev/nvme0n1p2	not_mounted
/dev/nvme0n1p3	not_mounted
/dev/nvme0n1p4	not_mounted
/dev/nvme0n1p5	/
/dev/nvme0n1p6	/home
```

/dev/sda1 is in RAID1 with /dev/sdd1, so I need to artificially change "/dev/sdd1 not_mounted" to "/dev/sdd1 raid_sda1"

### Output on 'gigajm'
```
/dev/sda1	/boot/efi
/dev/sda2	/
/dev/sda3	/home
/dev/sdb1	/media/ojr/L128
```

### Output on 'core6a'
```
/dev/sda1	not_mounted
/dev/sda2	/boot/efi
/dev/sda4	/
/dev/sda5	/home
```
### Output on 'super'
```
/dev/sda1	not_mounted
/dev/sda2	not_mounted
/dev/sda3	/LUBU1804
/dev/sdb1	/DATA
/dev/nvme0n1p1	/boot/efi
/dev/nvme0n1p2	/
/dev/nvme0n1p3	not_mounted
/dev/nvme0n1p4	/home
```


### Output on gigavg

```
/dev/sda1	/boot/efi
/dev/sda2	not_mounted
/dev/sda3	/
/dev/sda4	[SWAP]
/dev/sda5	not_mounted
```


# 5. [DUPLICATE] Summary command - showing device, filesystem, size, mounted:

## Same lsblk overview command as before

COMMAND: `lsblk -p -P -o NAME,TYPE,MOUNTPOINT | awk -F'"' '/TYPE="part"/{m=$6; if(m=="") m="not_mounted"; print $2 "\t" m}'`


### Output on 'diskos'
```
/dev/sda1	btrfs	21.8T	/mnt/raid24
/dev/sdb1		3.6T	not_mounted
/dev/sdc1		3.6T	not_mounted
/dev/sdd1	btrfs	21.8T	not_mounted
/dev/nvme0n1p1	vfat	100M	/boot/efi
/dev/nvme0n1p2		16M	not_mounted
/dev/nvme0n1p3	ntfs	207.5G	not_mounted
/dev/nvme0n1p4	ntfs	510M	not_mounted
/dev/nvme0n1p5	ext4	82G	/
/dev/nvme0n1p6	btrfs	175.7G	/home
```
Again, "/dev/sdd1	btrfs	21.8T   not_mounted" should be changed to  "/dev/sdd1 btrfs 21.8T   raid_sda1"


### Output on 'gigajm'
```
/dev/sda1	vfat	528M	/boot/efi
/dev/sda2	ext4	55.9G	/
/dev/sda3	btrfs	167.2G	/home
/dev/sdb1	ext4	119.2G	/media/ojr/L128
```

### Output on 'core6a'
```
/dev/sda1		476M	not_mounted
/dev/sda2	vfat	480M	/boot/efi
/dev/sda4	ext4	85.2G	/
/dev/sda5	btrfs	845.4G	/home
```

### Output on 'super'
```
/dev/sda1	ntfs	650M	not_mounted
/dev/sda2	vfat	260M	not_mounted
/dev/sda3	btrfs	930.6G	/LUBU1804
/dev/sdb1	btrfs	7.3T	/DATA
/dev/nvme0n1p1	vfat	285M	/boot/efi
/dev/nvme0n1p2	ext4	92.2G	/
/dev/nvme0n1p3	ext4	61.5G	not_mounted
/dev/nvme0n1p4	btrfs	1.6T	/home
```

### Output on 'gigavg'

```
/dev/sda1	/boot/efi
/dev/sda2	not_mounted
/dev/sda3	/
/dev/sda4	[SWAP]
/dev/sda5	not_mounted
```
