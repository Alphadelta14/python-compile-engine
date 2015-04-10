
try:
    from StringIO import StringIO as BytesIO
    binary_type = str
except:
    from io import BytesIO
    binary_type = bytes


class Engine(BytesIO):
    """Execute a decompiled function with this object to compile it
    """

    def write_value(self, value, size=4):
        """Write a fixed length value to the buffer

        Parameters
        ----------
        value : int
            Unsigned value to write
        size : int
            Number of bytes that value should occupy
        """
        buff = binary_type()
        for i in range(size):
            buff += chr((value >> i) & 0xFF)
        self.write(buff)
