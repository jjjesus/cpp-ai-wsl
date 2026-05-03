#include <gtest/gtest.h>

#include "widget.hpp"

TEST(WidgetTest, DescribesName) {
  EXPECT_EQ(widget::describe("sample"), "widget: sample");
}
