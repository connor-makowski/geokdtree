# Change to the script directory
cd "$(dirname "$0")"

# Remove the existing build directory.
sudo rm -r build
sudo rm -r ../geokdtree/bin

# Create a new build directory and navigate into it.
mkdir build
cd build

# Run CMake to configure the project and generate build files, then build the project.
cmake ..
cmake --build .

# Navigate back to the script directory.
cd ..

# Move the compiled binary to a 'bin' directory.
mkdir ../geokdtree/bin
touch ../geokdtree/bin/__init__.py
touch ../geokdtree/bin/.gitignore
printf "*\n!__init__.py\n!.gitignore" > ../geokdtree/bin/.gitignore

for f in build/*.so; do
    mv "$f" ../geokdtree/bin/
done

sudo rm -r build