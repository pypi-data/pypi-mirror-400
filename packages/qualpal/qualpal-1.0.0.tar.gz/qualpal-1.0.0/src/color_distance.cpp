/**
 * @file color_distance.cpp
 * @brief Implementation of color distance calculation functions
 */

#include "color_distance.h"

#include <qualpal/color_difference.h>
#include <qualpal/colors.h>
#include <qualpal/metrics.h>

// Forward declare from palettes.cpp
namespace qualpal {
std::map<std::string, std::vector<std::string>>
listAvailablePalettes();
}

double
color_difference_cpp(const std::string& hex1,
                     const std::string& hex2,
                     const std::string& metric)
{
  // Convert hex strings to RGB
  qualpal::colors::RGB color1(hex1);
  qualpal::colors::RGB color2(hex2);

  // Calculate distance based on metric
  if (metric == "ciede2000") {
    return qualpal::metrics::CIEDE2000{}(color1, color2);
  } else if (metric == "din99d") {
    return qualpal::metrics::DIN99d{}(color1, color2);
  } else if (metric == "cie76") {
    return qualpal::metrics::CIE76{}(color1, color2);
  } else {
    throw std::invalid_argument("Unknown metric: " + metric +
                                ". Must be 'ciede2000', 'din99d', or 'cie76'");
  }
}

std::vector<double>
color_distance_matrix_cpp(const std::vector<std::string>& hex_colors,
                          const std::string& metric)
{
  // Convert hex strings to RGB
  std::vector<qualpal::colors::RGB> colors;
  colors.reserve(hex_colors.size());
  for (const auto& hex : hex_colors) {
    colors.emplace_back(hex);
  }

  // Compute distance matrix based on metric
  qualpal::Matrix<double> matrix;
  if (metric == "ciede2000") {
    matrix = qualpal::colorDifferenceMatrix(colors, qualpal::metrics::CIEDE2000{});
  } else if (metric == "din99d") {
    matrix = qualpal::colorDifferenceMatrix(colors, qualpal::metrics::DIN99d{});
  } else if (metric == "cie76") {
    matrix = qualpal::colorDifferenceMatrix(colors, qualpal::metrics::CIE76{});
  } else {
    throw std::invalid_argument("Unknown metric: " + metric +
                                ". Must be 'ciede2000', 'din99d', or 'cie76'");
  }

  // Convert matrix to flat vector (row-major order)
  std::vector<double> result;
  const std::size_t n = matrix.nrow();
  result.reserve(n * n);
  for (std::size_t i = 0; i < n; ++i) {
    for (std::size_t j = 0; j < n; ++j) {
      result.push_back(matrix(i, j));
    }
  }

  return result;
}

std::map<std::string, std::vector<std::string>>
list_palettes_cpp()
{
  return qualpal::listAvailablePalettes();
}
