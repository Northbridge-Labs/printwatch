// PrintWatch Windows Print Processor
//
// A minimal print processor DLL that hooks PrintJob() and records job
// metadata (user, document, pages, printer, timestamp) to a JSONL log
// file at %ProgramData%\PrintWatch\jobs.jsonl. A separate Python agent
// tails the file and forwards entries to the backend over ZeroMQ.
//
// Build with MSVC (Visual Studio 2022, x64). See README.md.

#include "PrintProcessor.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <fstream>
#include <shlobj.h>
#include <sstream>
#include <string>
#include <windows.h>

static const wchar_t* kLogSubdir = L"PrintWatch";
static const wchar_t* kLogFile = L"jobs.jsonl";

static std::wstring ProgramDataPath() {
    wchar_t path[MAX_PATH] = {0};
    if (SUCCEEDED(SHGetFolderPathW(nullptr, CSIDL_COMMON_APPDATA,
                                   nullptr, 0, path))) {
        return std::wstring(path) + L"\\PrintWatch";
    }
    return L"C:\\ProgramData\\PrintWatch";
}

static void EnsureDirectory(const std::wstring& dir) {
    CreateDirectoryW(dir.c_str(), nullptr);
}

// Escape a string for JSON output.
static std::string JsonEscape(const std::string& in) {
    std::string out;
    out.reserve(in.size() + 8);
    for (char c : in) {
        switch (c) {
            case '"': out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default: out += c;
        }
    }
    return out;
}

static std::string TimestampUtc() {
    time_t now = time(nullptr);
    struct tm tmv;
    gmtime_s(&tmv, &now);
    char buf[32];
    strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tmv);
    return buf;
}

void PrintWatchLog(const std::string& printer, const std::string& user,
                   const std::string& document, int pages, int copies,
                   bool color, bool duplex) {
    std::wstring dir = ProgramDataPath();
    EnsureDirectory(dir);
    std::wstring path = dir + L"\\" + kLogFile;

    std::ofstream out(path.c_str(), std::ios::app);
    if (!out) return;

    out << "{"
        << "\"source\":\"windows\","
        << "\"printer\":\"" << JsonEscape(printer) << "\","
        << "\"username\":\"" << JsonEscape(user) << "\","
        << "\"document\":\"" << JsonEscape(document) << "\","
        << "\"pages\":" << pages << ","
        << "\"copies\":" << copies << ","
        << "\"color\":" << (color ? "true" : "false") << ","
        << "\"duplex\":" << (duplex ? "true" : "false") << ","
        << "\"submitted_at\":\"" << TimestampUtc() << "\""
        << "}\n";
}