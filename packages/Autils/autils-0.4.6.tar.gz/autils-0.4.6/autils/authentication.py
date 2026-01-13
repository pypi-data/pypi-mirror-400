
import pyotp


class TwoStepVerification(object):
    '''两步验证'''

    def __init__(self, login):
        self.login = login
        self.otp_str = pyotp.random_base32()

    def get_qrcode_string(self, issuer_name=None):
        '''获取用于生成二维码的字符'''
        return pyotp.TOTP(self.otp_str).provisioning_uri(self.login, issuer_name)

    @classmethod
    def check(cls, otp_str, code):
        """
        验证code是否正确
        """
        return pyotp.TOTP(otp_str).now() == code
