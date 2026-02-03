# Vercel Deployment Guide

## Prerequisites
1. GitHub repository pushed: ✅ https://github.com/BilalHq38/Your-Story-Generator-AI.git
2. Vercel account: https://vercel.com

## Deploy Steps

### 1. Import Project to Vercel
1. Go to https://vercel.com/new
2. Import your GitHub repository: `BilalHq38/Your-Story-Generator-AI`
3. Vercel will auto-detect the configuration from `vercel.json`

### 2. Configure Environment Variables
Add these in Vercel Dashboard → Project → Settings → Environment Variables:

**Required:**
```
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=your_neon_postgres_url
SECRET_KEY=your_secret_jwt_key_here
```

**Optional:**
```
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://your-domain.vercel.app
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**Your Current Neon DB URL:**
```
postgresql://neondb_owner:npg_rhmEOP9adZ4X@ep-spring-tree-a5i8vbn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### 3. Build Configuration
Vercel will use settings from `vercel.json`:
- **Backend**: Serverless function at `/api/index.py`
- **Frontend**: Static build from `Frontend/dist`
- **Build command**: `npm run build` (in Frontend directory)

### 4. Deploy
1. Click "Deploy" in Vercel dashboard
2. Wait for build to complete (~2-3 minutes)
3. Your app will be live at: `https://your-project-name.vercel.app`

## Post-Deployment

### Run Database Migrations
After first deploy, run migrations via Vercel CLI or dashboard:
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link project
vercel link

# Run migration (in serverless function context)
# You may need to trigger this via an API endpoint or manually in Neon dashboard
```

**Alternative**: Run migrations locally against Neon DB before deploying:
```bash
cd Backend
alembic upgrade head
```

### Update CORS Origins
After deployment, update `ALLOWED_ORIGINS` environment variable in Vercel to include your production domain:
```
ALLOWED_ORIGINS=https://your-project-name.vercel.app,http://localhost:3000
```

## Verify Deployment

1. **Health Check**: Visit `https://your-domain.vercel.app/health`
2. **API Docs**: Visit `https://your-domain.vercel.app/docs`
3. **Frontend**: Visit `https://your-domain.vercel.app`

## Troubleshooting

### Build Fails
- Check build logs in Vercel dashboard
- Ensure `Frontend/package.json` has `build` script
- Verify TypeScript compiles: `cd Frontend && npm run build`

### API Returns 500
- Check function logs in Vercel dashboard
- Verify environment variables are set
- Check database connection (Neon must allow external connections)

### Frontend Shows Blank Page
- Check browser console for errors
- Verify API URL in `Frontend/src/api/client.ts`
- Ensure VITE_API_URL is set if needed

## Custom Domain (Optional)
1. Go to Vercel Dashboard → Project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update `ALLOWED_ORIGINS` to include custom domain

## Continuous Deployment
Vercel automatically deploys when you push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Your app will redeploy automatically!
