#include "color_conversions.h"

#include <array>
#include <qualpal.h>

// Forward declare from cvd.cpp
namespace qualpal {
colors::RGB
simulateCvd(const colors::RGB& rgb,
            const std::string_view cvd_type,
            double cvd_severity);
}

std::array<double, 3>
rgb_to_hsl(double r, double g, double b)
{
  qualpal::colors::RGB rgb(r, g, b);
  qualpal::colors::HSL hsl(rgb);
  return { hsl.h(), hsl.s(), hsl.l() };
}

std::array<double, 3>
hsl_to_rgb(double h, double s, double l)
{
  qualpal::colors::HSL hsl(h, s, l);
  qualpal::colors::RGB rgb(hsl);
  return { rgb.r(), rgb.g(), rgb.b() };
}

std::array<double, 3>
rgb_to_xyz(double r, double g, double b)
{
  qualpal::colors::RGB rgb(r, g, b);
  qualpal::colors::XYZ xyz(rgb);
  return { xyz.x(), xyz.y(), xyz.z() };
}

std::array<double, 3>
rgb_to_lab(double r, double g, double b)
{
  qualpal::colors::RGB rgb(r, g, b);
  qualpal::colors::Lab lab(rgb);
  return { lab.l(), lab.a(), lab.b() };
}

std::array<double, 3>
rgb_to_lch(double r, double g, double b)
{
  qualpal::colors::RGB rgb(r, g, b);
  qualpal::colors::LCHab lch(rgb);
  return { lch.l(), lch.c(), lch.h() };
}

std::array<double, 3>
simulate_cvd_cpp(double r,
                 double g,
                 double b,
                 const std::string& cvd_type,
                 double severity)
{
  qualpal::colors::RGB rgb(r, g, b);
  qualpal::colors::RGB simulated = qualpal::simulateCvd(rgb, cvd_type, severity);
  return { simulated.r(), simulated.g(), simulated.b() };
}
