---
title: Poor man's RAID on a Raspberry Pi
permalink: /computer/raspberry-RAID
excerpt: Hey! The Raspberry Pi has 4 USB ports. That sounds like a 4-disk RAID waiting to happen!
parent: Raspberry Pi
---

# Intro

RAID disks have always fascinated me; some of my co-workers have mini
RAID enclosures sitting under their desks and the message is clear:
there is some serious computer juju going on here. I had toyed with
the idea of getting an enclosure, adding some cheap HDs and joining
the ranks of my 1337 bretheren, but could never justify the cost. I
didn't _need_ RAID storage, I only _wanted_ RAID storage. Enter the
Raspberry Pi. With it's stash-behind-a-couch mentality and 4 USB ports
it seemed like a perfect opportunity to have some fun learning about
RAID storage without breaking the bank.

What follows is a description of my setup and some tests I did to
optimize the array. I learned everything from the incompareable [Arch
Linux Wiki](https://wiki.archlinux.org/index.php/RAID), but that page
is perhaps a little verbose. I also try to answer some questions like
"what chunk size should I use?".

# Hardware

Apart from the Pi itself all I needed was some cheap USB drives. I
went with the [Kingston 16GB Data
Traveler](https://www.amazon.com/gp/product/B00URLZTNU/) mostly due to
the form factor; these drives are no wider than the USB port itself so
I didn't have to worry about fitting them into the Pi's tight USB hub.

I initially bought three of these guys so that I had one free port for
other peripherals and later upgraded the array to have 4 disks. As you
will see below, just because you buy the same product doesn't mean
you'll get _exactly_ the same revision. I would have saved myself a
slight headache (but missed out on some learning) had I bought all 4
at once.

# Setup

**NOTE:** I run Arch ARM on my Pi, but the following instructions
  should work for all flavors of Linux

## Format the disks

The basics here are pretty simple. First you need to correctly
partition your disks. Plug them all into the Pi and they should show
up as ```/dev/sdX``` (probably ```sda``` through ```sdd```). I like
using ```gdisk``` to create the partitions because it saves me some
math when determeing the partition size, but ```fdisk``` also works
just fine. 

However you choose to do it you'll want to change the partition table
to have only one partition that has type code ```FD00 (Linux
RAID)```. When choosing the size I highly recommend leaving about
100 MB of unpartitioned space on the disk. As mentioned on the Arch
Wiki this is to give you some wiggle room if adding other disks or
otherwise modifing the array. I didn't do this the first time and it
burned me: I had bought 3 identical disks and so I figured that I
could just use the whole disk because they were all the same. Later on
I wanted to add a fourth disk and bought _the exact same product_, but
it had a slightly different number of blocks. In this case it had
fewer blocks, so I couldn't add it to the array. Long story short I
had to completely reformat all the old disks and remake the
array. Woof. ```gdisk``` makes this easy: when it asks you for the
last block just type ```-100M```, which will make the last block 100
MB before the end of the disk. Neat.

Once you've formatted the first disk we'll use ```sfdisk``` to creat identical partition tables on the remaining disks:

```
$ sfdisk --dump /dev/sda > my_RAID_partition_table.sfd
$ sfdisk /dev/sdb < my_RAID_partition_table.sfd
$ sfdisk /dev/sdc < my_RAID_partition_table.sfd
...
```
and so on. All you're doing is saving the partition table from your first disk and writing it to the other disks with no user interaction. A very easy way to make sure all your disks are exactly the same.

## Create the array

```mdadm``` is the Linux RAID management tool. I'll show the command
first and then walk you through it:

```
$ mdadm --create --verbose --level=5 --chunk=64 --raid-devices=4 /dev/md0 /dev/sda1 /dev/sdb1 /dev/sdc1 /dev/sdd1
```

The first two options are pretty self explanatory; we want to create a
new array and we want the program to tell us what's going on. Next we
have the RAID level. I chose RAID 5 because it seems the coolest, but
you might want a different [RAID
level](https://en.wikipedia.org/wiki/Standard_RAID_levels). Next is
the chunk size, which we'll get to in depth below. It is 100% OK to
omit this and just use the default chunk size. After that is how many
disks will be in the array. Different RAID levels have different
constraints on what this number can be and some levels also make use
of the ```--spare-devices=N``` option. After the options come the
device arguments. The first argument will be the name of the new RAID
device. ```/dev/mdX``` seems to be what the cool kids do and I'm not
going to argue with that. Finally you just list all of the devices
that will be in the array. Notice that you need to specify the actual
_partitions_ (i.e., ```/dev/sda1``` vs. ```/dev/sda```).

Congrats! You know have a virtual RAID device (```/dev/md0```) that
you can treat like any other device. Most (all?) RAID levels require
some number crunching to stripe/mirror/calculate parity/etc. you can
check on the status of this via:

```
$ cat /proc/mdstat
```

You do **not** need to wait for this to finish before you start using
the array, but performance will be lower while it is happening.

## Some configurations

If you want your array to get automatically assembled on system
startup you need to edit a configuration file. The file in question is
```/etc/mdadm.conf``` and you probably have a default version with
everything commented out. All you need to do is add two lines. The first is simply

```
DEVICE partitions
```

this tells ```mdadm``` to look through ```/dev``` for some partitions
that have RAID superblock info (this is what ```mdadm --create```
created). The next line is specific to the array you just made. Run the command

```
$ mdadm --detail --scan
```

and simply copy the entire output into ```/etc/mdadm.conf```. You could even use

```
$ mdadm --detail --scan >> /etc/mdadm.conf
```

if you're feeling 1337. Now you'll always have ```/dev/md0``` when you
reboot your computer (assuming the disks are plugged in).

## Using the array

If you followed the above steps you now have a device ```/dev/md0```
and you can treat it like any other device. In my case I eventually
ended up using the RAID as a network attached storage (NAS) for my
Mac, so I needed to create a Mac-readable filesystem. After much
testing and frustration I setteled on using hfs+, which is easily achieved via:

```
$ mkfs.hfsplus /dev/md0
```

(on Arch hfs+ support comes via the ```hfsprogs``` package). I can now mount the RAID and use it:

```
$ mkdir -p /d/my_RAID
$ mount /dev/md0 /d/my_RAID
```

If you want some sort of permenance you can edit ```/etc/fstab``` with the following:

```
/dev/md0 /d/my_RAID hfsplus defauls,nofail,umask=0 0 0
```

I learned the hard way that the ```nofail``` option is a very good idea.

# Performance tests

What should I sent `--chunk` to when I create the array? Good
question! To test this I used my good friend `dd` to test read and
write speed for different block sizes. For each block size the test
commands looked like this (run from a directory on the mounted RAID):

```
$ dd if=/dev/zero of=tmp bs=XXX count=YYYY conv=fdatasync,notrunc status=progress
$ echo 3 > /proc/sys/vm/drop_caches
$ dd if=tmp of=/dev/null bs=XXX count=YYYY status=progress
$ dd if=tmp of=/dev/null bs=XXX count=YYYY status=progress
```

Where `XXX` is the block size and `YYYY` is some multiple of 2 such
that the total amount of data writen is around 1 GB (i.e., if `XXX=1M`
then `YYY=1024`). The first line here tests the write speed, the
second line clears the buffer so that the third line can test the
unbuffered read speed, and finally the fourth line tests the buffered
read speed. With this method I tested a few differnet `--chunk` sizes
with different block sizes to mimic different types of I/O
operations. The results are in the tables below:

**NOTE:** All of the following results are for a level 5 RAID.

### Write speed

|`--chunk` size | 64k | 512k | 1m |
| block size (`bs`) | | | |
| --- | --- | --- | --- |
| 128k | 6.8 MB/s | 10 MB/s | 10 MB/s |
| 512k | 6.3 MB/s | 9.9 MB/s | 9.8 MB/s |
| 1M | 7.3 MB/s | 9.6 MB/s | 9.0 MB/s |

### Unbuffered read speed

|`--chunk` size | 64k | 512k | 1m |
| block size (`bs`) | | | |
| --- | --- | --- | --- |
| 128k | 35 MB/s | 37 MB/s | 39 MB/s |
| 512k | 35 MB/s | 35 MB/s | 38 MB/s |
| 1M | 35 MB/s | 37 MB/s | 39 MB/s |

### Buffered read speed

|`--chunk` size | 64k | 512k | 1m |
| block size (`bs`) | | | |
| --- | --- | --- | --- |
| 128k | 580 MB/s | 531 MB/s | 500 MB/s |
| 512k | 535 MB/s | 500 MB/s | 550 MB/s |
| 1M | 35 MB/s | 37 MB/s | 39 MB/s |

So there you have it. I had heard rumours that large chunk sizes are
better for RAID 5 and the data seems to support that, but all of the
chunk sizes I tested are pretty close to one another.

In the end I actually wound up using a chunk size of `64k` because it seems to provide the best performance for `monerod`, but that's a story for another time....