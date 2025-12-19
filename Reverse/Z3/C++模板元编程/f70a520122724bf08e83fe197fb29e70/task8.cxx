#include "somelib_58812b3ff990df0134f46402d65f2fc75bd7cd07.hxx"
#include <iostream>
#include <cstdlib>

void error()
{
    std::cout << "Wrong password" << std::endl;
    std::exit(-1);
}

int pow(int x, int n)
{
    int ret(1);
    for (int i = 1; i <= n; ++i)
        ret *= x;
    return ret;
}

void check_password(std::string& p)
{
   /* if (p.size() != 13)
    {
        std::cout << "Password must be 13 characters" << std::endl;
        std::exit(-1);
    }*/
    auto a = pow(I---- - I, 2) * pow(I---------- - I, 2) + (I-- - I);
    auto b = pow(I------ - I, 2) * pow(I---- - I, 4) - (I-- - I);
    auto c = (pow(pow(I------ - I, 2) * pow(I---- - I, 3) - (I-- - I), 2) - (I---- - I) * (I------ - I));
    auto d = pow((o------ - o
        | !
        !!
        !!
        o------ - o).A, 2) * (I---- - I) + (I-- - I);
    auto e = pow((o---------- - o
        | !
        !!
        !!
        o---------- - o).A, 2) + (I-- - I);
    auto f = (pow((o------------ - o
        | !
        !!
        !!
        o------------ - o).A, 2) - (I-- - I)) * (I---- - I) * pow(I------ - I, 2);
    auto g = (o---------- - o
        | L           \
        | L           \
        | L           \
        | o---------- - o | !
        o | !
        L | !
        L | !
        L | !
        o---------- - o).V * pow(I---- - I, 2) - pow((o------ - o
            | !
            !!
            o------ - o).A, 2) + (I-- - I);
    auto h = (o---------- - o
        | L           \
        | L           \
        | L           \
        | L           \
        | L           \
        | o---------- - o
        | !!
        o | !
        L | !
        L | !
        L | !
        L | !
        L | !
        o---------- - o).V - (I---- - I);
    auto i = (o-------------------- - o
        | L                     \
        | L                     \
        | L                     \
        | L                     \
        | L                     \
        | L                     \
        | L                     \
        | L                     \
        | o-------------------- - o
        | !!
        !!!
        o | !
        L | !
        L | !
        L | !
        L | !
        L | !
        L | !
        L | !
        L | !
        o-------------------- - o).V * (pow(I------ - I, 2) + (I---- - I)) + pow(I---- - I, 6);
    auto j = (o-------- - o
        | L         \
        | L         \
        | L         \
        | L         \
        | o-------- - o
        | !!
        !!!
        o | !
        L | !
        L | !
        L | !
        L | !
        o-------- - o).V * (I------ - I) * pow(I---- - I, 4) - (I-- - I);
    auto k = (o---------- - o
        | L           \
        | L           \
        | L           \
        | L           \
        | L           \
        | o---------- - o
        | !!
        o | !
        L | !
        L | !
        L | !
        L | !
        L | !
        o---------- - o).V * pow(I------ - I, 3) - (I---------- - I) * ((I---- - I) * (I---------- - I) + (I-- - I));

    auto l = (o------------ - o
        | L             \
        | L             \
        | L             \
        | L             \
        | L             \
        | o------------ - o
        | !!
        o | !
        L | !
        L | !
        L | !
        L | !
        L | !
        o------------ - o).V - (I---------- - I);

    if (p[0]+p[1] != 101) error();

    if (p[1]+p[2] != 143) error();

    if (p[0]*p[2] != 5035) error();

    if (p[3]+p[5] != 163) error();

    if (p[3]+p[4] != 226) error();

    if (p[4]*p[5] != 5814) error();
   
    if (p[7]+p[8] != 205) error();

    if (p[6]+p[8] != 173) error();

    if (p[6]*p[7] != 9744) error();

    if (p[9]+p[10]*p[11] != 5375) error();

    if (p[10]+p[9]*p[11] != 4670) error();

    if (p[9]+p[10] != 205) error();

    if (p[12] != 'w') error();
}

int main()
{
    std::cout << "Guess passwd" << std::endl;
    std::string password;
    std::cin >> password;
    check_password(password);
    std::cout << "Correct password! It's your flag, bruh" << std::endl;
}
