# -*- coding: utf-8 -*-
# 
# The main script module file to control PTZ cameras based on VISCA serial protocol
# By Samarthya Lykamanuella
# Licensed under GPL-3.0
# ---
# Original work of this library is due to Matthew Mage
# -> SOURCE: https://github.com/Sciguymjm/python-visca
# VISCA command documentation was obtained from Crestron
# -> SOURCE: https://docs.crestron.com/en-us/9326/Content/Topics/Configuration/VISCA-Comands.htm

from scipy.interpolate import interp1d
import binascii
import re
import serial

class Camera(object):
    _input = None
    _input_string = None
    _output = None
    _output_string = None

    def __init__(self, output='COM10'):
        """General VISCA-based PTZ control class.
        
        Initializes camera object by connecting to serial port.
        :param output: Outbound serial port string. (default: 'COM10')
        :type output: str
        """
        self._output = serial.Serial(output)

    @staticmethod
    def close():
        """Closes current serial port.

        :param serial_port: Serial port to modify.
        :return: True if successful, False if not.
        :rtype: bool
        """
        if self._output.isOpen():
            self._output.close()
            return True
        else:
            print("Error closing serial port: Already closed.")
            return False
        
    def command(self, com):
        """Sends hexadecimal string to serial port.

        :param com: Command string. Hexadecimal format.
        :type com: str
        :return: Success.
        :rtype: bool
        """
        try:
            self._output.write(binascii.unhexlify(com))
            return True
        except Exception as e:
            print(com, e)
            return False

    @staticmethod
    def open(serial_port):
        """Opens serial port.

        :param serial_port: Serial port to modify.
        :return: True if successful, False if not.
        :rtype: bool
        """
        if not self._output.isOpen():
            self._output = serial.Serial(serial_port)
            self._output.open()
            return True
        else:
            print("Error opening serial port: Already open.")
            return False
        
    def read(self, amount=3):
        total = ""
        while True:
            msg = binascii.hexlify(self._output.read())
            total = total + msg
            if msg == "ff":
                break
        return total


