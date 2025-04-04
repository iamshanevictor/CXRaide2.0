# Render.com Deployment Guide for CXRaide

This guide explains how to deploy the CXRaide application to Render.com.

## 1. Deploy the Backend Service

1. Log in to your Render.com account and go to the Dashboard
2. Click "New" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:

   - **Name**: `cxraide-backend`
   - **Environment**: Docker
   - **Region**: Choose the one closest to your users
   - **Branch**: main (or your preferred branch)
   - **Build Command**: (leave blank, Docker will handle this)
   - **Start Command**: `gunicorn server.app:app --bind 0.0.0.0:$PORT --workers 2`

5. Add the following environment variables:

   ```
   DB_NAME=your_database_name
   FLASK_ENV=production
   MONGO_URI=your_mongodb_connection_string
   PORT=10000
   SECRET_KEY=your_secret_key
   ```

6. Click "Create Web Service"

## 2. Deploy the Frontend Service

1. Click "New" and select "Static Site"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `cxraide`
   - **Branch**: main (or your preferred branch)
   - **Root Directory**: (leave blank)
   - **Build Command**: `cd client && npm install && npm run build`
   - **Publish Directory**: `client/dist`
4. Add the following environment variables:

   ```
   VITE_API_URL=https://cxraide-backend.onrender.com
   ```

5. Click "Create Static Site"

## 3. Additional Setup

### Custom Domain (Optional)

1. In your service's settings, go to "Custom Domain"
2. Follow the instructions to add your domain

### Database Monitoring

1. Regularly check your MongoDB logs for any issues
2. Consider setting up monitoring through MongoDB Atlas

## 4. First-Time Login

After deployment, you can log in using the hardcoded admin credentials:

- Username: `admin`
- Password: `admin123`

**IMPORTANT**: This is only for initial setup. After deployment, you should:

1. Create proper user accounts
2. Remove or change the hardcoded admin credentials

## 5. Production Security Considerations

For production deployment, you should:

1. Remove the hardcoded admin credentials after setting up proper accounts
2. Remove the temporary verification bypasses once all users have migrated to the new password format
3. Set strong, unique values for SECRET_KEY and other sensitive environment variables
4. Set FLASK_ENV=production to ensure stricter security checks
5. Consider enabling HTTPS-only cookies for the JWT tokens

## 6. Troubleshooting

If you encounter issues:

1. Check the Render.com logs for both services
2. Verify that your environment variables are set correctly
3. Ensure your MongoDB connection string is correct and the database is accessible
4. Test API endpoints using tools like Postman or curl
5. Check browser console for any CORS errors

## 7. Ongoing Maintenance

1. Update the code in your GitHub repository as needed
2. Render.com will automatically deploy new changes
3. Monitor server logs for errors
4. Regularly back up your MongoDB database
