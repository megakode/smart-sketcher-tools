# smart-sketcher-tools
Tools and protocol specifications for the smART Sketcher Projecter 2.0

If you bought your kid the above mentioned device, you probably got really angry when you opened the app and discovered the outrages monthly prices they tried to get you to pay, just for a tiny bunch of clip art images, which there are thousands of freely available on the internet (i.e. http://clipart-library.com/).

For you, the angry parent, i hereby give you a free alternative, for you to either use directly or build your own app/tool upon.

# Tool usage

`sketcher.py` is small python tool, that can transfer images in most formats directly from your PC to the projector.

**Usage:**

`python3 sketcher.py sendimage dog.jpg`

This will automatically try to scan for a nearby device and send an image to it.

You can also specify the Bluetooth address directly (which is a lot faster):

`python3 sketcher.py --adr 11:22:33:44:55:66 sendimage dog.jpg`

**Requirements:**

The required Python packages can be seen in the usual `requirements.txt` file:

```
asyncclick
anyio
progress
pil
bleak
```
