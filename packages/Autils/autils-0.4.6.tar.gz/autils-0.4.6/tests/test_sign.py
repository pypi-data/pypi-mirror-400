
from autils import Sign, CRCXMODEM
import unittest
from hashlib import md5


class TestSign(unittest.TestCase):

    def test_dict_sign_lower(self):
        params = {
            "doloadUrl": "http://odoo.mixoo.cn/8.0/MoYao-Raspiberry-Controller-1.0.tar.gz",
            "name": "main",
            "timeStamp": "1528858347",
            "tradeNo": "41",
            "tranType": "T0008",
            "transCode": "10016",
            "version": "1.0.2",
        }

        sign = Sign()

        self.assertEqual(sign.dict_order_sign(params),
                         "c0a4ad7304425de1b01cd5700972f61a")

    def test_crc_xmodem(self):
        crc = CRCXMODEM()
        self.assertEqual(crc.calculate(b'123'),int('9752',16))

    def test_dict_order(self):
        data = {
            "appId":"wx69d3ddf5dc6cfba7",
            "nonceStr":"qzF33vU9uGJqxpZp",
            "package":"prepay_id=wx20185220358456013ef5bf331847465548",
            "signType":"MD5",
            "timeStamp":"1542711143",
            
        }
        
        self.assertEqual(Sign().wechat_sign(data,"3MlPTPhS2Lbm9mEL6jCZYa5D5OeVijVU"),"032F74C594F0024C9258B20A8B097C5F")

if __name__ == '__main__':
    unittest.main()
