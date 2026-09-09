Vagrant.configure("2") do |config|
    # General Vagrant VM configuration.
    config.vm.box = "bento/ubuntu-24.04"
    config.ssh.insert_key = false
    config.vm.synced_folder ".", "/vagrant", disabled: true
    config.vm.provider :virtualbox do |v|
        v.memory = 2048
        v.cpus = 2
        v.linked_clone = true
end

# Frontend server.
config.vm.define "frontend" do |frontend|
    frontend.vm.hostname = "frontend"
    frontend.vm.network :private_network, ip: "192.168.56.11"
end
# DB server.
config.vm.define "db" do |db|
    db.vm.hostname = "database"
    db.vm.network :private_network, ip: "192.168.56.12"
end
# API server.
config.vm.define "api" do |api|
    api.vm.hostname = "api"
    api.vm.network :private_network, ip: "192.168.56.13"
    end
end