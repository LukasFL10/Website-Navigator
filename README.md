# Navigator Tool for Web Browsing

## Introduction

This repository contains a specialized Navigator Tool developed for automating web browsing activities on a specific website. The tool is not intended for public use or contribution, as it has been anonymized and customized for a particular use case. It is designed primarily to demonstrate the capabilities of automated web navigation through code and is tailored to operate on Linux systems. The tool is a prototype, showcasing a foundation that could be expanded into a more comprehensive application. Users should note that this tool's effectiveness is closely tied to screen resolution, requiring adjustments and new screenshots for different environments.

## Features

The Navigator Tool comprises four main classes, each contributing to the tool's ability to automate web navigation and interaction:

### Chrome Controller

Manages basic interactions with the Chrome browser, including opening and closing the browser, managing window state, and navigating to URLs.

### Navigate Cursor

Simulates human-like cursor movements to interact with web elements. It locates elements by analyzing screenshots and moves the cursor in a curved path to emulate natural mouse movement.

### Screenshot

Determines the loading state of the current website by taking screenshots and identifying specific unloading elements or patterns, providing a simple yet effective way to monitor page readiness.

### Movement Controller

Implements directional movement commands (left, down, right, up) using PyAutoGUI, facilitating precise control over cursor navigation across the screen.

## Note on Usage

This tool is specifically designed for Linux and is shaped to navigate a particular website. The functionality and classes are built with the flexibility to be adapted for other uses. However, it is crucial to understand that the tool operates based on screen resolution. Changes in resolution necessitate the recapture of target screenshots for accurate operation. As a prototype, this tool demonstrates a potential approach to automated web navigation, with room for further development and customization.