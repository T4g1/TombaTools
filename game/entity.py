from bitutils import TypeSize, read_int, write_int

GAME_ENTITY_ADDRESS = 0x0A5970
GAME_ENTITY_COUNT = 200

OBJECT_SLOTS_ADDRESS = 0x0A55C0
OBJECT_SLOTS_COUNT = 0x2D

EVENT_CHAR_ADDRESS = 0x0B0B88
EVENT_CHAR_COUNT = 0x2D

ENTITY_HANDLERS_BASE_ADDRESS = {
    0x02: 0x800772BC,
    0x03: 0x8007C6B0,
    0x04: 0x8007D30C,
    0x05: 0x8007E8A8,
}


class Entity:
    SIZE = 0xD4

    def __init__(self, address: int):
        self.address = address
        self.load(bytearray(Entity.SIZE))

    def load(self, raw: bytearray):
        self.raw = raw.copy()

        self.occupied = raw[0]
        self.active = raw[1]
        self.handler_id = raw[2]
        self.param_2 = raw[3]
        self.status = raw[4]
        self.step = raw[5]
        self.clut = read_int(raw, 0x08, TypeSize.HALF_WORD) * 32
        self.flags = raw[0x0C:0x10]

        self.position_x = read_int(raw, 0x12, TypeSize.HALF_WORD, signed=True)
        self.position_y = read_int(raw, 0x16, TypeSize.HALF_WORD, signed=True)
        self.position_z = read_int(raw, 0x1C, TypeSize.HALF_WORD, signed=True)

        self.handlers_array_id = raw[0x1C]

        self.vram_page_offset = read_int(
            raw, 0x1E, TypeSize.HALF_WORD, byteorder="little"
        )

        self.ttl = read_int(raw, 0x20, TypeSize.WORD)

        self.current_frame = read_int(raw, 0x24, TypeSize.WORD)
        self.frame_array = read_int(raw, 0x3C, TypeSize.WORD)

        self.rotation_x = read_int(raw, 0x84, TypeSize.HALF_WORD)
        self.rotation_y = read_int(raw, 0x88, TypeSize.HALF_WORD)
        self.rotation_z = read_int(raw, 0x8C, TypeSize.HALF_WORD)

        self.target_x = read_int(raw, 0xC4, TypeSize.HALF_WORD, signed=True)
        self.target_y = read_int(raw, 0xC6, TypeSize.HALF_WORD, signed=True)

        self.texture_x_start = read_int(raw, 0x6C, TypeSize.HALF_WORD)
        self.texture_y_start = read_int(raw, 0x6E, TypeSize.HALF_WORD)
        self.texture_x_end = read_int(raw, 0x70, TypeSize.HALF_WORD)
        self.texture_y_end = read_int(raw, 0x72, TypeSize.HALF_WORD)

        self.addr_bc = read_int(raw, 0xBC, TypeSize.WORD)

        self.linked_entity = raw[0x94:0x98]

    def __str__(self):
        value = f"{hex(self.address)} - Occupied: {hex(self.occupied)}, "
        value += f"Param 1: {hex(self.handler_id)}, "
        value += f"Param 2: {hex(self.param_2)}, "
        value += f"Status: {hex(self.status)}, "
        value += f"CLUT: {hex(self.clut)}, "
        value += f"TTL: 0x{self.addr_bc:04X}, "
        value += f"Flags: {self.flags.hex()}, "
        value += f"BC: 0x{self.addr_bc:04X}, "
        value += f"Position: {hex(self.position_x)}, {hex(self.position_y)}, "
        value += f"Texture: 0x{self.texture_x_start:04X}, 0x{self.texture_y_start:04X}, 0x{self.texture_x_end:04X}, 0x{self.texture_y_end:04X}, "
        return value

    def to_bytearray(self) -> bytearray:
        data = self.raw
        data[0x00] = self.occupied
        data[0x01] = self.active
        data[0x02] = self.handler_id
        data[0x03] = self.param_2
        data[0x04] = self.status
        data[0x05] = self.step
        data = write_int(data, 0x08, TypeSize.HALF_WORD, self.clut)

        data = write_int(data, 0x12, TypeSize.HALF_WORD, self.position_x)
        data = write_int(data, 0x16, TypeSize.HALF_WORD, self.position_y)
        data = write_int(data, 0x1C, TypeSize.HALF_WORD, self.position_z)

        data[0x1C] = self.handlers_array_id

        data = write_int(data, 0x1E, TypeSize.WORD, self.vram_page_offset)

        data = write_int(data, 0x20, TypeSize.WORD, self.ttl)

        data = write_int(data, 0x24, TypeSize.WORD, self.current_frame)
        data = write_int(data, 0x3C, TypeSize.WORD, self.frame_array)

        data = write_int(data, 0x40, TypeSize.WORD, self.address + 0x10)
        data = write_int(data, 0x44, TypeSize.WORD, self.address + 0x18)

        data = write_int(data, 0x84, TypeSize.HALF_WORD, self.rotation_x)
        data = write_int(data, 0x88, TypeSize.HALF_WORD, self.rotation_y)
        data = write_int(data, 0x8C, TypeSize.HALF_WORD, self.rotation_z)

        data = write_int(data, 0xC4, TypeSize.HALF_WORD, self.target_x, signed=True)
        data = write_int(data, 0xC6, TypeSize.HALF_WORD, self.target_y, signed=True)

        return data

    def get_handler_address(self) -> int:
        base_address = ENTITY_HANDLERS_BASE_ADDRESS.get(self.handlers_array_id, None)
        if base_address is None:
            return 0x00

        return base_address + self.handler_id * TypeSize.WORD
