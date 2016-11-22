---
title: More Raspberry RAID tests
permalink: /computer/raspberry-RAID-tests
excerpt: A collection of further tests on Raspberry RAID performance. Now using all 4 usb ports.
parent: Raspberry Pi
---

# Intro

In a [previous post](raspberry-RAID.html) I detailed how
I set up a simple RAID device on as Raspberry Pi and provided some
performance metrics for various three-disk RAID 5
configurations. Below I report the results of similar tests using all
4 of the Pi's USB ports. I'm sticking with RAID 5 for now, but I might
try other levels in the future (especially RAID 10).

The testing methodology is exactly the same as [before](raspberry-RAID.html):

```
$ dd if=/dev/zero of=tmp bs=XXX count=YYYY conv=fdatasync,notrunc status=progress
$ echo 3 > /proc/sys/vm/drop_caches
$ dd if=tmp of=/dev/null bs=XXX count=YYYY status=progress
$ dd if=tmp of=/dev/null bs=XXX count=YYYY status=progress
```

## Write speed

|`--chunk` size | 4k | 64k | 512k | 1m | 4m |
| block size (`bs`) | | | | | |
| --- | --- | --- | --- | --- | --- |
| 128k | 24 MB/s | 18 MB/s | 18 MB/s | 18 MB/s | 5.9 MB/s |
| 512k | 13 MB/s | 8.0 MB/s | 10 MB/s | 7.3 MB/s | 3.6 MB/s |
| 1M | 15 MB/s | 8.3 MB/s | 12 MB/s | 8.3 MB/s | 4.5 MB/s |

## Unbuffered read speed

|`--chunk` size | 4k | 64k | 512k | 1m | 4m |
| block size (`bs`) | | | | |
| --- | --- | --- | --- | --- | --- |
| 128k | 35 MB/s | 45 MB/s | 45 MB/s | 45 MB/s | 43 MB/s |
| 512k | 35 MB/s | 45 MB/s | 45 MB/s | 38 MB/s | 43 MB/s |
| 1M | 35 MB/s | 38 MB/s | 38 MB/s | 41 MB/s | 43 MB/s |

## Buffered read speed

|`--chunk` size | 4k | 64k | 512k | 1m | 4m |
| block size (`bs`) | | | | | |
| --- | --- | --- | --- | --- | --- |
| 128k | 580 MB/s | 560 MB/s | 570 MB/s | 560 MB/s | 570 MB/s |
| 512k | 530 MB/s | 550 MB/s | 550 MB/s | 550 MB/s | 550 MB/s |
| 1M | 35 MB/s | 45 MB/s | 38 MB/s | 40 MB/s | 42 MB/s |

These results run counter to what we saw in the three disk array. In
that case a larger chunk size gave better performance, but here a
small, 4k chunk size (the smallest allowed by `mdadm`) gives clearly
better write performace. That said, a 4k chunk resulted in the slowest
unbuffered read speeds, which is interesting given that read speeds
were mostly constant for all other chunk sizes. Still the increase in
write speed (~33% in the worst case) is larger than the dip in read
performace (~30%) which makes a 4k chunk the winner in my book.

As further proof of the superiority of a 4k chunk, `monerod` runs with
essentially no problems on a 4 disk level 5 RAID with a 4k chunk. This
cannot be said of the other chunk sizes.