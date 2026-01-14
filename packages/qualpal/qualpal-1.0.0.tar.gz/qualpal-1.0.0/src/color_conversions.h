/**
 * @file color_conversions.h
 * @brief Color space conversion functions for Python bindings
 *
 * This file provides color space conversion functions that wrap the
 * qualpal C++ library's color conversion capabilities. All functions
 * operate on floating-point RGB values in the range [0, 1].
 */

#pragma once

#include <array>
#include <string>

/**
 * @brief Convert RGB to HSL color space
 * @param r Red component in range [0, 1]
 * @param g Green component in range [0, 1]
 * @param b Blue component in range [0, 1]
 * @return Array of [hue, saturation, lightness] where:
 *         - hue is in degrees [0, 360)
 *         - saturation is in range [0, 1]
 *         - lightness is in range [0, 1]
 */
std::array<double, 3>
rgb_to_hsl(double r, double g, double b);

/**
 * @brief Convert HSL to RGB color space
 * @param h Hue in degrees [0, 360)
 * @param s Saturation in range [0, 1]
 * @param l Lightness in range [0, 1]
 * @return Array of [red, green, blue] in range [0, 1]
 */
std::array<double, 3>
hsl_to_rgb(double h, double s, double l);

/**
 * @brief Convert RGB to CIE XYZ color space
 * @param r Red component in range [0, 1]
 * @param g Green component in range [0, 1]
 * @param b Blue component in range [0, 1]
 * @return Array of [X, Y, Z] tristimulus values
 */
std::array<double, 3>
rgb_to_xyz(double r, double g, double b);

/**
 * @brief Convert RGB to CIE Lab color space
 * @param r Red component in range [0, 1]
 * @param g Green component in range [0, 1]
 * @param b Blue component in range [0, 1]
 * @return Array of [L*, a*, b*] where:
 *         - L* (lightness) is in range [0, 100]
 *         - a* (green-red axis) is typically in range [-128, 127]
 *         - b* (blue-yellow axis) is typically in range [-128, 127]
 */
std::array<double, 3>
rgb_to_lab(double r, double g, double b);

/**
 * @brief Convert RGB to CIE LCH (cylindrical Lab) color space
 * @param r Red component in range [0, 1]
 * @param g Green component in range [0, 1]
 * @param b Blue component in range [0, 1]
 * @return Array of [L*, C*, h] where:
 *         - L* (lightness) is in range [0, 100]
 *         - C* (chroma) is >= 0
 *         - h (hue) is in degrees [0, 360)
 */
std::array<double, 3>
rgb_to_lch(double r, double g, double b);

/**
 * @brief Simulate color vision deficiency on an RGB color
 * @param r Red component in range [0, 1]
 * @param g Green component in range [0, 1]
 * @param b Blue component in range [0, 1]
 * @param cvd_type Type of CVD: "protan", "deutan", or "tritan"
 * @param severity Severity in range [0, 1] where 0=normal, 1=complete deficiency
 * @return Array of [red, green, blue] in range [0, 1] after CVD simulation
 */
std::array<double, 3>
simulate_cvd_cpp(double r,
                 double g,
                 double b,
                 const std::string& cvd_type,
                 double severity);
