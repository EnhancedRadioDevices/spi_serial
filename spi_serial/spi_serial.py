import gpio as g
import time
import spidev


class SpiSerial():
    def __init__(self):
        # read cpuinfo to determine hw
        # f = file("/proc/cpuinfo")
        # proc = ""
        # for line in f:
            # if "Intel" in line:
                # proc = "Intel"
                # break

        # if "Intel" in proc:
            # self.CS0 = 23
            # self.SPI_FROM_DESC = "spi-raw-5-1"
            # self.RST_PIN = 36
        # else: # assume RPi
            # self.CS0 = 24
            # self.SPI_FROM_DESC = "spi-raw-0-0"
            # self.RST_PIN = 7
#        self.CS0 = (ord("C") - ord("A")) * 32 + 3 #PC3
        self.RST_PIN = (ord("E") - ord("A")) * 32 + 8 #PE8
        
#        self.cs0 = m.Gpio(self.CS0)
#        self.cs0.dir(m.DIR_OUT)
#        self.cs0.write(1)

#        self.dev = m.spiFromDesc(self.SPI_FROM_DESC)
        self.dev = spidev.SpiDev()           # create spi object
        self.dev.open(0, 0)                  # open spi port 0, device (CS) 0
        
        self.dev.max_speed_hz = (62500)
        self.dev.mode = 0b00 #(m.SPI_MODE0)
        self.dev.bits_per_word = (8)
        self.dev.lsbfirst = True
        self.timeout = 0
        self.rx_buf = []

    def close(self):
        self.dev.close()

    def write(self, tx_bytes):
#        tx_bytes = bytearray(tx_bytes)
        self.dev.xfer([0x99]) #spi_xfer(0x99)
        num_rxd = self.dev.xfer([len(tx_bytes)]) #spi_xfer(len(tx_bytes))
        num_rxd = num_rxd[0]
        rx = self.dev.xfer(tx_bytes)
        if (num_rxd > 0):
            to_rx = min(num_rxd, len(rx))
            self.rx_buf.extend(rx[:to_rx])
            num_rxd = num_rxd - to_rx
        if num_rxd > 0:
            rx = self.dev.xfer([0]*num_rxd)
            self.rx_buf.extend(rx)
#        for y in range(0, len(tx_bytes)):
#            rx = self.spi_xfer(tx_bytes[y])
#            if num_rxd > 0:
#                self.rx_buf.append(rx)
#                num_rxd -= 1
#        for y in range(0, num_rxd):
#            rx = self.spi_xfer(0)
#            self.rx_buf.append(rx)

    def read(self, num_bytes=0):
        if num_bytes == 0:
            num_bytes = len(self.rx_buf)
        ret_val = self.rx_buf[0:num_bytes]
        del(self.rx_buf[0:num_bytes])
        return ret_val

    def peek(self):
        return self.rx_buf[0]

    def pop(self):
        return self.read(1)

    def inWaiting(self):
        e = self.dev.xfer([0x99, 0x00])
        #num_rxd = self.dev.xfer([0])
        num_rxd = e[1]
        if num_rxd > 0:
            rx = self.dev.xfer([0]*num_rxd)
            self.rx_buf.extend(rx)
#        for y in range(0, num_rxd):
#            rx = self.spi_xfer(0)
#            self.rx_buf.append(rx)
        return len(self.rx_buf)

    def reset(self):
        #self.RST = m.Gpio(self.RST_PIN)
        #self.RST.dir(m.DIR_OUT)
        #self.RST.write(0)   # reset the device
        g.setup(self.RST_PIN, g.OUT)
        g.output(self.RST_PIN, 0)
        time.sleep(0.01)
        #self.RST.write(1)   # let the device out of reset
        g.output(self.RST_PIN, 1)
        time.sleep(2.01)    # wait for the CC1110 to come up
        # TODO: change the CC1110 code to not have a 2s delay
