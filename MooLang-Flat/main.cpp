#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <regex>
#include <variant>
#include <chrono>
#include <random>
#include <stdexcept>
#include <sstream>
#include <algorithm>
#include <memory>

std::string path = "code.ml2";
bool debugmode = false;

using Value = std::variant<int, double, std::string, std::vector<Value>>;
using VarMap = std::map<std::string, Value>;

class Forl {
public:
    std::string var;
    std::vector<std::string> lines;
    std::vector<Value> ins;

    Forl(const std::string& replacementvar, const std::vector<Value>& inside) 
        : var(replacementvar), ins(inside) {}

    void add_line(const std::string& line) { lines.push_back(line); }
    void run();
};

class Whilel {
public:
    std::string c;
    std::vector<std::string> lines;

    Whilel(const std::string& condition) : c(condition) {}

    void add_line(const std::string& line) { lines.push_back(line); }
    void run();
};

class Statement {
public:
    std::string condition;
    std::vector<std::string> lines;

    Statement(const std::string& cond) : condition(cond) {}

    void add_line(const std::string& line) { lines.push_back(line); }
    void run();
};

class Function {
public:
    std::string name;
    std::vector<std::string> param;
    std::vector<std::string> extravars;
    std::vector<std::string> lines;

    Function(const std::string& n, const std::vector<std::string>& p) : name(n), param(p) {}

    void add_line(const std::string& line);
    Value run(const std::vector<Value>& params);
private:
    void cleanup();
};

VarMap variables = {{"pi", 3.141592653589793}, {"moo", std::string("all_praise_moo")}};
std::vector<std::string> imports;
std::map<std::string, std::string> typeroo;
std::vector<std::pair<std::string, Function>> functions;
std::vector<std::unique_ptr<void, void(*)(void*)>> inside(0, {nullptr, [](void*){}});

bool is_name(const std::string& s) {
    std::regex name_regex("^[a-zA-Z_][a-zA-Z0-9_]*$");
    return std::regex_match(s, name_regex) && s != "MOO" && s != "PI";
}

void moocleanup() {
    for (auto it = typeroo.begin(); it != typeroo.end();) {
        if (variables.find(it->first) == variables.end()) {
            it = typeroo.erase(it);
        } else {
            ++it;
        }
    }
}

Value interpret(const std::string& line);

void Forl::run() {
    for (const auto& x : ins) {
        variables[var] = x;
        for (const auto& l : lines) {
            interpret(l);
        }
    }
    variables.erase(var);
}

void Whilel::run() {
    while (std::get<double>(interpret(c)) != 0) {  // Non-zero as true
        for (const auto& l : lines) {
            interpret(l);
        }
    }
}

void Statement::run() {
    if (std::get<double>(interpret(condition)) != 0) {
        for (const auto& l : lines) {
            interpret(l);
        }
    }
}

void Function::add_line(const std::string& line) {
    lines.push_back(line);
    std::regex makevar(R"(^\s*(\w+)\s*:\s*(\w+)\s*=\s*(.+)$)");
    std::smatch match;
    if (std::regex_match(line, match, makevar) && is_name(match[1])) {
        extravars.push_back(match[1]);
    }
}

Value Function::run(const std::vector<Value>& params) {
    if (params.size() != param.size()) {
        throw std::runtime_error("Argument count mismatch for function '" + name + "'");
    }
    for (size_t i = 0; i < param.size(); ++i) {
        variables[param[i]] = params[i];
    }
    for (const auto& line : lines) {
        if (line.find("return") == 0) {
            Value result = interpret(line.substr(6));
            cleanup();
            return result;
        }
        interpret(line);
    }
    cleanup();
    return Value{0.0};
}

void Function::cleanup() {
    for (const auto& p : param) variables.erase(p);
    for (const auto& v : extravars) variables.erase(v);
}

