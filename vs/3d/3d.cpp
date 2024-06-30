// 3d.cpp : このファイルには 'main' 関数が含まれています。プログラム実行の開始と終了がそこで行われます。
//

#include <functional>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

struct WriteTarget {
    int x;
    int y;
    std::string value;
};

struct RemoveTarget {
    int x;
    int y;
};

struct TimeWarpTarget {
    int source_x;
    int source_y;
    int destination_x;
    int destination_y;
    std::string value;
    int turn;
};

using Board = std::vector<std::vector<std::string>>;
using Integer = int64_t;
std::vector<Board> HISTORY;
int WIDTH;
int HEIGHT;

void Input(char* argv[]) {
    Board board;
    std::string line;
    // 1行目はコマンドが書かれていると仮定する。
    std::getline(std::cin, line);
    while (std::getline(std::cin, line)) {
        std::vector<std::string> row;
        std::string value;
        std::istringstream iss(line);
        while (iss >> value) {
            if (value == "A") {
                row.push_back(argv[1]);
            }
            else if (value == "B") {
                row.push_back(argv[2]);
            }
            else {
                row.push_back(value);
            }
        }
        board.push_back(row);
    }
    WIDTH = board[0].size();
    HEIGHT = board.size();
    HISTORY.push_back(board);
}

bool TryParse(const std::string& value, Integer& integer) {
    std::istringstream iss(value);
    if (iss >> integer) {
        return true;
    }
    else {
        return false;
    }
}

bool ProcessMoveOperator(
    const Board& board, int source_x, int source_y, int destination_x, int destination_y,
    std::vector<RemoveTarget>& remove_targets, std::vector<WriteTarget>& write_targets) {
    if (!(0 <= source_x && source_x < WIDTH && 0 <= source_y && source_y < HEIGHT)) {
        std::printf(
            "The source coordinates of a move operator are outside of the board. source_x=%d source_y=%d destination_x=%d destination_y=%d\n",
            source_x, source_y, destination_x, destination_y);
        return false;
    }

    if (!(0 <= destination_x && destination_x < WIDTH && 0 <= destination_y
        && destination_y < HEIGHT)) {
        std::printf(
            "The destination coordinates of a move operator are outside of the board. source_x=%d source_y=%d destination_x=%d destination_y=%d\n",
            source_x, source_y, destination_x, destination_y);
        return false;
    }

    if (board[source_y][source_x] == ".") {
        // 何もしない。
        return true;
    }

    write_targets.emplace_back(WriteTarget{ destination_x, destination_y, board[source_y][source_x] });
    remove_targets.emplace_back(RemoveTarget{ source_x, source_y });
    return true;
}

bool ProcessBinaryOperator(
    const Board& board, int x, int y, std::function<bool(int x, int y, const std::string& left,
        const std::string& up, std::vector<RemoveTarget>& remove_targets,
        std::vector<WriteTarget>& write_targets)> operand,
    std::vector<RemoveTarget>& remove_targets, std::vector<WriteTarget>& write_targets) {
    if (!(1 <= x && x < WIDTH - 1 && 1 <= y && y <= HEIGHT - 1)) {
        std::printf(
            "The target coordinates of a binary operator are outside of the board. x=%d y=%d\n",
            x, y);
        return false;
    }

    if (board[y][x - 1] == ".") {
        // 何もしない
        return true;
    }

    if (board[y - 1][x] == ".") {
        // 何もしない
        return true;
    }

    // 書き込み予定の値をリストに格納する。
    return operand(x, y, board[y][x - 1], board[y - 1][x], remove_targets, write_targets);
}

bool ProcessArithmeticBinaryOperator(
    const Board& board, int x, int y, const std::function<bool(int x, int y, Integer left_integer,
        Integer up_integer, std::vector<RemoveTarget>& remove_targets,
        std::vector<WriteTarget>& write_targets)>& operand,
    std::vector<RemoveTarget>& remove_targets, std::vector<WriteTarget>& write_targets) {
    auto internal_operand = [&operand, &write_targets](int x, int y, const std::string& left,
        const std::string& up, std::vector<RemoveTarget>& remove_targets,
        std::vector<WriteTarget>& write_targets) -> bool {
            Integer left_integer;
            if (!TryParse(left, left_integer)) {
                std::printf("The left value of a binary operator is not an integer. x=%d y=%d\n", x,
                    y);
                return false;
            }

            Integer up_integer;
            if (!TryParse(up, up_integer)) {
                std::printf("The right value of a binary operator is not an integer. x=%d y=%d\n",
                    x, y);
                return false;
            }

            return operand(x, y, left_integer, up_integer, remove_targets, write_targets);
    };

    return ProcessBinaryOperator(board, x, y, internal_operand, remove_targets, write_targets);
}

