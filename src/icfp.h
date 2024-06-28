#pragma once
#include <memory>
#include <string>
#include <iostream>

class ICFPValue {
public:
    virtual ~ICFPValue() {}
    virtual void print() const { 
        std::cout << repr() << std::endl;
    }
    // human readble string.
    virtual std::string repr() const = 0;
    // encode to ICFP language token.
    virtual std::string encode() const = 0;
    virtual std::shared_ptr<ICFPValue> applyUnaryOperator(const char op) const {
        throw std::runtime_error("Unsupported operation.");
    }
};

class BooleanValue : public ICFPValue {
    bool value;

public:
    BooleanValue(bool value) : value(value) {}

    bool getValue() const { return value; }

    static BooleanValue parse(const std::string& str) {
        if (str.size() != 1) throw std::runtime_error("boolean string size not 1");
        if (str[0] == 'T') return BooleanValue(true);
        if (str[0] == 'F') return BooleanValue(false);
        throw std::runtime_error("invalid boolean string");
    }

    std::string repr() const override {
        return (value ? "True" : "False");
    }

    std::string encode() const override {
        return value ? "T" : "F";
    }

    std::shared_ptr<ICFPValue> applyUnaryOperator(const char op) const override {
        if (op == '!') {
            return std::make_shared<BooleanValue>(!value);
        }
        return ICFPValue::applyUnaryOperator(op);
    }
};

class IntegerValue : public ICFPValue {
    int value;

public:
    IntegerValue(int value) : value(value) {}

    int getValue() const { return value; }

    static IntegerValue parse(const std::string& str) {
        if (str.size() < 2) throw std::runtime_error("integer string size too small");
        if (str[0] != 'I') throw std::runtime_error("invalid integer string");
        int val = 0;
        int base = 1;
        for (auto it = str.rbegin(); std::next(it) != str.rend(); ++it) {
            val += (*it - '!') * base;
            base *= 94;
        }
        return IntegerValue(val);
    }

    std::string repr() const override {
        return std::to_string(value);
    }

    std::string encode() const override {
        if (value == 0) return "I!";
        std::string result = "";
        int v = value;
        while (v > 0) {
            char c = '!' + (v % 94);
            result = c + result;
            v /= 94;
        }
        return "I" + result;
    }

    std::shared_ptr<ICFPValue> applyUnaryOperator(const char op) const override;
};

class StringValue : public ICFPValue {
    std::string value; // decoded string.

public:
    StringValue(const std::string& value) : value(value) {}

    std::string getValue() const { return value; }

    static StringValue parse(const std::string& str) {
        if (str.size() <= 1) throw std::runtime_error("string string size too small");
        if (str[0] != 'S') throw std::runtime_error("invalid string string");
        std::string result;
        for (char c : str.substr(1)) {
            result += decodeChar(c);
        }
        return StringValue(result);
    }

    static char decodeChar(char c) {
        static const std::string order = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ ";
        int index = c - '!';
        if (index >= 0 && index < static_cast<int>(order.size())) {
            return order[index];
        }
        return '?'; // 未知の文字の場合は '?' を返す
    }

    std::string repr() const override {
        return value;
    }

    std::string encode() const override {
        static const std::string order = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ ";
        std::string result;
        for (char c : value) {
            auto pos = order.find(c);
            if (pos != std::string::npos) {
                result += '!' + pos;
            } else {
                result += '?';  // 未知の文字の場合は '?' を使用
            }
        }
        return "S" + result;
    }

    std::shared_ptr<ICFPValue> applyUnaryOperator(const char op) const override {
        if (op == '#') {
            return std::make_shared<IntegerValue>(IntegerValue::parse("I" + encode().substr(1)));
        }
        return ICFPValue::applyUnaryOperator(op);
    }

};

