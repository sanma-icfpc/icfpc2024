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

TEST(BooleanValue, Binary) {
  EXPECT_EQ(BooleanValue(true).applyBinaryOperator('|', BooleanValue(false))->encode(), "T");
  EXPECT_EQ(BooleanValue(false).applyBinaryOperator('|', BooleanValue(false))->encode(), "F");
  EXPECT_EQ(BooleanValue(true).applyBinaryOperator('&', BooleanValue(true))->encode(), "T");
  EXPECT_EQ(BooleanValue(true).applyBinaryOperator('&', BooleanValue(false))->encode(), "F");
  EXPECT_EQ(BooleanValue(true).applyBinaryOperator('=', BooleanValue(true))->encode(), "T");
  EXPECT_EQ(BooleanValue(true).applyBinaryOperator('=', BooleanValue(false))->encode(), "F");
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

TEST(IntegerValue, Binary) {
  EXPECT_EQ(IntegerValue(3).applyBinaryOperator('+', IntegerValue(4))->repr(), "7");
  EXPECT_EQ(IntegerValue(3).applyBinaryOperator('-', IntegerValue(4))->repr(), "-1");
  EXPECT_EQ(IntegerValue(3).applyBinaryOperator('*', IntegerValue(4))->repr(), "12");
  EXPECT_EQ(IntegerValue(7).applyBinaryOperator('/', IntegerValue(4))->repr(), "1");
  EXPECT_EQ(IntegerValue(-7).applyBinaryOperator('/', IntegerValue(4))->repr(), "-1");
  EXPECT_EQ(IntegerValue(7).applyBinaryOperator('%', IntegerValue(4))->repr(), "3");

  EXPECT_EQ(IntegerValue(7).applyBinaryOperator('<', IntegerValue(4))->repr(), "False");
  EXPECT_EQ(IntegerValue(7).applyBinaryOperator('<', IntegerValue(7))->repr(), "False");
  EXPECT_EQ(IntegerValue(4).applyBinaryOperator('<', IntegerValue(7))->repr(), "True");

  EXPECT_EQ(IntegerValue(7).applyBinaryOperator('>', IntegerValue(4))->repr(), "True");
  EXPECT_EQ(IntegerValue(7).applyBinaryOperator('>', IntegerValue(7))->repr(), "False");
  EXPECT_EQ(IntegerValue(4).applyBinaryOperator('>', IntegerValue(7))->repr(), "False");

  EXPECT_EQ(IntegerValue(7).applyBinaryOperator('=', IntegerValue(4))->repr(), "False");
  EXPECT_EQ(IntegerValue(4).applyBinaryOperator('=', IntegerValue(4))->repr(), "True");
}

TEST(IntegerValueAndStringValue, Binary) {
  EXPECT_EQ(IntegerValue(3).applyBinaryOperator('T', StringValue("test"))->repr(), "tes");
  EXPECT_EQ(IntegerValue(3).applyBinaryOperator('D', StringValue("test"))->repr(), "t");
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

TEST(StringValue, Binary) {
  EXPECT_EQ(StringValue("a").applyBinaryOperator('=', StringValue("a"))->repr(), "True");
  EXPECT_EQ(StringValue("a").applyBinaryOperator('=', StringValue("b"))->repr(), "False");
  EXPECT_EQ(StringValue("te").applyBinaryOperator('.', StringValue("st"))->repr(), "test");
}