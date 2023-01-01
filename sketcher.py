import asyncio
from bleak import BleakClient, BleakScanner
from PIL import Image
import anyio
import asyncclick as click
from progress.bar import Bar

ble_char_uuid = "0000ffe3-0000-1000-8000-00805f9b34fb"

# delay between sending each line in the image. The device does send an OK notification when it's ready to receive a new line,
# but i can see that these are sometimes bundled together as one "OKOK" message and it just seems a bit unreliable. 
# Setting a fixed delay seemed to work better. If things seems unstable, try increaseing this a tiny bit.
delay_between_image_lines = 0.05 

def ble_notify_callback(sender: int, data: bytearray):
    '''Callback when receiving notifications from BLE device'''
    global state
    # print(f"Received: {data}")
    state = 1


@click.group()
@click.option('--adr', help='BT address of device e.g. 11:22:33:44:55:66')
@click.pass_context
async def cli(ctx,adr):
    '''example usage: sketcher.py --adr 11:22:33:44:55:66 sendimage'''
    ctx.ensure_object(dict)

    ctx.obj['adr'] = adr
    pass

@cli.command()
@click.pass_context
@click.argument('filename',type=click.Path(exists=True))
async def sendimage(ctx,filename):

    adr = ctx.obj['adr']
    image = Image.open(filename)
    # print(image.mode) # Output: RGB
    # print(f"Image size = {image.size}") # Output: (1920, 1280)

    if(image.size[0] != 160 or image.size[1] != 128):
        print("Image size is not 160x128, performing resizing.... (aspect ratio might be wrong)")
        image = image.resize(size=(160,128))

    image = image.convert('RGB')

    if adr is None:
        print("BT Address not given. Scanning for device instead...")

        devices = await BleakScanner.discover()
        detected_adr = None
        for d in devices:
            if d.name == "smART_sketcher2.0":
                detected_adr = d.address
                print(f'Found smART Sketchet 2.0 device with address {detected_adr}')
                break

        if detected_adr is None:
            print("Could not find a device nearby.")
            exit(0)

        adr = detected_adr

    print(f"Connecting to device with address {adr}")

    async with BleakClient(adr) as client:
        
        # for service in client.services:
        #     print(service)

        await client.start_notify(ble_char_uuid, ble_notify_callback)

        # "Send Image" command 
        data = [0x01,0x00,0x00,0x00,0x50,0x00,0x01,0x00]
        await client.write_gatt_char(char_specifier=ble_char_uuid,data=data)
        send_lines = 0
        x = 0
        y = 0
        bar = Bar('Sending image data', max=128,suffix="%(index)d / %(max)d Lines")
        while send_lines < 128:
            line_data = bytearray()
            for x in range(0,160):
                r,g,b = image.getpixel((x,y))

                # Convert to RGB565
                byte1 = (r & 0xf8) | (g>>5)
                byte2 = ( (g & 0x1c) << 3 ) | (g>>3)

                line_data.append(byte1)
                line_data.append(byte2)

            await asyncio.sleep(0.05) 
            # Send actual image data
            await client.write_gatt_char(char_specifier=ble_char_uuid,data=line_data)
            bar.next()
            send_lines+=1
            y += 1

        print("\r\nDone")

if __name__ == '__main__':
    cli()