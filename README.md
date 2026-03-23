# Project explanation & how to run

# 🛠️ Git & GitHub Commands (Step-by-Step)

---

## Step 1: Initialize Git Repository

```bash
git init
```

➡️ Creates a new Git repository in your project folder and starts tracking files.

---

## Step 2: Configure Git (First Time Only)

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

➡️ Sets your name and email for commits.

---

## Step 3: Check File Status

```bash
git status
```

➡️ Shows which files are:

* Untracked (new files)
* Modified (changed files)
* Staged (ready to commit)

---

## Step 4: Add Files to Staging Area

```bash
git add .
```

➡️ Adds all files to staging (ready to be saved).

---

## Step 5: Commit Changes

```bash
git commit -m "Initial commit"
```

➡️ Saves a snapshot of your project with a message.

---

## Step 6: Create Repository on GitHub

➡️ Go to GitHub and create a new repository.

---

## Step 7: Connect Local Project to GitHub

```bash
git remote add origin YOUR_REPOSITORY_URL
```

➡️ Links your local project to GitHub repository.

---

## Step 8: Set Main Branch

```bash
git branch -M main
```

➡️ Sets the default branch name to "main".

---

## Step 9: Push Project to GitHub (First Time)

```bash
git push -u origin main
```

➡️ Uploads your project to GitHub for the first time.

---

## Step 10: Make Changes in Code

➡️ Edit or add new code in your project using VS Code.

---

## Step 11: Check Changes Again

```bash
git status
```

➡️ Shows modified files after changes.

---

## Step 12: Add Updated Files

```bash
git add .
```

➡️ Adds updated files to staging.

---

## Step 13: Commit Updated Changes

```bash
git commit -m "Describe your changes"
```

➡️ Saves new changes.

---

## Step 14: Push Updates to GitHub

```bash
git push
```

➡️ Uploads latest changes to GitHub.

---

## Step 15: Ignore Unnecessary Files

Create `.gitignore` file and add:

```bash
fitness_env/
__pycache__/
*.pyc
```

➡️ Prevents unnecessary files from being uploaded.

---

## Step 16: Remove Already Tracked Files (if needed)

```bash
git rm -r --cached fitness_env
```

➡️ Stops tracking virtual environment files.

---

## Step 17: Delete Git and Start Fresh (Optional)

```bash
Remove-Item -Recurse -Force .git   # PowerShell
```

➡️ Deletes Git history and resets repository.

---

# 📌 Summary

* Git tracks changes locally
* GitHub stores code online
* Changes require: add → commit → push
* `.gitignore` prevents unwanted files

---
