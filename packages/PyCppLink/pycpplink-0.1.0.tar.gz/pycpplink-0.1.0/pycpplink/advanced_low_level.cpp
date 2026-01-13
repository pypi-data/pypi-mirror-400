// advanced_low_level.cpp - Complex classes + memory optimization + error handling
#include <Python.h>
#include <cstdio>
#include <cstring>
#include <stdint.h>
#include <new>

// ==================== 1. 错误码定义（标准化） ====================
typedef enum {
    ERR_SUCCESS = 0,        // 成功
    ERR_MEMORY = 1,         // 内存分配失败
    ERR_INVALID_PARAM = 2,  // 参数无效
    ERR_OUT_OF_RANGE = 3,   // 越界
    ERR_INTERNAL = 4        // 内部错误
} ErrorCode;

// 错误信息缓冲区（线程安全，栈分配，省内存）
#define ERR_MSG_LEN 128
typedef struct {
    ErrorCode code;
    char msg[ERR_MSG_LEN];
} ErrorInfo;

// ==================== 2. 内存极致优化：内存池（栈内存复用） ====================
// 小型内存池（栈分配，无堆开销，复用内存）
#define POOL_SIZE 1024  // 内存池大小（可根据需求调整）
class StackMemoryPool {
private:
    char pool[POOL_SIZE];  // 栈内存池（函数结束自动释放）
    uint32_t offset;       // 当前偏移量
public:
    StackMemoryPool() : offset(0) {
        memset(pool, 0, POOL_SIZE);
    }

    // 分配内存（零拷贝，复用栈内存）
    void* allocate(uint32_t size, ErrorInfo* err) {
        if (size == 0) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Allocate size is zero");
            return nullptr;
        }
        if (offset + size > POOL_SIZE) {
            err->code = ERR_OUT_OF_RANGE;
            snprintf(err->msg, ERR_MSG_LEN, "Memory pool overflow (offset=%u, size=%u)", offset, size);
            return nullptr;
        }
        void* ptr = pool + offset;
        offset += size;
        err->code = ERR_SUCCESS;
        snprintf(err->msg, ERR_MSG_LEN, "Allocate success (size=%u)", size);
        return ptr;
    }

    // 重置内存池（复用内存，无需释放）
    void reset(ErrorInfo* err) {
        offset = 0;
        memset(pool, 0, POOL_SIZE);
        err->code = ERR_SUCCESS;
        snprintf(err->msg, ERR_MSG_LEN, "Memory pool reset success");
    }

    // 获取剩余内存
    uint32_t get_remaining(ErrorInfo* err) {
        err->code = ERR_SUCCESS;
        snprintf(err->msg, ERR_MSG_LEN, "Get remaining success");
        return POOL_SIZE - offset;
    }
};

// ==================== 3. 复杂C++类（带成员函数+内存池依赖） ====================
class AdvancedProcessor {
private:
    StackMemoryPool* pool;  // 内存池指针（复用栈内存）
    int* data;              // 数据数组（内存池分配）
    uint32_t data_len;      // 数据长度
    ErrorInfo last_err;     // 最后错误信息（栈分配）
public:
    // 构造函数（内存池初始化）
    AdvancedProcessor(StackMemoryPool* pool_ptr) : pool(pool_ptr), data(nullptr), data_len(0) {
        last_err.code = ERR_SUCCESS;
        snprintf(last_err.msg, ERR_MSG_LEN, "Initialize success");
    }

    // 初始化数据（内存池分配，零拷贝）
    ErrorCode init_data(uint32_t len) {
        if (len == 0 || len > 100) {  // 限制长度，避免内存池溢出
            last_err.code = ERR_INVALID_PARAM;
            snprintf(last_err.msg, ERR_MSG_LEN, "Data length invalid (len=%u)", len);
            return last_err.code;
        }

        // 从内存池分配内存（栈内存，无堆开销）
        ErrorInfo err;
        data = (int*)pool->allocate(len * sizeof(int), &err);
        if (err.code != ERR_SUCCESS) {
            last_err = err;
            return last_err.code;
        }

        // 初始化数据（栈操作，无冗余）
        data_len = len;
        for (uint32_t i = 0; i < len; i++) {
            data[i] = i * 10;  // 示例：赋值为i*10
        }

        last_err.code = ERR_SUCCESS;
        snprintf(last_err.msg, ERR_MSG_LEN, "Init data success (len=%u)", len);
        return last_err.code;
    }

