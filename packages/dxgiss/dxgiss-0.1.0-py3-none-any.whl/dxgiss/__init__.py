import ctypes
import numpy as np
import os
from importlib.resources import files as resource_path

class DXGI:
    def __init__(self, autoRegion = True, needAlphaChannel=False):
        """
        :param autoRegion: enable auto full screen capture
        :param needAlphaChannel: keep Alpha channel in the captured image
        """
        dll_resource = resource_path('dxgiss').joinpath('DXGISS.dll')
        dll_path = str(dll_resource)
        if not os.path.exists(dll_path):
            raise FileNotFoundError(dll_path)

        # 使用 cdecl 调用约定
        self.dll = ctypes.CDLL(dll_path)

        # CreateDXGICapture -> void*
        self.dll.CreateDXGICapture.restype = ctypes.c_void_p

        # SetCaptureRegion(void*, uint, uint, uint, uint) -> void
        self.dll.SetCaptureRegion.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint
        ]

        # CaptureFrame(void*, uint8_t*, bool) -> bool
        self.dll.CaptureFrame.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_bool
        ]
        self.dll.CaptureFrame.restype = ctypes.c_bool

        # DXGIReleaseCapture(void*) -> void
        self.dll.DXGIReleaseCapture.argtypes = [ctypes.c_void_p]

        self._capture_instance = self.dll.CreateDXGICapture()
        if not self._capture_instance:
            raise RuntimeError('CreateDXGICapture failed.')
        self._needAplhaChannel = ctypes.c_bool(needAlphaChannel)

        self.height = 0
        self.width = 0
        if autoRegion:
            # 默认全屏捕获
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            self.set_capture_region(0, 0, screen_width, screen_height)

    def set_capture_region(self, x, y, width, height):
        """
        :param x: left coordinate
        :param y: up coordinate
        :param width: width of the capture region
        :param height: height of the capture region
        """
        if width <= 0 or height <= 0:
            raise ValueError('Invalid capture region size.')
        self.dll.SetCaptureRegion(
            self._capture_instance,
            ctypes.c_uint(x),
            ctypes.c_uint(y),
            ctypes.c_uint(width),
            ctypes.c_uint(height)
        )
        self.height = int(height)
        self.width = int(width)

    def capture_frame(self):
        """
        :return: numpy ndarray of the captured frame in shape (height, width, channels)
        if needAlphaChannel is True, channels = 4 (BGRA), else channels = 3 (BGR)
        """
        if self.height <= 0 or self.width <= 0:
            raise ValueError('Capture region not set or invalid.')

        channels = 4 if self._needAplhaChannel.value else 3
        # 使用连续内存的 uint8 数组
        img = np.empty((self.height, self.width, channels), dtype=np.uint8)
        img = np.require(img, dtype=np.uint8, requirements=['C', 'A'])

        img_ptr = img.ctypes.data_as(ctypes.c_void_p)

        ok = self.dll.CaptureFrame(
            self._capture_instance,
            img_ptr,
            self._needAplhaChannel
        )
        if not ok:
            raise RuntimeError('CaptureFrame failed.')

        return img

    def release(self):
        if self._capture_instance:
            self.dll.DXGIReleaseCapture(self._capture_instance)
            self._capture_instance = None
