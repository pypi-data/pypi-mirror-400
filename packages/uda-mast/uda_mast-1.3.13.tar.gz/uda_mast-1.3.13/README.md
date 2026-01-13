uda-mast is a wrapper around the basic [pyuda](https://test.pypi.org/project/uda/) data access layer that provides additional functinality specific to the data systems for [UKAEA's](https://www.gov.uk/government/organisations/uk-atomic-energy-authority) MAST and [MASTU](https://ccfe.ukaea.uk/programmes/mast-upgrade/) experimental fusion devices.

Note that the source code is currently hosted on an internal gitlab server that can only be accessed from the UKAEA network.

## Quickstart

Note that the `mast` module is registered subclient in pyuda, so if uda-mast is pip-installed it's functionality will be available when you import pyuda.

```sh
export UDA_META_PLUGINNAME=MASTU_DB
export UDA_METANEW_PLUGINNAME=MASTU_DB
```

```py
import pyuda

pyuda.Client.server = "<server_address>"
pyuda.Client.port = <port_number>
client = pyuda.Client()

signals = client.list_signals(shot=<experiment_id>)
signal_objects = client.get_batch(signals, <experiment_id>)

image_data = client.get_images(<file_alias>, <experiment_id>)

geometry_data = client.geometry(<signal_name>, <experiemnt_id>)
```

