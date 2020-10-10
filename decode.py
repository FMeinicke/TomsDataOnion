#!/usr/bin/env python3
#%%
from typing import Union
import urllib.request
import html

import layer0
import layer1
import layer2
import layer3
import layer4
import layer5
import layer6

def extract_payload(layer: Union[str, bytes]):
    """
    Extract the Ascii85 encoded payload from the layer description `layer`
    """
    return layer[layer.index(b'<~'):layer.rindex(b'~>')+2]

data_onion: bytes = b''

print("Fetching latest Data Onion...")
request = urllib.request.Request('https://www.tomdalling.com/toms-data-onion/', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(request) as doc:
    data_onion = doc.read()
    # we're only interested in the ASCII text describing and containing the onion
    data_onion = data_onion.split(b'<pre>')[1].split(b'</pre>')[0].strip()
    data_onion = html.unescape(data_onion.decode('utf-8')).encode('utf-8')

data_onion = layer0.decode(extract_payload(data_onion))
data_onion = layer1.decode(extract_payload(data_onion))
data_onion = layer2.decode(extract_payload(data_onion))
data_onion = layer3.decode(extract_payload(data_onion))
data_onion = layer4.decode(extract_payload(data_onion))
data_onion = layer5.decode(extract_payload(data_onion))
data_onion = layer6.decode(extract_payload(data_onion))

print("Done!\n", data_onion.decode('utf-8'))
