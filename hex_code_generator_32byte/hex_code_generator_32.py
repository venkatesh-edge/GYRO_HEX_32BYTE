import random
import struct
import serial
import time

def generate_32_byte_mock_data():
    # Header: Fixed 2 bytes
    data = b'\x5A\xA5'

    # Number of Data Bytes: Fixed 1 byte (0x1A for 26 bytes of payload)
    data += b'\x1A'

    # Identifier: Fixed 1 byte
    data += b'\x01'

    # Status 1 and Status 2: Random 1 byte each
    data += random.randint(0, 255).to_bytes(1, 'big')  # Status 1
    data += random.randint(0, 255).to_bytes(1, 'big')  # Status 2

    # Attitude (Heading, Roll, Pitch)
    # Apply resolution scaling
    heading = random.randint(0, (2 ** 15) - 1).to_bytes(2, byteorder="big")  # Scaled for 0 to 360
    scale_factor = (2 ** 15 - 1) // 90
    roll = random.randint(-90 * scale_factor, 90 * scale_factor).to_bytes(2, byteorder="big", signed=True)
    pitch = random.randint(-90 * scale_factor, 90 * scale_factor).to_bytes(2, byteorder="big", signed=True)
    data += heading + roll + pitch

    # Attitude Rates (Heading Rate, Roll Rate, Pitch Rate)
    for _ in range(3):
        rate_raw = random.randint(-(2**15), (2**15) - 1)  # ±1 rad/s raw (15 bits)
        data += rate_raw.to_bytes(2, 'big', signed=True)

    # INS Velocity (North, East, Down)
    for _ in range(3):
        velocity_raw = random.randint(-(2**15), (2**15) - 1)  # ±65.536 m/s raw (15 bits)
        data += velocity_raw.to_bytes(2, 'big', signed=True)

    # Linear Acceleration (North, East, Down)
    for _ in range(3):
        accel_raw = random.randint(-(2**15), (2**15) - 1)  # ±327.68 m/s² raw (15 bits)
        data += accel_raw.to_bytes(2, 'big', signed=True)

    # Check Byte: Mocked as the sum of all data bytes modulo 256
    checksum = sum(data) % 256
    data += checksum.to_bytes(1, 'big')

    # Terminator: Fixed 1 byte (0xAA)
    data += b'\xAA'

    return data


def main():
    port_name = input("Enter the mock serial port name (e.g., COM4 or /dev/pts/4): ")
    try:
        # Configure serial port with the specified settings
        with serial.Serial(
                port=port_name,
                baudrate=38400,          # Baud Rate: 19200
                stopbits=serial.STOPBITS_ONE,  # Stop Bit: 1
                parity=serial.PARITY_EVEN,    # Parity: Even
                timeout=1
        ) as ser:
            while True:
                mock_data = generate_32_byte_mock_data()
                # print(mock_data)
                ser.write(mock_data)  # Send data to the serial port
                print(f"Generated Mock Data: {' '.join(format(byte, '02X') for byte in mock_data)}")
                time.sleep(1)  # Simulate 1 Hz data rate
    except serial.SerialException as e:
        print(f"Error: {e}")





if __name__ == "__main__":
    main()
