---
title: Gameseed Development
description: blog about gameseed development
---
Email: [gameseed@proton.me](gameseed@proton.me)
Twitter: [@beefok](https://www.twitter.com/beefok)

The gameseed video game console project has been a passion of mine for the last _too many years_. I've iterated on it way too many times to count. However, I think it's finally time to release some sort of public announcement for it!

![gameseed scan](/images/gameseed-x1.png)

# Introduction
The goal of this project is to take the concept of a fantasy console, like [pico-8](https://www.lexaloffle.com/pico-8.php) or [tic-80](https://tic80.com/), and transform it into a real physical product, including a web-based solo/collab game development environment built into the system.

# Concept
The basic concept that I've been designing is a dual FPGA design with one FPGA dedicated to CPU/System-level interfacing and the other FPGA dedicated to the GPU (video and audio). 

I love how simple video/audio generation is for Analog NTSC/PAL TV systems, so in the spirit of simplicity and a 'retro' feel, I've opted for using composite video for the first system. Of course anything with RCA/composite inputs should work as well, provided the timing looks alright. I'm also in the process of designing my own RISC-V (rv32imc) CPU core as well as a unique 'Playstation One'-like GPU design (with optional perspective correct texture mapping.)

It also has to have some sort of user input (keyboards, mice, gamepads.) Instead of having to deal with the endless headaches of trying to implement something that works for everyone, I went down the road of bluetooth since it removes yet more wires. I also wanted some way of sharing games you make as well as being able to play other people's games either solo or multiplayer. The ESP32 fits these requirements perfectly!

I've also been working on a lightweight sandboxed lua API for the CPU/GPU.
I dream of being able to make video games while sitting in front of a TV like the old days, but with all of the great advances we've made in electronics, network, and software. Thanks to modern technology, the PCB is just 43 mm x 55 mm!

# Break-down
At the top-level, the system uses an ESP32-C3 to coordinate everything required to boot the system and maintain *sanity*.
- FPGA configuration and boot-up
- Dedicated QSPI master channel interface to the CPU FPGA
- Flash ROM read/write to/from CPU FPGA
- SD-CARD access (actually directed through the CPU FPGA)
- Bluetooth-based access to BLE 5.0 Keyboards, Mice, and gamepads (I'm using an 8bitdo lite-2 personally)
- WIFI:
--  networked games and remote openocd/gdb debugger to step-through debug the CPU FPGA (future task!)
--  hosting an http server for internal development features.


# Technical specifications

## Wifi/Bluetooth/System Interface
- ESP32-C3-WROOM-02 module: RISC-V Espressif MCU, 4MB Flash
- USB-C: JTAG/UART interface and system power 
- S25FL064LABNFI041: 8MB Flash ('gold' FPGA images, boot code, lua binaries, etc)
- Dedicated QSPI ESP32 <-> CPU bus for communication and programming.

## CPU FPGA
- LatticeSemi iCE40UP5k: 5280 LUT, 8 MAC16, 128 KByte SPRAM, 120 KBit EBRAM
- IS66WVH16M8DBLL-100B1LI: dedicated CPU HYPERRAM (16 MByte)
- Micro-SD card: ('updated' FPGA images, lua code, file system, games, etc)
- Dedicated 6-wire CPU <-> GPU bus for communication.

## GPU FPGA
- LatticeSemi iCE40UP5k: 5280 LUT, 8 MAC16, 128 KByte SPRAM, 120 KBit EBRAM
- IS66WVH16M8DBLL-100B1LI: dedicated GPU HYPERRAM (16 MByte)
- Composite video output using a 5-bit R2R DAC (capable enough to output 64 (rrggbb), 512 (rrrgggbbb), and potentially 4096 (rrrrggggbbbb) colors)
- Stereo audio output using two low-pass filtered PWM DACs

## Clocking
- Both FPGAs are clocked at 6X (21.47~ MHz), 8X (28.63~ MHz) or 12X (42.95~ MHz) the NTSC color burst frequency (= 315*N/88 MHz)
- For PAL, the OSC will need to be replaced with the correct PAL color burst frequency.


# Game console goals

## GS-RV32 RISC-V 32-bit CPU
- 3-stage pipeline: Fetch, Decode, Execute
- 21~ MHz clock frequency, mostly executing around 1 instruction/tick.
- Four-way 32 KB Unified L2 Cache
- Two-way 4 KB Unified L1 Cache
- 24-bit adddress range with 16 MByte main memory
- Gcc/clang open-source toolchain
- Integrated lua-based interpreter/compiler/graphical os
- Remote openocd/gdb step-thru debugging over WIFI via ESP32 (**big** TBD)

## GS-GX1 Graphics and Audio Processing Unit
- Analog NTSC/PAL Video and Audio Generation
- Video Resolution: 128 x 112, 128 x 120, 256 x 224, 256 x 240 @ 60 Hz
- Color: Hardwired 16 color palette, or customizable 64, or 256 color palettes.
- Pixel Blitter and dedicated polygon rasterizer using custom-designed tile-based renderer.
- Sound: 8-channel wavetable audio synthesis with effects @ 32KHz 8-bit stereo output.

# Notes

I will be updating my blog with my progress as I go along. I also (sometimes) update my twitter with whatever I'm working on as well.

# GPU experiments

## color output:

![gameseed tv](/images/gameseed-x2.png)

This is NTSC color video generation from a previous revision of the board. I will update these pictures as I work through the new PCB design.

## triangle rasterization

a simulation of experimental affine texture mapping (perspective soon!)

![gameseed polygon raster](/images/triraster7.gif)

## (hierarchical tile marching)

![gameseed hierarchical raster](/images/hierarchy2.gif)

Here is a simulation of experimental hierarchical tile marching implementation. I'm really proud of the technique used to search for polygons by marching through the barycentric coordinates in a hierarchical manner. I'm not certain if anyone has implemented it quite like this, and of course I stand on the shoulders of giants. Regardless, I'm looking forward to writing a blog post about it!
