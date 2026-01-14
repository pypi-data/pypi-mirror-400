#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <tuple>
#include <cstdlib>
#include <unordered_map>
#include <algorithm>    // std::random_shuffle
#include <time.h>
#include <chrono>       // Para alta resolução de tempo
#include <exception>
#include <cmath>
#include <stack>
#include <cctype>

// Compatibilidade Windows/Unix para getpid()
#ifdef _WIN32
    #include <process.h>
    #define getpid _getpid
#else
    #include <unistd.h>
#endif
