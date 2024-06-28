#include <gtest/gtest.h>
#include "icfp.h"

TEST(BooleanValue, Decode) {
  EXPECT_EQ(BooleanValue::parse("T").getValue(), true);
  EXPECT_EQ(BooleanValue::parse("F").getValue(), false);
}

TEST(BooleanValue, Encode) {
  EXPECT_EQ(BooleanValue(true).encode(), "T");
  EXPECT_EQ(BooleanValue(false).encode(), "F");
}

TEST(BooleanValue, Not) {
  EXPECT_EQ(BooleanValue(true).applyUnaryOperator('!')->encode(), "F");
}

TEST(IntegerValue, Decode) {
  EXPECT_EQ(IntegerValue::parse("I!").getValue(), 0);
}

TEST(IntegerValue, Encode) {
  EXPECT_EQ(IntegerValue(94).encode(), "I\"!");
}

TEST(IntegerValue, Negation) {
  EXPECT_EQ(IntegerValue(3).applyUnaryOperator('-')->repr(), "-3");
}

TEST(IntegerValue, IntToString) {
  EXPECT_EQ(IntegerValue::parse("I4%34").getValue(), 15818151);
  EXPECT_EQ(IntegerValue::parse("I4%34").applyUnaryOperator('$')->repr(), "test");
}

TEST(StringValue, Decode) {
  EXPECT_EQ(StringValue::parse("S'%4}).$%8").getValue(), "get index");
  EXPECT_EQ(StringValue::parse("S4%34").getValue(), "test");
}

TEST(StringValue, Encode) {
  EXPECT_EQ(StringValue("echo").encode(), "S%#(/");
}

TEST(StringValue, StringToInt) {
  EXPECT_EQ(StringValue::parse("S4%34").getValue(), "test");
  EXPECT_EQ(StringValue::parse("S4%34").applyUnaryOperator('#')->repr(), "15818151");
}