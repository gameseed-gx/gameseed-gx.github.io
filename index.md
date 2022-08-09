---
title: Gameseed Development
description: blog about gameseed development
---
Author: Matt 'beefok' Griffith

Email: [electrodev@gmail.com](gameseed@proton.me)

Twitter: [@beefok](https://www.twitter.com/beefok)

The gameseed video game console project has been a passion of mine for the _last too many years_. I've iterated on it too many times to count. I think it's finally time to release some sort of public announcement for it!

![gameseed scan](/images/gameseed-x1.png)

# Introduction
The basic concept I've been running with is a dual FPGA design with one dedicated to CPU/System-level interfacing and the other is dedicated to the GPU (video as well as audio).

I love how simple video/audio generation is for NTSC/PAL, so in the spirit of simplicity and a 'retro' feel, I've opted for using composite video for the first system.

My personal goal for the project is in implementing my own RISC-V (rv32imc) CPU core as well as my own 'Playstation One'-level GPU.
On top of that, I've been working on a lightweight sandboxed lua API for the CPU in order to implement my own fantasy-console-esque game development system, allowing pico-8/TIC-80 style game dev.

At the top-level, the system uses an ESP32-C3 to coordinate everything required to boot the system and maintain *sanity*.
- FPGA configuration and boot-up
- Dedicated QSPI master channel interface to the CPU FPGA
- Flash ROM read/write to/from CPU FPGA
- SD-CARD access (actually directed through the CPU FPGA)
- Bluetooth-based access to BLE 5.0 Keyboards, Mice, and gamepads (I'm using an 8bitdo lite-2)
- WIFI for networked games and openocd/gdb debugger to step-through debug the CPU FPGA (definitely a future task!) as well as hosting an http server for internal development features.

Another design based on dual Crosslink NX utilizing HDMI output is in the works as well, but with unpredictable chip stocking issues, I haven't spent a lot of time worrying about it.

# Technical specifications:
```
ESP32-C3-WROOM-02 module
USB-C connector for ESP32-C3 JTAG/UART interface and system power 

S25FL064LABNFI041 8MB Flash ('gold' FPGA images, boot code, lua binaries, etc)

iCE40UP5k CPU FPGA, to be used to implement the CPU design and 'SOC' features.
'CRAM', dedicated CPU HYPERRAM (16MB)
Micro-SD card interface ('updated' FPGA images, lua code, file system, games, etc)

iCE40UP5k GPU FPGA, to be used to implement the GPU and SPU design.
'GRAM', dedicated GPU HYPERRAM (16MB)
Composite video output using a 5-bit R2R DAC (capable enough to output 64 (rrggbb), 512 (rrrgggbbb), and potentially 4096 (rrrrggggbbbb) colors)
Stereo audio output using two low-pass filtered PWM DACs

Dedicated 6-wire CPU <-> GPU bus for communication.

Both FPGAs are clocked at 6X (21.47~ MHz), 8X (28.63~ MHz) or 12X (42.95~ MHz) the NTSC color burst frequency (= 315*N/88 MHz)
For PAL, the OSC will need to be replaced with the correct PAL color burst frequency.
```

# some fun!

## color output:
![gameseed tv](/images/gameseed-x2.png)

## simulated triangle rasterization (based on a work-in-progress GPU FPGA design)
![gameseed polygon raster](/images/triraster7.gif)
![gameseed hierarchical raster](/images/hierarchy2.gif)
