#include "widget.hpp"

#include <string_view>

#include <fmt/format.h>
#include <spdlog/spdlog.h>

namespace widget {

std::string describe(std::string_view name) {
  auto message = fmt::format("widget: {}", name);
  spdlog::debug("created description: {}", message);
  return message;
}

}  // namespace widget
