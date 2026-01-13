import logging
import sys, asyncio, struct, time
from typing import Optional

from ..ble.interface import BLEInterface, Advertisement
from ..logger.logger import GiciskyLogger, LogCategory

BASE_SERVICE = 0xFEF0
SERVICE_UUID = f"0000{BASE_SERVICE:04x}-0000-1000-8000-00805f9b34fb"
CHAR_CMD_UUID = f"0000{BASE_SERVICE+1:04x}-0000-1000-8000-00805f9b34fb"
CHAR_IMG_UUID = f"0000{BASE_SERVICE+2:04x}-0000-1000-8000-00805f9b34fb"

CHUNK_SIZE = 240
MTU_WAIT = 0.03

class GiciskyProtocol:

    def __init__(self, ble: BLEInterface, logger: Optional[logging.Logger] = None):
        self.ble = ble
        self.packet_index = 0
        self.ready_to_send = False
        self.img_hex = b""
        self.upload_done = True
        self.logger = GiciskyLogger(logger)

    async def handle_notification(self, data):
        hx = data.hex()
        self.logger.debug(f"Notify: {hx}", LogCategory.NOTIFICATION)
        if hx.startswith("01f400"):
            # Step 2: ready to accept image size
            self.logger.info("Device ready to accept image size", LogCategory.PROTOCOL)
            await self.send_command(2, struct.pack("<I", int(len(self.img_hex))) + b"\x00\x00\x00")
        elif hx.startswith("02"):
            # Step 3: begin upload
            self.logger.info("Starting image upload", LogCategory.DATA_TRANSFER)
            await self.send_command(3)
        elif hx.startswith("05"):
            # Image upload loop
            self.logger.debug(f"Handling response: {hx}, err: {hx[2:4]}, part: {hx[4:12]}", LogCategory.NOTIFICATION)
            err = hx[2:4]
            if err == "00":  # continue sending chunks
                await self.send_next_chunk(hx[4:12])
            elif err == "08":  # upload complete
                self.logger.info("Upload completed successfully.", LogCategory.DATA_TRANSFER)
                self.img_hex = b""
                self.upload_done = True
            else:
                self.logger.error(f"Error code during upload: {err}", LogCategory.DATA_TRANSFER)

    async def send_command(self, cmd_id, payload=b""):
        pkt = bytes([cmd_id]) + payload
        await self.ble.write(CHAR_CMD_UUID, pkt)
        self.logger.debug(f"Cmd {cmd_id:02x} sent: {pkt.hex()}", LogCategory.COMMAND)

    async def send_next_chunk(self, ack_hex):
        ack = struct.unpack("<I", bytes.fromhex(ack_hex))[0]
        if not self.img_hex:
            self.logger.debug("No more data to send.", LogCategory.DATA_TRANSFER)
            return

        if ack == self.packet_index:
            prefix = struct.pack("<I", self.packet_index)
            self.packet_index += 1
            chunk = self.img_hex[:CHUNK_SIZE]
            self.img_hex = self.img_hex[CHUNK_SIZE:]
            await self.ble.write(CHAR_IMG_UUID, prefix + chunk)
            self.logger.debug(f"Sent packet #{self.packet_index - 1} {ack_hex}", LogCategory.DATA_TRANSFER)
            await asyncio.sleep(MTU_WAIT)
        else:
            self.logger.warning(f"ACK mismatch ({ack} != {self.packet_index})", LogCategory.DATA_TRANSFER)

    async def upload_image(self, img: bytes):
        """Upload image to the device.
        
        Note: The display will not refresh until disconnect() is called, 
        or refresh_display() is used. This is a hardware limitation.
        
        Args:
            img: Image data as bytes to upload to the device
        """
        self.img_hex = img
        self.upload_done = False
        self.packet_index = 0

        await self.ble.start_notify(CHAR_CMD_UUID, self.handle_notification)
        self.logger.info("Notifications started.", LogCategory.PROTOCOL)
        await self.send_command(1)  # init command

        while not self.upload_done:
            await asyncio.sleep(0.5)
    
    async def refresh_display(self, mac: str):
        """Refresh the display by disconnecting, then re-connect automatically.
        
        This is required after image upload for the device to refresh its display.
        It is not required if the connection is closed after the upload.
        The device hardware requires a BLE disconnection to trigger the display refresh.
        
        Args:
            mac: The MAC address of the device to reconnect to
        """
        self.logger.info("Refreshing display (disconnecting)...", LogCategory.PROTOCOL)
        await self.ble.disconnect()
        
        self.logger.info("Reconnecting to refresh display...", LogCategory.PROTOCOL)
        await self.ble.connect(mac)
        
        self.logger.info("Display refreshed.", LogCategory.PROTOCOL)
