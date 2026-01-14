/**
 * @file palette_generation.h
 * @brief Palette generation functions for Python bindings
 */

#pragma once

#include <map>
#include <optional>
#include <qualpal.h>
#include <string>
#include <vector>

/**
 * @brief Convert RGB palette to vector of hex strings
 * @param pal Vector of RGB colors from qualpal
 * @return Vector of hex color strings (e.g., "#ff0000")
 */
std::vector<std::string>
rgb_palette_to_hex(const std::vector<qualpal::colors::RGB>& pal);

/**
 * @brief Apply optional configuration to Qualpal object
 * @param qp Qualpal object to configure
 * @param cvd Optional CVD simulation parameters
 * @param background Optional background color (hex string)
 * @param metric Optional distance metric ("ciede2000", "din99d", "cie76")
 * @param max_memory Optional memory limit in GB
 */
void
apply_optional_config(
  qualpal::Qualpal& qp,
  const std::optional<std::map<std::string, double>>& cvd,
  const std::optional<std::string>& background,
  const std::optional<std::string>& metric,
  const std::optional<double>& max_memory);

/**
 * @brief Unified palette generation function with full configuration
 * @param n Number of colors to generate
 * @param h_range Optional hue range [min, max] in degrees
 * @param c_range Optional chroma/saturation range [min, max] in [0, 1]
 * @param l_range Optional lightness range [min, max] in [0, 1]
 * @param colors Optional list of input hex colors
 * @param palette_name Optional named palette (e.g., "ColorBrewer:Set2")
 * @param cvd Optional CVD simulation parameters
 * @param background Optional background color
 * @param metric Optional distance metric
 * @param max_memory Optional memory limit
 * @return Vector of hex color strings
 */
std::vector<std::string>
generate_palette_unified_cpp(
  int n,
  const std::optional<std::vector<double>>& h_range,
  const std::optional<std::vector<double>>& c_range,
  const std::optional<std::vector<double>>& l_range,
  const std::optional<std::vector<std::string>>& colors,
  const std::optional<std::string>& palette_name,
  const std::optional<std::map<std::string, double>>& cvd,
  const std::optional<std::string>& background,
  const std::optional<std::string>& metric,
  const std::optional<double>& max_memory);

/**
 * @brief Generate palette using colorspace input
 * @param n Number of colors to generate
 * @param h_range Hue range [min, max] in degrees
 * @param c_range Chroma/saturation range [min, max] in [0, 1]
 * @param l_range Lightness range [min, max] in [0, 1]
 * @return Vector of hex color strings
 */
std::vector<std::string>
generate_palette_cpp(int n,
                     const std::vector<double>& h_range,
                     const std::vector<double>& c_range,
                     const std::vector<double>& l_range);

/**
 * @brief Generate palette using hex colors as input
 * @param n Number of colors to select
 * @param colors List of input hex colors
 * @return Vector of hex color strings (subset of input)
 */
std::vector<std::string>
generate_palette_from_colors_cpp(int n, const std::vector<std::string>& colors);

/**
 * @brief Generate palette using named palette as input
 * @param n Number of colors to select
 * @param palette_name Name of palette (e.g., "ColorBrewer:Set2")
 * @return Vector of hex color strings
 */
std::vector<std::string>
generate_palette_from_palette_cpp(int n, const std::string& palette_name);
