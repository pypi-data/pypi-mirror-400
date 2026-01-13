#ifndef FORMATTING_HPP
#define FORMATTING_HPP

#include "helpers/log.hpp"

#include <vector>
#include <string>
#include <span>
#include <cstdint>
#include <format>

struct Formatting {
    static std::string formatVector(const std::vector<uint64_t>& vec) {
        std::string result = "[ ";
        for (size_t i = 0; i < vec.size(); ++i) {
            result += std::to_string(vec[i]);
            if (i < vec.size() - 1) {
                result += ", ";
            }
        }
        result += " ]";
        return result;
    }

    static std::string formatInt(int value) {
        // Format with commas
        std::string valueStr = std::to_string(value);
        std::string formattedStr;
        int count = 0;
        for (int i = valueStr.length() - 1; i >= 0; --i) {
            formattedStr.insert(formattedStr.begin(), valueStr[i]);
            count++;
            if (count % 3 == 0 && i != 0) {
                formattedStr.insert(formattedStr.begin(), ',');
            }
        }
        return formattedStr;
    }

    static std::string getGradientFromValue(const double input) {
      if (input > .75) { return "█"; }
      if (input > .50) { return "▓"; }
      if (input > .25) { return "▒"; }
      return "_";
    }

    static std::string getHeightFromValue(const double input) {
      const double splits = 1.0 / 8;
      if (input > 1.0 - (splits * 1)) { return "█"; }
      if (input > 1.0 - (splits * 2)) { return "▇"; }
      if (input > 1.0 - (splits * 3)) { return "▆"; }
      if (input > 1.0 - (splits * 4)) { return "▅"; }
      if (input > 1.0 - (splits * 5)) { return "▄"; }
      if (input > 1.0 - (splits * 6)) { return "▃"; }
      if (input > 1.0 - (splits * 7)) { return "▂"; }
      return "▁";
    }

    static std::string buildPrintableArrayFromSpan(const std::span<double>& values) {
      std::string v = "[ ";
      double sum;
      for (double value : values) {
        sum += value;
        v += std::format("{:.2f}, ", value);
      }
      return std::format("{}] - Sum: {:.2f}", v, sum);
    }

    static void printProbabilityDistribution(const std::span<double>& distribution) {
      std::string weights = buildPrintableArrayFromSpan(distribution);
      Logger::p("\t");
      for (uint16_t i = 0; i < distribution.size(); i++) {
        Logger::p(Formatting::getHeightFromValue(distribution[i]) + " ");
      }
      Logger::p("\t\t" + weights + "\n\t");
      for (uint16_t i = 0; i < distribution.size(); i++) {
        Logger::p(std::format("{} ", i));
      }
      Logger::p("\n");
    }
};

#endif