class PTZ(Camera):
    """Command class for general PTZ controller.
    
    In the original repo by Matthew Mage, it was initially
    developed for Sony EVI-D100 VISCA control class.
    Further documentation on the VISCA protocol (broken link):
    https://pro.sony.com/bbsccms/assets/files/mkt/remotemonitoring/manuals/rm-EVID100_technical_manual.pdf
    """

    interp = None

    values = ["1161h", "116Dh", "122Ah", "123Ch", "12F3h", "13C2h", "151Eh", "1536h", "1844h", "226Fh", "3F2Ah",
              "40AAh", "62C9h", "82C1h"]
    y = [
        20,
        18,
        16,
        14,
        12,
        10,
        8,
        6,
        4,
        2,
        1.5,
        1,
        0.5,
        0.1]

    def __init__(self, output='COM1'):
        """Instantiates the VISCA PTZ camera object.
        
        Then initializes camera object by connecting to serial port.
        :param output: Serial port string. (default: 'COM1')
        :type output: str
        """
        self.interp = interp1d([int(f[:-1], 16) for f in self.values], self.y)
        super(self.__class__, self).__init__(output=output)

    def _move(self, string, a1, a2):
        h1 = "%X" % a1
        h1 = '0' + h1 if len(h1) < 2 else h1

        h2 = "%X" % a2
        h2 = '0' + h2 if len(h2) < 2 else h2
        return self.comm(string.replace('VV', h1).replace('WW', h2))
    
    def aperture_down(self):
        """Turn down the camera's aperture value (non-variable).
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040203FF')
    
    def aperture_reset(self):
        """Reset the camera's aperture to default value.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040200FF')
    
    def aperture_up(self):
        """Turn up the camera's aperture value (non-variable).
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040202FF')

    def autofocus(self):
        """Turns autofocus on.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101043802FF')

    def autofocus_sens_high(self):
        """Changes autofocus sensitivity to high.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101045802FF')

    def autofocus_sens_low(self):
        """Changes autofocus sensitivity to low.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101045803FF')
    
    def backlight(self, toggle=1):
        """Turning the backlight compensation on/off.
        
        Defaults to "on" if invalid option is specified.
        :return: True if successful, False if not.
        :rtype: bool
        """
        if toggle == False or toggle == 0:
            return self.comm('8101043303FF')
        else:
            return self.comm('8101043302FF')
    
    def bright_down(self):
        """Turn down the camera's brightness.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040D03FF')
    
    def bright_reset(self):
        """Reset the camera's brightness setting to default.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040D00FF')
    
    def bright_up(self):
        """Turn up the camera's brightness.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040D02FF')

    def cancel(self):
        """Cancels current command.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('81010001FF')
        
    def comm(self, com):
        """Sends hexadecimal string to serial port.

        :param com: Command string. Hexadecimal format.
        :type com: str
        :return: Success.
        :rtype: bool
        """
        super(self.__class__, self).command(com)

    def down(self, amount=5):
        """Modifies tilt to down.

        :param amount: Speed (0-24)
        :return: True if successful, False if not.
        """
        hs = "%X" % amount
        hs = '0' + hs if len(hs) < 2 else hs
        s = '81010601VVWW0302FF'.replace('VV', str(15)).replace('WW', hs)
        return self.comm(s)

    def exposure_full_auto(self):
        """Changes exposure to full-auto.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101043900FF')

    def focus_far(self, amount=5):
        """Focuses the camera to "far"
        
        :param amount: Speed (0-7), default=5
        :return: True if successful, False if not.
        """
        hs = "%X" % amount
        hs = 7 if int(hs, 16) > 7 else hs
        hs = 0 if int(hs, 16) < 0 else hs
        s = '810104082PFF'.replace('P', hs)
        return self.comm(s)

    def focus_near(self, amount=5):
        """Focuses the camera to "near"
        
        :param amount: Speed (0-7), default=5
        :return: True if successful, False if not.
        """
        hs = "%X" % amount
        hs = 7 if int(hs, 16) > 7 else hs
        hs = 0 if int(hs, 16) < 0 else hs
        s = '810104083PFF'.replace('P', hs)
        return self.comm(s)

    def focus_stop(self):
        """Stops any ongoing focus (near/far) movement.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040800FF')
    
    def freeze(self, toggle=1):
        """Freeze the camera immediately on or off.
        
        Defaults to "freeze on" if invalid option is specified.
        :return: True if successful, False if not.
        :rtype: bool
        """
        if toggle == False or toggle == 0:
            return self.comm('8101046203FF')
        else:
            return self.comm('8101046202FF')
    
    def gain_down(self):
        """Turn down the camera's gain (non-variable).
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040C03FF')
    
    def gain_reset(self):
        """Reset the camera's gain value to default.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040C00FF')
    
    def gain_up(self):
        """Turn up the camera's gain (non-variable).
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040C02FF')

    def get_speed(self, amount=5):
        
        self.comm('81090611FF')
        return super(self.__class__, self).read(amount=amount)

    def get_status(self, amount=5):
        
        self.comm('81090610FF')
        return super(self.__class__, self).read(amount=amount)

    def home(self):
        """Moves camera to home position.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('81010604FF')
    
    def iris_down(self):
        """Turn down the camera's iris setting.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040B03FF')
    
    def iris_reset(self):
        """Reset the camera's iris setting to default.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040B00FF')
    
    def iris_up(self):
        """Turn up the camera's iris setting.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040B02FF')

    def left(self, amount=5):
        """Modifies pan speed to left.

        :param amount: Speed (0-24)
        :return: True if successful, False if not.
        :rtype: bool
        """
        hex_string = "%X" % amount
        hex_string = '0' + hex_string if len(hex_string) < 2 else hex_string
        s = '81010601VVWW0103FF'.replace('VV', hex_string).replace('WW', str(15))
        return self.comm(s)

    def left_down(self, pan=5, tilt=5):
        return self._move('81010601VVWW0102FF', pan, tilt)

    def left_up(self, pan=5, tilt=5):
        return self._move('81010601VVWW0101FF', pan, tilt)

    @staticmethod
    def multi_replace(text, rep):
        """Replaces multiple parts of a string using regular expressions.

        :param text: Text to be replaced.
        :type text: str
        :param rep: Dictionary of key strings that are replaced with value strings.
        :type rep: dict
        :return: Replaced string.
        :rtype: str
        """
        rep = dict((re.escape(k), v) for k, v in rep.items())
        pattern = re.compile("|".join(list(rep.keys())))
        return pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

    def picture_effect_b_w(self):
        """Black and white picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046304FF')

    def picture_effect_mosaic(self):
        """Mosaic picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046306FF')

    def picture_effect_negative(self):
        """Negative picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046302FF')

    def picture_effect_off(self):
        """Off picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046300FF')

    def picture_effect_pastel(self):
        """Pastel picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046301FF')

    def picture_effect_sepia(self):
        """Sepia picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046303FF')

    def picture_effect_slim(self):
        """Slim picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046307FF')

    def picture_effect_solarize(self):
        """Solarize picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046305FF')

    def picture_effect_stretch(self):
        """Stretch picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046308FF')
    
    def power(self, toggle=1):
        """Turning the VISCA-based PTZ camera on or off.
        
        Defaults to "power on" if invalid option is specified.
        :return: True if successful, False if not.
        :rtype: bool
        """
        if toggle == False or toggle == 0:
            return self.comm('8101040003FF')
        else:
            return self.comm('8101040002FF')
    
    def preset_recall(self, memory):
        """Recall the assigned PTZ position from the memory bank 0-255.
        
        :return: True if successful, False if not.
        """
        num = memory
        num = 255 if num > 255 else num
        num = 0 if num < 0 else num
        # Convert 10-base decimal into hexadecimal
        hex_string = "%X" % num
        # Pad with zero, if less than two-digit
        hex_string = '0' + hex_string if len(hex_string) < 2 else hex_string
        # Send the command
        s = '8101043F02PPFF'.replace('PP', hex_string)
        return self.comm(s)
    
    def preset_set(self, memory):
        """Set/save the current position of the PTZ into memory bank 0-255.
        
        :return: True if successful, False if not.
        """
        num = memory
        num = 255 if num > 255 else num
        num = 0 if num < 0 else num
        # Convert 10-base decimal into hexadecimal
        hex_string = "%X" % num
        # Pad with zero, if less than two-digit
        hex_string = '0' + hex_string if len(hex_string) < 2 else hex_string
        # Send the command
        s = '8101043F01PPFF'.replace('PP', hex_string)
        return self.comm(s)

    def relative_position(self, pan, tilt, amount_pan, amount_tilt, direction_pan=1, direction_tilt=1):
        """Moves camera relative to current position.

        :param pan: Pan speed.
        :type pan: int
        :param tilt: Tilt speed.
        :type tilt: int
        :param amount_pan: Pan amount.
        :type amount_pan: int
        :param amount_tilt: Tilt amount.
        :type amount_tilt: int
        :param direction_pan: Pan direction (1 = right, -1 = left)
        :type direction_pan: int
        :param direction_tilt: Tilt direction (1 = up, -1 = down)
        :type direction_tilt: int
        :return: True if successful, False if not.
        :rtype: bool
        """
        if direction_pan != 1:
            amount_pan = 65532 - amount_pan
        if direction_tilt != 1:
            amount_tilt = 65500 - amount_tilt
        position_string = '81010603VVWW0Y0Y0Y0Y0Z0Z0Z0ZFF'
        pan_string = "%X" % amount_pan
        pan_string = pan_string if len(pan_string) > 3 else ("0" * (4 - len(pan_string))) + pan_string
        pan_string = "0" + "0".join(pan_string)

        tilt_string = "%X" % amount_tilt
        tilt_string = tilt_string if len(tilt_string) > 3 else ("0" * (4 - len(tilt_string))) + tilt_string
        tilt_string = "0" + "0".join(tilt_string)

        rep = {"VV": str(pan) if pan > 9 else "0" + str(pan), "WW": str(tilt) if tilt > 9 else "0" + str(tilt),
               "0Y0Y0Y0Y": pan_string, "0Z0Z0Z0Z": tilt_string}

        position_string = self.multi_replace(position_string, rep)
        return self.comm(position_string)

    def reset(self):
        """Resets camera.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('81010605FF')

    def right(self, amount=5):
        """Modifies pan speed to right.

        :param amount: Speed (0-24)
        :return: True if successful, False if not.
        """
        hex_string = "%X" % amount
        hex_string = '0' + hex_string if len(hex_string) < 2 else hex_string
        s = '81010601VVWW0203FF'.replace('VV', hex_string).replace('WW', str(15))
        return self.comm(s)

    def right_down(self, pan=5, tilt=5):
        return self._move('81010601VVWW0202FF', pan, tilt)

    def right_up(self, pan=5, tilt=5):
        return self._move('81010601VVWW0201FF', pan, tilt)

    def stop(self):
        """Stops camera movement (pan/tilt).

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101060115150303FF')

    def up(self, amount=5):
        """Modifies tilt speed to up.

        :param amount: Speed (0-24)
        :return: True if successful, False if not.
        """
        hs = "%X" % amount
        hs = '0' + hs if len(hs) < 2 else hs
        s = '81010601VVWW0301FF'.replace('VV', str(15)).replace('WW', hs)
        return self.comm(s)

    def white_balance_auto(self):
        """White balance: Automatic mode

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101043500FF')

    def white_balance_indoor(self):
        """White balance: Indoor mode

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101043501FF')

    def white_balance_outdoor(self):
        """White balance: Outdoor mode

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101043502FF')

    def wide_169(self):
        """Wide mode setting: 16:9

        Stretches picture to 16:9 format.
        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046002FF')

    def wide_cinema(self):
        """Wide mode setting: Cinema

        Places black bars above and below picture. Otherwise maintains resolution.
        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046001FF')

    def wide_off(self):
        """Wide mode setting: Off

        Returns to original 640x480 resolution.
        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046000FF')

    def zoom_in(self, amount=5):
        """Zooms the camera lens in.
        
        :param amount: Speed (0-7), default=5
        :return: True if successful, False if not.
        """
        hs = "%X" % amount
        hs = 7 if int(hs, 16) > 7 else hs
        hs = 0 if int(hs, 16) < 0 else hs
        s = '810104072PFF'.replace('P', hs)
        return self.comm(s)

    def zoom_out(self, amount=5):
        """Zooms the camera lens out.
        
        :param amount: Speed (0-7), default=5
        :return: True if successful, False if not.
        """
        hs = "%X" % amount
        hs = 7 if int(hs, 16) > 7 else hs
        hs = 0 if int(hs, 16) < 0 else hs
        s = '810104073PFF'.replace('P', hs)
        return self.comm(s)

    def zoom_stop(self):
        """Stops any ongoing zoom (tele/wide) movement.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040700FF')
