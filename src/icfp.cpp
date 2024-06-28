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
