#!/usr/bin/env python3

import argparse
import glob
import os
import pathlib
import shutil
import wx


def jpggen(basedir):
    d = pathlib.Path(basedir)
    for basedir, dirs, fnames in d.walk():
        try:
            dirs.remove("deleted")
        except ValueError:
            pass
        for fname in fnames:
            fpath = basedir / fname
            if not fpath.is_file():
                continue
            if fpath.suffix in ('.jpg', '.JPG', '.jpeg', '.JPEG'):
                yield fpath


def move_to_deleted(fpath):
    deleted_dir = fpath.parent / "deleted"
    deleted_dir.mkdir(exist_ok=True)
    newpath = deleted_dir / fpath.name
    fpath.rename(newpath)


def scale_image_to_fit_view(image, viewsize):
    imgsize = image.GetSize()

    # Calculate the aspect ratio of the image.
    aspect_ratio = imgsize.width / imgsize.height

    # Determine the maximum height and width the image can be while fitting in the view.
    max_height = viewsize.height
    max_width = int(max_height * aspect_ratio)

    if max_width > viewsize.width:
        max_width = viewsize.width
        max_height = int(max_width / aspect_ratio)

    image.Rescale(max_width, max_height)


class MainWindow(wx.Frame):
    def __init__(self, path):
        super().__init__(None)
        self.current_jpg = None
        self.jpggen = jpggen(path)
        self.bmp = wx.StaticBitmap(self)
        self.panel = wx.Panel(self)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.panel.SetFocus()

    def next_jpg(self):
        self.current_jpg = next(self.jpggen)
        image = wx.Image(str(self.current_jpg))
        scale_image_to_fit_view(image, self.GetSize())
        self.bmp.SetBitmap(image)

    def on_key_down(self, event):
        keycode = event.GetUnicodeKey()
        if keycode != wx.WXK_NONE:
            c = chr(keycode).lower()
            match c:
                case ' ':
                    self.next_jpg()
                case 'x':
                    if self.current_jpg:
                        move_to_deleted(self.current_jpg)
                    self.next_jpg()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    app = wx.App()
    gui = MainWindow(args.path)
    gui.Show()
    app.MainLoop()
