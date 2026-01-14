"""Created by ervan achirou, untested yet.
"""

import struct, os
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


def ramp_stimwrite(duration=30, peak=10, ramp=10, off=0):
    """Creates a stimulation pattern as a bin file

    Parameters
    ----------
    duration = 30;   int,
    in ms total duration of our stimulus
    peak = 10;       int,
    in Hz amplitude of our stimulus
    ramp = 10;      int
    in ms duration of ramping acceleration and deceleration of our stimulus
    ramp_down = 10; int
    in ms duration for the ramp down of the stimulus
    fs = 20000;     int, optional
    In Hertz, default sampling frequency of our motor
    in volt defines the amplitude of the stimulation using the peak frequency
    StimNr = 1;    int
    Number of stimulations

    """
    fs = 200000
    total_time = duration / 1000
    ramp_time = ramp / 1000

    nb_of_point_total = int(total_time * fs)
    nb_of_point_ramp = int(ramp_time * fs)

    t_total = np.linspace(0, total_time, nb_of_point_total)
    t_tramp = np.linspace(0, total_time, nb_of_point_ramp)

    v_total = np.zeros(nb_of_point_total)
    v_ramp = np.linspace(0, 2 * np.pi, nb_of_point_ramp)

    up_ramp = (signal.sawtooth(v_ramp, width=1) + 1) / 2
    up_ramp[-1] = 1
    down_ramp = (signal.sawtooth(v_ramp, width=0) + 1) / 2
    down_ramp[-1] = 0

    fname = f"{duration}ms_{ramp}ms_{peak}V_{1}nr.bin "

    v_total[: up_ramp.shape[0]] = up_ramp
    v_total[up_ramp.shape[0] : -down_ramp.shape[0]] = 1
    v_total[-down_ramp.shape[0] :] = down_ramp
    fname = f"{duration}ms_{ramp}ms_{peak}V_{1}nr.bin "
    print(v_total)
    return t_total, v_total * peak, fname


def train(
    train_duration=1000,
    frequence=10,
    duration=30,
    peak=10,
    bytes_size=1,
    ramp=10,
    off=0,
    plot=True,
):
    _, single_pulse, fname1 = ramp_stimwrite(duration, peak, ramp, off)

    fs = 200000
    total_time = train_duration / 1000
    nb_of_point_total = int(total_time * fs)

    repetition_time = 1 / frequence
    if repetition_time < duration / 1000:
        raise ValueError(
            f"Frequency {frequence}Hz is too large for a pulse duration of length {duration}ms.\n"
            f"Maximum duration for that repretition would be {repetition_time * 1000}"
        )

    point_offset = int(fs / frequence)

    v_total = np.zeros(nb_of_point_total)
    t_total = np.linspace(0, total_time, nb_of_point_total)

    fname = f"{duration}ms_{ramp}ms_{peak}V_{frequence}Hz_{repetition_time}nr.bin "
    position = 0

    while position < v_total.shape[0]:
        v_total[position : position + single_pulse.shape[0]] = single_pulse
        position += point_offset

    if plot:
        plt.plot(
            t_total,
            v_total,
            label=f"duration = {duration}, peak = {peak}, ramp={ramp} '",
        )
        plt.legend(loc=(0.25, 1.015))
        plt.show

    return t_total, v_total, fname


from Inflow import bins

# train( train_duration = 1000, frequence = 10, duration = 30, peak = 10, ramp= 10,off = 0, plot = True, format ='d', byte_order ='@')


def piezzo_stim_write(v_total, fname, bytes_size=1, format="d", byte_order="@"):
    file_path = rf"\\cajal\cajal_data2\ONE\MotorSense\stimuli\_{fname}"

    with open(file_path, "wb") as file:
        byte_data = []
        for index in range(0, len(v_total), bytes_size):
            byte = v_total[index : index + bytes_size].item()
            byte_data.append(struct.pack(byte_order + format, byte))
            file.write(byte_data[index])


(t_total, v_total, fname) = train(
    train_duration=1000,
    frequence=10,
    duration=15,
    peak=10,
    bytes_size=1,
    ramp=0.5,
    off=0,
    plot=True,
)

piezzo_stim_write(v_total, fname)
stim_path = rf"\\cajal\cajal_data2\ONE\MotorSense\stimuli\_{fname}"
stim_data = bins.Reader(stim_path).piezzo_stim_data()
# stim_data.isec[0:0.5].timeline : comment couper temporellement in TimelinedArray
plt.plot(*stim_data.pack)
