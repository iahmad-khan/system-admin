if $operatingsystemmajrelease == 6 {
  exec {"/sbin/mkfs.ext4 /dev/$volume_mount":
    unless => "/sbin/blkid -t TYPE=ext4 /dev/$volume_mount"
  }
}
elsif  $operatingsystemmajrelease == 7 {
  exec {"/sbin/mkfs.xfs /dev/$volume_mount":
    unless => "/sbin/blkid -t TYPE=xfs /dev/$volume_mount"
  }
} 
