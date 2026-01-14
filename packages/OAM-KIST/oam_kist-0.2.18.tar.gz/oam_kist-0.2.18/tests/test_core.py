import pytest
import os
import numpy as np

from OAM_KIST.holography import generate_oam_superposition, encode_hologram
from OAM_KIST.utils import inv_sinc


def test_inv_sinc_accuracy():
    """inv_sinc 함수가 예상된 수학적 값을 반환하는지 테스트"""
    x_val = 0.5
    expected = 1.89547036302816116
    result = inv_sinc(x_val)

    assert np.isclose(result, expected, atol=1e-4)


def test_generate_oam_superposition_shape():
    """OAM 중첩 함수가 올바른 크기의 배열을 반환하는지 테스트"""
    res = [100, 100]
    pixel_pitch = 8e-6
    beam_w0 = 8e-4
    l_modes = [-1, 1]
    p_modes = [0, 0]
    weights = [0.5, 0.5]

    amp, phase, X, Y = generate_oam_superposition(res, pixel_pitch, beam_w0, l_modes, p_modes, weights)

    assert amp.shape == (100, 100)
    assert phase.shape == (100, 100)
    assert X.shape == (100, 100)
    assert Y.shape == (100, 100)

    assert np.max(amp) <= 1.0 + 1e-9
    assert np.min(amp) >= 0.0


def test_encode_hologram_save(tmp_path):
    """
    tmp_path: pytest가 제공하는 임시 폴더 Fixture (테스트 끝나면 자동 삭제됨)
    실제로 파일을 저장하고 잘 생기는지 테스트합니다.
    """
    res = 50
    X, Y = np.meshgrid(np.linspace(-1, 1, res), np.linspace(-1, 1, res))
    amp = np.random.rand(res, res)
    phase = np.random.rand(res, res) * 2 * np.pi - np.pi

    save_dir = tmp_path / "test_outputs"
    file_name = "test_hologram"

    encode_hologram(
        Amp=amp, Phase=phase, X=X, Y=Y,
        pixel_pitch=1e-6, d=10,
        prepare=True, save=True,
        path=str(save_dir), name=file_name
    )

    expected_file = save_dir / (file_name + ".bmp")
    assert expected_file.exists()