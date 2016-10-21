# formate a disk using puppet.

exec {"/sbin/mkfs.ext4 /dev/$disk":
unless => "/sbin/blkid -t TYPE=ext4 /dev/$disk"
} 
