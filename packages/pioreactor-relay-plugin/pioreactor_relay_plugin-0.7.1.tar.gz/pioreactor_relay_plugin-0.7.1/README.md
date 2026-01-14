
## Pioreactor relay plugin

This relay plugin allows the user to turn on or off any additional hardware piece on their Pioreactor at a specific channel (as stated in the Configuration).

## Installation

Install from the Pioreactor plugins web interface or the command line:

```
pio plugins install pioreactor-relay-plugin    # to install directly on the Pioreactor

# OR, on the leader's command line:

pios plugins install pioreactor-relay-plugin   # to install on all Pioreactors in a cluster
```

Or install through the web interface (_Plugins_ tab). This will install the plugin on all Pioreactors within the cluster.

(Optional) Edit the following to your `config.ini`, or in the _Configurations_ tab on the web interface:

```
[PWM]
<the PWM channel you pick>=relay

[relay.config]
hz=100
post_delay_duration=0.2
pre_delay_duration=1.5
enable_dodging_od=1
```

## Usage

#### Through the command line:
```
pio run relay
```

#### Through the UI:

Under _Manage_, there will be a new _Activities_ option called _Relay_. Editable settings include an "on/off" switch to allow the plugin to be toggled while active.

## Plugin documentation

Documentation for plugins can be found on the [Pioreactor docs](https://docs.pioreactor.com/developer-guide/intro-plugins).
