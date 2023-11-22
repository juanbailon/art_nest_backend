
class PasswordResetOTPError(Exception):
    pass

class BlacklistedOTPError(PasswordResetOTPError):
    pass

class MaxFailedAttemptsOTPError(PasswordResetOTPError):
    pass

class ExpiredOTPError(PasswordResetOTPError):
    pass