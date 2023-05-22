from PyQt6 import QtWidgets


def convert_mm_to_px(mm):
    screen = QtWidgets.QApplication.primaryScreen()
    width_mm = screen.physicalSize().width()
    width_px = screen.geometry().width()
    ratio = width_px / width_mm
    result = mm * ratio
    return result


def convert_px_to_mm(px):
    screen = QtWidgets.QApplication.primaryScreen()
    width_mm = screen.physicalSize().width()
    width_px = screen.geometry().width()
    ratio = width_px / width_mm
    result = px / ratio
    return result


def convert_percent_to_px_w(percent):
    screen = QtWidgets.QApplication.primaryScreen()
    width_px = screen.geometry().width()
    ratio = width_px / 100
    result = ratio * percent
    return result


def convert_percent_to_px_h(percent):
    screen = QtWidgets.QApplication.primaryScreen()
    height_px = screen.geometry().height()
    ratio = height_px / 100
    result = ratio * percent
    return result

