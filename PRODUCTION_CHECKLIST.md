# Production Configuration Checklist

This checklist covers important considerations for deploying to production.

## Security

- [ ] **JWT Secret**: Generate a strong random secret for JWT_SECRET
  ```bash
  openssl rand -hex 32
  ```
  
- [ ] **API Keys**: Never commit API keys to version control
  - Use environment variables for all keys
  - Rotate keys regularly
  - Use separate keys for development and production

- [ ] **CORS**: Update CORS_ORIGINS to only include your production domains
  ```
  CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
  ```

- [ ] **HTTPS**: Always use HTTPS in production
  - Most deployment platforms (Vercel, Netlify, Railway) provide this by default

- [ ] **Database**: Use PostgreSQL or another production database
  - SQLite is fine for development but not recommended for production with multiple instances
  ```
  DATABASE_URL=postgresql://user:password@host:5432/dbname
  ```

## Performance

- [ ] **Database Connection Pooling**: Configure connection pooling for production
  - SQLModel/SQLAlchemy handles this, but tune for your workload

- [ ] **Caching**: Consider adding caching for frequently accessed data
  - Redis for session storage
  - CDN for static assets

- [ ] **Rate Limiting**: Add rate limiting to prevent abuse
  ```python
  from slowapi import Limiter
  # Add to FastAPI app
  ```

## Monitoring

- [ ] **Error Tracking**: Set up error tracking
  - Sentry, Rollbar, or similar service
  
- [ ] **Logging**: Configure structured logging
  - Ship logs to a centralized service (DataDog, CloudWatch, etc.)

- [ ] **Health Checks**: Use the `/health` and `/api/health` endpoints
  - Set up uptime monitoring (UptimeRobot, Pingdom, etc.)

- [ ] **Metrics**: Track key metrics
  - Request rates
  - Error rates
  - Response times
  - Database query performance

## Scalability

- [ ] **Horizontal Scaling**: Ensure app is stateless
  - Store sessions in a shared store (Redis, database)
  - Use external storage for file uploads (S3, GCS)

- [ ] **Background Jobs**: For long-running tasks
  - Consider Celery, RQ, or similar job queue

- [ ] **CDN**: Use a CDN for static assets
  - Cloudflare, AWS CloudFront, etc.

## Backup and Recovery

- [ ] **Database Backups**: Set up automated database backups
  - Daily backups minimum
  - Test restore procedures

- [ ] **Disaster Recovery**: Document recovery procedures
  - What to do if the database fails
  - What to do if the API is down
  - What to do if there's a security breach

## Deployment Process

- [ ] **CI/CD**: Set up continuous deployment
  - GitHub Actions, GitLab CI, CircleCI, etc.
  - Run tests before deploying
  - Automated rollback on failures

- [ ] **Zero-Downtime Deployments**: Use rolling updates
  - Most platforms (Vercel, Railway) handle this automatically

- [ ] **Environment Variables**: Never hardcode configuration
  - Use platform environment variable management
  - Keep development and production configs separate

## Testing

- [ ] **Load Testing**: Test application under load
  - Use tools like Apache JMeter, k6, or Locust
  - Test both frontend and backend

- [ ] **Security Testing**: Run security scans
  - OWASP ZAP, Burp Suite
  - Regular dependency updates (`npm audit`, `pip-audit`)

## Documentation

- [ ] **API Documentation**: Keep API docs up to date
  - FastAPI provides automatic OpenAPI docs at `/docs`
  
- [ ] **Runbooks**: Document common operations
  - Deployment process
  - Rollback procedures
  - Troubleshooting guides

- [ ] **Architecture Diagrams**: Keep architecture documentation current

## Compliance

- [ ] **Data Privacy**: Ensure GDPR/CCPA compliance if applicable
  - Data retention policies
  - User data export/deletion

- [ ] **Terms of Service**: Have clear ToS and Privacy Policy

- [ ] **User Authentication**: Implement proper authentication
  - JWT tokens with expiration
  - Refresh token rotation
  - Account lockout after failed attempts

## Specific Platform Notes

### Replit
- Uses ephemeral storage - files may be lost on restart
- Consider external database (Neon, PlanetScale)
- Always-on requires paid plan

### Netlify
- Great for frontend, limited backend support
- Use serverless functions for API routes
- 125k serverless function requests/month on free tier

### Vercel
- Excellent for frontend and Node.js
- Serverless functions have execution time limits (10s hobby, 60s pro)
- Python backend needs separate hosting

### Railway
- Full backend support including Python
- PostgreSQL database included
- Pay per usage model

### Render
- Similar to Railway
- Free tier available with limitations (spins down after inactivity)
- Good for both Node.js and Python backends
