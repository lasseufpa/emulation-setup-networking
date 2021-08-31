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

`install.py` will try to install all depedencies needed in a `tools/` folder. Everything should work, but in case something goes wrong, you will need to install the dependencies that failed in `tools/` (or in the system).

Run install.py:

``` console
$ python3 install.py
```

We use tmux for managing terminal windows, we recommend using the `.tmux.conf` configuration file if you are not familiar with tmux.

``` console
$ cp .tmux.conf ~/
```

Handy [cheatsheet](https://github.com/klaxalk/linux-setup/wiki/tmux) for using tmux with our `.tmux.conf`.

# How to use & Configuration

Run to start the emulation setup, use:

``` console
$ ./start.sh
```

## Running a network scenario

## Creating a network scenario

## Using the routing module

## Controlling network performance

# Troubleshooting & FAQ

* Grafana dashboard is not loading, what to do?
    - Probably grafana-server service is not running, try:

        ``` console
        $ sudo  systemctl  start  grafana-server
        $ sudo  systemctl  is-active  grafana-server
        ```

