class hg_vocmssdt::sdt::cmsdocker {

  include "afs"

  Exec { path => [ '/bin/', '/sbin/' , '/usr/bin/', '/usr/sbin/' ] }


  cmssw::build_environment{"build-environment": }

  cmssw::runtime_environment {"runtime-environment": }


  #globally set exec paths

  firewall { "0 enable all connections":
               proto  => "tcp",
               action => "accept",
  }

  firewall { "600 allow AFS cache callback":
               proto  => "udp",
               action => "accept",
               dport  => [7001],
  }

  yumrepo { "dockerrepo":
              baseurl  => 'https://yum.dockerproject.org/repo/main/centos/7/',
              gpgcheck => 1,
              gpgkey   => 'https://yum.dockerproject.org/gpg',
              enabled  => 1,
  }->

  package { "docker":
              ensure => latest,
  }->

  file { "/build/docker":
            ensure => directory,
  }->


  file { "/var/lib/docker":
           ensure  => link,
           target  => "/build/docker",
           require => File["/build/docker"],
           mode    => 772,
           force   => true,
  }->

  file { "/usr/lib/systemd/system/docker.service":
          ensure  => present,
          source  => "puppet:///modules/hg_vocmssdt/usr/lib/systemd/system/docker.service",
          require => Package['docker'],
  }->

  exec { "realod-systemd":
          command     => "systemctl daemon-reload",
          subscribe   => File["/usr/lib/systemd/system/docker.service"],
          refreshonly => true,
  }->

  service { "docker":
             ensure    => running,
             enable    => true,
             subscribe => File["/usr/lib/systemd/system/docker.service"],
  }

  group { 'docker':
         ensure => present,
         notify => Service['docker'],
  }


  exec { "adds cmsbld into docker group":
           command => "usermod -aG docker cmsbld",
           onlyif  => "grep  -q 'docker[[:space:]]*cmsbld' /etc/group",
           require => User['cmsbld'],
  }

  file { "/var/opt/increase.sh":
           source => "puppet:///modules/hg_vocmssdt/lvm_increase/increase.sh",
           mode   => 755,
           owner  => "root",
           group  => "root",
  }
  exec { "increase_lv_size":
           command => "/var/opt/increase.sh",
           unless  => "/usr/bin/test -e /etc/volume_expanded",
           require => File["/var/opt/increase.sh"],
  }

  file { '/home/cmsbld/.docker':
          ensure => directory,
          owner  => cmsbld,
          group  => cmsbld,
          mode   => 640,
  }

}
