@echo off
cd /d c:\Users\srich\internship_project
git config user.email "dev@omnisight.local" > commit_output.txt 2>&1
git config user.name "OmniSight Dev" >> commit_output.txt 2>&1
git add backend/ >> commit_output.txt 2>&1
git commit -m "feat: Phase 2 - FastAPI backend foundation for OmniSight" >> commit_output.txt 2>&1
echo Exit: %ERRORLEVEL% >> commit_output.txt