    // 成员函数：处理数据（指针操作，底层）
    ErrorCode process_data(uint32_t index, int value) {
        if (data == nullptr) {
            last_err.code = ERR_INTERNAL;
            snprintf(last_err.msg, ERR_MSG_LEN, "Data not initialized");
            return last_err.code;
        }
        if (index >= data_len) {
            last_err.code = ERR_OUT_OF_RANGE;
            snprintf(last_err.msg, ERR_MSG_LEN, "Index out of range (index=%u, len=%u)", index, data_len);
            return last_err.code;
        }

        // 指针操作（最底层，无下标开销）
        int* p = data + index;
        *p = value;  // 直接修改内存

        last_err.code = ERR_SUCCESS;
        snprintf(last_err.msg, ERR_MSG_LEN, "Process data success (index=%u, value=%d)", index, value);
        return last_err.code;
    }

    // 成员函数：获取数据（指针返回，零拷贝）
    int get_data(uint32_t index, ErrorCode* err_code) {
        if (data == nullptr) {
            *err_code = ERR_INTERNAL;
            snprintf(last_err.msg, ERR_MSG_LEN, "Data not initialized");
            return -1;
        }
        if (index >= data_len) {
            *err_code = ERR_OUT_OF_RANGE;
            snprintf(last_err.msg, ERR_MSG_LEN, "Index out of range (index=%u, len=%u)", index, data_len);
            return -1;
        }

        *err_code = ERR_SUCCESS;
        return *(data + index);  // 指针解引用
    }

    // 获取最后错误信息
    void get_last_error(ErrorInfo* err) {
        *err = last_err;
    }

    // 新增：设置错误信息（解决私有成员访问问题）
    void set_last_error(ErrorCode code, const char* msg) {
        last_err.code = code;
        snprintf(last_err.msg, ERR_MSG_LEN, "%s", msg);
    }

    // 析构函数（无需释放内存池，栈内存自动释放）
    ~AdvancedProcessor() {
        data = nullptr;
        data_len = 0;
    }
};

