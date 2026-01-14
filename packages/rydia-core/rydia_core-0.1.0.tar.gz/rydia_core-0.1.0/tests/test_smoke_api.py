import rydia


def test_public_api_importable():
    """
    Ensure that all symbols declared in rydia.__all__
    are actually present on the rydia module.
    """
    for name in rydia.__all__:
        assert hasattr(rydia, name), f"rydia missing public symbol: {name}"


def test_sinosc_smoke():
    """
    Basic smoke test for SinOsc:
    - object can be constructed
    - process() returns a float
    """
    osc = rydia.SinOsc(48000.0)
    y = osc.process(440.0)
    assert isinstance(y, float)


def test_lfo_smoke():
    """
    Basic smoke test for Lfo:
    - object can be constructed
    - process() returns a tuple of floats
    """
    lfo = rydia.Lfo(48000.0)
    y, y_qp = lfo.process(1.0)
    assert isinstance(y, float)
    assert isinstance(y_qp, float)


def test_white_noise_smoke():
    """
    Basic smoke test for WhiteNoise:
    - object can be constructed
    - process() returns a float
    """
    white = rydia.WhiteNoise()
    y = white.process()
    assert isinstance(y, float)


def test_ring_buffer_smoke():
    """
    Basic smoke test for RingBufferS:
    - write() and read() do not raise
    - read() returns a float
    """
    rb = rydia.RingBufferS(8)
    rb.write(1.0)
    y = rb.read(1)
    assert isinstance(y, float)


def test_delay_smoke():
    """
    Basic smoke test for DelayS:
    - process() runs without error
    - returns a float
    """
    d = rydia.DelayS(8)
    y = d.process(1.0, 1)
    assert isinstance(y, float)


def test_biquad_smoke():
    """
    Basic smoke test for Biquad:
    - identity coefficients behave sensibly
    - reset() does not break processing
    """
    # Identity biquad: y = x
    bq = rydia.Biquad(1.0, 0.0, 0.0, 0.0, 0.0)
    y = bq.process(0.5)
    assert isinstance(y, float)

    bq.reset()
    y2 = bq.process(0.5)
    assert isinstance(y2, float)


def test_leak_dc_smoke():
    """
    Basic smoke test for LeakDc:
    - stateful processing works
    - reset() clears internal state
    """
    dc = rydia.LeakDc()
    y1 = dc.process(1.0)
    y2 = dc.process(1.0)
    assert isinstance(y1, float)
    assert isinstance(y2, float)

    dc.reset()
    y3 = dc.process(0.0)
    assert isinstance(y3, float)


def test_pan2_smoke():
    """
    Basic smoke test for pan2:
    - function runs
    - returns a stereo (left, right) tuple of floats
    """
    l, r = rydia.pan2(1.0, 0.0)
    assert isinstance(l, float)
    assert isinstance(r, float)
