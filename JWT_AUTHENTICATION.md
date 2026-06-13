# JWT Authentication & API Integration Guide


### Register
**Endpoint:** `POST /prototype/auth/register/`

```javascript
const res = await fetch('http://localhost:8000/prototype/auth/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'user@example.com',
        full_name: 'John Doe',
        password: 'password123',
        password2: 'password123'
    })
});

const data = await res.json();
if (res.ok) {
    localStorage.setItem('accessToken', data.access);
    localStorage.setItem('refreshToken', data.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
}
```

### Login
**Endpoint:** `POST /prototype/auth/login/`

```javascript
const res = await fetch('http://localhost:8000/prototype/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'password123'
    })
});

const data = await res.json();
if (res.ok) {
    localStorage.setItem('accessToken', data.access);
    localStorage.setItem('refreshToken', data.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
}
```

### Logout
**Endpoint:** `POST /prototype/auth/logout/`

```javascript
const refreshToken = localStorage.getItem('refreshToken');
const res = await fetch('http://localhost:8000/prototype/auth/logout/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
    },
    body: JSON.stringify({ refresh: refreshToken })
});

if (res.ok) {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
}
```

### Refresh Token
**Endpoint:** `POST /prototype/auth/token/refresh/`

```javascript
const refreshToken = localStorage.getItem('refreshToken');
const res = await fetch('http://localhost:8000/prototype/auth/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken })
});

const data = await res.json();
if (res.ok) {
    localStorage.setItem('accessToken', data.access);
}
```

## API Requests with Authentication

### Header Format
All API requests require the access token in the Authorization header:
```javascript
headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
}
```

### Upload Video
**Endpoint:** `POST /prototype/video/upload/`

```javascript
const formData = new FormData();
formData.append('original', videoFile);
formData.append('titre', 'Video Title');

const res = await fetch('http://localhost:8000/prototype/video/upload/', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` },
    body: formData
});
```

### Process Video
**Endpoint:** `POST /prototype/video/processing/`

```javascript
const res = await fetch('http://localhost:8000/prototype/video/processing/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
    },
    body: JSON.stringify({
        video_id: 1,
        action: 'trim',
        params: {
            start: '00:00:00',
            end: '00:00:10'
        }
    })
});
```

### Check Processing Status
**Endpoint:** `GET /prototype/video/processing/status/<video_id>/`

```javascript
const res = await fetch('http://localhost:8000/prototype/video/processing/status/1/', {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
});
```

### Create Reels
**Endpoint:** `POST /prototype/video/reel/`

```javascript
const res = await fetch('http://localhost:8000/prototype/video/reel/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
    },
    body: JSON.stringify({
        video_id: 1,
        params: {
            mode: 'classic',
            clips: [
                { start: '00:00:00', end: '00:00:10' },
                { start: '00:00:10', end: '00:00:20' }
            ]
        }
    })
});
```

### Export Video
**Endpoint:** `POST /prototype/video/export/`

```javascript
const res = await fetch('http://localhost:8000/prototype/video/export/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
    },
    body: JSON.stringify({
        video_id: 1,
        format: 'mp4',
        quality: 'medium'
    })
});
```

### Check Export Status
**Endpoint:** `GET /prototype/video/export/status/<task_id>/`

```javascript
const res = await fetch('http://localhost:8000/prototype/video/export/status/<task_id>/', {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
});
```

### Download Exported Video
**Endpoint:** `GET /prototype/video/export/download/<task_id>/`

```javascript
const res = await fetch('http://localhost:8000/prototype/video/export/download/<task_id>/', {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
});

const blob = await res.blob();
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'video.mp4';
a.click();
```

### Upload Watermark
**Endpoint:** `POST /prototype/watermark/upload/`

```javascript
const formData = new FormData();
formData.append('image', imageFile);

const res = await fetch('http://localhost:8000/prototype/watermark/upload/', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` },
    body: formData
});
```

## Error Handling

### Unauthorized (401)
If you get a 401 error, the token has expired. Use the refresh endpoint to get a new access token:

```javascript
if (error.status === 401) {
    const refreshToken = localStorage.getItem('refreshToken');
    const res = await fetch('http://localhost:8000/prototype/auth/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (res.ok) {
        const data = await res.json();
        localStorage.setItem('accessToken', data.access);
        // Retry original request with new token
    } else {
        // Token refresh failed, redirect to login
        window.location.href = '/login';
    }
}
```

## Testing

Visit these endpoints to test authentication:
- **Login/Register:** `http://localhost:8000/prototype/test/login/`
- **Logout:** `http://localhost:8000/prototype/test/logout/`
- **Process Video:** `http://localhost:8000/prototype/test/process/`
- **Export Video:** `http://localhost:8000/prototype/test/export/`

## Response Format

### Success (200/201/202)
```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe"
    },
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Error (400/401/404/500)
```json
{
    "error": "utilisateur non authentifie",
    "erreur": "Video introuvable ou acces refuse"
}
```

## Key Changes from Previous Version

- **User authentication required** for all API endpoints
- **JWT tokens** stored in localStorage (`accessToken`, `refreshToken`, `user`)
- **Token refresh** mechanism for expired access tokens
- **Per-user data isolation** - users only see their own videos
- **Logout endpoint** blacklists refresh tokens
