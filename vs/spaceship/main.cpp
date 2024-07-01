#include <iostream>

int main_spaceship(int argc, char* argv[]);
int main_full_search(int argc, char* argv[]);

int main(int argc, char* argv[]) {
    std::cout << "solve spaceship" << argv[1] << " ";

    //return main_spaceship(argc, argv);
    return main_full_search(argc, argv);
}
