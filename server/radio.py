from rtlsdr import RtlSdr
import numpy as np
from matplotlib import pyplot as plt
import os
import secrets


class Radio:
    def __init__(self, center_freq: int, mask_offset: int, sample_count: int):
        try:
            self.sdr = RtlSdr()
            self.sdr.freq_correction = 60
            self.sdr.gain = 5
            self.sdr.center_freq = center_freq
            self.mask_offset = 20 * np.log10(mask_offset)
            self.sample_count = sample_count
            self.current_mask = secrets.token_hex(32)
        except:
            print("Error happened in Radio module. Further action is impossible.")
            raise

    
    @staticmethod
    def decimal_to_decibel(arr: np.array) -> np.array:
        return np.multiply(np.log10(arr), 20)


    def learn(self):
        pass
    

    def check_danger(self):
        pass