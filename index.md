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
The goal of this project is to take the concept of a fantasy console, like [pico-8](https://www.lexaloffle.com/pico-8.php) or [tic-80](https://tic80.com/), and transform it into a real physical product, including a web-based solo/collab game development environment built into the system.

# Concept:
The basic concept I've been running with is a dual FPGA design with one dedicated to CPU/System-level interfacing and the other dedicated to the GPU (video and audio). 

I love how simple video/audio generation is for Analog NTSC/PAL TV systems, so in the spirit of simplicity and a 'retro' feel, I've opted for using composite video for the first system. Of course anything with RCA/composite inputs should work as well, provided the timing looks alright. I'm also in the process of designing my own RISC-V (rv32imc) CPU core as well as a unique 'Playstation One'-like GPU design (with optional perspective correct texture mapping.)

It also has to have some sort of user input (keyboards, mice, gamepads.) Instead of having to deal with the endless headaches of trying to implement something that works for everyone, I went down the road of bluetooth since it removes yet more wires. I also wanted some way of sharing games you make as well as being able to play other people's games either solo or multiplayer. The ESP32 fits these requirements perfectly!

I've also been working on a lightweight sandboxed lua API for the CPU/GPU.
I dream of being able to make video games while sitting in front of a TV like the old days, but with all of the great advances we've made in electronics, network, and software. Thanks to modern technology, the PCB is just 43mm x 55mm!

# Break-down:
At the top-level, the system uses an ESP32-C3 to coordinate everything required to boot the system and maintain *sanity*.
- FPGA configuration and boot-up
- Dedicated QSPI master channel interface to the CPU FPGA
- Flash ROM read/write to/from CPU FPGA
- SD-CARD access (actually directed through the CPU FPGA)
- Bluetooth-based access to BLE 5.0 Keyboards, Mice, and gamepads (I'm using an 8bitdo lite-2 personally)
- WIFI:
--  networked games and remote openocd/gdb debugger to step-through debug the CPU FPGA (future task!)
--  hosting an http server for internal development features.

# Technical specifications:

## Wifi/Bluetooth/System Interface:
- ESP32-C3-WROOM-02 module: RISC-V Espressif MCU, 4MB Flash
- USB-C: JTAG/UART interface and system power 
- S25FL064LABNFI041: 8MB Flash ('gold' FPGA images, boot code, lua binaries, etc)
- Dedicated QSPI ESP32 <-> CPU bus for communication and programming.

## CPU FPGA
- LatticeSemi iCE40UP5k: 5280 LUT, 8 MAC16, 128 KB SPRAM, 120 KB EBRAM
- IS66WVH16M8DBLL-100B1LI: dedicated CPU HYPERRAM (16MB)
- Micro-SD card: ('updated' FPGA images, lua code, file system, games, etc)
- Dedicated 6-wire CPU <-> GPU bus for communication.

## GPU FPGA
- LatticeSemi iCE40UP5k: 5280 LUT, 8 MAC16, 128 KB SPRAM, 120 KB EBRAM
- IS66WVH16M8DBLL-100B1LI: dedicated GPU HYPERRAM (16MB)
- Composite video output using a 5-bit R2R DAC (capable enough to output 64 (rrggbb), 512 (rrrgggbbb), and potentially 4096 (rrrrggggbbbb) colors)
- Stereo audio output using two low-pass filtered PWM DACs

## Clocking
- Both FPGAs are clocked at 6X (21.47~ MHz), 8X (28.63~ MHz) or 12X (42.95~ MHz) the NTSC color burst frequency (= 315*N/88 MHz)
- For PAL, the OSC will need to be replaced with the correct PAL color burst frequency.

Another design (gameseed NX) based on dual Crosslink NX FPGAs capable of much higher performance and HDMI output is in the works at some future date. With unpredictable chip stocking issues, I haven't spent a lot of time worrying about it.

Regardless of all my design ideas, this product could be used in ways I haven't considered such as a MiSTER system!

# here's some gpu fun!

## color output:
![gameseed tv](/images/gameseed-x2.png)

## triangle rasterization

simulation of experimental affine texture mapping (perspective soon!)

![gameseed polygon raster](/images/triraster7.gif)

## triangle rasterization

simulation of experimental hierarchical tile marching implementation

![gameseed hierarchical raster](/images/hierarchy2.gif)
