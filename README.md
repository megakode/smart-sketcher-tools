# smart-sketcher-tools
Tools and protocol specifications for the smART Sketcher Projecter 2.0

If you bought your kid the above mentioned device, you probably got really angry when you opened the app and discovered the outrages monthly prices they tried to get you to pay, just for a tiny bunch of clip art images, which there are thousands of freely available on the internet (i.e. http://clipart-library.com/).

For you, the angry parent, i hereby give you a free alternative ❤️, for you to either use directly or build your own app/tool upon.

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

# Protocol specification

***BLE***

All interaction with the device (both sending commands, image data and receiving notifications), is done using the following BLE characteristic:

```0000ffe3-0000-1000-8000-00805f9b34fb```

The device generally takes a command and then sends a notification back as an answer. Most commands just answer with a status message in plain ascii: `OK`

***Sending images***

Images needs to be transfered in 160 x 128 pixels in RGB565 format. A single pixel thus takes up two bytes:

```RRRRRGGG GGGBBBBB```

Before sending the actual image data, a "Send Image" command needs to be send. After that, image data transfer happens 4 packets at a time, until the device sends an `OK` notification back, indicating that it is ready for more data. (Maybe the packet sizes can be set to something else, i have not experimented with that)


Send Image command:
```
[0x01,0x00,0x00,0x00,0x50,0x00,0x01,0x00]
```

Image Data (repeat this for all 128 lines):
```
[one horizontal line of image data in RGB565 format]
```

Device will send a notification after each line, indicating it is ready for the next:
```
[0x4F 0x4B] ('OK' in ASCII)
```
