import os

import numpy as np
import cv2
from scipy.special import factorial, eval_genlaguerre

from .utils import inv_sinc, inv_sinc_minus


def generate_oam_superposition(res, pixel_pitch, beam_w0, l_modes, p_modes, weights):
    """ Creat E field of superimposed OAM mode (Interferogram method)

    Args:
        res (list[int]): resolution of SLM. [x resolution, y resolution]
        pixel_pitch (float): pixel size. specified at device document
        beam_w0 (float): beam-waist at z=0.
        l_modes (list[int]): selected l indices for superposion. list with length 1 for eigen mode
        weights (list[float]): weights for selected l modes.

    Returns:
        np.ndarray[float], np.ndarray[float], np.ndarray[float], np.ndarray[float]: information about E field and meshgrid i.e. superimosed

    Example:
        >>> res = [1920, 1080]
        >>> pixel_pitch = 8e-1
        >>> beam_w0 = 0.8e-3
        >>> l_modes = [-3, -1, 1, 3]
        >>> weights = [0.4, 0.03, 0.07, 0.5]
        >>> amp, phase, X, Y = generate_oam_superposition(res, pixel_pitch, beam_w0, l_modes, weights)
    """
    x = np.linspace(-res[0] * pixel_pitch / 2, res[0] * pixel_pitch / 2, res[0])
    y = np.linspace(-res[1] * pixel_pitch / 2, res[1] * pixel_pitch / 2, res[1])
    X, Y = np.meshgrid(x, y)

    R = np.sqrt(X ** 2 + Y ** 2)
    Phi = np.arctan2(Y, X)

    R[R == 0] = 1e-10

    E_total = np.zeros_like(Phi, dtype=complex)
    for l, p, w in zip(l_modes, p_modes, weights):
        C = np.sqrt(2 * factorial(p)/(np.pi*factorial(np.abs(l))))
        E_total += w * C * ((np.sqrt(2) * R / beam_w0) ** abs(l)) * eval_genlaguerre(p,abs(l),2*((R**2)/(beam_w0**2))) * np.exp(-(R**2) / (beam_w0**2)) * np.exp(-1j * l * Phi)

    Amp = np.abs(E_total)
    Phase = np.angle(E_total)

    return Amp, Phase, X, Y


def encode_hologram(Amp, Phase, X, Y, pixel_pitch, d, N_steps=0, M=1, prepare=False, measure=False, save=False, path="", name="", use_inv_sinc_minus=False):
    """phase mask for given amplitude and phase map of superimposed OAM mode.

    입력받은 위상, 진폭 정보를 논문 공식에 대입하여 이 상태를 인코딩하는 SLM 홀로그램을 생성합니다.
    Fundamental Gaussian 모드와의 분리를 위해서 간격이 d 픽셀인 그레이팅이 적용됩니다.
    상태 준비에 사용될지, 측정에 사용될지에 따라서 그레이팅의 방향이 바뀝니다. 변수 parity가 이것을 반영합니다.
    생성된 홀로그램을 저장할 수 있습니다.

    Args:
        Amp (np.ndarray[float]): amplitude map of superimposed OAM mode. 0. <= *Amp <= 1.
        Phase (np.ndarray[float]): phase map of superimposed OAM mode. -pi < *Phase <= pi
        X (np.ndarray[float]): x dependent meshgrid.
        Y (np.ndarray[float]): y dependent meshgrid.
        pixel_pitch (float): pixel size. specified at device document
        d (float): grating width. dimension in # of pixel
        N_steps (float): number of steps per grating with period d. N_steps=0 is equal to N_steps=d (continuous)
        M (int): phase depth. M is basically 1
        prepare (bool): decide whether to prepare.
        measure (bool): decide whether to measure.
        save (bool): decide whether to save.
        path (string): directory path for images. needed only when arg save is True
        name (string): filename of this image. needed only when arg save is True

    Return:
        np.ndarray[float] or None: returns carculated hologram.
        if arg save is False(default), a hologram in numpy ndarray. And if not, hologram is saved in the directory addording to arg path.

    Example:
        >>> res = [1920, 1080]
        >>> pixel_pitch = 8e-1
        >>> beam_w0 = 0.8e-3
        >>> l_modes = [-3, -1, 1, 3]
        >>> weights = [0.4, 0.03, 0.07, 0.5]
        >>> amp, phase, X, Y = generate_oam_superposition(res, pixel_pitch, beam_w0, l_modes, weights)
        >>> encode_hologram(amp, phase, X, Y, pixel_pitch, 16, 0, prepare=True, save=True, path="./images", name="l8_dim16")
    """

    if not use_inv_sinc_minus:
        modified_amp = 1 + (1/np.pi)*inv_sinc(Amp)
    elif use_inv_sinc_minus:
        modified_amp = 1 + (1/np.pi)*inv_sinc_minus(Amp)
    else:
        raise NotImplementedError("use_inv_sinc_minus argument must be True or False")
    modified_amp = modified_amp / np.max(modified_amp)
    modified_phase = Phase - np.pi*modified_amp

    parity = 0
    if prepare: parity = -1
    elif measure: parity = 1

    if N_steps==0: N_steps = d
    res = np.shape(X)[1]
    X_normalized = (X + (res*pixel_pitch/2))/(pixel_pitch*d*M)
    X_grating = X_normalized - X_normalized.astype(int)
    X_stepped = np.floor(X_grating * N_steps)
    X_final = cv2.normalize(X_stepped, X_stepped, 0, 1, cv2.NORM_MINMAX)

    hologram = modified_amp * np.mod(modified_phase + (parity * 2*np.pi * X_final), 2*np.pi)


    hologram_final = cv2.normalize(hologram, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    if not save:
        return hologram_final
    elif save:
        if not os.path.exists(path):
            os.mkdir(path)
        cv2.imwrite(path+"/"+name+".bmp", hologram_final)
        return 0
    else:
        return 0