bool ProcessTimeWarpOperator(const Board& board, int x, int y,
    std::vector<TimeWarpTarget>& time_warp_targets) {
    if (!(1 <= x && x < WIDTH - 1 && 1 <= y && y <= HEIGHT - 1)) {
        std::printf(
            "The target coordinates of a time warp operator are outside of the board. x=%d y=%d\n",
            x, y);
        return false;
    }

    if (board[y - 1][x] == ".") {
        // 何もしない
        return true;
    }

    Integer left;
    if (!TryParse(board[y][x - 1], left)) {
        std::printf("The left value of a time warp operator is not an integer. x=%d y=%d\n", x, y);
        return false;
    }

    Integer down;
    if (!TryParse(board[y + 1][x], down)) {
        std::printf("The down value of a time warp operator is not an integer. x=%d y=%d\n", x, y);
        return false;
    }

    Integer right;
    if (!TryParse(board[y][x + 1], right)) {
        std::printf("The right value of a time warp operator is not an integer. x=%d y=%d\n", x, y);
        return false;
    }

    time_warp_targets.emplace_back(TimeWarpTarget{
        x, y, x - static_cast<int>(left), y - static_cast<int>(right), board[y - 1][x],
        static_cast<int>(down) });
    return true;
}

bool ProcessTurn(std::vector<std::string>& submitted) {
    const auto& board = HISTORY.back();
    std::vector<RemoveTarget> remove_targets;
    std::vector<WriteTarget> write_targets;
    std::vector<TimeWarpTarget> time_warp_targets;

    // 削除される要素を盤面から取り除く。
    // 同時に、書き込まれる値をリストに保存する。
    // 削除・読み込みのあと、書き込みが行われる挙動を実現するため。
    for (int y = 0; y < HEIGHT; ++y) {
        for (int x = 0; x < WIDTH; ++x) {
            Integer integer = 0;
            if (board[y][x] == "<") {
                if (!ProcessMoveOperator(board, x + 1, y, x - 1, y, remove_targets, write_targets)) {
                    return false;
                }
            }
            else if (board[y][x] == ">") {
                if (!ProcessMoveOperator(board, x - 1, y, x + 1, y, remove_targets, write_targets)) {
                    return false;
                }
            }
            else if (board[y][x] == "^") {
                if (!ProcessMoveOperator(board, x, y + 1, x, y - 1, remove_targets, write_targets)) {
                    return false;
                }
            }
            else if (board[y][x] == "v") {
                if (!ProcessMoveOperator(board, x, y - 1, x, y + 1, remove_targets, write_targets)) {
                    return false;
                }
            }
            else if (board[y][x] == "+") {
                auto operand = [](int x, int y, Integer left_integer, Integer up_integer,
                    std::vector<RemoveTarget>& remove_targets,
                    std::vector<WriteTarget>& write_targets) -> bool {
                        write_targets.emplace_back(WriteTarget{
                            x + 1, y, std::to_string(left_integer + up_integer) });
                        write_targets.emplace_back(WriteTarget{
                            x, y + 1, std::to_string(left_integer + up_integer) });
                        remove_targets.emplace_back(RemoveTarget{ x - 1, y });
                        remove_targets.emplace_back(RemoveTarget{ x, y - 1 });
                        return true;
                };
                if (!ProcessArithmeticBinaryOperator(board, x, y, operand, remove_targets,
                    write_targets)) {
                    return false;
                }
            }
            else if (board[y][x] == "-") {
                auto operand = [](int x, int y, Integer left_integer, Integer up_integer,
                    std::vector<RemoveTarget>& remove_targets,
                    std::vector<WriteTarget>& write_targets) -> bool {
                        write_targets.emplace_back(WriteTarget{
                            x + 1, y, std::to_string(left_integer - up_integer) });
                        write_targets.emplace_back(WriteTarget{
                            x, y + 1, std::to_string(left_integer - up_integer) });
                        remove_targets.emplace_back(RemoveTarget{ x - 1, y });
                        remove_targets.emplace_back(RemoveTarget{ x, y - 1 });
                        return true;
                };
                if (!ProcessArithmeticBinaryOperator(board, x, y, operand, remove_targets,
                    write_targets)) {
                    return false;
                }
            }
            else if (board[y][x] == "*") {
                auto operand = [](int x, int y, Integer left_integer, Integer up_integer,
                    std::vector<RemoveTarget>& remove_targets,
                    std::vector<WriteTarget>& write_targets) -> bool {
                        write_targets.emplace_back(WriteTarget{
                            x + 1, y, std::to_string(left_integer * up_integer) });
                        write_targets.emplace_back(WriteTarget{
                            x, y + 1, std::to_string(left_integer * up_integer) });
                        remove_targets.emplace_back(RemoveTarget{ x - 1, y });
                        remove_targets.emplace_back(RemoveTarget{ x, y - 1 });
                        return true;
                };
                if (!ProcessArithmeticBinaryOperator(board, x, y, operand, remove_targets,
                    write_targets)) {
                    return false;
                }
            }
            else if (board[y][x] == "/") {
                auto operand = [](int x, int y, Integer left_integer, Integer up_integer,
                    std::vector<RemoveTarget>& remove_targets,
                    std::vector<WriteTarget>& write_targets) -> bool {
                        if (up_integer == 0) {
                            std::printf("Divided by zero. x=%d y=%d\n", x, y);
                            return false;
                        }

                        write_targets.emplace_back(WriteTarget{
                            x + 1, y, std::to_string(left_integer / up_integer) });
                        write_targets.emplace_back(WriteTarget{
                            x, y + 1, std::to_string(left_integer / up_integer) });
                        remove_targets.emplace_back(RemoveTarget{ x - 1, y });
                        remove_targets.emplace_back(RemoveTarget{ x, y - 1 });
                        return true;
                };
                if (!ProcessArithmeticBinaryOperator(board, x, y, operand, remove_targets,
                    write_targets)) {
                    return false;
                }
            }
            else if (board[y][x] == "%") {
                auto operand = [](int x, int y, Integer left_integer, Integer up_integer,
                    std::vector<RemoveTarget>& remove_targets,
                    std::vector<WriteTarget>& write_targets) -> bool {
                        if (up_integer == 0) {
                            std::printf("Divided by zero. x=%d y=%d\n", x, y);
                            return false;
                        }

                        write_targets.emplace_back(WriteTarget{
                            x + 1, y, std::to_string(left_integer % up_integer) });
                        write_targets.emplace_back(WriteTarget{
                            x, y + 1, std::to_string(left_integer % up_integer) });
                        remove_targets.emplace_back(RemoveTarget{ x - 1, y });
                        remove_targets.emplace_back(RemoveTarget{ x, y - 1 });
                        return true;
                };
                if (!ProcessArithmeticBinaryOperator(board, x, y, operand, remove_targets,
                    write_targets)) {
                    return false;
                }
            }
            else if (board[y][x] == "@") {
                if (!ProcessTimeWarpOperator(board, x, y, time_warp_targets)) {
                    return false;
                }
            }
            else if (board[y][x] == "=") {
                auto operand = [](int x, int y, const std::string& left, const std::string& up,
                    std::vector<RemoveTarget>& remove_targets,
                    std::vector<WriteTarget>& write_targets) -> bool {
                        if (left != up) {
                            // 何もしない。
                            return true;
                        }

                        write_targets.emplace_back(WriteTarget{ x + 1, y, up });
                        write_targets.emplace_back(WriteTarget{ x, y + 1, left });
                        remove_targets.emplace_back(RemoveTarget{ x - 1, y });
                        remove_targets.emplace_back(RemoveTarget{ x, y - 1 });
                        return true;
                };
                if (!ProcessBinaryOperator(board, x, y, operand, remove_targets, write_targets)) {
                    return false;
                }
            }
            else if (board[y][x] == "#") {
                auto operand = [](int x, int y, const std::string& left, const std::string& up,
                    std::vector<RemoveTarget>& remove_targets,
                    std::vector<WriteTarget>& write_targets) -> bool {
                        if (left == up) {
                            // 何もしない。
                            return true;
                        }

                        write_targets.emplace_back(WriteTarget{ x + 1, y, up });
                        write_targets.emplace_back(WriteTarget{ x, y + 1, left });
                        remove_targets.emplace_back(RemoveTarget{ x - 1, y });
                        remove_targets.emplace_back(RemoveTarget{ x, y - 1 });
                        return true;
                };
                if (!ProcessBinaryOperator(board, x, y, operand, remove_targets, write_targets)) {
                    return false;
                }
            }
            else if (board[y][x] == "S") {
                // 2フェーズ目で処理する。
            }
            else if (board[y][x] == "A") {
                std::printf("'A' must not be processed here. x=%d y=%d value=%s\n", x, y,
                    board[y][x].c_str());
                return false;
            }
            else if (board[y][x] == "B") {
                std::printf("'B' must not be processed here. x=%d y=%d value=%s\n", x, y,
                    board[y][x].c_str());
                return false;
            }
            else if (board[y][x] == ".") {
                // 何もしない
            }
            else if (TryParse(board[y][x], integer)) {
                // 何もしない
            }
            else {
                std::printf("Unknown character: x=%d y=%d value=%s\n", x, y, board[y][x].c_str());
                return false;
            }
        }
    }

    // タイムワープしなかった。
    Board new_board = board;

    // 削除予定の値を削除する。
    for (const auto& remove_target : remove_targets) {
        int x = remove_target.x;
        int y = remove_target.y;
        new_board[y][x] = ".";
    }

    // 書き込み予定の値を書き込む。
    std::vector<std::vector<bool>> written(HEIGHT, std::vector<bool>(WIDTH));
    for (const auto& write_target : write_targets) {
        int x = write_target.x;
        int y = write_target.y;
        const auto& value = write_target.value;
        if (written[y][x]) {
            std::printf("Conflicting writes into the same cell. x=%d y=%d value=%s,%s\n", x, y,
                new_board[y][x].c_str(), value.c_str());
            return false;
        }

        if (new_board[y][x] == "S") {
            submitted.push_back(value);
        }

        new_board[y][x] = value;
    }

    // タイムワープを処理する。
    if (submitted.empty() && !time_warp_targets.empty()) {
        // 異なる時間軸にタイムワープしようとしているか確認する。
        for (const auto& time_warp_target : time_warp_targets) {
            if (time_warp_target.turn != time_warp_targets.front().turn) {
                std::printf(
                    "Two different warp operators attempt to travel to different times in the same tick. "
                    "source_x0=%d source_y0=%d destination_x0=%d destination_y0=%d value0=%s source_x1=%d source_y1=%d destination_x1=%d destination_y1=%d value1=%s\n",
                    time_warp_target.source_x, time_warp_target.source_y,
                    time_warp_target.destination_x, time_warp_target.destination_y,
                    board[time_warp_target.source_y - 1][time_warp_target.source_x].c_str(),
                    time_warp_targets.front().source_x, time_warp_targets.front().source_y,
                    time_warp_targets.front().destination_x, time_warp_targets.front().destination_y,
                    board[time_warp_targets.front().source_y - 1][time_warp_targets.front().source_y].c_str());
                return false;
            }
        }

        // 時間を巻き戻す。
        HISTORY.resize(HISTORY.size() - time_warp_targets.front().turn);

        // タイムワープ値を書き込む。
        std::vector<std::vector<bool>> written(HEIGHT, std::vector<bool>(WIDTH));
        for (const auto& time_warp_target : time_warp_targets) {
            int source_x = time_warp_target.source_x;
            int source_y = time_warp_target.source_y;
            int destination_x = time_warp_target.destination_x;
            int destination_y = time_warp_target.destination_y;
            const auto& value = time_warp_target.value;

            if (!(0 <= destination_x && destination_x < WIDTH && 0 <= destination_y && destination_y < HEIGHT)) {
                std::printf(
                    "A time warp is trying to write a value outside of the board. "
                    "source_x=%d source_y=%d destination_x=%d destination_y=%d value=%s\n",
                    source_x, source_y, destination_x, destination_y, value.c_str());
                return false;
            }

            if (written[destination_y][destination_x] && HISTORY.back()[destination_y][destination_x] != value) {
                std::printf(
                    "Two different warp operators attempt to write different values into the same destination cell at the same destination time. "
                    "source_x=%d source_y=%d destination_x=%d destination_y=%d value0=%s value1=%s\n",
                    source_x, source_y, destination_x, destination_y,
                    HISTORY.back()[destination_y][destination_x].c_str(), value.c_str());
                return false;
            }

            HISTORY.back()[destination_y][destination_x] = value;
            written[destination_y][destination_x] = true;
        }

        return true;
    }

    HISTORY.push_back(new_board);

    return true;
}

int main3d(int argc, char* argv[])
{
    if (argc != 3) {
        std::printf("Usage: 3d (A) (B)\n");
        return -1;
    }

    Input(argv);

    std::vector<std::string> submitted;
    int num_total_turns = 1;
    while (submitted.empty()) {
        std::printf("num_total_turns=%d t=%d\n", num_total_turns, static_cast<int>(HISTORY.size()));

        if (!ProcessTurn(submitted)) {
            break;
        }

        for (const auto& row : HISTORY.back()) {
            for (int x = 0; x < row.size(); ++x) {
                if (x) {
                    std::printf(" ");
                }

                if (row[x] == "%") {
                    std::printf("%%");
                }
                else {
                    std::printf(row[x].c_str());
                }
            }
            std::printf("\n");
        }

        ++num_total_turns;
    }

    for (const auto& s : submitted) {
        if (submitted.front() != s) {
            std::printf("It is an error to submit multiple different values.\n");
        }
    }

    std::printf(submitted.front().c_str());
}
