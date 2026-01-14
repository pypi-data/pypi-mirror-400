#include "color_conversions.h"
#include "color_distance.h"
#include "palette_generation.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(_qualpal,
                m,
                py::mod_gil_not_used(),
                py::multiple_interpreters::per_interpreter_gil())
{
  m.doc() = "qualpal C++ core algorithms";

  // Unified generation function with all options
  m.def("generate_palette_unified",
        &generate_palette_unified,
        py::arg("n"),
        py::arg("h_range") = py::none(),
        py::arg("c_range") = py::none(),
        py::arg("l_range") = py::none(),
        py::arg("colors") = py::none(),
        py::arg("palette_name") = py::none(),
        py::arg("cvd") = py::none(),
        py::arg("background") = py::none(),
        py::arg("metric") = py::none(),
        py::arg("max_memory") = py::none(),
        "Generate palette with full configuration options");

  // Convenience wrappers (backwards compatible)
  m.def("generate_palette",
        &generate_palette,
        py::arg("n"),
        py::arg("h_range"),
        py::arg("c_range"),
        py::arg("l_range"),
        "Generate palette using colorspace input");

  m.def("generate_palette_from_colors",
        &generate_palette_from_colors,
        py::arg("n"),
        py::arg("colors"),
        "Generate palette using hex colors as input");

  m.def("generate_palette_from_palette",
        &generate_palette_from_palette,
        py::arg("n"),
        py::arg("palette_name"),
        "Generate palette using named palette as input");

  // Color space conversions
  m.def("rgb_to_hsl",
        &rgb_to_hsl,
        py::arg("r"),
        py::arg("g"),
        py::arg("b"),
        "Convert RGB to HSL");

  m.def("hsl_to_rgb",
        &hsl_to_rgb,
        py::arg("h"),
        py::arg("s"),
        py::arg("l"),
        "Convert HSL to RGB");

  m.def("rgb_to_xyz",
        &rgb_to_xyz,
        py::arg("r"),
        py::arg("g"),
        py::arg("b"),
        "Convert RGB to XYZ");

  m.def("rgb_to_lab",
        &rgb_to_lab,
        py::arg("r"),
        py::arg("g"),
        py::arg("b"),
        "Convert RGB to Lab");

  m.def("rgb_to_lch",
        &rgb_to_lch,
        py::arg("r"),
        py::arg("g"),
        py::arg("b"),
        "Convert RGB to LCH");

  m.def("simulate_cvd",
        &simulate_cvd,
        py::arg("r"),
        py::arg("g"),
        py::arg("b"),
        py::arg("cvd_type"),
        py::arg("severity"),
        "Simulate color vision deficiency on RGB color");

  // Color distance calculations
  m.def("color_difference",
        &color_difference,
        py::arg("hex1"),
        py::arg("hex2"),
        py::arg("metric"),
        "Calculate color difference between two colors");

  m.def("color_distance_matrix",
        &color_distance_matrix,
        py::arg("hex_colors"),
        py::arg("metric"),
        "Calculate distance matrix for a list of colors");

  m.def("list_palettes", &list_palettes, "List all available named palettes");

  m.def("get_palette",
        &get_palette,
        py::arg("palette_name"),
        "Get a specific named palette");
}
