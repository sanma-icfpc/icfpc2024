#include "stdafx.h"
#include "icfp.h"

std::shared_ptr<ICFPValue> IntegerValue::applyUnaryOperator(const char op) const {
    if (op == '-') {
        return std::make_shared<IntegerValue>(-value);
    } else if (op == '$') {
        return std::make_shared<StringValue>(StringValue::parse("S" + encode().substr(1)));
    }
    return ICFPValue::applyUnaryOperator(op);
}

std::shared_ptr<ICFPValue> IntegerValue::applyBinaryOperator(const char op, const ICFPValue& right) const {
    if (op == 'T') {
        const auto& rightVal = dynamic_cast<const StringValue&>(right);
        return std::make_shared<StringValue>(rightVal.getValue().substr(0, value));
    } else if (op == 'D') {
        const auto& rightVal = dynamic_cast<const StringValue&>(right);
        return std::make_shared<StringValue>(rightVal.getValue().substr(value));
    } else {
        const auto& rightVal = dynamic_cast<const IntegerValue&>(right);
        switch (op) {
            case '+':
                return std::make_shared<IntegerValue>(value + rightVal.value);
            case '-':
                return std::make_shared<IntegerValue>(value - rightVal.value);
            case '*':
                return std::make_shared<IntegerValue>(value * rightVal.value);
            case '/':
                if (rightVal.value == 0) throw std::runtime_error("Division by zero.");
                return std::make_shared<IntegerValue>(value / rightVal.value);
            case '%':
                if (rightVal.value == 0) throw std::runtime_error("Modulo by zero.");
                return std::make_shared<IntegerValue>(value % rightVal.value);
            case '<':
                return std::make_shared<BooleanValue>(value < rightVal.value);
            case '>':
                return std::make_shared<BooleanValue>(value > rightVal.value);
            case '=':
                return std::make_shared<BooleanValue>(value == rightVal.value);
            default:
                return ICFPValue::applyBinaryOperator(op, right);
        }
    }
}