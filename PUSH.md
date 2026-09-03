# Initialize repo and push to GitHub

# 1. Init (only if not already a git repo)
git init

# 2. Configure local identity (only if not set globally)
# git config user.name "Your Name"
# git config user.email "you@example.com"

# 3. Stage everything (respects .gitignore)
git add .

# 4. Verify what's about to be committed
git status

# 5. First commit
git commit -m "Initial commit: file sorter CLI with --recursive and --dry-run"

# 6. Add remote — replace URL with your repo URL
git remote add origin https://github.com/YOUR_USERNAME/file-sorter.git

# 7. Push
git branch -M main
git push -u origin main