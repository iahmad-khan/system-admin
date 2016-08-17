class hg_vocmssdt::sdt::cmsdocker {

  include "afs"

  yumrepo {
          "dockerrepo":
             baseurl  => 'https://yum.dockerproject.org/repo/main/centos/7/',
             gpgcheck => 1,
             gpgkey   => 'https://yum.dockerproject.org/gpg',
             enabled  => 1,
  }->

  package {
          "docker":
             ensure => latest,
  }->

  file {
       "/build/docker":
          ensure => directory,
  }->


  file {
       "/var/lib/docker":
          ensure  => link,
          target  => "/build/docker",
          require => File["/build/docker"],
          mode    => 772,
          force   => true,
  }->

  file {
       "/usr/lib/systemd/system/docker.service":
         ensure  => present,
         source  => "puppet:///modules/hg_vocmssdt/usr/lib/systemd/system/docker.service",
         require => Package['docker'],
  }->

  exec {
       "realod-systemd":
         command     => "systemctl daemon-reload",
         path        => "/usr/bin",
         subscribe   => File["/usr/lib/systemd/system/docker.service"],
         refreshonly => true,
  }->

  service {
          "docker":
             ensure    => running,
             enable    => true,
             subscribe => File["/usr/lib/systemd/system/docker.service"],
 }
}
