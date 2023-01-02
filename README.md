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

### BLE

All interaction with the device (both sending commands, image data and receiving notifications), is done using the following BLE characteristic:

```0000ffe3-0000-1000-8000-00805f9b34fb```


### Commands

All commands are 8 bytes long and has the general form:

```
========================================
| # Bytes | Description                |
========================================
|    2    | Command ID (Little endian) |
========================================
|    6    | Command parameters         |
========================================
```

The following commands IDs are available:

```
0x01 (01) - Send Image
0x02 (02) - Exercise (short exercise_id)
0x05 (05) - Next Step
0x06 (06) - Previous Step
0x07 (07) - Replay Steps
0x08 (08) - Get SD Id
0x09 (09) - Get System Version
0x0a (10) - Animation Speed Toggle
0x0b (11) - Get Animation Speed
0x0c (12) - Get "Where Am I" (Response = "OK_12_00_00_00_00_00" !?)
0x0f (15) - Update Brightness (short brightness)
0x10 (16) - Get Brightness
0x15 (21) - Reset SD Card (not tested! clone your SD card before testing!)
0x17 (23) - Send Partial Image (x,y,w,h)
0x20 (32) - Get LCD version
```

Unless indicated in the above list, the commands has no arguments besides the command id. The rest of the 8 commands bytes are then set to 0x00.

When sending images, the actual image data has to be preceeded by a "Send Image" command. More info in the "Sending Images" section below.

```
=========================================================
| Name    | Send Image                                  |
=========================================================
| Cmd ID  | 01                                          |
=========================================================
| Format  | [0x01,0x00,0x00,0x00,  *4,0x00,  *6,0x00]   |     
=========================================================
| Example | [0x01,0x00,0x00,0x00,0x50,0x00,0x01,0x00]   |
| Notes   | *4 = In the app there is some logic looking |
|           at an unknown parameter:                    |
|           cmd[4] = i >= 160 ? (byte) -96 : (byte) 80; |
|                                                       |
|           *6 = Image comp.                            |
|                if (useImageTransferComp) {            |
|                   cmd[6] = 1;                         |
|                 } else {                              |
|                   if (chipset == Chipset.HM_17) {     |
|                     cmd[6] = Byte.MIN_VALUE;          |
|                   } else {                            |
|                     cmd[6] = 2;                       |
|                   }                                   |
|                 }                                     |
|                                                       |
|         The option can be toggled in the mobile app   |
|                                                       |
|=======================================================|

=========================================================
| Name    | Exercise                                    |
=========================================================
| Cmd ID  | 0x02                                        |
=========================================================
| Format  [0x02,0x00,0x00,0x00,0x00,0x00,EID,EID]       |
|                                                       |
| EID = Exercise ID (2 bytes, little endian)            |
|                                                       |
=========================================================

=========================================================
| Name    | Update Brightness                           |
=========================================================
| Cmd ID  | 0x0F (15)                                   |
=========================================================
| Format  [0x02,0x00,0x00,0x00,0x00,0x00,BR,BR]         |
|                                                       |
| BR = Brightness (2 bytes, little endian)              |
| (TODO: Determine range)                               |
=========================================================

=========================================================
| Name    | Send Partial Image                          |
=========================================================
| Cmd ID  | 0x17 (23)                                   |
=========================================================
| Format  [0x17,0x00,0x02,0x00,x,y,w,h]                 |
|                                                       |
| x,y - Destination of the partial image                |
| w,h - Width and Height of the partial image           |
| The function of the short at index[2] and index[3]    |
| with the hardcoded value 0x0002 is yet to be          |
| determined.                                           |
|                                                       |
=========================================================

```


***Responses***

All responses are send as a notification from the GATT characteristic and are in ASCII form. 

Most commands reply with an "OK_nn" if they are successfull, where nn = Command ID in decimal.

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
