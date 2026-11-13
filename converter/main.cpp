
#include <iostream>  // Allows us to print text in the terminal.

int main()
{
    // This message confirms that C++ is running.
    std::cout << "My Video Converter is starting!\n";

    // This asks the user for a video link.
    std::string videoURL;

    std::cout << "Paste a video URL: ";
    std::getline(std::cin, videoURL);

    // Display the link to confirm that the input works.
    std::cout << "\nYou entered: " << videoURL << "\n";

    // Wait for the user to finish reading the output.
    std::cout << "\nPress Enter to close...";
    std::cin.get();

    return 0; // Tells Windows the program finished successfully.
}
