// PrintWatch Windows Print Processor header
#pragma once

#include <string>

void PrintWatchLog(const std::string& printer, const std::string& user,
                    const std::string& document, int pages, int copies,
                    bool color, bool duplex);