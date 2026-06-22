# Docker Guide

## Build and run

From `C:\Users\IT\Desktop\CMS\CMS`:

```powershell
docker compose up --build
```

Open:

```text
http://localhost:3000
```

The compose stack starts:

- `frontend`: React app served by Nginx on host port `3000`
- `backend`: FastAPI app on host port `8001`
- `mongo`: MongoDB on host port `27017`

## Use a real JWT secret

Create a `.env` file beside `docker-compose.yml`:

```env
JWT_SECRET=your-long-random-secret-here
```

Then run:

```powershell
docker compose up --build
```

## Move to another device

Copy the project folder to the new device, install Docker Desktop, then run:

```powershell
docker compose up --build
```

To stop:

```powershell
docker compose down
```

To stop and delete MongoDB data:

```powershell
docker compose down -v
```