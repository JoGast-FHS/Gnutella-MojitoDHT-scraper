from src._general_._utilities_ import swap_byteorder

def processExtBlock(block_str):
    if block_str == "" or block_str == None:
        print("No ext block given to process")
        return

    bytelen = 2
    if block_str[:1*bytelen] != "c3":  # see GGEP documentation
        print("GGEP magic byte not found - corrupt extension block or different format")
        return

    lenHexStr = swap_byteorder(block_str[1*bytelen:-18*bytelen])  # see GGEP documentation for details
    portHexStr = swap_byteorder(block_str[-18*bytelen:-16*bytelen])
    addrHexStr = block_str[-16*bytelen:]
    # byte_data = lenHexStr.encode()  # Convert to bytes
    # masked_data = bytes(b & 0x3F for b in byte_data)  # Mask off the highest two bits
    # len = int(masked_data.hex(), 16)

    print(f"Extracted from Extension Block:\nLen: {lenHexStr}\nPort: {int(portHexStr, 16)}\nAddress: {addrHexStr}")