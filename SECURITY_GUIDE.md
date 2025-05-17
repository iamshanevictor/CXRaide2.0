# CXRaide Security Guide

## Managing Credentials and Secrets

This document outlines best practices for managing credentials and secrets in the CXRaide project.

### MongoDB Credentials

1. **Never commit credentials to Git**
   - MongoDB connection strings contain your username and password
   - These should never be stored directly in code files
   - All `.env` files are already added to `.gitignore`

2. **Use Environment Variables**
   - Create a `.env` file in the `server/` directory with your credentials:
     ```
     MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/...
     DB_NAME=cxraide
     SECRET_KEY=your_secure_random_key
     ```
   - This file will be automatically loaded by the application

3. **For Docker Deployments**
   - Pass environment variables at runtime:
     ```
     docker run -e MONGO_URI=mongodb+srv://... -e DB_NAME=cxraide ...
     ```
   - Or use Docker Compose environment variables:
     ```yaml
     services:
       backend:
         environment:
           - MONGO_URI=mongodb+srv://...
           - DB_NAME=cxraide
     ```
   - For CI/CD platforms, use their secrets management features

4. **For Local Development**
   - Set environment variables in your terminal:
     - Windows: `$env:MONGO_URI="mongodb+srv://..."`
     - Linux/Mac: `export MONGO_URI="mongodb+srv://..."`
   - Or run the `run_backend.ps1` script which will prompt for credentials

### API Keys and Other Secrets

Follow the same principles for all other secrets:
1. Store in `.env` files locally
2. Use environment variables for deployment
3. Never commit directly in code

### Checking for Leaked Credentials

If you accidentally commit credentials:
1. Change your passwords immediately
2. Use tools like BFG Repo-Cleaner to remove the sensitive data from Git history
3. Force push to overwrite the remote repository
4. Contact your MongoDB Atlas administrators to reset credentials

Remember: Security is everyone's responsibility. When in doubt, err on the side of caution. 