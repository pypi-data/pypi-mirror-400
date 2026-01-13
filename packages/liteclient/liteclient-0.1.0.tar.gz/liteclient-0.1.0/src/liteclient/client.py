import socket


class LiteClient:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.file = self.socket.makefile("rb")

    def _send_command(self, *args):
        """Encodes and sends a command as a RESP Array of Bulk Strings."""
        # RESP Arrays start with '*' followed by the number of elements
        cmd = [f"*{len(args)}\r\n"]
        for arg in args:
            # Each argument is a Bulk String: '$' + length + data
            s_arg = str(arg)
            cmd.append(f"${len(s_arg)}\r\n{s_arg}\r\n")

        self.socket.sendall("".join(cmd).encode("utf-8"))
        return self._read_response()

    def _read_response(self):
        """Parses the RESP response from the server."""
        line = self.file.readline()
        if not line:
            return None

        prefix = line[0:1]
        payload = line[1:-2]  # Strip prefix and CRLF (\r\n)

        if prefix == b"+":  # Simple String (e.g., +OK)
            return payload.decode("utf-8")
        elif prefix == b"-":  # Error
            raise Exception(f"Redis Error: {payload.decode('utf-8')}")
        elif prefix == b":":  # Integer
            return int(payload)
        elif prefix == b"$":  # Bulk String
            length = int(payload)
            if length == -1:
                return None  # Null Bulk String
            data = self.file.read(length)
            self.file.read(2)  # Consume trailing CRLF
            return data.decode("utf-8")
        elif prefix == b"*":  # Array
            count = int(payload)
            if count == -1:
                return None
            return [self._read_response() for _ in range(count)]

    # Supported Commands
    def set(self, key, value):
        return self._send_command("SET", key, value)

    def get(self, key):
        return self._send_command("GET", key)

    def delete(self, key):
        return self._send_command("DEL", key)

    def lpush(self, key, value):
        return self._send_command("LPUSH", key, value)

    def rpop(self, key):
        return self._send_command("RPOP", key)

    def blpop(self, keys, timeout=0):
        """
        Blocking pop. 'keys' can be a single string or a list of keys.
        'timeout' 0 means block indefinitely.
        """
        if isinstance(keys, str):
            keys = [keys]
        # Command format: BLPOP key1 key2 ... timeout
        return self._send_command("BLPOP", *keys, timeout)

    def close(self):
        self.socket.close()


# Usage Example:
# client = LiteClient('localhost', 6379)
# client.set('mykey', 'hello')
# print(client.get('mykey'))
