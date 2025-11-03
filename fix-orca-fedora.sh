#!/bin/bash

# Fix OrcaSlicer on Wayland with NVIDIA
# This script configures OrcaSlicer Flatpak to work properly on Wayland systems with NVIDIA GPUs

echo "Resetting OrcaSlicer Flatpak overrides..."
flatpak override --user --reset io.github.softfever.OrcaSlicer

echo "Applying fixes for Wayland + NVIDIA..."
flatpak override --user io.github.softfever.OrcaSlicer \
  --env=GBM_BACKEND=dri \
  --env=WEBKIT_DISABLE_DMABUF_RENDERER=1 \
  --env=GDK_BACKEND=x11 \
  --socket=x11 \
  --socket=fallback-x11 \
  --device=dri \
  --filesystem=host \
  --filesystem=/mnt \
  --filesystem=/media

echo "Done! Close and reopen OrcaSlicer for changes to take effect."