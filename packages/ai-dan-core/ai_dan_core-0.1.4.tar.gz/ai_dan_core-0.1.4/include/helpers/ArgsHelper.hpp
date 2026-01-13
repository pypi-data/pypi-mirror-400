#ifndef ARGS_HELPER_HPP
#define ARGS_HELPER_HPP

#include <string>
#include <iostream>

struct ArgsConfig {
  ArgsConfig(const int argc, const char* argv[]) {
    train = false;
    benchmark = false;

    for (int i = 1; i < argc; ++i) {
      std::string arg = argv[i];
      std::cout << "Arg: " << arg << std::endl;
      // Input Path
      if (arg == "-i" || arg == "--input") {
        input_path = argv[i + 1];
        continue;
      }

      // Save Path
      if (arg == "-o" || arg == "--output") {
        output_path = argv[i + 1];
        continue;
      }

      // Train
      if (arg == "-t" || arg == "--train") {
        train = true;
        continue;
      }

      // Benchmark
      if (arg == "-b" || arg == "--benchmark") {
        benchmark = true;
        continue;
      }
    }
  }

  std::string input_path = "";
  std::string output_path = "";
  bool train;
  bool benchmark;
};

#endif
