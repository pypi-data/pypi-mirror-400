/**
 * @file color_distance.h
 * @brief Color distance calculation functions for Python bindings
 */

#pragma once

#include <map>
#include <string>
#include <vector>

/**
 * @brief Calculate color difference between two colors
 * @param hex1 First color as hex string (e.g., "#ff0000")
 * @param hex2 Second color as hex string (e.g., "#00ff00")
 * @param metric Distance metric: "ciede2000", "din99d", or "cie76"
 * @return Perceptual color difference as a double
 */
double
color_difference(const std::string& hex1,
                 const std::string& hex2,
                 const std::string& metric);

/**
 * @brief Calculate distance matrix for a list of colors
 * @param hex_colors Vector of hex color strings
 * @param metric Distance metric: "ciede2000", "din99d", or "cie76"
 * @return Flattened distance matrix (row-major order, symmetric)
 */
std::vector<double>
color_distance_matrix(const std::vector<std::string>& hex_colors,
                      const std::string& metric);