// ==================== 4. C风格封装函数（供Python调用） ====================
extern "C" {
    #ifdef _WIN32
    #define DLL_EXPORT __declspec(dllexport)
    #else
    #define DLL_EXPORT
    #endif

    // -------------------- 内存池操作 --------------------
    // 创建内存池（栈分配，返回指针）
    DLL_EXPORT void* memory_pool_create(ErrorInfo* err) {
        // 移除catch，改用nothrow+手动判断（因为关闭了异常）
        StackMemoryPool* pool = new (std::nothrow) StackMemoryPool();
        if (pool == nullptr) {
            err->code = ERR_MEMORY;
            snprintf(err->msg, ERR_MSG_LEN, "Create memory pool failed (out of memory)");
            return nullptr;
        }
        err->code = ERR_SUCCESS;
        snprintf(err->msg, ERR_MSG_LEN, "Create memory pool success");
        return pool;
    }

    // 释放内存池
    DLL_EXPORT void memory_pool_destroy(void* pool_ptr, ErrorInfo* err) {
        if (pool_ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Pool pointer is null");
            return;
        }
        // 移除catch，直接释放（无异常）
        delete (StackMemoryPool*)pool_ptr;
        err->code = ERR_SUCCESS;
        snprintf(err->msg, ERR_MSG_LEN, "Destroy memory pool success");
    }

    // 内存池分配
    DLL_EXPORT void* memory_pool_allocate(void* pool_ptr, uint32_t size, ErrorInfo* err) {
        if (pool_ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Pool pointer is null");
            return nullptr;
        }
        return ((StackMemoryPool*)pool_ptr)->allocate(size, err);
    }

    // 内存池重置
    DLL_EXPORT void memory_pool_reset(void* pool_ptr, ErrorInfo* err) {
        if (pool_ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Pool pointer is null");
            return;
        }
        ((StackMemoryPool*)pool_ptr)->reset(err);
    }

    // 获取剩余内存
    DLL_EXPORT uint32_t memory_pool_get_remaining(void* pool_ptr, ErrorInfo* err) {
        if (pool_ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Pool pointer is null");
            return 0;
        }
        return ((StackMemoryPool*)pool_ptr)->get_remaining(err);
    }

    // -------------------- 高级处理器类操作 --------------------
    // 创建处理器实例
    DLL_EXPORT void* processor_create(void* pool_ptr, ErrorInfo* err) {
        if (pool_ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Pool pointer is null");
            return nullptr;
        }
        // 移除catch，改用nothrow+手动判断
        AdvancedProcessor* processor = new (std::nothrow) AdvancedProcessor((StackMemoryPool*)pool_ptr);
        if (processor == nullptr) {
            err->code = ERR_MEMORY;
            snprintf(err->msg, ERR_MSG_LEN, "Create processor failed (out of memory)");
            return nullptr;
        }
        err->code = ERR_SUCCESS;
        snprintf(err->msg, ERR_MSG_LEN, "Create processor success");
        return processor;
    }

    // 释放处理器实例
    DLL_EXPORT void processor_destroy(void* processor_ptr, ErrorInfo* err) {
        if (processor_ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Processor pointer is null");
            return;
        }
        // 移除catch，直接释放
        delete (AdvancedProcessor*)processor_ptr;
        err->code = ERR_SUCCESS;
        snprintf(err->msg, ERR_MSG_LEN, "Destroy processor success");
    }

    // 初始化处理器数据
    DLL_EXPORT ErrorCode processor_init_data(void* processor_ptr, uint32_t len) {
        if (processor_ptr == nullptr) {
            return ERR_INVALID_PARAM;
        }
        return ((AdvancedProcessor*)processor_ptr)->init_data(len);
    }

    // 处理处理器数据
    DLL_EXPORT ErrorCode processor_process_data(void* processor_ptr, uint32_t index, int value) {
        if (processor_ptr == nullptr) {
            return ERR_INVALID_PARAM;
        }
        return ((AdvancedProcessor*)processor_ptr)->process_data(index, value);
    }

    // 获取处理器数据
    DLL_EXPORT int processor_get_data(void* processor_ptr, uint32_t index, ErrorCode* err_code) {
        if (processor_ptr == nullptr) {
            *err_code = ERR_INVALID_PARAM;
            // 改用set_last_error设置错误（新增的公有方法）
            ((AdvancedProcessor*)processor_ptr)->set_last_error(ERR_INVALID_PARAM, "Processor pointer is null");
            return -1;
        }
        return ((AdvancedProcessor*)processor_ptr)->get_data(index, err_code);
    }

    // 获取最后错误信息
    DLL_EXPORT void processor_get_last_error(void* processor_ptr, ErrorInfo* err) {
        if (processor_ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Processor pointer is null");
            return;
        }
        ((AdvancedProcessor*)processor_ptr)->get_last_error(err);
    }

    // -------------------- 指针操作函数 --------------------
    // 写入字节到指针
    DLL_EXPORT ErrorCode pointer_write_byte(void* ptr, uint32_t offset, uint8_t value) {
        if (ptr == nullptr) {
            return ERR_INVALID_PARAM;
        }
        uint8_t* p = (uint8_t*)ptr + offset;
        *p = value;
        return ERR_SUCCESS;
    }

    // 写入短整型到指针
    DLL_EXPORT ErrorCode pointer_write_short(void* ptr, uint32_t offset, int16_t value) {
        if (ptr == nullptr) {
            return ERR_INVALID_PARAM;
        }
        int16_t* p = (int16_t*)((uint8_t*)ptr + offset);
        *p = value;
        return ERR_SUCCESS;
    }

    // 写入整型到指针
    DLL_EXPORT ErrorCode pointer_write_int(void* ptr, uint32_t offset, int32_t value) {
        if (ptr == nullptr) {
            return ERR_INVALID_PARAM;
        }
        int32_t* p = (int32_t*)((uint8_t*)ptr + offset);
        *p = value;
        return ERR_SUCCESS;
    }

    // 写入长整型到指针
    DLL_EXPORT ErrorCode pointer_write_long(void* ptr, uint32_t offset, int64_t value) {
        if (ptr == nullptr) {
            return ERR_INVALID_PARAM;
        }
        int64_t* p = (int64_t*)((uint8_t*)ptr + offset);
        *p = value;
        return ERR_SUCCESS;
    }

    // 写入浮点型到指针
    DLL_EXPORT ErrorCode pointer_write_float(void* ptr, uint32_t offset, float value) {
        if (ptr == nullptr) {
            return ERR_INVALID_PARAM;
        }
        float* p = (float*)((uint8_t*)ptr + offset);
        *p = value;
        return ERR_SUCCESS;
    }

    // 写入双精度浮点型到指针
    DLL_EXPORT ErrorCode pointer_write_double(void* ptr, uint32_t offset, double value) {
        if (ptr == nullptr) {
            return ERR_INVALID_PARAM;
        }
        double* p = (double*)((uint8_t*)ptr + offset);
        *p = value;
        return ERR_SUCCESS;
    }

    // 从指针读取字节
    DLL_EXPORT uint8_t pointer_read_byte(void* ptr, uint32_t offset, ErrorInfo* err) {
        if (ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Pointer is null");
            return 0;
        }
        uint8_t* p = (uint8_t*)ptr + offset;
        err->code = ERR_SUCCESS;
        return *p;
    }

    // 从指针读取短整型
    DLL_EXPORT int16_t pointer_read_short(void* ptr, uint32_t offset, ErrorInfo* err) {
        if (ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Pointer is null");
            return 0;
        }
        int16_t* p = (int16_t*)((uint8_t*)ptr + offset);
        err->code = ERR_SUCCESS;
        return *p;
    }

    // 从指针读取整型
    DLL_EXPORT int32_t pointer_read_int(void* ptr, uint32_t offset, ErrorInfo* err) {
        if (ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Pointer is null");
            return 0;
        }
        int32_t* p = (int32_t*)((uint8_t*)ptr + offset);
        err->code = ERR_SUCCESS;
        return *p;
    }

    // 从指针读取长整型
    DLL_EXPORT int64_t pointer_read_long(void* ptr, uint32_t offset, ErrorInfo* err) {
        if (ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Pointer is null");
            return 0;
        }
        int64_t* p = (int64_t*)((uint8_t*)ptr + offset);
        err->code = ERR_SUCCESS;
        return *p;
    }

    // 从指针读取浮点型
    DLL_EXPORT float pointer_read_float(void* ptr, uint32_t offset, ErrorInfo* err) {
        if (ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Pointer is null");
            return 0.0f;
        }
        float* p = (float*)((uint8_t*)ptr + offset);
        err->code = ERR_SUCCESS;
        return *p;
    }

    // 从指针读取双精度浮点型
    DLL_EXPORT double pointer_read_double(void* ptr, uint32_t offset, ErrorInfo* err) {
        if (ptr == nullptr) {
            err->code = ERR_INVALID_PARAM;
            snprintf(err->msg, ERR_MSG_LEN, "Pointer is null");
            return 0.0;
        }
        double* p = (double*)((uint8_t*)ptr + offset);
        err->code = ERR_SUCCESS;
        return *p;
    }

    // 指针偏移
    DLL_EXPORT void* pointer_offset(void* ptr, int32_t offset) {
        if (ptr == nullptr) {
            return nullptr;
        }
        return (uint8_t*)ptr + offset;
    }

    // 指针复制
    DLL_EXPORT ErrorCode pointer_copy(void* dest, void* src, uint32_t size) {
        if (dest == nullptr || src == nullptr) {
            return ERR_INVALID_PARAM;
        }
        memcpy(dest, src, size);
        return ERR_SUCCESS;
    }

    // 指针比较
    DLL_EXPORT int pointer_compare(void* ptr1, void* ptr2) {
        if (ptr1 == ptr2) {
            return 0;
        }
        if (ptr1 < ptr2) {
            return -1;
        }
        return 1;
    }

    // 内存填充
    DLL_EXPORT ErrorCode pointer_fill(void* ptr, uint32_t size, uint8_t value) {
        if (ptr == nullptr) {
            return ERR_INVALID_PARAM;
        }
        memset(ptr, value, size);
        return ERR_SUCCESS;
    }

    // 内存清零
    DLL_EXPORT ErrorCode pointer_zero(void* ptr, uint32_t size) {
        if (ptr == nullptr) {
            return ERR_INVALID_PARAM;
        }
        memset(ptr, 0, size);
        return ERR_SUCCESS;
    }
}

// Python module initialization
#ifdef _WIN32
#define EXPORT_SYMBOL __declspec(dllexport)
#else
#define EXPORT_SYMBOL __attribute__((visibility("default")))
#endif

extern "C" {
    EXPORT_SYMBOL PyObject* PyInit__core(void) {
        Py_INCREF(Py_None);
        return Py_None;
    }
}