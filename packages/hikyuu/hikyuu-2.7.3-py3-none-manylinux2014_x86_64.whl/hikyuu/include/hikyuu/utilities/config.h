#pragma once
#ifndef HKU_UTILS_CONFIG_H_
#define HKU_UTILS_CONFIG_H_

#include "osdef.h"

// clang-format off

#ifndef HKU_ENABLE_MYSQL
#define HKU_ENABLE_MYSQL 1
#if HKU_ENABLE_MYSQL && HKU_OS_WINDOWS
#ifndef NOMINMAX
#define NOMINMAX
#endif
#endif
#endif

#ifndef HKU_ENABLE_SQLITE
#define HKU_ENABLE_SQLITE 1
#endif
#ifndef HKU_ENABLE_SQLCIPHER
#define HKU_ENABLE_SQLCIPHER 0
#endif
#ifndef HKU_SQL_TRACE
/* #define HKU_SQL_TRACE 0 */
#endif

#ifndef HKU_SUPPORT_DATETIME
#define HKU_SUPPORT_DATETIME 1
#endif

#ifndef HKU_ENABLE_INI_PARSER
#define HKU_ENABLE_INI_PARSER 1
#endif

#ifndef HKU_ENABLE_STACK_TRACE
#define HKU_ENABLE_STACK_TRACE 0
#endif

#ifndef HKU_CLOSE_SPEND_TIME
#define HKU_CLOSE_SPEND_TIME 0
#endif

#ifndef HKU_USE_SPDLOG_ASYNC_LOGGER
#define HKU_USE_SPDLOG_ASYNC_LOGGER 0
#endif
#ifndef HKU_LOG_ACTIVE_LEVEL
#define HKU_LOG_ACTIVE_LEVEL 2
#endif

#ifndef HKU_ENABLE_HTTP_CLIENT
#define HKU_ENABLE_HTTP_CLIENT 1
#endif
#ifndef HKU_ENABLE_HTTP_CLIENT_SSL
#define HKU_ENABLE_HTTP_CLIENT_SSL 0
#endif
#ifndef HKU_ENABLE_HTTP_CLIENT_ZIP
#define HKU_ENABLE_HTTP_CLIENT_ZIP 0
#endif

#ifndef HKU_ENABLE_NODE
#define HKU_ENABLE_NODE 1
#endif

// clang-format on

#endif /* HKU_UTILS_CONFIG_H_ */