Value interpret(const std::string& line) {
    std::string trimmed = line;
    while (!trimmed.empty() && trimmed.back() == ';') trimmed.pop_back();
    if (debugmode) std::cout << "DEBUG: " << trimmed << std::endl;

    std::smatch match;
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*console\.out\((.+)\)$)"))) {
        Value result = interpret(match[1]);
        std::visit([](auto&& arg) { std::cout << arg << std::endl; }, result);
        return result;
    }
    if (trimmed.size() >= 2 && (trimmed[0] == '"' || trimmed[0] == '\'') && trimmed[0] == trimmed.back()) {
        return trimmed.substr(1, trimmed.size() - 2);
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*use\s+<(.+)>$)"))) {
        imports.push_back(match[1]);
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(\w+)\s*:\s*(\w+)\s*=\s*(.+)$)"))) {
        std::string name = match[1], type = match[2], value = match[3];
        if (!is_name(name)) {
            std::cerr << "Moo Error: Invalid variable name '" << name << "'\n";
            return Value{-1.0};
        }
        Value val = interpret(value);
        if (type == "int") {
            if (std::holds_alternative<double>(val)) val = static_cast<int>(std::get<double>(val));
            else if (std::holds_alternative<std::string>(val)) val = std::stoi(std::get<std::string>(val));
        } else if (type == "float" || type == "double") {
            if (std::holds_alternative<std::string>(val)) val = std::stod(std::get<std::string>(val));
        }
        variables[name] = val;
        typeroo[name] = type;
        return val;
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*rmv\s+(.+)$)"))) {
        variables.erase(match[1]);
        typeroo.erase(match[1]);
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*inp\[(.+)\]$)"))) {
        std::string prompt = std::get<std::string>(interpret(match[1]));
        std::cout << prompt;
        std::string input;
        std::getline(std::cin, input);
        return input;
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*if\s*\((.+)\)\s*then\s*\{$)"))) {
        inside.emplace_back(std::make_unique<Statement>(match[1]).release(), [](void* p) { delete static_cast<Statement*>(p); });
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*for\s+(\w+)\s+in\s*\((.+)\)\s*\{$)"))) {
        std::vector<Value> range = std::get<std::vector<Value>>(interpret(match[2]));
        inside.emplace_back(std::make_unique<Forl>(match[1], range).release(), [](void* p) { delete static_cast<Forl*>(p); });
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*while\s*\((.+)\)\s*do\s*\{$)"))) {
        inside.emplace_back(std::make_unique<Whilel>(match[1]).release(), [](void* p) { delete static_cast<Whilel*>(p); });
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*define\s+(\w+)\s+with\s+(.+)\s*\{$)"))) {
        if (is_name(match[1])) {
            std::vector<std::string> params;
            std::stringstream ss(match[2]);
            std::string param;
            while (std::getline(ss, param, ',')) {
                param.erase(param.find_last_not_of(" \t") + 1);
                param.erase(0, param.find_first_not_of(" \t"));
                params.push_back(param);
            }
            inside.emplace_back(std::make_unique<Function>(match[1], params).release(), [](void* p) { delete static_cast<Function*>(p); });
        }
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*not\s+(.+)$)"))) {
        return std::get<double>(interpret(match[1])) == 0 ? Value{1.0} : Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(.+?)\s*==\s*(.+)$)"))) {
        Value a = interpret(match[1]), b = interpret(match[2]);
        return std::visit([](auto&& x, auto&& y) { return x == y ? Value{1.0} : Value{0.0}; }, a, b);
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(.+?)\s*>\s*(.+)$)"))) {
        return std::get<double>(interpret(match[1])) > std::get<double>(interpret(match[2])) ? Value{1.0} : Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(.+?)\s*<\s*(.+)$)"))) {
        return std::get<double>(interpret(match[1])) < std::get<double>(interpret(match[2])) ? Value{1.0} : Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(.+?)\s*>=\s*(.+)$)"))) {
        return std::get<double>(interpret(match[1])) >= std::get<double>(interpret(match[2])) ? Value{1.0} : Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(.+?)\s*<=\s*(.+)$)"))) {
        return std::get<double>(interpret(match[1])) <= std::get<double>(interpret(match[2])) ? Value{1.0} : Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(.+?)\s+and\s+(.+)$)"))) {
        return (std::get<double>(interpret(match[1])) != 0 && std::get<double>(interpret(match[2])) != 0) ? Value{1.0} : Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(.+?)\[(.+?)\]$)"))) {
        auto& vec = std::get<std::vector<Value>>(variables[interpret(match[1])]);
        return vec[static_cast<size_t>(std::get<double>(interpret(match[2])))];
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*range\{(.+)\}$)"))) {
        int n = static_cast<int>(std::get<double>(interpret(match[1])));
        std::vector<Value> result;
        for (int i = 0; i < n; ++i) result.push_back(static_cast<double>(i));
        return result;
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(\w+)\s*\+=\s*(.+)$)"))) {
        std::string var = match[1];
        if (variables.count(var)) {
            variables[var] = std::get<double>(variables[var]) + std::get<double>(interpret(match[2]));
        }
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(\w+)\s*-=\s*(.+)$)"))) {
        std::string var = match[1];
        if (variables.count(var)) {
            variables[var] = std::get<double>(variables[var]) - std::get<double>(interpret(match[2]));
        }
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(.+?)\s*\+\s*(.+)$)"))) {
        Value a = interpret(match[1]), b = interpret(match[2]);
        if (std::holds_alternative<std::string>(a) || std::holds_alternative<std::string>(b)) {
            return std::get<std::string>(a) + std::get<std::string>(b);
        }
        return std::get<double>(a) + std::get<double>(b);
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(.+?)\s*-\s*(.+)$)"))) {
        return std::get<double>(interpret(match[1])) - std::get<double>(interpret(match[2]));
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(.+?)\s*\*\s*(.+)$)"))) {
        return std::get<double>(interpret(match[1])) * std::get<double>(interpret(match[2]));
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(.+?)\s*/\s*(.+)$)"))) {
        return std::get<double>(interpret(match[1])) / std::get<double>(interpret(match[2]));
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*wait\((.+)\)$)"))) {
        std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(std::get<double>(interpret(match[1])) * 1000)));
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*clear\(\)$)"))) {
        std::cout << "\033[2J\033[1;1H";  // ANSI clear screen
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*rand\((.+),(.+)\)$)"))) {
        int a = static_cast<int>(std::get<double>(interpret(match[1]))), b = static_cast<int>(std::get<double>(interpret(match[2])));
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(a, b);
        return static_cast<double>(dis(gen));
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*len\((.+)\)$)"))) {
        Value val = interpret(match[1]);
        if (std::holds_alternative<std::string>(val)) return static_cast<double>(std::get<std::string>(val).size());
        if (std::holds_alternative<std::vector<Value>>(val)) return static_cast<double>(std::get<std::vector<Value>>(val).size());
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*append\((.+),(.+)\)$)"))) {
        std::string var = match[1];
        if (variables.count(var) && std::holds_alternative<std::vector<Value>>(variables[var])) {
            std::get<std::vector<Value>>(variables[var]).push_back(interpret(match[2]));
        }
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*remove\((.+),(.+)\)$)"))) {
        std::string var = match[1];
        if (variables.count(var) && std::holds_alternative<std::vector<Value>>(variables[var])) {
            auto& vec = std::get<std::vector<Value>>(variables[var]);
            size_t idx = static_cast<size_t>(std::get<double>(interpret(match[2])));
            if (idx < vec.size()) vec.erase(vec.begin() + idx);
        }
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*reverse\((.+)\)$)"))) {
        Value val = interpret(match[1]);
        if (std::holds_alternative<std::string>(val)) {
            std::string s = std::get<std::string>(val);
            std::reverse(s.begin(), s.end());
            return s;
        }
        if (std::holds_alternative<std::vector<Value>>(val)) {
            auto vec = std::get<std::vector<Value>>(val);
            std::reverse(vec.begin(), vec.end());
            return vec;
        }
        return Value{0.0};
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*exit\(\)$)"))) {
        std::exit(0);
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*type\((.+)\)$)"))) {
        Value val = interpret(match[1]);
        if (std::holds_alternative<int>(val)) return std::string("int");
        if (std::holds_alternative<double>(val)) return std::string("double");
        if (std::holds_alternative<std::string>(val)) return std::string("string");
        if (std::holds_alternative<std::vector<Value>>(val)) return std::string("list");
        return std::string("unknown");
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*uppercase\((.+)\)$)"))) {
        std::string s = std::get<std::string>(interpret(match[1]));
        std::transform(s.begin(), s.end(), s.begin(), ::toupper);
        return s;
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*lowercase\((.+)\)$)"))) {
        std::string s = std::get<std::string>(interpret(match[1]));
        std::transform(s.begin(), s.end(), s.begin(), ::tolower);
        return s;
    }
    if (std::regex_match(trimmed, match, std::regex(R"(^\s*(\w+)\.(.+)$)"))) {
        std::string mod = match[1], func = match[2];
        if (std::find(imports.begin(), imports.end(), mod) != imports.end()) {
            if (mod == "random" && func.find("randint") == 0) {
                std::regex rand_args(R"(randint\((\d+),(\d+)\))");
                std::smatch rand_match;
                if (std::regex_match(func, rand_match, rand_args)) {
                    int a = std::stoi(rand_match[1]), b = std::stoi(rand_match[2]);
                    std::random_device rd;
                    std::mt19937 gen(rd());
                    std::uniform_int_distribution<> dis(a, b);
                    return static_cast<double>(dis(gen));
                }
            }
        }
        std::cerr << "Moo Error: Module '" << mod << "' not imported or function not supported\n";
        return Value{-1.0};
    }
    if (variables.count(trimmed)) {
        return variables[trimmed];
    }
    if (trimmed[0] == '$' && variables.count(trimmed.substr(1))) {
        return trimmed.substr(1);
    }
    for (const auto& [name, func] : functions) {
        std::regex call(R"(^" + name + R"(\((.*)\)$)");
        if (std::regex_match(trimmed, match, call)) {
            std::vector<Value> params;
            std::stringstream ss(match[1]);
            std::string param;
            while (std::getline(ss, param, ',')) {
                param.erase(param.find_last_not_of(" \t") + 1);
                param.erase(0, param.find_first_not_of(" \t"));
                params.push_back(interpret(param));
            }
            return func.run(params);
        }
    }

    moocleanup();
    try {
        return std::stod(trimmed);
    } catch (...) {
        return trimmed;
    }
}

