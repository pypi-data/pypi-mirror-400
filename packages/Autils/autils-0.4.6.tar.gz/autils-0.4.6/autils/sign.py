'''
编程工具
'''
from hashlib import md5

class Sign(object):
    '''
    校验
    '''

    def dict_order_sign(self, params, lower=True):
        '''
        字典序排序
        先转大小写再md5返回
        将参数按字典序排序，形如a=b&b=d，然后返回md5值
        params: 参数字典
        lower: 默认小写
        '''
        strs = '&'.join(['{}={}'.format(key, params.get(key))
                         for key in sorted(params.keys()) if params.get(key)])
        if lower:
            return md5(strs.lower().encode('utf-8')).hexdigest()
        return md5(strs.upper().encode('utf-8')).hexdigest()

    def dict_order_post(self,params):
        '''
        字典序排序
        返回utf-8编码后的值
        '''
        strs = '&'.join(['{}={}'.format(key, params.get(key))
                         for key in sorted(params.keys()) if params.get(key)])
        return strs.encode("utf-8")

    def wechat_sign(self,params,key):
        '''
        微信验签版
        key为商户密钥
        '''
        return md5(self.dict_order_post(params) + "&key={}".format(key).encode("utf-8")).hexdigest().upper()


from ctypes import c_ushort

class CRCCCITT(object):
    '''
    CCITT 模式 CRC校验
    '''
    crc16kermit_tab = []

    # The CRC's are computed using polynomials. Here is the most used
    # coefficient for CRC16 SICK
    crc16Kermit_constant = 0x8408

    def __init__(self):
        # initialize the precalculated tables
        if not len(self.crc16kermit_tab):
            self.init_crc16kermit()

    def calculate(self, input_data=None):
        try:
            is_string = isinstance(input_data, str)
            is_bytes = isinstance(input_data, bytes)

            if not is_string and not is_bytes:
                raise Exception("Please provide a string or a byte sequence "
                                "as argument for calculation.")

            crcValue = 0x0000

            for c in input_data:
                d = ord(c) if is_string else c
                tmp = crcValue ^ d
                crcValue = c_ushort(crcValue >> 8).value ^ int(
                    self.crc16kermit_tab[(tmp & 0x00ff)], 0)

            # After processing, the one's complement of the CRC is calculated
            # and two bytes of the CRC are swapped.
            # low_byte = (crcValue & 0xff00) >> 8
            # high_byte = (crcValue & 0x00ff) << 8
            low_byte = (crcValue & 0xff00) >> 8
            high_byte = (crcValue & 0x00ff) << 8
            # crcValue = low_byte | high_byte

            return crcValue
        except Exception as e:
            print("EXCEPTION(calculate): {}".format(e))

    def init_crc16kermit(self):
        '''The algorithm use tables with precalculated values'''
        for i in range(0, 256):
            crc = c_ushort(i).value
            for j in range(0, 8):
                if (crc & 0x0001):
                    crc = c_ushort(crc >> 1).value ^ self.crc16Kermit_constant
                else:
                    crc = c_ushort(crc >> 1).value
            self.crc16kermit_tab.append(hex(crc))

class CRCXMODEM(object):
    '''
    XMODEM CRC计算
    '''
    crc_ccitt_tab = []

    # The CRC's are computed using polynomials.
    # Here is the most used coefficient for CRC CCITT
    crc_ccitt_constant = 0x1021

    def __init__(self, version='XModem'):
        try:
            dict_versions = {'XModem': 0x0000, 'FFFF': 0xffff, '1D0F': 0x1d0f}
            if version not in dict_versions.keys():
                raise Exception("Your version parameter should be one of \
                    the {} options".format("|".join(dict_versions.keys())))

            self.starting_value = dict_versions[version]

            # initialize the precalculated tables
            if not len(self.crc_ccitt_tab):
                self.init_crc_ccitt()
        except Exception as e:
            print("EXCEPTION(calculate): {}".format(e))

    def calculate(self, input_data=None):
        try:
            is_string = isinstance(input_data, str)
            is_bytes = isinstance(input_data, bytes)

            if not is_string and not is_bytes:
                raise Exception("Please provide a string or a byte sequence \
                    as argument for calculation.")

            crcValue = self.starting_value

            for c in input_data:
                d = ord(c) if is_string else c
                tmp = (c_ushort(crcValue >> 8).value) ^ d
                crcValue = (c_ushort(crcValue << 8).value) ^ int(
                    self.crc_ccitt_tab[tmp], 0)

            return crcValue
        except Exception as e:
            print("EXCEPTION(calculate): {}".format(e))

    def init_crc_ccitt(self):
        '''The algorithm uses tables with precalculated values'''
        for i in range(0, 256):
            crc = 0
            c = i << 8

            for j in range(0, 8):
                if ((crc ^ c) & 0x8000):
                    crc = c_ushort(crc << 1).value ^ self.crc_ccitt_constant
                else:
                    crc = c_ushort(crc << 1).value

                c = c_ushort(c << 1).value  # equivalent of c = c << 1
            self.crc_ccitt_tab.append(hex(crc))


if __name__ == "__main__":
    crc = CRCXMODEM()

