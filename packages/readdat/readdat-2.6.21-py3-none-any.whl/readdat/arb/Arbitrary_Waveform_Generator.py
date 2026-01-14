"""
Shaojie, Olivier 04/2025

"""
from typing import Optional, Literal

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import os



def arbitrary_waveform_generator(
    signal_type: str,
    duration: float =1.0,            # Total signal duration in seconds
    sampling_rate: float =1e6,       # Sampling rate in Hz
    amplitude: float=1.0,           # Peak amplitude (V)
    frequency: float=1.0,           # Signal frequency in Hz
    initial_phase: float=0.0,       # Initial phase (in radians)
    offset: float=0.0,              # DC offset added to the signal
    duty_cycle: float=0.5,          # For square/pulse waveforms (0.0 to 1.0)
    window: Optional[Literal[
        "sine", "square", "triangle", "sawtooth", "pulse", "pwm",
        "hanning", "hamming", "blackman"]]=None,  # Window type
    qc: bool = False,  # enables visual quality control
        ) -> tuple[np.ndarray, np.ndarray]:

    """
    Generate time-domain samples for various signal types at a given time resolution.
    Optionally, plot the generated signal.

    Parameters
    ----------
    signal_type : str
        Type of signal to generate. Options include:
        'sine', 'square', 'triangle', 'sawtooth', 'pulse', etc.
    duration : float, optional
        Total duration of the signal in seconds.
    sampling_rate : float
        Number of samples per second (Hz).
    amplitude : float, optional
        Peak amplitude of the signal.
    frequency : float, optional
        Frequency in Hz.
    initial_phase : float, optional
        Initial phase (in radians).
    offset : float, optional
        DC offset added to the final waveform.
    duty_cycle : float, optional
        Duty cycle for square/pulse waveforms (0.0 to 1.0).
    window : str or None, optional
        Window (filter) to apply to the generated signal. 
        Examples: 'hanning', 'hamming', 'blackman'.
        If None, no window is applied.
    plot : bool, optional
        If True, display a plot of the generated waveform.

    Returns
    -------
    t : ndarray
        Time array of shape (num_samples,).
    waveform : ndarray
        The generated waveform array of shape (num_samples,).

    Raises
    ------
    ValueError
        If the signal_type is unsupported, or if there's no variation in the data (v_range=0).
    """
    # Construct time array
    time_step = 1 / sampling_rate
    num_samples = int(duration * sampling_rate)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # Generate the raw waveform
    stype = signal_type.lower()

    if stype == 'sine':
        waveform = amplitude * np.sin(2 * np.pi * frequency * t + initial_phase)

    elif stype == 'square':
        waveform = amplitude * signal.square(
            2 * np.pi * frequency * t + initial_phase,
            duty=duty_cycle)

    elif stype == 'triangle':
        # sawtooth() with width=0.5 gives a triangle wave
        waveform = amplitude * signal.sawtooth(
            2 * np.pi * frequency * t + initial_phase,
            width=0.5)

    elif stype == 'sawtooth':
        waveform = amplitude * signal.sawtooth(
            2 * np.pi * frequency * t + initial_phase)

    elif stype in ['pulse', 'pwm']:
        # Create a square wave, then clip it to 0/1, then scale
        raw_square = signal.square(
            2 * np.pi * frequency * t + initial_phase,
            duty=duty_cycle)
        # Convert -1/+1 -> 0/+1, then scale by amplitude
        waveform = amplitude * ((raw_square + 1.0) / 2.0)

    else:
        raise ValueError(
            f"Unsupported signal type '{signal_type}'. "
            f"Choose from sine, square, triangle, sawtooth, pulse, etc.")

    # Apply an optional window (filter)
    if window is not None:
        w = window.lower()
        if w == 'hamming':
            win_vals = np.hamming(num_samples)

        elif w in ['hanning', 'hann']:
            win_vals = np.hanning(num_samples)

        elif w == 'blackman':
            win_vals = np.blackman(num_samples)

        else:
            raise ValueError(f"Unsupported window '{window}'. Use hamming, hanning, blackman, or None.")

        waveform *= win_vals

    # Add the DC offset
    waveform += offset

    # Plot the generated signal
    if qc:
        plt.figure()
        plt.plot(t, waveform)
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.title(f"Generated {signal_type} Waveform")
        plt.show()

    return t, waveform



def generate_arb_file(filename: str, voltage_data: np.ndarray, time_data: np.ndarray):
    """
    Generate an .arb file from the given voltage and time data.
    ;param filename: str, the name of the output .arb file
    ;param voltage_data: np.ndarray, the voltage data to be written to the file
    ;param time_data: np.ndarray, the time data corresponding to the voltage data

    """
    # Ensure the output file is saved in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    # Calculate sample rate
    time_step = np.mean(np.diff(time_data))
    sample_rate = int(1 / time_step)
    v_max = 10
    v_min = -10
    # Determine dynamic high and low levels
    # v_max = np.max(voltage_data)
    # v_min = np.min(voltage_data)
    # v_center = (v_max + v_min) / 2
    # v_range = (v_max - v_min) / 2
    # Avoid division by zero
    if v_max == v_min:
        raise ValueError("Voltage data has no variation.")
    # Convert voltages to 16-bit integers
    # int_data = ((voltage_data - v_center) / v_range * 32767).astype(int)
    int_data = (voltage_data * 32767).astype(int)
    # Write to .arb file
    with open(filepath, 'w') as f:
        f.write("Copyright: © 2010 Keysight Technologies, Inc.\n")
        f.write("File Format:1.10\n")
        f.write("Channel Count:1\n")
        f.write(f"Sample Rate:{sample_rate}\n")
        f.write(f"High Level:{v_max}\n")
        f.write(f"Low Level:{v_min}\n")
        f.write("Filter:\"NORMAL\"\n")
        f.write(f"Data Points:{len(int_data)}\n")
        f.write("Data:\n")
        for val in int_data:
            f.write(f"{val}\n")


if __name__ == "__main__":
    awg_t, awg_waveform = arbitrary_waveform_generator(
        signal_type="sine",
        duration=6e-5,
        sampling_rate=1e7,
        amplitude=1,
        frequency=1e5,
        window="hanning")
    generate_arb_file('generated_sine_hanning.arb', awg_waveform, awg_t)
    plt.show()