void work(const std::string& txt) {
    std::ifstream file(txt);
    if (!file.is_open()) {
        std::cerr << "Moo Error: File '" << txt << "' not found\n";
        return;
    }

    int lnn = 1;
    std::string line;
    while (std::getline(file, line)) {
        line.erase(line.find_last_not_of(" \t\n\r") + 1);
        if (line.empty()) continue;

        if (!inside.empty()) {
            if (line == "}") {
                if (auto* stmt = static_cast<Statement*>(inside.back().get())) {
                    stmt->run();
                } else if (auto* forl = static_cast<Forl*>(inside.back().get())) {
                    forl->run();
                } else if (auto* whilel = static_cast<Whilel*>(inside.back().get())) {
                    whilel->run();
                } else if (auto* func = static_cast<Function*>(inside.back().get())) {
                    functions.emplace_back(func->name, *func);
                }
                inside.pop_back();
            } else {
                if (auto* stmt = static_cast<Statement*>(inside.back().get())) {
                    stmt->add_line(line);
                } else if (auto* forl = static_cast<Forl*>(inside.back().get())) {
                    forl->add_line(line);
                } else if (auto* whilel = static_cast<Whilel*>(inside.back().get())) {
                    whilel->add_line(line);
                } else if (auto* func = static_cast<Function*>(inside.back().get())) {
                    func->add_line(line);
                }
            }
        } else {
            Value result = interpret(line);
            if (std::holds_alternative<double>(result) && std::get<double>(result) == -1.0) break;
        }
        lnn++;
    }
    file.close();
}

int main() {
    auto start = std::chrono::high_resolution_clock::now();
    work(path);
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;
    std::cout << "Ran in " << diff.count() << " secs\n";
    return 0;
}
