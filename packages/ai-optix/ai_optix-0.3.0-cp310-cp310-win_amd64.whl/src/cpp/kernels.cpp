#include <iostream>
#if defined(_OPENMP)
#include <omp.h>
#endif
#include <cstdint>

extern "C" {

    // ID, Payload, Type (0=Start, 1=End)
    typedef void (*TraceCallback)(uint64_t, uint64_t, uint32_t);
    static TraceCallback g_profiler_callback = nullptr;

    void init_profiler_cb(size_t callback_addr) {
        g_profiler_callback = (TraceCallback)callback_addr;
        std::cout << "C++ Profiler Initialized with callback at " << callback_addr << std::endl;
    }

    // Simple FNV-1a hash for compile-time constants (or runtime strings)
    constexpr uint64_t fnv1a_hash(const char* str, size_t n) {
        uint64_t hash = 14695981039346656037ULL;
        for (size_t i = 0; i < n; ++i) {
            hash ^= (uint64_t)str[i];
            hash *= 1099511628211ULL;
        }
        return hash;
    }

    void mat_mul_cpu(const float* a, const float* b, float* c, int M, int N, int K) {
        static const uint64_t KERNEL_ID = fnv1a_hash("mat_mul_cpu", 11);
        
        // Payload: Pack some "grid" info. For CPU, let's say M*N is the grid size.
        // We act like block_size is 1 for now.
        // Payload = (block_size << 32) | (grid_size & 0xFFFFFFFF)
        uint64_t grid_size = (uint64_t)(M * N);
        uint64_t block_size = 1; 
        uint64_t payload = (block_size << 32) | (grid_size & 0xFFFFFFFF);

        if (g_profiler_callback) g_profiler_callback(KERNEL_ID, payload, 0); // Start
        
        // A is MxK, B is KxN, C is MxN
        
        #if defined(_OPENMP)
        #pragma omp parallel for collapse(2)
        #endif
        for (int i = 0; i < M; ++i) {
            for (int j = 0; j < N; ++j) {
                float sum = 0.0f;
                // Naive implementation - can be optimized with blocking/SIMD
                for (int k = 0; k < K; ++k) {
                    sum += a[i * K + k] * b[k * N + j];
                }
                c[i * N + j] = sum;
            }
        }
        
        if (g_profiler_callback) g_profiler_callback(KERNEL_ID, payload, 1); // End
    }

}
