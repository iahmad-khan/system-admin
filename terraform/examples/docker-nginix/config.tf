provider "docker" {
  host = "tcp://docker:2345/"
}

resource "docker_image" "nginx" {
  name = "nginx:1.9"
}

resource "docker_container" "nginx-server" {
  name = "nginx-server"
  image = "${docker_image.nginx.latest}"
  ports {
    internal = 80
  }
  volumes {
    container_path  = "/usr/share/nginx/html"
    host_path = "/home/scrapbook/tutorial/www"
    read_only = true
  }
}
