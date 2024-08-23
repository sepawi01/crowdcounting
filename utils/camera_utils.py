import cv2
import numpy as np
import torch
import torch.nn.functional as F


def convert_to_pixel_coords(mask_points, width, height):
    """ Convert mask points from percentage to pixel coordinates"""
    return [(int(p[0] * width / 100), int(p[1] * height / 100)) for p in mask_points]


def create_polygon_mask(image_shape, polygon):
    """ Create a polygon mask from the polygon points"""
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(polygon, dtype=np.int32)], 255)
    return mask


def apply_mask(image, mask, fill_color=(255, 255, 255)):
    """ Apply the mask to the image"""
    masked_image = image.copy()
    masked_image[mask == 0] = fill_color
    return masked_image


def resize_density_map(x, size):
    x_sum = torch.sum(x, dim=(-1, -2))
    x = F.interpolate(x, size=size, mode="bilinear")
    scale_factor = torch.nan_to_num(torch.sum(x, dim=(-1, -2)) / x_sum, nan=0.0, posinf=0.0, neginf=0.0)
    return x * scale_factor
