# emulation-setup-networking


# Introduction

Emulation setup for networking experiments.

# Requirements

Tested with **Ubuntu 18.04**.

Dependencies:

1. ContainerNet
2. Ryu
3. python3 & pip
4. sFlow RT 
5. Prometheus
6. Grafana
7. Docker
8. Tmux

# Installation

First, make sure you have python3 with pip installed.

`install.py` will try to install all dependencies needed in a `tools/` folder. Everything should work, but if something goes wrong, you will need to install the dependencies that failed in `tools/` (or in the system).

Run install.py:

``` console
python3 install.py
```

We use Tmux for managing terminal windows. We recommend using the `.tmux.conf` configuration file if you are not familiar with Tmux.

``` console
cp .tmux.conf ~/
```

Handy [cheatsheet](https://github.com/klaxalk/linux-setup/wiki/tmux) for using tmux with our `.tmux.conf`.

# How to use & Configuration

To start the emulation setup, use:

``` console
./start.sh
```

`start.sh` will start Tmux, initializing all tools and opening firefox with Prometheus, sFlow, and Grafana dashboards.

For demonstration purposes, go to the window `scenario` in Tmux and run:

``` console
sudo python3 run_demo.py
```

That is it! You will see the emulated network topology, and after closing the view, the cointainernet CLI will start. You can play around with the network using the CLI.

It is recommended that you look at the `run_demo.py` code to see how it works. There are some extras there.

## Custom network topology

You can emulate any network topology with containernet, which uses the same interface as Mininet.

For further information on implementing custom network topologies on Mininet, please check Mininet [documentation](https://github.com/mininet/mininet/wiki/Introduction-to-Mininet#creating-topologies).

We also provide an example of a custom network topology, the NSFNet topology. You can check it out at `src/topologies/nsfnet.py`. You can use it with `run_demo.py` to take a look.

We recommend using the following convention when creating a new network topology:

- `hX` for hosts, where X is an integer between 1 and the number of hosts.
- `sX` for switches, where X is an integer between 1 and the number of switches.
- `IP(hX)` = `10.0.0.X`, the IP address of a host `hX` is directly related to the host id `X`.
- `mac(hX)` = `00:00:00:00:00:X`, the mac address of a host `hX` is directly related to the host id `X` in hexadecimal.

PS: For now, our routing module only supports a maximum of 255 hosts.

## Control of the network performance

You can control the following parameters dynamically via our REST server:
- link rate
- link delay
- link packet drop rate
- switch interface buffer size
- routing

REST server endpoint:

### http://127.0.0.1:5000/manage_switch_traffic
```json
{
    "type": "delay", // parameter to change
    "switchId": 1, // for switch s1
    "ifacePort": 1, // for interface s1-eth1
    "value": 100 // new value for parameter
}
```

Explanation:
- `type` can be `[delay, loss, rate, limit]`, where 
    - delay: link delay
    - loss: link packet drop rate
    - rate: link rate
    - limit: buffer size
- `switchId` is the id of a switch in the network
- `ifacePort` is the id of the switch interface where the link in question connects.
- `value` new value for the `type` paramenter, example:
    - for delay: `"value": 100ms` is a `100ms` delay.
    - for loss: `"value": 10%` is a `10%` loss.
    - for rate: `"value": 250kbit` is a rate of `250kbit`. 

## Custom routing

You can route the network ~~manually~~ with the REST API, use our `StaticRouter` implementation, or even build your own `<insert here>Router` by inheriting our `BaseRouter` class.

REST server end point:
### http://127.0.0.1:5000/route
```json
{
    "switchId": 1, // for switch s1
    "portIn": 1, // for interface s1-eth1
    "portOut": 2, // for interface s1-eth2
    "hostOrigin": 1, // for host h1
    "hostDestiny": 2 // for host h2
}
```

Routing packets works in the following way:
1. Select a switch `S.`
2. Select origin host `U` and destiny host `V.`
3. Select the in/out switch interfaces `S-I`, `S-O`.
4. Route packets that arrive in `S` through `S-I` from `U` to `V`, to `S-O`.

Our `StaticRouter` implementation uses the REST API to route the network based on hopping distance. There is an example of how to use it in `run_demo.py`.

## Connect applications to the network

Please check the Mininet [documention](https://github.com/mininet/mininet/wiki/Introduction-to-Mininet#running-programs-in-hosts) on how to connect applications to hosts in the network topology. If you want to connect a docker container, check containernet [documentation](https://containernet.github.io/#get-started).

## Data collection

Data collection is made automatically with sFlow-RT. We use the default configuration for sFlow-RT, but there are plenty of customizations [available](https://sflow-rt.com/).

We store the data collected by sFlow-RT with Prometheus. `prometheus.yml` contains the relevant Configuration, including `scrape_interval`. Check Prometheus [documentation](https://prometheus.io/docs/prometheus/latest/configuration/configuration/) for more information. If you want to change the default configuration in `prometheus.yml`, make the changes and then use:

``` console
cp prometheus.yml tools/prometheus-2.26.0.linux-amd64
```

You can export the data from Prometheus to a CSV file by using the program in `data/data_collection.py`. Specify each metrics you want to export, the time interval (Unix timestamps), and other intuitive configurations in `data/config.yml`.

The program will generate a `.csv` file organized as `['metric', 'intf', 'value', 'timestamp']`, where `metric` is the index of the metric in the list on `data/config.yml` file, `intf` is the switch interface where the data point comes from, `value` is the value of the metric at time `timestamp`.

To generate the `.csv` file, run:

``` console
cd data
python3 data_collection.py
```

## Data visualization

To visualize data in real-time, you need to connect Grafana to Prometheus. Please refer to the Prometheus [documentation](https://prometheus.io/docs/visualization/grafana/).

# Troubleshooting & FAQ

* Grafana dashboard is not loading. What to do?
    - Probably grafana-server service is not running, try:

        ``` console
        sudo  systemctl  start  grafana-server
        sudo  systemctl  is-active  grafana-server
        ```

