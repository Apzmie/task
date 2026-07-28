```
docker run -it python:3.11-slim bash
export AI_API_KEY=""

apt update
apt install -y git

git init
git config user.name "Your Name"
git config user.email "your@email.com"

git add .
git commit -m "initial project"

echo "# test" >> test.txt
git add test.txt
git commit -m "add test file"

echo "hello" >> test.txt
git status
git diff
```
