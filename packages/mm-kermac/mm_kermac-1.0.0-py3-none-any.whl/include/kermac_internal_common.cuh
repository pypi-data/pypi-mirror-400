#pragma once

#include <cuda/std/cstdint>
#include <cuda/std/type_traits>

// Define custom is_same and is_same_v for cutlass
namespace std {

template<typename T, typename U>
struct is_same {
    static constexpr bool value = false;
};

template<typename T>
struct is_same<T, T> {
    static constexpr bool value = true;
};

template<typename T, typename U>
inline constexpr bool is_same_v = is_same<T, U>::value;
}

enum class Majorness {
    COL_MAJOR,
    ROW_MAJOR
};

enum class Alignment {
    ALIGN_1,
    ALIGN_4
};
