---
title: Gameseed Development
description: blog about gameseed development
---
Author: Matt 'beefok' Griffith

Email: [electrodev@gmail.com](gameseed@proton.me)

Twitter: [@beefok](https://www.twitter.com/beefok)

The gameseed video game console project has been a passion of mine for the last _too many years_. I've iterated on it way too many times to count. However, I think it's finally time to release some sort of public announcement for it!

![gameseed scan](/images/gameseed-x1.png)

# Introduction
The basic concept I've been running with is a dual FPGA design with one dedicated to CPU/System-level interfacing and the other dedicated to the GPU (video and audio).

I love how simple video/audio generation is for Analog NTSC/PAL TV systems, so in the spirit of simplicity and a 'retro' feel, I've opted for using composite video for the first system. Of course anything with RCA/composite inputs should work as well, provided the timing looks alright.

One of my personal goals for the project is to bring the concept of a fantasy console (like pico-8 or tic-80) and making it a real product. To do so, I'm in the process of implementing my own RISC-V (rv32imc) CPU core as well as my own 'Playstation One'-level GPU design.

I've also been working on a lightweight sandboxed lua API for the CPU. I want to be able to make video games while sitting in front of a TV like the old days!

At the top-level, the system uses an ESP32-C3 to coordinate everything required to boot the system and maintain *sanity*.
- FPGA configuration and boot-up
- Dedicated QSPI master channel interface to the CPU FPGA
- Flash ROM read/write to/from CPU FPGA
- SD-CARD access (actually directed through the CPU FPGA)
- Bluetooth-based access to BLE 5.0 Keyboards, Mice, and gamepads (I'm using an 8bitdo lite-2)
- WIFI for networked games and openocd/gdb debugger to step-through debug the CPU FPGA (definitely a future task!) as well as hosting an http server for internal development features.

# Technical specifications:

## Wifi/Bluetooth/System Interface:
- ESP32-C3-WROOM-02 module: RISC-V Espressif MCU, 4MB Flash
- USB-C: JTAG/UART interface and system power 
- S25FL064LABNFI041: 8MB Flash ('gold' FPGA images, boot code, lua binaries, etc)

## CPU FPGA
- iCE40UP5k: 5280 LUT, 128KB SPRAM, 120 KB EBRAM
- 'CRAM': dedicated CPU HYPERRAM (16MB)
- Micro-SD card: ('updated' FPGA images, lua code, file system, games, etc)
- Dedicated 6-wire CPU <-> GPU bus for communication.

## GPU FPGA
- iCE40UP5k: 5280 LUT, 128KB SPRAM, 120 KB EBRAM
- 'GRAM', dedicated GPU HYPERRAM (16MB)
- Composite video output using a 5-bit R2R DAC (capable enough to output 64 (rrggbb), 512 (rrrgggbbb), and potentially 4096 (rrrrggggbbbb) colors)
- Stereo audio output using two low-pass filtered PWM DACs

## Clocking
- Both FPGAs are clocked at 6X (21.47~ MHz), 8X (28.63~ MHz) or 12X (42.95~ MHz) the NTSC color burst frequency (= 315*N/88 MHz)
- For PAL, the OSC will need to be replaced with the correct PAL color burst frequency.

Another design based on dual Crosslink NX utilizing HDMI output is in the works as well, but with unpredictable chip stocking issues, I haven't spent a lot of time worrying about it.

Regardless of all my design ideas, this product could be used in ways I haven't considered, such as a MiSTER system!

# here's some fun!

## color output:
![gameseed tv](/images/gameseed-x2.png)

## simulated triangle rasterization (based on a work-in-progress GPU FPGA design)
![gameseed polygon raster](/images/triraster7.gif)
![gameseed hierarchical raster](/images/hierarchy2.gif)
