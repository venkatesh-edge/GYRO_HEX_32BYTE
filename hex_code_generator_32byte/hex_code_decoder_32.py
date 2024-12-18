import serial

def decode_data(raw_data, roll, pitch):
    if len(raw_data) == 32 and raw_data[:2] == b'\x5A\xA5' and raw_data[-1] == 0xAA:
        data = {
            "Status 1": raw_data[4],
            "Status 2": raw_data[5],
            "Attitude Heading (°)": round(int.from_bytes(raw_data[6:8], byteorder="big") * (180 / 2 ** 15), 3),
            "Attitude Roll (°)": round(int.from_bytes(raw_data[8:10], byteorder="big", signed=True) * (90 / 2 ** 15),3),
            "Attitude Pitch (°)": round(int.from_bytes(raw_data[10:12], byteorder="big", signed=True) * (90 / 2 ** 15),3),
            "Attitude Heading rate": round(int.from_bytes(raw_data[12:14], byteorder="big") * (1 / 2 ** 15), 3),
            "Attitude Roll rate": round(int.from_bytes(raw_data[14:16], byteorder="big", signed=True) * (1 / 2 ** 15), 3),
            "Attitude Pitch rate": round(int.from_bytes(raw_data[16:18], byteorder="big", signed=True) * (1 / 2 ** 15),3),
            "INS North Velocity (m/s)": round(int.from_bytes(raw_data[18:20], byteorder="big", signed=True) * 0.002, 3),
            "INS East Velocity (m/s)": round(int.from_bytes(raw_data[20:22], byteorder="big", signed=True) * 0.002, 3),
            "INS Down Velocity (m/s)": round(int.from_bytes(raw_data[22:24], byteorder="big", signed=True) * 0.002, 3),
            "Linear Acceleration North": round(int.from_bytes(raw_data[24:26], byteorder="big", signed=True) * 0.01, 3),
            "Linear Acceleration East": round(int.from_bytes(raw_data[26:28], byteorder="big", signed=True) * 0.01, 3),
            "Linear Acceleration Down": round(int.from_bytes(raw_data[28:30], byteorder="big", signed=True) * 0.01, 3)
        }
        roll= round(int.from_bytes(raw_data[8:10], byteorder="big", signed=True) * (90 / 2 ** 15), 3)
        pitch = round(int.from_bytes(raw_data[10:12], byteorder="big", signed=True) * (90 / 2 ** 15), 3)

        for key, value in data.items():
            print(f"{key} : {value}")
        return data, roll, pitch
    else:
        return {"Error": "Invalid or incomplete data"}

def main():
    roll = 0
    pitch = 0
    serRead = serial.Serial(port="COM2", baudrate=38400, timeout=1, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_EVEN)
    serWrite = serial.Serial(port="COM20", baudrate=38400, timeout=1)
    while True:
        raw_data = serRead.read(32)
        if len(raw_data) == 32:
            data, roll, pitch = decode_data(raw_data, roll, pitch)
            # print(data)
            print(f"Roll: {roll}")
            print(f"Pitch: {pitch}")
            serWrite.write(f"{roll}, {pitch}".encode())
            raw_data = f"{' '.join(format(byte, '02X') for byte in raw_data)}"
            print(raw_data)


if __name__ == "__main__":
    main()
