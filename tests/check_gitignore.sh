#!/bin/bash
echo "Testing .gitignore configuration..."
echo ""

# Create a test file in test_datasets
mkdir -p test_datasets
touch test_datasets/test_file.csv

# Check if it's ignored
if git check-ignore test_datasets/test_file.csv > /dev/null 2>&1; then
    echo "✅ test_datasets/ is properly ignored"
else
    echo "❌ test_datasets/ is NOT ignored - please add it to .gitignore"
fi

# Clean up
rm -rf test_datasets/

echo ""
echo "Current .gitignore contents:"
echo "----------------------------"
cat .gitignore 2>/dev/null || echo "No .gitignore file found"

#chmod +x tests/check_gitignore.sh                       
#tests/check_gitignore.sh 